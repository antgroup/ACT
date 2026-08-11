import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_ENV_FILE = resolve(HERE, "../metered-rest-provider/.env");

const REQUIRED_SELLER_FIELDS = [
  "ALIPAY_GATEWAY_URL",
  "ALIPAY_APP_ID",
  "ALIPAY_SELLER_ID",
  "ALIPAY_SELLER_NAME",
  "ALIPAY_SERVICE_ID",
  "ALIPAY_GOODS_NAME",
  "ALIPAY_RESOURCE_ID",
  "ALIPAY_AMOUNT",
];

const PLACEHOLDER = /replace-with|x{4,}|example|changeme|todo/i;

export function parseEnvText(text) {
  const result = {};
  for (const rawLine of String(text).split(/\r?\n/u)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const separator = line.indexOf("=");
    if (separator <= 0) continue;
    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if (
      (value.startsWith("\"") && value.endsWith("\"")) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    result[key] = value;
  }
  return result;
}

export function commandAvailable(command, args) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: "pipe",
  });
  return result.status === 0;
}

function secretConfigured(env, directName, fileName, fileExists) {
  const direct = env[directName];
  if (direct && !PLACEHOLDER.test(direct)) return true;
  const path = env[fileName];
  return Boolean(path && !PLACEHOLDER.test(path) && fileExists(path));
}

export function inspectSandboxReadiness({
  envFile = DEFAULT_ENV_FILE,
  envFileExists = existsSync(envFile),
  envText = envFileExists ? readFileSync(envFile, "utf8") : "",
  fileExists = existsSync,
  commands = {
    npm: commandAvailable("npm", ["--version"]),
    alipayBot: commandAvailable("alipay-bot", ["--help"]),
    java: commandAvailable("java", ["-version"]),
    maven: commandAvailable("mvn", ["-version"]),
  },
} = {}) {
  const failures = [];
  const env = parseEnvText(envText);

  if (!commands.npm) failures.push("npm is missing");
  if (!commands.alipayBot) failures.push("official alipay-bot is missing");
  if (!commands.java) failures.push("JDK 8+ is missing");
  if (!commands.maven) failures.push("Maven 3.8+ is missing");
  if (!envFileExists) {
    failures.push("seller .env is missing");
  } else {
    for (const field of REQUIRED_SELLER_FIELDS) {
      const value = env[field];
      if (!value) {
        failures.push(`${field} is missing`);
      } else if (PLACEHOLDER.test(value)) {
        failures.push(`${field} still contains a placeholder`);
      }
    }
    if (
      !secretConfigured(
        env,
        "ALIPAY_PRIVATE_KEY",
        "ALIPAY_PRIVATE_KEY_FILE",
        fileExists,
      )
    ) {
      failures.push("Alipay application private key is not configured");
    }
    if (
      !secretConfigured(
        env,
        "ALIPAY_ALIPAY_PUBLIC_KEY",
        "ALIPAY_ALIPAY_PUBLIC_KEY_FILE",
        fileExists,
      )
    ) {
      failures.push("Alipay public key is not configured");
    }
  }

  return {
    status: failures.length ? "not-ready" : "local-preflight-passed",
    failures,
    checks: {
      npm: commands.npm,
      official_alipay_bot: commands.alipayBot,
      java: commands.java,
      maven: commands.maven,
      seller_env: envFileExists,
      seller_required_fields:
        envFileExists &&
        REQUIRED_SELLER_FIELDS.every(
          (field) => env[field] && !PLACEHOLDER.test(env[field]),
        ),
      seller_private_key: envFileExists
        ? secretConfigured(
            env,
            "ALIPAY_PRIVATE_KEY",
            "ALIPAY_PRIVATE_KEY_FILE",
            fileExists,
          )
        : false,
      alipay_public_key: envFileExists
        ? secretConfigured(
            env,
            "ALIPAY_ALIPAY_PUBLIC_KEY",
            "ALIPAY_ALIPAY_PUBLIC_KEY_FILE",
            fileExists,
          )
        : false,
    },
    external_steps: [
      "Complete AIPay sandbox product activation and service registration.",
      "Start the seller service and obtain its reachable paid-resource URL.",
      "Use the official buyer Skill/CLI with an explicit user-authorized sandbox payment.",
      "Record only sanitized evidence; never export full proof, keys, tokens, or replayable requests.",
    ],
  };
}

function printHuman(result) {
  console.log(`Sandbox local preflight: ${result.status}`);
  for (const [name, passed] of Object.entries(result.checks)) {
    console.log(`${passed ? "PASS" : "FAIL"}: ${name}`);
  }
  for (const failure of result.failures) {
    console.error(`ACTION: ${failure}`);
  }
  console.log(
    "This command does not create an order, initiate payment, or claim sandbox success.",
  );
}

function main() {
  const result = inspectSandboxReadiness();
  if (process.argv.includes("--json")) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printHuman(result);
  }
  if (result.failures.length) process.exitCode = 1;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main();

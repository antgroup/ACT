import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const OFFICIAL_INSTALL_COMMAND =
  "npx -y @alipay/agent-payment@latest install";

export function parseNodeMajor(version = process.versions.node) {
  const major = Number.parseInt(String(version).split(".")[0], 10);
  return Number.isFinite(major) ? major : 0;
}

export function parseNpmMajor(version) {
  const major = Number.parseInt(String(version || "").trim().split(".")[0], 10);
  return Number.isFinite(major) ? major : 0;
}

export function commandVersion(command, args = ["--version"]) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: "pipe",
  });
  return result.status === 0 ? String(result.stdout || "").trim() : "";
}

export function commandAvailable(command, args = ["--version"]) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: "pipe",
  });
  return result.status === 0;
}

export function runPreflight() {
  const failures = [];
  const nodeMajor = parseNodeMajor();
  const npmVersion = commandVersion("npm");
  const npmMajor = parseNpmMajor(npmVersion);

  if (nodeMajor < 22) {
    failures.push(`Node.js 22+ is required by the current AIPay guide; found ${process.versions.node}.`);
  }
  if (!npmVersion) {
    failures.push("npm is not available on PATH.");
  } else if (npmMajor < 10) {
    failures.push(`npm 10+ is required by the current AIPay guide; found ${npmVersion}.`);
  }

  const cliInstalled = commandAvailable("alipay-bot", ["--help"]);
  return { failures, cliInstalled };
}

function main() {
  const result = runPreflight();
  console.log(`Node.js: ${process.versions.node}`);
  console.log(`npm: ${commandVersion("npm") || "missing"}`);
  console.log(`alipay-bot: ${result.cliInstalled ? "available" : "not found"}`);
  console.log(`Official install: ${OFFICIAL_INSTALL_COMMAND}`);

  if (result.failures.length) {
    for (const failure of result.failures) console.error(`ERROR: ${failure}`);
    process.exitCode = 1;
    return;
  }

  console.log("Preflight passed. Installation and payment remain official Alipay steps.");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main();

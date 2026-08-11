import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const OFFICIAL_INSTALL_COMMAND =
  "npx -y @alipay/agent-payment@latest install";

export function parseNodeMajor(version = process.versions.node) {
  const major = Number.parseInt(String(version).split(".")[0], 10);
  return Number.isFinite(major) ? major : 0;
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

  if (nodeMajor < 18) {
    failures.push(`Node.js 18+ is required; found ${process.versions.node}.`);
  }
  if (!commandAvailable("npm")) {
    failures.push("npm is not available on PATH.");
  }

  const cliInstalled = commandAvailable("alipay-bot", ["--help"]);
  return { failures, cliInstalled };
}

function main() {
  const result = runPreflight();
  console.log(`Node.js: ${process.versions.node}`);
  console.log(`npm: ${commandAvailable("npm") ? "available" : "missing"}`);
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

#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { runDemo } from "../../examples/end-to-end-demo.ts";
import { runConformance } from "../conformance/runner.ts";
import { startSandboxServer } from "../http/server.ts";

function print(value: unknown): void {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

async function readInput(argument: string | undefined): Promise<Record<string, unknown>> {
  if (!argument) {
    throw new Error("A JSON object or @file path is required");
  }
  const source = argument.startsWith("@")
    ? await readFile(argument.slice(1), "utf8")
    : argument;
  const value: unknown = JSON.parse(source);
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error("Input must be a JSON object");
  }
  return value as Record<string, unknown>;
}

async function request(
  method: string,
  path: string,
  body?: Record<string, unknown>,
): Promise<unknown> {
  const baseUrl = process.env.ACT_TSD_CRD_BASE_URL ?? "http://127.0.0.1:8787";
  const response = await fetch(new URL(path, baseUrl), {
    method,
    headers: body ? { "content-type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const payload: unknown = await response.json();
  if (!response.ok) {
    throw new Error(`Sandbox returned HTTP ${response.status}: ${JSON.stringify(payload)}`);
  }
  return payload;
}

function usage(): string {
  return [
    "Usage:",
    "  act-tsd-crd demo run",
    "  act-tsd-crd conformance",
    "  act-tsd-crd serve [port]",
    "  act-tsd-crd association request '<json>' | @file",
    "  act-tsd-crd association prepare <request-id>",
    "  act-tsd-crd association confirm-attested <request-id>",
    "  act-tsd-crd association confirm-direct <request-id> '<json>' | @file",
    "  act-tsd-crd credential status <credential-id>",
    "  act-tsd-crd credential revoke <credential-id> '<json>' | @file",
    "  act-tsd-crd authorization create '<json>' | @file",
    "  act-tsd-crd authorization revoke <authorization-id> '<json>' | @file",
    "  act-tsd-crd verify '<json>' | @file",
    "",
    "Set ACT_TSD_CRD_BASE_URL to call a running Sandbox. Default: http://127.0.0.1:8787",
  ].join("\n");
}

async function main(args: string[]): Promise<void> {
  const [group, action, ...rest] = args;

  if (group === "demo" && action === "run") {
    return print(runDemo());
  }
  if (group === "conformance" && action === undefined) {
    const report = runConformance();
    print(report);
    if (!report.passed) process.exitCode = 1;
    return;
  }
  if (group === "serve") {
    const port = action ? Number(action) : undefined;
    if (port !== undefined && !Number.isInteger(port)) {
      throw new Error(`Invalid port: ${action}`);
    }
    startSandboxServer({ port });
    return;
  }
  if (group === "association" && action === "request") {
    return print(await request("POST", "/v1/association-applications", await readInput(rest[0])));
  }
  if (group === "association" && action === "prepare") {
    if (!rest[0]) throw new Error("request-id is required");
    return print(await request(
      "POST",
      `/v1/association-applications/${encodeURIComponent(rest[0])}/preparations`,
      {},
    ));
  }
  if (group === "association" && action === "confirm-attested") {
    if (!rest[0]) throw new Error("request-id is required");
    return print(await request(
      "POST",
      `/v1/association-applications/${encodeURIComponent(rest[0])}/confirmations`,
      { confirmationMethod: "ATTESTED_CONFIRMATION" },
    ));
  }
  if (group === "association" && action === "confirm-direct") {
    if (!rest[0]) throw new Error("request-id is required");
    return print(await request(
      "POST",
      `/v1/association-applications/${encodeURIComponent(rest[0])}/confirmations`,
      await readInput(rest[1]),
    ));
  }
  if (group === "credential" && action === "status") {
    if (!rest[0]) throw new Error("credential-id is required");
    return print(await request(
      "GET",
      `/v1/association-credentials/${encodeURIComponent(rest[0])}/status`,
    ));
  }
  if (group === "credential" && action === "revoke") {
    if (!rest[0]) throw new Error("credential-id is required");
    return print(await request(
      "POST",
      `/v1/association-credentials/${encodeURIComponent(rest[0])}/revocations`,
      await readInput(rest[1]),
    ));
  }
  if (group === "authorization" && action === "create") {
    return print(await request("POST", "/v1/credit-query-authorizations", await readInput(rest[0])));
  }
  if (group === "authorization" && action === "revoke") {
    if (!rest[0]) throw new Error("authorization-id is required");
    return print(await request(
      "POST",
      `/v1/credit-query-authorizations/${encodeURIComponent(rest[0])}/revocations`,
      await readInput(rest[1]),
    ));
  }
  if (group === "verify") {
    const input = action ?? rest[0];
    return print(await request("POST", "/v1/verifications", await readInput(input)));
  }

  process.stdout.write(`${usage()}\n`);
  if (group && group !== "help" && group !== "--help" && group !== "-h") {
    process.exitCode = 1;
  }
}

main(process.argv.slice(2)).catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});

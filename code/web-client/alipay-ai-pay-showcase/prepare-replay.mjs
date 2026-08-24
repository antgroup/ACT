import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { parseEvents, validateEvents } from "./validate-evidence.mjs";

const FORBIDDEN_TEXT = [
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/i,
  /\b(?:access_token|app_auth_token|payment-proof|client_session|binding_code|password)\b/i,
  /\bsk-[A-Za-z0-9_-]{12,}\b/,
];

export function createReplay(events, { validationId, reviewedBy, ackSanitized }) {
  const live = validateEvents(events);
  if (live.mode !== "LIVE_SANDBOX") throw new Error("replay input must be LIVE_SANDBOX evidence");
  if (!validationId?.trim()) throw new Error("--validation-id is required");
  if (!reviewedBy?.trim()) throw new Error("--reviewed-by is required");
  if (ackSanitized !== true) throw new Error("--ack-sanitized is required after manual review");

  const serialized = JSON.stringify(events);
  for (const pattern of FORBIDDEN_TEXT) {
    if (pattern.test(serialized)) throw new Error(`evidence contains forbidden sensitive text: ${pattern}`);
  }

  const replay = events.map((event) => ({
    ...event,
    mode: "SANITIZED_REPLAY",
    sanitized: true,
    origin_validation_id: validationId.trim(),
    sanitization_review_ref: reviewedBy.trim(),
  }));
  validateEvents(replay);
  return replay;
}

function parseArguments(args) {
  const [path, ...options] = args;
  const parsed = { path, ackSanitized: false };
  for (let index = 0; index < options.length; index += 1) {
    const option = options[index];
    if (option === "--ack-sanitized") {
      parsed.ackSanitized = true;
      continue;
    }
    const value = options[index + 1];
    if (!value) throw new Error(`${option} requires a value`);
    if (option === "--validation-id") parsed.validationId = value;
    else if (option === "--reviewed-by") parsed.reviewedBy = value;
    else throw new Error(`unsupported option: ${option}`);
    index += 1;
  }
  return parsed;
}

async function main() {
  const options = parseArguments(process.argv.slice(2));
  if (!options.path) {
    throw new Error(
      "usage: node prepare-replay.mjs live.ndjson --validation-id <id> --reviewed-by <ref> --ack-sanitized",
    );
  }
  const replay = createReplay(parseEvents(await readFile(options.path, "utf8")), options);
  process.stdout.write(`${replay.map((event) => JSON.stringify(event)).join("\n")}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    process.stderr.write(`[FAIL] ${error.message}\n`);
    process.exitCode = 1;
  });
}

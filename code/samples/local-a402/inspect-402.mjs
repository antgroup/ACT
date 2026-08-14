import { fileURLToPath } from "node:url";

const REQUIRED_PROTOCOL_FIELDS = [
  "method_id", "method_version", "out_trade_no", "amount", "currency",
  "resource_id", "pay_before", "seller_unique_id", "request_method",
  "request_fingerprint", "replay_window_seconds", "signer_id",
  "signature_content", "signature_type",
];

export function decodePaymentNeeded(header) {
  if (!header || header.length > 32 * 1024) {
    throw new Error("Payment-Needed is missing or too large");
  }
  let value;
  try {
    value = JSON.parse(Buffer.from(header, "base64url").toString("utf8"));
  } catch {
    throw new Error("Payment-Needed must be Base64URL-encoded UTF-8 JSON");
  }
  assertObject(value.protocol, "protocol");
  assertObject(value.method, "method");
  for (const field of REQUIRED_PROTOCOL_FIELDS) {
    if (value.protocol[field] === undefined || value.protocol[field] === "") {
      throw new Error("protocol." + field + " is required");
    }
  }
  if (!/^[A-Z]{3}$/.test(value.protocol.currency)) {
    throw new Error("protocol.currency must be a three-letter uppercase code");
  }
  if (Number.isNaN(Date.parse(value.protocol.pay_before))) {
    throw new Error("protocol.pay_before must be an ISO 8601 timestamp");
  }
  if (!/^sha-256:[A-Za-z0-9_-]{43}$/.test(value.protocol.request_fingerprint)) {
    throw new Error("protocol.request_fingerprint must use sha-256 Base64URL format");
  }
  return value;
}

export function sanitizedSummary(value) {
  return {
    method_id: value.protocol.method_id,
    amount: value.protocol.amount,
    currency: value.protocol.currency,
    resource_id: value.protocol.resource_id,
    pay_before: value.protocol.pay_before,
    psp_id: value.method.psp_id,
  };
}

export async function inspectPaymentRequirement(url) {
  const response = await fetch(url, { redirect: "manual" });
  if (response.status !== 402) {
    throw new Error("Expected HTTP 402, received " + response.status);
  }
  const decoded = decodePaymentNeeded(response.headers.get("payment-needed"));
  return { status: response.status, decoded, summary: sanitizedSummary(decoded) };
}

function assertObject(value, path) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(path + " must be an object");
  }
}

async function main(url) {
  const result = await inspectPaymentRequirement(url);
  console.log(JSON.stringify(result.summary, null, 2));
  console.log("Payment requirement inspection passed. No payment was performed.");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const url = process.argv[2];
  if (!url) {
    console.error("Usage: npm run inspect -- <paid-resource-url>");
    process.exitCode = 2;
  } else {
    main(url).catch((error) => {
      console.error("Inspection failed: " + error.message);
      process.exitCode = 1;
    });
  }
}

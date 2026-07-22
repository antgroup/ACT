import { fileURLToPath } from "node:url";

const REQUIRED_PROTOCOL_FIELDS = [
  "out_trade_no",
  "amount",
  "currency",
  "resource_id",
  "pay_before",
  "seller_signature",
  "seller_sign_type",
  "seller_unique_id",
];

const REQUIRED_METHOD_FIELDS = [
  "seller_name",
  "seller_id",
  "seller_app_id",
  "goods_name",
  "seller_unique_id_key",
  "service_id",
];

export function decodePaymentNeeded(header) {
  if (!header || header.length > 32 * 1024) {
    throw new Error("Payment-Needed is missing or too large");
  }
  const value = JSON.parse(Buffer.from(header, "base64url").toString("utf8"));
  assertObject(value.protocol, "protocol");
  assertObject(value.method, "method");
  assertFields(value.protocol, REQUIRED_PROTOCOL_FIELDS, "protocol");
  assertFields(value.method, REQUIRED_METHOD_FIELDS, "method");
  if (value.protocol.seller_sign_type !== "RSA2") {
    throw new Error("protocol.seller_sign_type must be RSA2 for the current Alipay profile");
  }
  if (Number.isNaN(Date.parse(value.protocol.pay_before))) {
    throw new Error("protocol.pay_before must be an ISO8601 timestamp");
  }
  return value;
}

export function sanitizedSummary(value) {
  return {
    amount: value.protocol.amount,
    currency: value.protocol.currency,
    resource_id: value.protocol.resource_id,
    pay_before: value.protocol.pay_before,
    seller_name: value.method.seller_name,
    goods_name: value.method.goods_name,
    sign_type: value.protocol.seller_sign_type,
  };
}

async function inspect(url) {
  const response = await fetch(url, { redirect: "manual" });
  if (response.status !== 402) {
    throw new Error(`Expected HTTP 402, received ${response.status}`);
  }
  const decoded = decodePaymentNeeded(response.headers.get("payment-needed"));
  console.log(JSON.stringify(sanitizedSummary(decoded), null, 2));
  console.log("Payment requirement inspection passed. No payment was performed.");
}

function assertObject(value, path) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${path} must be an object`);
  }
}

function assertFields(value, fields, path) {
  for (const field of fields) {
    if (typeof value[field] !== "string" || value[field].length === 0) {
      throw new Error(`${path}.${field} is required`);
    }
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const url = process.argv[2];
  if (!url) {
    console.error("Usage: npm run inspect -- <paid-resource-url>");
    process.exitCode = 2;
  } else {
    inspect(url).catch((error) => {
      console.error(`Inspection failed: ${error.message}`);
      process.exitCode = 1;
    });
  }
}

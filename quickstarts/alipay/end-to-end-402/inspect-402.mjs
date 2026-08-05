import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const PAYMENT_NEEDED_PROFILE_SCHEMA = JSON.parse(
  readFileSync(
    new URL(
      "../../../profiles/alipay-ai-pay/schemas/payment-needed.preview.schema.json",
      import.meta.url,
    ),
    "utf8",
  ),
);

const REQUIRED_PROTOCOL_FIELDS =
  PAYMENT_NEEDED_PROFILE_SCHEMA.properties.protocol.required;
const REQUIRED_METHOD_FIELDS =
  PAYMENT_NEEDED_PROFILE_SCHEMA.properties.method.required;

export function decodePaymentNeeded(header) {
  if (!header || header.length > 32 * 1024) {
    throw new Error("Payment-Needed is missing or too large");
  }
  const value = JSON.parse(Buffer.from(header, "base64url").toString("utf8"));
  assertObject(value.protocol, "protocol");
  assertObject(value.method, "method");
  assertFields(value.protocol, REQUIRED_PROTOCOL_FIELDS, "protocol");
  assertFields(value.method, REQUIRED_METHOD_FIELDS, "method");
  const requiredSignType =
    PAYMENT_NEEDED_PROFILE_SCHEMA.properties.protocol.properties.seller_sign_type
      .const;
  if (value.protocol.seller_sign_type !== requiredSignType) {
    throw new Error("protocol.seller_sign_type must be RSA2 for the current Alipay profile");
  }
  const currencyPattern = new RegExp(
    PAYMENT_NEEDED_PROFILE_SCHEMA.properties.protocol.properties.currency.pattern,
  );
  if (!currencyPattern.test(value.protocol.currency)) {
    throw new Error("protocol.currency must be a three-letter uppercase code");
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

export async function inspectPaymentRequirement(url) {
  const response = await fetch(url, { redirect: "manual" });
  if (response.status !== 402) {
    throw new Error(`Expected HTTP 402, received ${response.status}`);
  }
  const decoded = decodePaymentNeeded(response.headers.get("payment-needed"));
  return {
    status: response.status,
    decoded,
    summary: sanitizedSummary(decoded),
  };
}

async function inspect(url) {
  const result = await inspectPaymentRequirement(url);
  console.log(JSON.stringify(result.summary, null, 2));
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

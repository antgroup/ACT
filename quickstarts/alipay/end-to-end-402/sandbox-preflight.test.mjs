import assert from "node:assert/strict";
import test from "node:test";

import {
  inspectSandboxReadiness,
  parseEnvText,
} from "./sandbox-preflight.mjs";

const COMPLETE_ENV = `
ALIPAY_GATEWAY_URL=https://openapi-sandbox.dl.alipaydev.com/gateway.do
ALIPAY_APP_ID=2026000000000001
ALIPAY_PRIVATE_KEY_FILE=/safe/app-private-key.txt
ALIPAY_ALIPAY_PUBLIC_KEY_FILE=/safe/alipay-public-key.txt
ALIPAY_SELLER_ID=2088000000000001
ALIPAY_SELLER_NAME=Sandbox merchant
ALIPAY_SERVICE_ID=service-001
ALIPAY_GOODS_NAME=ACT sandbox resource
ALIPAY_RESOURCE_ID=resource-001
ALIPAY_AMOUNT=0.01
`;

test("parses env assignments without evaluating shell content", () => {
  const parsed = parseEnvText("A=value\nB='quoted value'\n# ignored\n");
  assert.deepEqual(parsed, { A: "value", B: "quoted value" });
});

test("reports a complete local sandbox preflight without initiating payment", () => {
  const result = inspectSandboxReadiness({
    envFileExists: true,
    envText: COMPLETE_ENV,
    fileExists: () => true,
    commands: {
      npm: true,
      alipayBot: true,
      java: true,
      maven: true,
    },
  });
  assert.equal(result.status, "local-preflight-passed");
  assert.deepEqual(result.failures, []);
});

test("reports missing configuration by field name and never returns values", () => {
  const result = inspectSandboxReadiness({
    envFileExists: true,
    envText: "ALIPAY_APP_ID=replace-with-sandbox-app-id\n",
    fileExists: () => false,
    commands: {
      npm: true,
      alipayBot: false,
      java: true,
      maven: true,
    },
  });
  assert.equal(result.status, "not-ready");
  assert.ok(result.failures.includes("official alipay-bot is missing"));
  assert.ok(
    result.failures.includes("ALIPAY_APP_ID still contains a placeholder"),
  );
  assert.equal(JSON.stringify(result).includes("replace-with-sandbox-app-id"), false);
});

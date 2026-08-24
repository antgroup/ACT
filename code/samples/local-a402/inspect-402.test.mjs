import assert from "node:assert/strict";
import test from "node:test";

import { decodePaymentNeeded, sanitizedSummary } from "./inspect-402.mjs";
import { createSampleRequirement } from "./sample-server.mjs";

test("decodes a channel-neutral A402 Payment-Needed value", () => {
  const requirement = createSampleRequirement(new Date("2026-08-12T00:00:00Z"));
  const encoded = Buffer.from(JSON.stringify(requirement), "utf8").toString("base64url");
  assert.deepEqual(decodePaymentNeeded(encoded), requirement);
});

test("summary excludes signatures and order identifiers", () => {
  const summary = sanitizedSummary(createSampleRequirement());
  assert.equal(summary.amount, "0.01");
  assert.equal(summary.resource_id, "professional-data-sample");
  assert.equal("signature_content" in summary, false);
  assert.equal("out_trade_no" in summary, false);
});

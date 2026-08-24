import assert from "node:assert/strict";
import test from "node:test";

import { demoAssociationRequest } from "../src/adapters/mock-providers.ts";
import {
  antiReplayValue,
  validateAssociationApplication,
} from "../src/application/validation.ts";

test("validates the reference-v1 demo association application", () => {
  const application = validateAssociationApplication(demoAssociationRequest());
  assert.equal(application.confirmationMethod, "ATTESTED_CONFIRMATION");
  assert.equal(application.agentId, "agent-demo-shopping");
  assert.equal(
    antiReplayValue(application.antiReplay),
    "nonce:demo-association-nonce-001",
  );
});

test("rejects a short anti-replay nonce", () => {
  const input = {
    ...demoAssociationRequest(),
    antiReplay: { nonce: "short" },
  };
  assert.throws(
    () => validateAssociationApplication(input),
    /antiReplay requires nonce or idempotencyKey/,
  );
});

test("rejects an unsupported confirmation method", () => {
  const input = {
    ...demoAssociationRequest(),
    confirmationMethod: "AGENT_SIGNATURE",
  };
  assert.throws(
    () => validateAssociationApplication(input),
    /Unsupported confirmationMethod/,
  );
});

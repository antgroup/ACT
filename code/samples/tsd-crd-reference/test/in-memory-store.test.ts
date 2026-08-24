import assert from "node:assert/strict";
import test from "node:test";

import { InMemoryStore } from "../src/adapters/in-memory-store.ts";

test("replay keys are consumed exactly once", () => {
  const store = new InMemoryStore();
  assert.equal(store.consumeReplayKey("application", "nonce-1"), true);
  assert.equal(store.consumeReplayKey("application", "nonce-1"), false);
  assert.equal(store.consumeReplayKey("verification", "nonce-1"), true);
});

test("stored values are cloned on read", () => {
  const store = new InMemoryStore();
  store.saveAssociationRequest({
    applicationId: "app-1",
    status: "PENDING",
    antiReplay: { nonce: "0123456789abcdef" },
    createdAt: "2026-08-12T00:00:00.000Z",
    updatedAt: "2026-08-12T00:00:00.000Z",
  });
  const first = store.getAssociationRequest("app-1");
  assert.ok(first);
  first.status = "REVOKED";
  assert.equal(store.getAssociationRequest("app-1")?.status, "PENDING");
});

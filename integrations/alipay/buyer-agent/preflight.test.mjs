import assert from "node:assert/strict";
import test from "node:test";

import {
  OFFICIAL_INSTALL_COMMAND,
  parseNodeMajor,
  parseNpmMajor,
} from "./preflight.mjs";

test("parses supported Node versions", () => {
  assert.equal(parseNodeMajor("18.20.0"), 18);
  assert.equal(parseNodeMajor("22.1.0"), 22);
  assert.equal(parseNodeMajor("invalid"), 0);
});

test("parses the official npm minimum", () => {
  assert.equal(parseNpmMajor("10.8.2"), 10);
  assert.equal(parseNpmMajor("9.9.4"), 9);
  assert.equal(parseNpmMajor("invalid"), 0);
});

test("pins the public installer name without executing it", () => {
  assert.equal(
    OFFICIAL_INSTALL_COMMAND,
    "npx -y @alipay/agent-payment@latest install",
  );
});

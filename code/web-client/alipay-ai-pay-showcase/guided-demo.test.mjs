import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const index = await readFile(new URL("./public/index.html", import.meta.url), "utf8");
const app = await readFile(new URL("./public/app.js", import.meta.url), "utf8");
const packageJson = JSON.parse(await readFile(new URL("./package.json", import.meta.url), "utf8"));

test("offers guided L1, L2, and L3 scenarios", () => {
  for (const level of ["L1", "L2", "L3"]) {
    assert.match(index, new RegExp(`value="${level}"`));
    assert.match(app, new RegExp(`${level}: \\[`));
  }
});

test("does not expose a sandbox, live-event, or evidence-replay mode", () => {
  const published = `${index}\n${app}\n${JSON.stringify(packageJson.scripts)}`;
  for (const marker of ["LIVE_SANDBOX", "SANITIZED_REPLAY", "liveTab", "replayTab", "连接官方沙箱事件", "证据回放"]) {
    assert.equal(published.includes(marker), false, `unexpected demo mode: ${marker}`);
  }
});

test("keeps the demo explicitly non-operational", () => {
  assert.match(index, /不会连接或执行真实支付/);
  assert.equal(packageJson.scripts.emit, undefined);
  assert.equal(packageJson.scripts["adapt:buyer"], undefined);
  assert.equal(packageJson.scripts["prepare:replay"], undefined);
});

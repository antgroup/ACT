import { inspectPaymentRequirement } from "./inspect-402.mjs";
import { SAMPLE_SIGNATURE, startSampleServer } from "./sample-server.mjs";

function closeServer(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

async function main() {
  const { server, baseUrl } = await startSampleServer();
  try {
    console.log("ACT local A402 sample (NON-PAYABLE)");
    const inspected = await inspectPaymentRequirement(baseUrl + "/paid-resource");
    if (inspected.decoded.protocol.signature_content !== SAMPLE_SIGNATURE) {
      throw new Error("The local sample marker is missing");
    }
    const retry = await fetch(baseUrl + "/paid-resource", {
      headers: { "Payment-Proof": "NON_PAYABLE_FAKE_PROOF" },
    });
    const body = await retry.json();
    if (
      retry.status !== 402 ||
      retry.headers.get("X-ACT-Sample-Mode") !== "non-payable" ||
      body.resource_delivered !== false
    ) {
      throw new Error("The sample must reject unverified proof and withhold the resource");
    }
    console.log(JSON.stringify(inspected.summary, null, 2));
    console.log("PASS: challenge decoded; fake proof rejected; no resource delivered.");
  } finally {
    await closeServer(server);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});

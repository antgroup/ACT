import { inspectPaymentRequirement } from "./inspect-402.mjs";
import { PREVIEW_MARKER, startPreviewServer } from "./local-preview-server.mjs";

function closeServer(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

async function main() {
  const { server, baseUrl } = await startPreviewServer();

  try {
    console.log("ACT local A402 Golden Path (NON-PAYABLE)");
    const inspected = await inspectPaymentRequirement(`${baseUrl}/paid-resource`);

    if (inspected.decoded.protocol.seller_signature !== PREVIEW_MARKER) {
      throw new Error("The local preview marker is missing");
    }

    const retry = await fetch(`${baseUrl}/paid-resource`, {
      headers: { "Payment-Proof": "NON_PAYABLE_FAKE_PROOF" },
    });
    const retryBody = await retry.json();

    if (
      retry.status !== 402 ||
      retry.headers.get("X-ACT-Preview-Mode") !== "non-payable" ||
      retryBody.resource_delivered !== false
    ) {
      throw new Error("The preview must reject proof and withhold the resource");
    }

    console.log(JSON.stringify(inspected.summary, null, 2));
    console.log("PASS: challenge decoded; fake proof rejected; no resource delivered.");
    console.log("Next: use the official Alipay Skill flow for a real sandbox payment.");
  } finally {
    await closeServer(server);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});

import http from "node:http";
import { fileURLToPath } from "node:url";

export const SAMPLE_SIGNATURE = "Tk9OX1BBWUFCTEVfTE9DQUxfU0FNUExF";

export function createSampleRequirement(now = new Date()) {
  return {
    protocol: {
      method_id: "example:a402/local",
      method_version: "1.0.0",
      out_trade_no: "LOCAL-SAMPLE-ORDER",
      amount: "0.01",
      currency: "CNY",
      resource_id: "professional-data-sample",
      pay_before: new Date(now.getTime() + 10 * 60 * 1000).toISOString(),
      seller_unique_id: "local-sample-seller",
      request_method: "GET",
      request_fingerprint: "sha-256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
      replay_window_seconds: 600,
      signer_id: "local-sample-key",
      signature_content: SAMPLE_SIGNATURE,
      signature_type: "ED25519",
    },
    method: {
      psp_id: "example-psp",
      endpoint: "https://example.invalid/pay",
    },
  };
}

export function encodePaymentNeeded(requirement) {
  return Buffer.from(JSON.stringify(requirement), "utf8").toString("base64url");
}

function sendJson(response, status, body, headers = {}) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  response.end(JSON.stringify(body, null, 2) + "\n");
}

export function createSampleServer() {
  return http.createServer((request, response) => {
    const requestUrl = new URL(request.url ?? "/", "http://localhost");
    if (requestUrl.pathname === "/health") {
      sendJson(response, 200, { status: "ok", mode: "non-payable-local-sample" });
      return;
    }
    if (requestUrl.pathname !== "/paid-resource") {
      sendJson(response, 404, {
        error: "NOT_FOUND",
        available_paths: ["/health", "/paid-resource"],
      });
      return;
    }
    const proofWasSupplied = Boolean(request.headers["payment-proof"]);
    sendJson(
      response,
      402,
      {
        error: "LOCAL_SAMPLE_NO_PAYMENT",
        payment_performed: false,
        resource_delivered: false,
        message: proofWasSupplied
          ? "The local sample rejects unverified Payment-Proof and withholds paid content."
          : "Inspect Payment-Needed locally; use a product integration for real payment.",
      },
      {
        "Payment-Needed": encodePaymentNeeded(createSampleRequirement()),
        "X-ACT-Sample-Mode": "non-payable",
      },
    );
  });
}

export function startSampleServer({ host = "127.0.0.1", port = 0 } = {}) {
  const server = createSampleServer();
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, () => {
      server.removeListener("error", reject);
      const address = server.address();
      if (!address || typeof address === "string") {
        reject(new Error("Could not determine the local sample address"));
        return;
      }
      resolve({ server, baseUrl: "http://" + host + ":" + address.port });
    });
  });
}

async function main() {
  const port = Number.parseInt(process.env.ACT_SAMPLE_PORT ?? "18080", 10);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("ACT_SAMPLE_PORT must be an integer between 1 and 65535");
  }
  const { baseUrl } = await startSampleServer({ port });
  console.log("ACT local A402 sample: " + baseUrl + "/paid-resource");
  console.log("The sample never performs payment or delivers paid content.");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

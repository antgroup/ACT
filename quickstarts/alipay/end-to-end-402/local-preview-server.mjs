import http from "node:http";
import { fileURLToPath } from "node:url";

export const PREVIEW_MARKER = "NON_PAYABLE_LOCAL_PREVIEW";

export function createPreviewBill(now = new Date()) {
  return {
    protocol: {
      out_trade_no: "act_local_preview_order",
      amount: "0.01",
      currency: "CNY",
      resource_id: "act://local-preview/paid-resource",
      pay_before: new Date(now.getTime() + 10 * 60 * 1000).toISOString(),
      seller_signature: PREVIEW_MARKER,
      seller_sign_type: "RSA2",
      seller_unique_id: "act-local-preview-seller",
    },
    method: {
      seller_name: "ACT local preview",
      seller_id: "LOCAL_PREVIEW_ONLY",
      seller_app_id: "LOCAL_PREVIEW_ONLY",
      goods_name: "Non-payable A402 preview resource",
      seller_unique_id_key: "seller_id",
      service_id: "LOCAL_PREVIEW_ONLY",
    },
  };
}

export function encodePaymentNeeded(bill) {
  return Buffer.from(JSON.stringify(bill), "utf8").toString("base64url");
}

function sendJson(response, status, body, headers = {}) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  response.end(`${JSON.stringify(body, null, 2)}\n`);
}

export function createPreviewServer() {
  return http.createServer((request, response) => {
    const requestUrl = new URL(request.url ?? "/", "http://localhost");

    if (requestUrl.pathname === "/health") {
      sendJson(response, 200, {
        status: "ok",
        mode: "non-payable-local-preview",
      });
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
        error: "LOCAL_PREVIEW_NO_PAYMENT",
        preview: true,
        payment_performed: false,
        resource_delivered: false,
        message: proofWasSupplied
          ? "This local preview never validates Payment-Proof or delivers paid content."
          : "Inspect Payment-Needed locally; use the official Alipay flow for real payment.",
      },
      {
        "Payment-Needed": encodePaymentNeeded(createPreviewBill()),
        "X-ACT-Preview-Mode": "non-payable",
      },
    );
  });
}

export function startPreviewServer({ host = "127.0.0.1", port = 0 } = {}) {
  const server = createPreviewServer();

  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, () => {
      server.removeListener("error", reject);
      const address = server.address();
      if (!address || typeof address === "string") {
        reject(new Error("Could not determine the local preview address"));
        return;
      }
      resolve({
        server,
        baseUrl: `http://${host}:${address.port}`,
      });
    });
  });
}

async function main() {
  const requestedPort = Number.parseInt(process.env.ACT_PREVIEW_PORT ?? "18080", 10);
  if (!Number.isInteger(requestedPort) || requestedPort < 1 || requestedPort > 65535) {
    throw new Error("ACT_PREVIEW_PORT must be an integer between 1 and 65535");
  }

  const { baseUrl } = await startPreviewServer({ port: requestedPort });
  console.log("ACT non-payable local preview is running.");
  console.log(`Inspect: node inspect-402.mjs ${baseUrl}/paid-resource`);
  console.log("It never validates a proof, performs payment, or delivers paid content.");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

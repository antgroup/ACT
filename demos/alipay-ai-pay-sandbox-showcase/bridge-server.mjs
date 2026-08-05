import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { assertNoSensitiveFields, statesForScenario, validateEvidenceEvent } from "./validate-evidence.mjs";

const types = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};

const displayFields = new Set([
  "state",
  "source",
  "evidence_ref",
  "amount",
  "currency",
  "resource_id",
  "goods_name",
  "seller_name",
  "result_summary",
  "scenario",
  "correlation_ref",
  "method_id",
  "psp_id",
  "request_ref",
  "request_digest",
  "http_method",
  "order_ref",
  "transaction_ref",
  "fulfillment_ref",
  "validation_mapping",
  "recovery_action",
]);

export function createDemoServer({ root, host = "127.0.0.1", port = 4173 }) {
  const clients = new Set();
  const events = [];
  let scenario = "SUCCESS";
  let listeningPort = null;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url, `http://${request.headers.host || `${host}:${port}`}`);

    if (request.method === "GET" && url.pathname === "/events") {
      response.writeHead(200, {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-store",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
      });
      response.write(": ACT demo event stream\n\n");
      events.forEach((event) => response.write(`data: ${JSON.stringify(event)}\n\n`));
      clients.add(response);
      request.on("close", () => clients.delete(response));
      return;
    }

    if (request.method === "GET" && url.pathname === "/events/state") {
      const requiredStates = statesForScenario(scenario);
      sendJson(response, 200, {
        scenario,
        event_count: events.length,
        next_state: requiredStates[events.length] || null,
        complete: events.length === requiredStates.length,
      });
      return;
    }

    if (request.method === "GET" && url.pathname === "/events/export") {
      const requiredStates = statesForScenario(scenario);
      if (events.length !== requiredStates.length) {
        sendJson(response, 409, {
          error: "evidence_incomplete",
          scenario,
          event_count: events.length,
          expected_count: requiredStates.length,
          next_state: requiredStates[events.length] || null,
        });
        return;
      }
      response.writeHead(200, {
        "Content-Type": "application/x-ndjson; charset=utf-8",
        "Content-Disposition": "attachment; filename=act-live-sandbox-evidence.ndjson",
        "Cache-Control": "no-store",
      });
      response.end(`${events.map((event) => JSON.stringify(event)).join("\n")}\n`);
      return;
    }

    if (request.method === "POST" && url.pathname === "/events/reset") {
      try {
        const body = await readOptionalJson(request);
        const nextScenario = body?.scenario || "SUCCESS";
        const requiredStates = statesForScenario(nextScenario);
        scenario = nextScenario;
        events.splice(0, events.length);
        broadcast(clients, "event: reset\ndata: {}\n\n");
        sendJson(response, 200, { scenario, event_count: 0, next_state: requiredStates[0] });
      } catch (error) {
        sendJson(response, 400, { error: "reset_rejected", message: error.message });
      }
      return;
    }

    if (request.method === "POST" && url.pathname === "/events") {
      try {
        const input = await readJson(request);
        assertNoSensitiveFields(input);
        if (events.length === 0 && input.scenario) scenario = input.scenario;
        const event = normalizeEvent(input, events.length, scenario);
        validateEvidenceEvent(event, events.length, "LIVE_SANDBOX", scenario);
        const prior = events.at(-1);
        if (prior && Date.parse(event.occurred_at) < Date.parse(prior.occurred_at)) {
          throw new Error("event timestamps must not move backwards");
        }
        events.push(event);
        broadcast(clients, `data: ${JSON.stringify(event)}\n\n`);
        sendJson(response, 202, event);
      } catch (error) {
        sendJson(response, 400, { error: "event_rejected", message: error.message });
      }
      return;
    }

    if (request.method !== "GET" && request.method !== "HEAD") {
      sendJson(response, 405, { error: "method_not_allowed" });
      return;
    }

    await serveStatic(root, url.pathname, request.method, response);
  });

  return {
    async start() {
      await new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(port, host, () => {
          server.removeListener("error", reject);
          listeningPort = server.address().port;
          resolve();
        });
      });
    },
    port() {
      if (listeningPort === null) throw new Error("server is not listening");
      return listeningPort;
    },
    async close() {
      clients.forEach((client) => client.end());
      clients.clear();
      if (!server.listening) return;
      await new Promise((resolve, reject) =>
        server.close((error) => error ? reject(error) : resolve()));
    },
  };
}

function normalizeEvent(input, index, scenario) {
  const event = {
    sequence: index + 1,
    mode: "LIVE_SANDBOX",
    environment: "SANDBOX",
    scenario,
    occurred_at: input.occurred_at || new Date().toISOString(),
  };
  for (const key of displayFields) {
    if (input[key] !== undefined) event[key] = input[key];
  }
  return event;
}

async function readOptionalJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 4 * 1024) throw new Error("reset body is too large");
    chunks.push(chunk);
  }
  if (chunks.length === 0) return null;
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new Error("event body is not valid JSON");
  }
}

async function readJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 32 * 1024) throw new Error("event body is too large");
    chunks.push(chunk);
  }
  if (chunks.length === 0) throw new Error("event body is empty");
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new Error("event body is not valid JSON");
  }
}

function broadcast(clients, message) {
  clients.forEach((client) => client.write(message));
}

async function serveStatic(root, pathname, method, response) {
  const candidate = normalize(join(root, pathname === "/" ? "index.html" : pathname));
  if (!candidate.startsWith(`${root}/`) && candidate !== root) {
    sendJson(response, 403, { error: "forbidden" });
    return;
  }
  try {
    const metadata = await stat(candidate);
    const path = metadata.isDirectory() ? join(candidate, "index.html") : candidate;
    const body = method === "HEAD" ? null : await readFile(path);
    response.writeHead(200, {
      "Content-Type": types[extname(path)] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    response.end(body);
  } catch {
    sendJson(response, 404, { error: "not_found" });
  }
}

function sendJson(response, status, body) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  response.end(JSON.stringify(body));
}

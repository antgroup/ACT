import { createServer as createNodeServer, type IncomingMessage, type ServerResponse } from "node:http";
import { pathToFileURL } from "node:url";
import { createReferenceSuite, type ReferenceSuite } from "../application/reference-suite.ts";

const MAX_BODY_BYTES = 1024 * 1024;

class HttpError extends Error {
  statusCode: number;
  code: string;

  constructor(statusCode: number, code: string, message: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

async function readJson(request: IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = [];
  let size = 0;

  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > MAX_BODY_BYTES) {
      throw new HttpError(413, "PAYLOAD_TOO_LARGE", "Request body exceeds 1 MiB");
    }
    chunks.push(buffer);
  }

  if (chunks.length === 0) {
    return {};
  }

  try {
    const value: unknown = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    if (value === null || Array.isArray(value) || typeof value !== "object") {
      throw new Error("JSON body must be an object");
    }
    return value as Record<string, unknown>;
  } catch (error) {
    throw new HttpError(
      400,
      "INVALID_JSON",
      error instanceof Error ? error.message : "Invalid JSON body",
    );
  }
}

function sendJson(response: ServerResponse, statusCode: number, body: unknown): void {
  response.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
  });
  response.end(`${JSON.stringify(body, null, 2)}\n`);
}

function methodNotAllowed(response: ServerResponse): void {
  sendJson(response, 405, {
    error: { code: "METHOD_NOT_ALLOWED", message: "Method not allowed" },
  });
}

export function createSandboxServer(suite: ReferenceSuite = createReferenceSuite()) {
  return createNodeServer(async (request, response) => {
    const method = request.method ?? "GET";
    const url = new URL(request.url ?? "/", "http://localhost");

    try {
      if (url.pathname === "/health") {
        if (method !== "GET") return methodNotAllowed(response);
        return sendJson(response, 200, {
          status: "ok",
          service: "tsd-crd-reference-sandbox",
          profile: "reference-v1",
        });
      }

      if (url.pathname === "/v1/association-applications") {
        if (method !== "POST") return methodNotAllowed(response);
        const result = suite.createAssociationRequest(await readJson(request));
        return sendJson(response, 201, suite.protocolAssociationApplication(result));
      }

      const preparationMatch = url.pathname.match(
        /^\/v1\/association-applications\/([^/]+)\/preparations$/,
      );
      if (preparationMatch) {
        if (method !== "POST") return methodNotAllowed(response);
        const result = suite.prepareDirectConfirmation(
          decodeURIComponent(preparationMatch[1]),
        );
        return sendJson(response, 200, result);
      }

      const confirmationMatch = url.pathname.match(
        /^\/v1\/association-applications\/([^/]+)\/confirmations$/,
      );
      if (confirmationMatch) {
        if (method !== "POST") return methodNotAllowed(response);
        const result = suite.confirmAssociation(
          decodeURIComponent(confirmationMatch[1]),
          await readJson(request),
        );
        return sendJson(response, 201, result.credential);
      }

      const credentialMatch = url.pathname.match(
        /^\/v1\/association-credentials\/([^/]+)$/,
      );
      if (credentialMatch) {
        if (method !== "GET") return methodNotAllowed(response);
        const result = suite.getCredential(decodeURIComponent(credentialMatch[1]));
        if (!result) {
          throw new HttpError(404, "ASSOCIATION_CREDENTIAL_NOT_FOUND", "Credential not found");
        }
        return sendJson(response, 200, result);
      }

      const statusMatch = url.pathname.match(
        /^\/v1\/association-credentials\/([^/]+)\/status$/,
      );
      if (statusMatch) {
        if (method !== "GET") return methodNotAllowed(response);
        const result = suite.getCredentialStatus(decodeURIComponent(statusMatch[1]));
        if (!result) {
          throw new HttpError(404, "ASSOCIATION_CREDENTIAL_NOT_FOUND", "Credential not found");
        }
        return sendJson(response, 200, result);
      }

      const lifecycleMatch = url.pathname.match(
        /^\/v1\/association-credentials\/([^/]+)\/(suspensions|resumptions|revocations)$/,
      );
      if (lifecycleMatch) {
        if (method !== "POST") return methodNotAllowed(response);
        const targetByOperation = {
          suspensions: "SUSPENDED",
          resumptions: "ACTIVE",
          revocations: "REVOKED",
        } as const;
        const body = await readJson(request);
        const credentialId = decodeURIComponent(lifecycleMatch[1]);
        const targetStatus = targetByOperation[
          lifecycleMatch[2] as keyof typeof targetByOperation
        ];
        const result = suite.changeCredentialStatusFromRequest(
          credentialId,
          targetStatus,
          body,
        );
        return sendJson(response, 200, result);
      }

      if (url.pathname === "/v1/credit-query-authorizations") {
        if (method !== "POST") return methodNotAllowed(response);
        const result = suite.createQueryAuthorization(await readJson(request));
        return sendJson(response, 201, result);
      }

      const authorizationRevokeMatch = url.pathname.match(
        /^\/v1\/credit-query-authorizations\/([^/]+)\/revocations$/,
      );
      if (authorizationRevokeMatch) {
        if (method !== "POST") return methodNotAllowed(response);
        const body = await readJson(request);
        const authorizationId = decodeURIComponent(authorizationRevokeMatch[1]);
        const result = suite.revokeQueryAuthorizationFromRequest(
          authorizationId,
          body,
        );
        return sendJson(response, 200, result);
      }

      if (url.pathname === "/v1/verifications") {
        if (method !== "POST") return methodNotAllowed(response);
        const result = suite.verify(await readJson(request));
        return sendJson(response, 200, result);
      }

      if (url.pathname === "/v1/demo/reset") {
        if (method !== "POST") return methodNotAllowed(response);
        suite.reset();
        return sendJson(response, 200, { reset: true });
      }

      return sendJson(response, 404, {
        error: { code: "NOT_FOUND", message: "Route not found" },
      });
    } catch (error) {
      if (error instanceof HttpError) {
        return sendJson(response, error.statusCode, {
          error: { code: error.code, message: error.message },
        });
      }

      const message = error instanceof Error ? error.message : "Unexpected error";
      const isNotFound = /not found/i.test(message);
      return sendJson(response, isNotFound ? 404 : 400, {
        error: {
          code: isNotFound ? "NOT_FOUND" : "INVALID_REQUEST",
          message,
        },
      });
    }
  });
}

export function startSandboxServer(options: { port?: number; host?: string } = {}) {
  const port = options.port ?? Number(process.env.PORT ?? 8787);
  const host = options.host ?? process.env.HOST ?? "127.0.0.1";
  const server = createSandboxServer();
  server.listen(port, host, () => {
    const address = server.address();
    const actualPort = typeof address === "object" && address ? address.port : port;
    process.stdout.write(
      `ACT TSD-CRD reference sandbox listening on http://${host}:${actualPort}\n`,
    );
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  startSandboxServer();
}

import { readFileSync, readdirSync } from "node:fs";
import { verify as verifyEd25519 } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { demoAssociationRequest } from "../adapters/mock-providers.ts";
import { validateAssociationApplication } from "../application/validation.ts";
import {
  canTransitionStatus,
  createAuthorization,
  createMappingTrace,
  generateEd25519KeyPair,
  issueAttestedCredential,
  issueDirectCredential,
  REASON_CODES,
  VERIFICATION_RESULTS,
  verifyCredentialProof,
  type AssociationCredential,
} from "../core/index.ts";

export type ConformanceCheck = {
  id: string;
  passed: boolean;
  detail?: string;
};

export type ConformanceReport = {
  profile: "reference-v1";
  passed: boolean;
  total: number;
  passedCount: number;
  failedCount: number;
  checks: ConformanceCheck[];
};

function check(id: string, action: () => void): ConformanceCheck {
  try {
    action();
    return { id, passed: true };
  } catch (error) {
    return {
      id,
      passed: false,
      detail: error instanceof Error ? error.message : String(error),
    };
  }
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function credentialDraft(): AssociationCredential {
  return {
    credentialId: "credential-conformance-001",
    credentialVersion: "reference-v1",
    associationApplicationId: "application-conformance-001",
    agentId: "agent-conformance-001",
    subjectId: "subject-conformance-001",
    associationRole: "OPERATOR",
    issuerId: "issuer-conformance-001",
    relationshipEvidenceRef: "urn:acp:relationship:conformance-001",
    confirmationMethod: "ATTESTED_CONFIRMATION",
    subjectCreditAssertionRef: "urn:acp:credit-assertion:conformance-001",
    associatedCreditValue: { level: "A" },
    creditSource: "ASSOCIATED_CREDIT",
    mappingPolicy: { id: "conformance-mapping", version: "1.0" },
    confirmationStatement: "The subject confirms the relationship.",
    purpose: "CONFORMANCE_TEST",
    scope: ["test"],
    associationApplicationRequestedAt: "2026-08-12T00:00:00.000Z",
    associationApplicationAntiReplay: { nonce: "conformance-direct-nonce-001" },
    issuedAt: "2026-08-12T00:00:00.000Z",
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2030-01-01T00:00:00.000Z",
    statusQuery: { uri: "/v1/association-credentials/credential-conformance-001/status" },
    issuerSignature: "",
    issuerSignatureAlgorithm: "",
  };
}

type JsonVector = {
  kind: "valid" | "invalid";
  name: string;
  value: unknown;
};

type Ed25519Vector = {
  algorithm: "Ed25519";
  canonicalPayload: string;
  publicKey: string;
  signature: string;
  expectedValid: boolean;
};

type ReasonCodeVector = {
  operation: "verificationReasonCode";
  expectedResult: string;
  expectedReasonCode: string;
  expectedValid: true;
};

function loadJsonVectors(): JsonVector[] {
  const currentDir = dirname(fileURLToPath(import.meta.url));
  const vectorsRoot = join(
    currentDir,
    "..",
    "..",
    "..",
    "..",
    "schemas",
    "tsd-crd",
    "reference-v1",
    "test-vectors",
  );
  const vectors: JsonVector[] = [];
  for (const kind of ["valid", "invalid"] as const) {
    const directory = join(vectorsRoot, kind);
    let files: string[] = [];
    try {
      files = readdirSync(directory).filter((file) => file.endsWith(".json"));
    } catch {
      continue;
    }
    for (const file of files) {
      vectors.push({
        kind,
        name: `${kind}/${file}`,
        value: JSON.parse(readFileSync(join(directory, file), "utf8")),
      });
    }
  }
  return vectors;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && !Array.isArray(value) && typeof value === "object";
}

function vectorById(vectors: JsonVector[], id: string): JsonVector {
  const vector = vectors.find(
    ({ value }) => isRecord(value) && value.id === id,
  );
  assert(vector !== undefined, `Missing test vector: ${id}`);
  return vector;
}

function asEd25519Vector(vector: JsonVector): Ed25519Vector {
  assert(isRecord(vector.value), `${vector.name} must contain a JSON object`);
  const value = vector.value;
  assert(value.algorithm === "Ed25519", `${vector.name} must use Ed25519`);
  assert(
    typeof value.canonicalPayload === "string",
    `${vector.name} canonicalPayload must be a string`,
  );
  assert(typeof value.publicKey === "string", `${vector.name} publicKey must be a string`);
  assert(typeof value.signature === "string", `${vector.name} signature must be a string`);
  assert(
    typeof value.expectedValid === "boolean",
    `${vector.name} expectedValid must be a boolean`,
  );
  return value as Ed25519Vector;
}

function executeEd25519Vector(vector: JsonVector): boolean {
  const value = asEd25519Vector(vector);
  try {
    return verifyEd25519(
      null,
      Buffer.from(value.canonicalPayload, "utf8"),
      value.publicKey,
      Buffer.from(value.signature, "base64url"),
    );
  } catch {
    return false;
  }
}

function reasonCodeVectors(vectors: JsonVector[]): ReasonCodeVector[] {
  return vectors.flatMap(({ value, name }) => {
    if (!isRecord(value) || value.operation !== "verificationReasonCode") return [];
    assert(
      typeof value.expectedReasonCode === "string",
      `${name} expectedReasonCode must be a string`,
    );
    assert(
      typeof value.expectedResult === "string",
      `${name} expectedResult must be a string`,
    );
    assert(value.expectedValid === true, `${name} must be a valid outcome vector`);
    return [value as ReasonCodeVector];
  });
}

export function runConformance(): ConformanceReport {
  const issuerKeys = generateEd25519KeyPair("issuer-conformance#key-1");
  const subjectKeys = generateEd25519KeyPair("subject-conformance#key-1");
  const vectors = loadJsonVectors();
  const checks: ConformanceCheck[] = [
    check("ASC.APPLICATION.BASELINE", () => {
      const value = validateAssociationApplication(demoAssociationRequest());
      assert(value.messageVersion === "reference-v1", "Wrong profile version");
    }),
    check("MAP.TRACEABILITY.TRIAD", () => {
      const mapping = createMappingTrace({
        subjectCreditAssertionRef: "urn:acp:assertion:1",
        associatedCreditValue: { level: "A" },
        mappingPolicy: { id: "policy-1", version: "1" },
      });
      assert(mapping.creditSource === "ASSOCIATED_CREDIT", "Wrong credit source");
    }),
    check("ASC.ATTESTED.ONE_SIGNATURE_LAYER", () => {
      const credential = issueAttestedCredential({
        credential: credentialDraft(),
        issuerPrivateKey: issuerKeys.privateKey,
      });
      assert(credential.issuerSignature.length > 0, "Issuer signature missing");
      assert(credential.subjectSignature === undefined, "Subject signature must be absent");
      assert(credential.subjectPublicKey === undefined, "Subject public key must be absent");
      assert(verifyCredentialProof({ credential, issuerPublicKey: issuerKeys.publicKey }), "Proof invalid");
    }),
    check("ASC.DIRECT.TWO_SIGNATURE_LAYERS", () => {
      const credential = issueDirectCredential({
        credential: credentialDraft(),
        subjectPrivateKey: subjectKeys.privateKey,
        subjectPublicKey: subjectKeys.publicKey,
        issuerPrivateKey: issuerKeys.privateKey,
      });
      assert(credential.subjectSignature?.length, "Subject signature missing");
      assert(credential.issuerSignature.length > 0, "Issuer signature missing");
      assert(verifyCredentialProof({ credential, issuerPublicKey: issuerKeys.publicKey }), "Proof invalid");
    }),
    check("LCM.TERMINAL.REVOKED", () => {
      assert(!canTransitionStatus("REVOKED", "ACTIVE"), "REVOKED must be terminal");
    }),
    check("LCM.TERMINAL.EXPIRED", () => {
      assert(!canTransitionStatus("EXPIRED", "ACTIVE"), "EXPIRED must be terminal");
    }),
    check("AUTH.PER_REQUEST.BOUND_REQUEST", () => {
      const authorizationKeys = generateEd25519KeyPair(
        "subject-conformance#authorization-key-1",
      );
      const authorization = createAuthorization({
        authorizationId: "authorization-conformance-001",
        mode: "PER_REQUEST",
        subjectId: "subject-conformance-001",
        relyingPartyIds: ["rp-conformance-001"],
        agentIds: ["agent-conformance-001"],
        purpose: "CONFORMANCE_TEST",
        allowedDataItems: ["associatedCreditValue"],
        validFrom: "2026-01-01T00:00:00.000Z",
        expiresAt: "2030-01-01T00:00:00.000Z",
        boundRequestId: "verification-conformance-001",
        subjectPrivateKey: authorizationKeys.privateKey,
        subjectKeyId: authorizationKeys.keyId,
      });
      assert(authorization.boundRequestId === "verification-conformance-001", "Request binding missing");
    }),
    check("VECTORS.JSON.PARSE", () => {
      assert(vectors.length > 0, "No JSON test vectors found");
    }),
    check("VECTORS.EXPECTED_VALID.DIRECTORY_SEMANTICS", () => {
      let declarations = 0;
      for (const vector of vectors) {
        assert(isRecord(vector.value), `${vector.name} must contain a JSON object`);
        if (!("expectedValid" in vector.value)) continue;
        declarations += 1;
        assert(
          typeof vector.value.expectedValid === "boolean",
          `${vector.name} expectedValid must be a boolean`,
        );
        const expectedForDirectory = vector.kind === "valid";
        assert(
          vector.value.expectedValid === expectedForDirectory,
          `${vector.name} declares expectedValid=${String(vector.value.expectedValid)} `
            + `but is stored under ${vector.kind}/`,
        );
      }
      assert(declarations > 0, "No expectedValid declarations found");
    }),
    check("VECTORS.REASON_CODES.COMPLETE", () => {
      const reasonVectors = reasonCodeVectors(vectors);
      const covered = new Set(reasonVectors.map((vector) => vector.expectedReasonCode));
      const missing = REASON_CODES.filter((reasonCode) => !covered.has(reasonCode));
      const unknown = [...covered].filter(
        (reasonCode) => !REASON_CODES.includes(reasonCode as never),
      );
      assert(missing.length === 0, `Missing reason-code vectors: ${missing.join(", ")}`);
      assert(unknown.length === 0, `Unknown reason codes in vectors: ${unknown.join(", ")}`);
      assert(
        reasonVectors.every((vector) =>
          VERIFICATION_RESULTS.includes(vector.expectedResult as never)),
        "Reason-code vectors contain an unsupported verification result",
      );
    }),
    check("CRYPTO.ED25519.FIXED.VALID", () => {
      const vector = vectorById(vectors, "canonical-ed25519-verification");
      const value = asEd25519Vector(vector);
      assert(value.expectedValid, `${vector.name} must expect a valid signature`);
      assert(executeEd25519Vector(vector), "Fixed Ed25519 signature did not verify");
    }),
    check("CRYPTO.ED25519.FIXED.TAMPERED", () => {
      const vector = vectorById(vectors, "canonical-ed25519-tampered");
      const value = asEd25519Vector(vector);
      assert(!value.expectedValid, `${vector.name} must expect an invalid signature`);
      assert(!executeEd25519Vector(vector), "Tampered Ed25519 payload unexpectedly verified");
    }),
  ];

  const passedCount = checks.filter((entry) => entry.passed).length;
  return {
    profile: "reference-v1",
    passed: passedCount === checks.length,
    total: checks.length,
    passedCount,
    failedCount: checks.length - passedCount,
    checks,
  };
}

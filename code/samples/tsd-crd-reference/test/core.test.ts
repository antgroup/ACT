import assert from "node:assert/strict";
import test from "node:test";

import {
  canonicalize,
  createAuthorization,
  createMappingTrace,
  evaluateAuthorization,
  generateEd25519KeyPair,
  issueAttestedCredential,
  issueDirectCredential,
  issueDirectCredentialFromConfirmation,
  revokeAuthorization,
  signCanonical,
  transitionStatus,
  verifyAssociationCredential,
  verifyAuthorizationProof,
  verifyAssociatedCredit,
  verifyCanonicalSignature,
  verifyCredentialProof,
  type AssociationCredential,
} from "../src/core/index.ts";

const now = "2026-08-12T00:00:00.000Z";
const issuer = generateEd25519KeyPair("issuer#1");
const subject = generateEd25519KeyPair("subject#1");

function credentialDraft(overrides: Record<string, unknown> = {}) {
  return {
    credentialId: "credential-1",
    credentialVersion: "reference-v1",
    associationApplicationId: "application-1",
    agentId: "agent-1",
    subjectId: "subject-1",
    associationRole: "OPERATOR",
    issuerId: "issuer-1",
    relationshipEvidenceRef: "evidence-1",
    subjectCreditAssertionRef: "assertion-1",
    associatedCreditValue: { band: "A", limit: "1000" },
    creditSource: "ASSOCIATED_CREDIT",
    mappingPolicy: { id: "demo-map", version: "1" },
    confirmationStatement: "I confirm the stated association.",
    purpose: "PURCHASE_RISK_CHECK",
    scope: ["shopping"],
    associationApplicationRequestedAt: "2026-01-01T00:00:00.000Z",
    associationApplicationAntiReplay: { nonce: "core-direct-signature-nonce-001" },
    issuedAt: now,
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    statusQuery: { uri: "https://issuer.example/status/credential-1" },
    ...overrides,
  };
}

test("canonical JSON is deterministic and rejects non-interoperable values", () => {
  assert.equal(
    canonicalize({ z: 1, a: { y: true, x: [3, 2, 1] } }),
    '{"a":{"x":[3,2,1],"y":true},"z":1}',
  );
  assert.throws(() => canonicalize(-0), /negative zero/);
  assert.throws(() => canonicalize({ value: undefined }), /cannot serialize undefined/);
});

test("Ed25519 signs canonical values", () => {
  const left = { z: 1, a: "same" };
  const right = { a: "same", z: 1 };
  const proof = signCanonical(left, issuer.privateKey, issuer.keyId);
  assert.equal(verifyCanonicalSignature(right, proof, issuer.publicKey), true);
  assert.equal(
    verifyCanonicalSignature({ ...right, z: 2 }, proof, issuer.publicKey),
    false,
  );
});

test("MAP creates the required traceability triad", () => {
  const trace = createMappingTrace({
    subjectCreditAssertionRef: "assertion-1",
    associatedCreditValue: { band: "A" },
    mappingPolicy: { id: "map-1", version: "1" },
  });
  assert.equal(trace.creditSource, "ASSOCIATED_CREDIT");
});

test("ASC issues and verifies attested and direct credentials", () => {
  const attested = issueAttestedCredential({
    credential: credentialDraft() as never,
    issuerPrivateKey: issuer.privateKey,
  });
  assert.equal(attested.confirmationMethod, "ATTESTED_CONFIRMATION");
  assert.equal(
    verifyCredentialProof({ credential: attested, issuerPublicKey: issuer.publicKey }),
    true,
  );

  const direct = issueDirectCredential({
    credential: credentialDraft() as never,
    subjectPrivateKey: subject.privateKey,
    subjectPublicKey: subject.publicKey,
    issuerPrivateKey: issuer.privateKey,
  });
  assert.equal(direct.confirmationMethod, "DIRECT_SIGNATURE");
  assert.equal(
    verifyCredentialProof({ credential: direct, issuerPublicKey: issuer.publicKey }),
    true,
  );
  const subjectProof = {
    subjectPublicKey: direct.subjectPublicKey!,
    subjectSignature: direct.subjectSignature!,
    subjectSignatureAlgorithm: direct.subjectSignatureAlgorithm!,
  };
  const issuedFromProof = issueDirectCredentialFromConfirmation({
    credential: credentialDraft() as never,
    ...subjectProof,
    issuerPrivateKey: issuer.privateKey,
  });
  assert.equal(
    verifyCredentialProof({
      credential: issuedFromProof,
      issuerPublicKey: issuer.publicKey,
    }),
    true,
  );
  const tampered = {
    ...direct,
    purpose: "DIFFERENT_PURPOSE",
  } satisfies AssociationCredential;
  assert.equal(
    verifyCredentialProof({ credential: tampered, issuerPublicKey: issuer.publicKey }),
    false,
  );
});

test("LCM enforces allowed transitions and terminal states", () => {
  assert.equal(transitionStatus("ACTIVE", "SUSPENDED", now).status, "SUSPENDED");
  assert.throws(
    () => transitionStatus("REVOKED", "ACTIVE", now),
    /Invalid credential status transition/,
  );
});

test("AUTH enforces per-request scope and revocation", () => {
  const authorization = createAuthorization({
    authorizationId: "authorization-1",
    mode: "PER_REQUEST",
    subjectId: "subject-1",
    relyingPartyIds: ["rp-1"],
    agentIds: ["agent-1"],
    purpose: "PURCHASE_RISK_CHECK",
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    boundRequestId: "request-1",
    subjectPrivateKey: subject.privateKey,
    subjectKeyId: subject.keyId,
  });
  const request = {
    requestId: "request-1",
    relyingPartyId: "rp-1",
    agentId: "agent-1",
    verificationLevel: "ASSOCIATED_CREDIT" as const,
    purpose: "PURCHASE_RISK_CHECK",
    requestedDataItems: ["associatedCreditValue"],
  };
  const allowed = evaluateAuthorization(authorization, request, now);
  assert.equal(allowed.allowed, true);
  assert.equal(allowed.runtimeState.useCount, 1);
  assert.equal(
    evaluateAuthorization(
      allowed.authorization,
      request,
      now,
      allowed.runtimeState.usageTimestamps.map((usedAt) => ({ usedAt })),
    ).allowed,
    false,
  );
  assert.equal(
    evaluateAuthorization(revokeAuthorization(authorization, now), request, now).reasonCode,
    "AUTHORIZATION_REVOKED",
  );
  assert.equal(verifyAuthorizationProof(authorization, subject.publicKey), true);
  assert.equal(
    verifyAuthorizationProof(revokeAuthorization(authorization, now), subject.publicKey),
    true,
  );
});

test("AUTH enforces platform delegate identity and frequency", () => {
  const authorization = createAuthorization({
    authorizationId: "authorization-platform-1",
    mode: "PLATFORM_DELEGATED",
    subjectId: "subject-1",
    relyingPartyIds: ["rp-1"],
    platformDelegateId: "platform-1",
    agentIds: ["agent-1"],
    purpose: "PURCHASE_RISK_CHECK",
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    frequencyLimit: {
      maxRequestsPerWindow: 1,
      windowDurationSeconds: 60,
    },
    subjectPrivateKey: subject.privateKey,
    subjectKeyId: subject.keyId,
  });
  const request = {
    requestId: "platform-request-1",
    relyingPartyId: "rp-1",
    platformDelegateId: "platform-1",
    agentId: "agent-1",
    verificationLevel: "ASSOCIATED_CREDIT" as const,
    purpose: "PURCHASE_RISK_CHECK",
    requestedDataItems: ["associatedCreditValue", "mappingPolicy"],
  };
  const first = evaluateAuthorization(authorization, request, now);
  assert.equal(first.allowed, true);
  const second = evaluateAuthorization(
    authorization,
    request,
    now,
    first.runtimeState.usageTimestamps.map((usedAt) => ({ usedAt })),
  );
  assert.equal(second.allowed, false);
  assert.equal(second.reasonCode, "AUTHORIZATION_SCOPE_MISMATCH");
  assert.equal(
    evaluateAuthorization(
      authorization,
      { ...request, platformDelegateId: "platform-wrong" },
      now,
    ).allowed,
    false,
  );
});

test("VER separates credential verification from authorized minimal disclosure", () => {
  const credential = issueAttestedCredential({
    credential: credentialDraft() as never,
    issuerPrivateKey: issuer.privateKey,
  });
  const base = {
    credential,
    issuerPublicKey: issuer.publicKey,
    status: "ACTIVE" as const,
    agentId: "agent-1",
    purpose: "PURCHASE_RISK_CHECK",
    requestedDataItems: ["associatedCreditValue"],
    now,
  };
  const levelOne = verifyAssociationCredential(base);
  assert.equal(levelOne.result, "PASS");
  assert.equal(levelOne.associatedCreditValue, undefined);

  const missingAuthorization = verifyAssociatedCredit({
    ...base,
    creditAssertionValid: true,
    mappingPolicySupported: true,
  });
  assert.equal(missingAuthorization.reasonCode, "AUTHORIZATION_REQUIRED");

  const authorization = createAuthorization({
    authorizationId: "authorization-verification",
    mode: "PER_REQUEST",
    subjectId: "subject-1",
    relyingPartyIds: ["rp-1"],
    agentIds: ["agent-1"],
    purpose: "PURCHASE_RISK_CHECK",
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    boundRequestId: "request-verification",
    subjectPrivateKey: subject.privateKey,
    subjectKeyId: subject.keyId,
  });
  const levelTwo = verifyAssociatedCredit({
    ...base,
    authorization,
    creditAssertionValid: true,
    mappingPolicySupported: true,
  });
  assert.equal(levelTwo.result, "PASS");
  assert.deepEqual(levelTwo.associatedCreditValue, { band: "A", limit: "1000" });
  assert.deepEqual(levelTwo.mappingPolicy, { id: "demo-map", version: "1" });
});

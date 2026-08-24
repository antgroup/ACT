import assert from "node:assert/strict";
import test from "node:test";

import { demoAssociationRequest } from "../src/adapters/mock-providers.ts";
import { createReferenceSuite } from "../src/application/reference-suite.ts";
import {
  createAuthorization,
  generateEd25519KeyPair,
  signCanonical,
  verificationRequestSigningPayload,
  verifyCanonicalSignature,
  verifyCredentialProof,
  verifyVerificationResponseProof,
} from "../src/core/index.ts";

const NOW = "2026-08-12T00:00:00.000Z";
const relyingPartyKeys = generateEd25519KeyPair("relying-party-demo-shop#key-1");
const subjectKeys = generateEd25519KeyPair("subject-demo-alice#key-1");

function strictSuite(now = NOW) {
  return createReferenceSuite({
    now: () => now,
    resolveRelyingPartyPublicKey: (relyingPartyId, keyId) =>
      relyingPartyId === "relying-party-demo-shop" && keyId === relyingPartyKeys.keyId
        ? relyingPartyKeys.publicKey
        : undefined,
    resolveSubjectPublicKey: (subjectId, keyId) =>
      subjectId === "subject-demo-alice" && keyId === subjectKeys.keyId
        ? subjectKeys.publicKey
        : undefined,
  });
}

function protocolVerificationRequest(
  input: Record<string, unknown>,
): Record<string, unknown> {
  const requestId = String(input.requestId);
  const unsigned = {
    messageVersion: "reference-v1",
    relyingPartyId: "relying-party-demo-shop",
    businessContext: { orderId: `order-${requestId}` },
    requestedAt: NOW,
    antiReplay: { nonce: `verification-nonce-${requestId}` },
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: relyingPartyKeys.keyId,
      signatureValue: "PENDING",
    },
    ...input,
  };
  const proof = signCanonical(
    verificationRequestSigningPayload(unsigned as never),
    relyingPartyKeys.privateKey,
    relyingPartyKeys.keyId,
  );
  return { ...unsigned, requestProof: proof };
}

function signedAuthorization(input: Record<string, unknown>): Record<string, unknown> {
  return createAuthorization({
    ...input,
    mode: String(input.mode) as "PER_REQUEST" | "PLATFORM_DELEGATED",
    authorizationId: String(input.authorizationId),
    subjectId: String(input.subjectId),
    relyingPartyIds: input.relyingPartyIds as string[],
    agentIds: input.agentIds as string[],
    purpose: String(input.purpose),
    allowedDataItems: input.allowedDataItems as string[],
    validFrom: String(input.validFrom),
    expiresAt: String(input.expiresAt),
    boundRequestId: typeof input.boundRequestId === "string" ? input.boundRequestId : undefined,
    platformDelegateId: typeof input.platformDelegateId === "string"
      ? input.platformDelegateId
      : undefined,
    frequencyLimit: input.frequencyLimit as never,
    subjectPrivateKey: subjectKeys.privateKey,
    subjectKeyId: subjectKeys.keyId,
  }) as unknown as Record<string, unknown>;
}

function signedSubjectRequest(input: Record<string, unknown>): Record<string, unknown> {
  const unsigned = {
    ...input,
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: subjectKeys.keyId,
      signatureValue: "PENDING",
    },
  };
  const payload = structuredClone(unsigned);
  delete payload.requestProof;
  return {
    ...unsigned,
    requestProof: signCanonical(payload, subjectKeys.privateKey, subjectKeys.keyId),
  };
}

test("ATTESTED_CONFIRMATION issues a credential with outer signature only", () => {
  const suite = createReferenceSuite({ now: () => NOW });
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });

  assert.equal(credential.confirmationMethod, "ATTESTED_CONFIRMATION");
  assert.equal(typeof credential.issuerSignature, "string");
  assert.equal(credential.issuerSignatureAlgorithm, "Ed25519");
  assert.equal(credential.subjectPublicKey, undefined);
  assert.equal(credential.subjectSignature, undefined);
  assert.equal(credential.subjectSignatureAlgorithm, undefined);
  assert.equal(suite.getCredentialStatus(credential.credentialId)?.status, "ACTIVE");
});

test("rejects replayed association applications", () => {
  const suite = createReferenceSuite({ now: () => NOW });
  suite.createAssociationRequest(demoAssociationRequest());
  const replay = {
    ...demoAssociationRequest(),
    applicationId: "association-application-demo-002",
  };
  assert.throws(
    () => suite.createAssociationRequest(replay),
    /REPLAY_DETECTED/,
  );
});

test("DIRECT_SIGNATURE accepts a locally created subject signature and adds the outer signature", () => {
  const suite = strictSuite();
  const applicationInput = {
    ...demoAssociationRequest(),
    applicationId: "association-application-direct-001",
    confirmationMethod: "DIRECT_SIGNATURE",
    antiReplay: { nonce: "direct-signature-nonce-001" },
  };
  const application = suite.createAssociationRequest(applicationInput);
  const preparation = suite.prepareDirectConfirmation(application.applicationId);
  const proof = signCanonical(
    preparation.signingPayload,
    subjectKeys.privateKey,
    subjectKeys.keyId,
  );
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "DIRECT_SIGNATURE",
    subjectPublicKey: subjectKeys.publicKey,
    subjectSignature: proof.signatureValue,
    subjectSignatureAlgorithm: proof.signatureAlgorithm,
  });

  assert.equal(credential.confirmationMethod, "DIRECT_SIGNATURE");
  assert.equal(credential.subjectSignature, proof.signatureValue);
  assert.equal(credential.subjectSignatureAlgorithm, "Ed25519");
  assert.equal(credential.issuerSignatureAlgorithm, "Ed25519");
  assert.equal(
    credential.associationApplicationRequestedAt,
    applicationInput.requestedAt,
  );
  assert.deepEqual(
    credential.associationApplicationAntiReplay,
    applicationInput.antiReplay,
  );
  assert.equal(
    verifyCredentialProof({
      credential: {
        ...credential,
        associationApplicationAntiReplay: { nonce: "tampered-direct-nonce-001" },
      },
      issuerPublicKey: suite.issuerPublicKey,
    }),
    false,
  );
});

test("associated credit requires authorization and discloses only allowed items", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });

  const baseRequest = {
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "ASSOCIATED_CREDIT",
    relyingPartyId: "relying-party-demo-shop",
    subjectCreditAssertionRef: credential.subjectCreditAssertionRef,
    purpose: credential.purpose,
    requestedDataItems: ["associatedCreditValue", "mappingPolicy"],
  };
  const denied = suite.verify(protocolVerificationRequest({
    requestId: "verify-denied",
    ...baseRequest,
    authorizationId: "authorization-missing",
  }));
  assert.equal(denied.reasonCode, "AUTHORIZATION_REQUIRED");

  const authorization = suite.createQueryAuthorization(signedAuthorization({
    authorizationId: "authorization-once",
    mode: "PER_REQUEST",
    subjectId: credential.subjectId,
    relyingPartyIds: ["relying-party-demo-shop"],
    agentIds: [credential.agentId],
    purpose: credential.purpose,
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    boundRequestId: "verify-allowed",
  }));
  const allowed = suite.verify(protocolVerificationRequest({
    requestId: "verify-allowed",
    ...baseRequest,
    authorizationId: authorization.authorizationId,
  }));
  assert.equal(allowed.result, "PASS");
  assert.equal(allowed.completedLevel, "ASSOCIATED_CREDIT");
  assert.equal(allowed.purposeLimited, true);
  assert.equal(allowed.responseProof.signatureAlgorithm, "Ed25519");
  assert.equal(
    verifyVerificationResponseProof(allowed, suite.issuerPublicKey),
    true,
  );
  assert.ok("associatedCreditValue" in allowed);
  assert.equal("mappingPolicy" in allowed, true);
});

test("revoked credentials cannot produce a new PASS result", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  suite.changeCredentialStatusFromRequest(
    credential.credentialId,
    "REVOKED",
    signedSubjectRequest({
      requestId: "status-revoke-for-verification-001",
      credentialId: credential.credentialId,
      targetStatus: "REVOKED",
      reasonCode: "SUBJECT_REQUEST",
      requestedBy: credential.subjectId,
      requestedAt: NOW,
      antiReplay: { nonce: "status-revoke-for-verification-nonce-001" },
    }),
  );
  const verification = suite.verify(protocolVerificationRequest({
    requestId: "verify-revoked",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "CREDENTIAL",
    relyingPartyId: "relying-party-demo-shop",
    purpose: credential.purpose,
    requestedDataItems: ["credentialStatus"],
  }));
  assert.equal(verification.result, "FAIL");
  assert.equal(verification.reasonCode, "ASSOCIATION_CREDENTIAL_NOT_ACTIVE");
  const status = suite.getCredentialStatus(credential.credentialId)!;
  const { statusProof, ...unsignedStatus } = status;
  assert.equal(status.statusVersion, 2);
  assert.equal(
    verifyCanonicalSignature(
      unsignedStatus,
      statusProof,
      suite.issuerPublicKey,
    ),
    true,
  );
});

test("verifies relying-party request proof and rejects replay when a resolver is configured", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const unsigned = protocolVerificationRequest({
    requestId: "verify-signed-request",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "CREDENTIAL",
    purpose: credential.purpose,
    requestedDataItems: ["credentialStatus"],
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: relyingPartyKeys.keyId,
      signatureValue: "PENDING",
    },
  });
  const proof = signCanonical(
    verificationRequestSigningPayload(unsigned as never),
    relyingPartyKeys.privateKey,
    relyingPartyKeys.keyId,
  );
  const signed = { ...unsigned, requestProof: proof };

  assert.equal(suite.verify(signed).result, "PASS");
  assert.throws(() => suite.verify(signed), /REPLAY_DETECTED/);
});

test("validates lifecycle and authorization revocation envelopes", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const authorization = suite.createQueryAuthorization(signedAuthorization({
    authorizationId: "authorization-revoke-envelope-001",
    mode: "PER_REQUEST",
    subjectId: credential.subjectId,
    relyingPartyIds: ["relying-party-demo-shop"],
    agentIds: [credential.agentId],
    purpose: credential.purpose,
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    boundRequestId: "unused-request",
  }));
  const statusRequest = signedSubjectRequest({
    requestId: "status-revoke-request-001",
    credentialId: credential.credentialId,
    targetStatus: "REVOKED",
    reasonCode: "SUBJECT_REQUEST",
    requestedBy: credential.subjectId,
    requestedAt: NOW,
    antiReplay: { nonce: "status-revoke-request-nonce-001" },
  });
  assert.equal(
    suite.changeCredentialStatusFromRequest(
      credential.credentialId,
      "REVOKED",
      statusRequest,
    ).status,
    "REVOKED",
  );
  assert.throws(
    () => suite.changeCredentialStatusFromRequest(
      credential.credentialId,
      "REVOKED",
      statusRequest,
    ),
    /REPLAY_DETECTED/,
  );

  const revocationRequest = signedSubjectRequest({
    requestId: "authorization-revoke-request-001",
    authorizationId: authorization.authorizationId,
    subjectId: authorization.subjectId,
    reasonCode: "SUBJECT_REQUEST",
    requestedAt: NOW,
    antiReplay: { nonce: "authorization-revoke-nonce-001" },
  });
  assert.equal(
    suite.revokeQueryAuthorizationFromRequest(
      authorization.authorizationId,
      revocationRequest,
    ).status,
    "REVOKED",
  );
});

test("fails closed when trusted proof resolvers are missing or proofs are forged", () => {
  const unconfigured = createReferenceSuite({ now: () => NOW });
  const application = unconfigured.createAssociationRequest(demoAssociationRequest());
  const { credential } = unconfigured.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const signedRequest = protocolVerificationRequest({
    requestId: "strict-default-request-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "CREDENTIAL",
    purpose: credential.purpose,
    requestedDataItems: ["credentialStatus"],
  });
  assert.throws(
    () => unconfigured.verify(signedRequest),
    /trusted relying-party key resolver is required/,
  );

  const configured = strictSuite();
  const configuredApplication = configured.createAssociationRequest(demoAssociationRequest());
  const configuredCredential = configured.confirmAssociation(
    configuredApplication.applicationId,
    { confirmationMethod: "ATTESTED_CONFIRMATION" },
  ).credential;
  const forgedRequest = {
    ...protocolVerificationRequest({
      requestId: "forged-request-proof-001",
      credential: { credentialId: configuredCredential.credentialId },
      agentId: configuredCredential.agentId,
      verificationLevel: "CREDENTIAL",
      purpose: configuredCredential.purpose,
      requestedDataItems: ["credentialStatus"],
    }),
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: relyingPartyKeys.keyId,
      signatureValue: "NOT_A_REAL_SIGNATURE",
    },
  };
  assert.throws(() => configured.verify(forgedRequest), /REQUEST_PROOF_INVALID/);

  const forgedAuthorization = {
    ...signedAuthorization({
      authorizationId: "authorization-forged-proof-001",
      mode: "PER_REQUEST",
      subjectId: configuredCredential.subjectId,
      relyingPartyIds: ["relying-party-demo-shop"],
      agentIds: [configuredCredential.agentId],
      purpose: configuredCredential.purpose,
      allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
      validFrom: "2026-01-01T00:00:00.000Z",
      expiresAt: "2027-01-01T00:00:00.000Z",
      boundRequestId: "authorization-forged-proof-request-001",
    }),
    authorizationProof: {
      signatureAlgorithm: "Ed25519",
      keyId: subjectKeys.keyId,
      signatureValue: "NOT_A_REAL_SIGNATURE",
    },
  };
  assert.throws(
    () => configured.createQueryAuthorization(forgedAuthorization),
    /authorizationProof is invalid/,
  );

  const forgedStatusRequest = {
    ...signedSubjectRequest({
      requestId: "status-forged-proof-001",
      credentialId: configuredCredential.credentialId,
      targetStatus: "SUSPENDED",
      reasonCode: "FORGED_REQUEST",
      requestedBy: configuredCredential.subjectId,
      requestedAt: NOW,
      antiReplay: { nonce: "status-forged-proof-nonce-001" },
    }),
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: subjectKeys.keyId,
      signatureValue: "NOT_A_REAL_SIGNATURE",
    },
  };
  assert.throws(
    () => configured.changeCredentialStatusFromRequest(
      configuredCredential.credentialId,
      "SUSPENDED",
      forgedStatusRequest,
    ),
    /status-change proof is invalid/,
  );
});

test("rejects unsigned status rollback after revocation", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  suite.changeCredentialStatusFromRequest(
    credential.credentialId,
    "REVOKED",
    signedSubjectRequest({
      requestId: "status-strict-revoke-001",
      credentialId: credential.credentialId,
      targetStatus: "REVOKED",
      reasonCode: "SUBJECT_REQUEST",
      requestedBy: credential.subjectId,
      requestedAt: NOW,
      antiReplay: { nonce: "status-strict-revoke-nonce-001" },
    }),
  );
  assert.throws(
    () => suite.store.saveCredentialStatus({
      credentialId: credential.credentialId,
      status: "ACTIVE",
      statusVersion: 3,
      reasonCode: "UNSIGNED_ROLLBACK",
      effectiveAt: NOW,
      updatedAt: NOW,
      statusProof: {
        signatureAlgorithm: "Ed25519",
        signatureValue: "NOT_A_REAL_SIGNATURE",
      },
    }),
    /Invalid credential status transition/,
  );
});

test("rejects a stored status whose issuer proof is invalid", () => {
  const suite = strictSuite();
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const status = suite.getCredentialStatus(credential.credentialId)!;
  suite.store.credentialStatuses.set(credential.credentialId, {
    ...status,
    status: "SUSPENDED",
    statusVersion: status.statusVersion + 1,
    statusProof: {
      signatureAlgorithm: "Ed25519",
      signatureValue: "NOT_A_REAL_SIGNATURE",
    },
  });
  assert.throws(
    () => suite.verify(protocolVerificationRequest({
      requestId: "verification-forged-status-001",
      credential: { credentialId: credential.credentialId },
      agentId: credential.agentId,
      verificationLevel: "CREDENTIAL",
      purpose: credential.purpose,
      requestedDataItems: ["credentialStatus"],
    })),
    /credential status proof is invalid/,
  );
});

test("rejects expired subject credit assertions during issuance", () => {
  const suite = strictSuite("2031-01-01T00:00:00.000Z");
  const application = suite.createAssociationRequest({
    ...demoAssociationRequest(),
    requestedAt: "2031-01-01T00:00:00.000Z",
    validFrom: "2031-01-01T00:00:00.000Z",
    expiresAt: "2032-01-01T00:00:00.000Z",
  });
  assert.throws(
    () => suite.confirmAssociation(application.applicationId, {
      confirmationMethod: "ATTESTED_CONFIRMATION",
    }),
    /CREDIT_ASSERTION_INVALID/,
  );
});

test("rejects an expired subject credit assertion during associated-credit verification", () => {
  let currentTime = NOW;
  const suite = createReferenceSuite({
    now: () => currentTime,
    resolveRelyingPartyPublicKey: (relyingPartyId, keyId) =>
      relyingPartyId === "relying-party-demo-shop" && keyId === relyingPartyKeys.keyId
        ? relyingPartyKeys.publicKey
        : undefined,
    resolveSubjectPublicKey: (subjectId, keyId) =>
      subjectId === "subject-demo-alice" && keyId === subjectKeys.keyId
        ? subjectKeys.publicKey
        : undefined,
  });
  const application = suite.createAssociationRequest({
    ...demoAssociationRequest(),
    expiresAt: "2032-01-01T00:00:00.000Z",
  });
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const authorization = suite.createQueryAuthorization(signedAuthorization({
    authorizationId: "authorization-credit-assertion-expiry-001",
    mode: "PER_REQUEST",
    subjectId: credential.subjectId,
    relyingPartyIds: ["relying-party-demo-shop"],
    agentIds: [credential.agentId],
    purpose: credential.purpose,
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2032-01-01T00:00:00.000Z",
    boundRequestId: "verification-credit-assertion-expiry-001",
  }));
  currentTime = "2031-01-01T00:00:00.000Z";
  const response = suite.verify(protocolVerificationRequest({
    requestId: "verification-credit-assertion-expiry-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "ASSOCIATED_CREDIT",
    subjectCreditAssertionRef: credential.subjectCreditAssertionRef,
    authorizationId: authorization.authorizationId,
    purpose: credential.purpose,
    requestedDataItems: ["associatedCreditValue", "mappingPolicy"],
    requestedAt: currentTime,
    antiReplay: { nonce: "verification-credit-assertion-expiry-nonce-001" },
  }));
  assert.equal(response.result, "FAIL");
  assert.equal(response.reasonCode, "CREDIT_ASSERTION_INVALID");
});

test("requires an ACTIVE subject-agent credential before authorization creation", () => {
  const suite = strictSuite();
  assert.throws(
    () => suite.createQueryAuthorization(signedAuthorization({
      authorizationId: "authorization-without-credential-001",
      mode: "PER_REQUEST",
      subjectId: "subject-demo-alice",
      relyingPartyIds: ["relying-party-demo-shop"],
      agentIds: ["agent-without-active-credential"],
      purpose: "DEMO_TRUST_CHECK",
      allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
      validFrom: "2026-01-01T00:00:00.000Z",
      expiresAt: "2027-01-01T00:00:00.000Z",
      boundRequestId: "authorization-without-credential-request-001",
    })),
    /ACTIVE association credential is required/,
  );

  const application = suite.createAssociationRequest(demoAssociationRequest());
  const { credential } = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  suite.changeCredentialStatusFromRequest(
    credential.credentialId,
    "REVOKED",
    signedSubjectRequest({
      requestId: "authorization-precondition-revoke-001",
      credentialId: credential.credentialId,
      targetStatus: "REVOKED",
      reasonCode: "SUBJECT_REQUEST",
      requestedBy: credential.subjectId,
      requestedAt: NOW,
      antiReplay: { nonce: "authorization-precondition-revoke-nonce-001" },
    }),
  );
  assert.throws(
    () => suite.createQueryAuthorization(signedAuthorization({
      authorizationId: "authorization-after-revocation-001",
      mode: "PER_REQUEST",
      subjectId: credential.subjectId,
      relyingPartyIds: ["relying-party-demo-shop"],
      agentIds: [credential.agentId],
      purpose: credential.purpose,
      allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
      validFrom: "2026-01-01T00:00:00.000Z",
      expiresAt: "2027-01-01T00:00:00.000Z",
      boundRequestId: "authorization-after-revocation-request-001",
    })),
    /ACTIVE association credential is required/,
  );
});

import { pathToFileURL } from "node:url";

import { demoAssociationRequest } from "../src/adapters/mock-providers.ts";
import { createReferenceSuite } from "../src/application/reference-suite.ts";
import {
  createAuthorization,
  generateEd25519KeyPair,
  signCanonical,
  verificationRequestSigningPayload,
  type Ed25519KeyPair,
} from "../src/core/index.ts";

const DEMO_NOW = "2026-08-12T00:00:00.000Z";

function verificationRequest(
  input: Record<string, unknown>,
  relyingPartyKeys: Ed25519KeyPair,
): Record<string, unknown> {
  const requestId = String(input.requestId);
  const unsigned = {
    messageVersion: "reference-v1",
    relyingPartyId: "relying-party-demo-shop",
    businessContext: { demoRun: true },
    requestedAt: DEMO_NOW,
    antiReplay: { nonce: `verification-nonce-${requestId}` },
    requestProof: {
      signatureAlgorithm: "Ed25519",
      keyId: relyingPartyKeys.keyId,
      signatureValue: "PENDING",
    },
    ...input,
  };
  return {
    ...unsigned,
    requestProof: signCanonical(
      verificationRequestSigningPayload(unsigned as never),
      relyingPartyKeys.privateKey,
      relyingPartyKeys.keyId,
    ),
  };
}

function signedSubjectRequest(
  input: Record<string, unknown>,
  subjectKeys: Ed25519KeyPair,
): Record<string, unknown> {
  const payload = structuredClone(input);
  return {
    ...input,
    requestProof: signCanonical(payload, subjectKeys.privateKey, subjectKeys.keyId),
  };
}

export function runDemo(): Record<string, unknown> {
  const relyingPartyKeys = generateEd25519KeyPair("relying-party-demo-shop#key-1");
  const subjectKeys = generateEd25519KeyPair("subject-demo-alice#key-1");
  const suite = createReferenceSuite({
    now: () => DEMO_NOW,
    resolveRelyingPartyPublicKey: (relyingPartyId, keyId) =>
      relyingPartyId === "relying-party-demo-shop" && keyId === relyingPartyKeys.keyId
        ? relyingPartyKeys.publicKey
        : undefined,
    resolveSubjectPublicKey: (subjectId, keyId) =>
      subjectId === "subject-demo-alice" && keyId === subjectKeys.keyId
        ? subjectKeys.publicKey
        : undefined,
  });
  const application = suite.createAssociationRequest(demoAssociationRequest());
  const issued = suite.confirmAssociation(application.applicationId, {
    confirmationMethod: "ATTESTED_CONFIRMATION",
  });
  const credential = issued.credential;

  const credentialVerification = suite.verify(verificationRequest({
    requestId: "verification-demo-credential-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "CREDENTIAL",
    relyingPartyId: "relying-party-demo-shop",
    purpose: credential.purpose,
    requestedDataItems: ["credentialStatus"],
  }, relyingPartyKeys));

  const withoutAuthorization = suite.verify(verificationRequest({
    requestId: "verification-demo-credit-unauthorized-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "ASSOCIATED_CREDIT",
    subjectCreditAssertionRef: credential.subjectCreditAssertionRef,
    authorizationId: "authorization-demo-missing",
    relyingPartyId: "relying-party-demo-shop",
    purpose: credential.purpose,
    requestedDataItems: ["associatedCreditValue", "mappingPolicy"],
  }, relyingPartyKeys));

  const authorization = suite.createQueryAuthorization(createAuthorization({
    authorizationId: "authorization-demo-per-request-001",
    mode: "PER_REQUEST",
    subjectId: credential.subjectId,
    relyingPartyIds: ["relying-party-demo-shop"],
    agentIds: [credential.agentId],
    purpose: credential.purpose,
    allowedDataItems: ["associatedCreditValue", "mappingPolicy"],
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2027-01-01T00:00:00.000Z",
    boundRequestId: "verification-demo-credit-authorized-001",
    subjectPrivateKey: subjectKeys.privateKey,
    subjectKeyId: subjectKeys.keyId,
  }) as unknown as Record<string, unknown>);

  const withAuthorization = suite.verify(verificationRequest({
    requestId: "verification-demo-credit-authorized-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "ASSOCIATED_CREDIT",
    subjectCreditAssertionRef: credential.subjectCreditAssertionRef,
    relyingPartyId: "relying-party-demo-shop",
    purpose: credential.purpose,
    requestedDataItems: ["associatedCreditValue", "mappingPolicy"],
    authorizationId: authorization.authorizationId,
  }, relyingPartyKeys));

  const revokedStatus = suite.changeCredentialStatusFromRequest(
    credential.credentialId,
    "REVOKED",
    signedSubjectRequest({
      requestId: "status-revoke-demo-001",
      credentialId: credential.credentialId,
      targetStatus: "REVOKED",
      reasonCode: "SUBJECT_REQUEST",
      requestedBy: credential.subjectId,
      requestedAt: DEMO_NOW,
      antiReplay: { nonce: "status-revoke-demo-nonce-001" },
    }, subjectKeys),
  );
  const afterRevocation = suite.verify(verificationRequest({
    requestId: "verification-demo-after-revocation-001",
    credential: { credentialId: credential.credentialId },
    agentId: credential.agentId,
    verificationLevel: "CREDENTIAL",
    relyingPartyId: "relying-party-demo-shop",
    purpose: credential.purpose,
    requestedDataItems: ["credentialStatus"],
  }, relyingPartyKeys));

  return {
    profile: "reference-v1",
    confirmationMethod: credential.confirmationMethod,
    credentialSignatureLayers: 1,
    application,
    credential,
    credentialVerification,
    withoutAuthorization,
    authorization,
    withAuthorization,
    revokedStatus,
    afterRevocation,
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.stdout.write(`${JSON.stringify(runDemo(), null, 2)}\n`);
}

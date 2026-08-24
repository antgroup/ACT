import { randomUUID } from "node:crypto";
import {
  createAuthorization,
  createMappingTrace,
  createVerificationRecord,
  effectiveCredentialStatus,
  evaluateAuthorization,
  generateEd25519KeyPair,
  issueAttestedCredential,
  issueDirectCredentialFromConfirmation,
  revokeAuthorization,
  signCanonical,
  subjectConfirmationPayload,
  transitionStatus,
  verifyAssociationCredential,
  verifyAuthorizationProof,
  verifyAssociatedCredit,
  verifyCanonicalSignature,
  verifyCredentialProof,
  verifyVerificationRequest,
  type AssociationCredential,
  type CoreVerificationResult,
  type PublicKeyReference,
  type QueryAuthorization,
} from "../core/index.ts";
import {
  InMemoryStore,
  type CredentialStatusRecord,
  type StoredAssociationRequest,
  type StoredAuthorization,
} from "../adapters/in-memory-store.ts";
import {
  MockAttestationProvider,
  MockCreditAssertionProvider,
  MockIdentityProvider,
  MockRelationshipVerifier,
  isCreditAssertionCurrent,
} from "../adapters/mock-providers.ts";
import {
  antiReplayValue,
  asString,
  asStringArray,
  validateAssociationApplication,
  validateAuthorizationRevocationRequest,
  validateStatusChangeRequest,
  validateVerificationRequest,
} from "./validation.ts";

export type ReferenceSuiteOptions = {
  now?: () => string;
  store?: InMemoryStore;
  resolveRelyingPartyPublicKey?: (
    relyingPartyId: string,
    keyId: string | undefined,
  ) => PublicKeyReference | undefined;
  resolveSubjectPublicKey?: (
    subjectId: string,
    keyId: string | undefined,
  ) => PublicKeyReference | undefined;
};

export type ReferenceSuite = ReturnType<typeof createReferenceSuite>;

function recordToCredential(value: Record<string, unknown>): AssociationCredential {
  return value as unknown as AssociationCredential;
}

function authorizationToStored(value: QueryAuthorization): StoredAuthorization {
  const protocolValue = structuredClone(value) as unknown as Record<string, unknown>;
  delete protocolValue.revokedAt;
  return {
    ...protocolValue,
    authorizationId: value.authorizationId,
    status: value.status as StoredAuthorization["status"],
    usageTimestamps: [],
  };
}

function authorizationFromStored(value: StoredAuthorization): QueryAuthorization {
  const copy = structuredClone(value) as Record<string, unknown>;
  delete copy.usageTimestamps;
  return copy as unknown as QueryAuthorization;
}

function protocolAssociationApplication(
  value: StoredAssociationRequest,
): Record<string, unknown> {
  const copy = structuredClone(value) as Record<string, unknown>;
  for (const field of [
    "status",
    "createdAt",
    "updatedAt",
    "preparedCredential",
    "identityVerification",
    "relationshipVerification",
    "attestation",
    "credentialId",
  ]) {
    delete copy[field];
  }
  return copy;
}

function optionalRecord(
  value: Record<string, unknown>,
  field: string,
): Record<string, unknown> | undefined {
  const candidate = value[field];
  if (candidate === undefined) return undefined;
  if (candidate === null || Array.isArray(candidate) || typeof candidate !== "object") {
    throw new TypeError(`${field} must be an object`);
  }
  return candidate as Record<string, unknown>;
}

function credentialInput(value: Record<string, unknown>): {
  credentialId: string;
  inlineCredential?: AssociationCredential;
} {
  const candidate = value.credential;
  if (candidate === null || Array.isArray(candidate) || typeof candidate !== "object") {
    throw new TypeError("credential must be a credential or credential reference");
  }
  const record = candidate as Record<string, unknown>;
  const id = asString(record, "credentialId");
  return "issuerSignature" in record
    ? { credentialId: id, inlineCredential: recordToCredential(record) }
    : { credentialId: id };
}

function unsignedStatus(
  status: CredentialStatusRecord | Omit<CredentialStatusRecord, "statusProof">,
): Omit<CredentialStatusRecord, "statusProof"> {
  const copy = structuredClone(status) as unknown as Record<string, unknown>;
  delete copy.statusProof;
  return copy as Omit<CredentialStatusRecord, "statusProof">;
}

function requestSigningPayload(value: Record<string, unknown>): Record<string, unknown> {
  const copy = structuredClone(value);
  delete copy.requestProof;
  return copy;
}

export function createReferenceSuite(options: ReferenceSuiteOptions = {}) {
  const store = options.store ?? new InMemoryStore();
  const now = options.now ?? (() => new Date().toISOString());
  const identityProvider = new MockIdentityProvider();
  const relationshipVerifier = new MockRelationshipVerifier();
  const attestationProvider = new MockAttestationProvider();
  const creditAssertionProvider = new MockCreditAssertionProvider();
  const issuerKeys = generateEd25519KeyPair("issuer-demo-reference-suite#key-1");

  function trustedSubjectPublicKey(subjectId: string, keyId: string | undefined) {
    if (options.resolveSubjectPublicKey === undefined) {
      throw new Error("REQUEST_PROOF_INVALID: trusted subject key resolver is required");
    }
    const publicKey = options.resolveSubjectPublicKey(subjectId, keyId);
    if (publicKey === undefined) {
      throw new Error("REQUEST_PROOF_INVALID: subject key was not resolved");
    }
    return publicKey;
  }

  function credentialStatusProofIsValid(status: CredentialStatusRecord): boolean {
    return verifyCanonicalSignature(
      unsignedStatus(status),
      status.statusProof,
      issuerKeys.publicKey,
    );
  }

  function hasActiveCredential(subjectId: string, agentId: string, currentTime: string): boolean {
    return store.listCredentials().some((record) => {
      const credential = recordToCredential(record);
      if (credential.subjectId !== subjectId || credential.agentId !== agentId) return false;
      if (!verifyCredentialProof({ credential, issuerPublicKey: issuerKeys.publicKey })) return false;
      if (Date.parse(currentTime) < Date.parse(credential.validFrom)) return false;
      const status = store.getCredentialStatus(credential.credentialId);
      if (status === undefined || !credentialStatusProofIsValid(status)) return false;
      return effectiveCredentialStatus(
        {
          credentialId: credential.credentialId,
          status: status.status,
          changedAt: status.updatedAt,
        },
        credential.expiresAt,
        currentTime,
      ) === "ACTIVE";
    });
  }

  function buildCredentialDraft(
    application: StoredAssociationRequest,
    currentTime: string,
    credentialId = `credential-${randomUUID()}`,
  ) {
    const subjectId = String(application.subjectId);
    const agentId = String(application.agentId);
    const associationRole = String(application.associationRole);
    const relationshipEvidenceRefs = application.relationshipEvidenceRefs as string[];
    const purpose = String(application.purpose);
    const scope = application.scope as string[];

    const identity = identityProvider.verify(subjectId, currentTime);
    if (!identity.verified) throw new Error("Subject identity verification failed");
    const relationship = relationshipVerifier.verify({
      subjectId,
      agentId,
      relationshipRole: associationRole,
      relationshipEvidenceRef: relationshipEvidenceRefs[0],
      now: currentTime,
    });
    if (!relationship.verified) throw new Error("Relationship verification failed");

    const creditAssertion = creditAssertionProvider.get(subjectId);
    if (creditAssertion === undefined) throw new Error("CREDIT_ASSERTION_UNAVAILABLE");
    if (!isCreditAssertionCurrent(creditAssertion, currentTime)) {
      throw new Error("CREDIT_ASSERTION_INVALID");
    }
    const mapping = createMappingTrace({
      subjectCreditAssertionRef: creditAssertion.assertionRef,
      associatedCreditValue: {
        level: creditAssertion.level,
        status: creditAssertion.status,
      },
      mappingPolicy: { id: "mock-level-mapping", version: "1.0" },
    });

    const credential = {
      credentialId,
      credentialVersion: "reference-v1",
      associationApplicationId: application.applicationId,
      agentId,
      subjectId,
      associationRole,
      issuerId: String(application.issuerId),
      relationshipEvidenceRef: relationship.evidenceRef,
      confirmationMethod: String(application.confirmationMethod),
      subjectCreditAssertionRef: mapping.subjectCreditAssertionRef,
      associatedCreditValue: mapping.associatedCreditValue,
      creditSource: "ASSOCIATED_CREDIT",
      mappingPolicy: mapping.mappingPolicy,
      confirmationStatement: `The subject confirms the ${associationRole} relationship for ${purpose}.`,
      purpose,
      scope,
      ...(application.confirmationMethod === "DIRECT_SIGNATURE"
        ? {
            associationApplicationRequestedAt: String(application.requestedAt),
            associationApplicationAntiReplay: structuredClone(application.antiReplay),
          }
        : {}),
      issuedAt: currentTime,
      validFrom: String(application.validFrom),
      ...(application.expiresAt ? { expiresAt: String(application.expiresAt) } : {}),
      statusQuery: {
        uri: `/v1/association-credentials/${encodeURIComponent(credentialId)}/status`,
        method: "GET",
      },
    } as unknown as AssociationCredential;
    return { credential, identity, relationship };
  }

  function createAssociationRequest(input: Record<string, unknown>) {
    const application = validateAssociationApplication(input);
    const replayValue = antiReplayValue(application.antiReplay);
    if (!store.consumeReplayKey("association-application", replayValue)) {
      throw new Error("REPLAY_DETECTED: antiReplay value was already used");
    }

    const stored: StoredAssociationRequest = {
      ...application,
      status: "PENDING",
      createdAt: now(),
      updatedAt: now(),
    };
    store.saveAssociationRequest(stored);
    return structuredClone(stored);
  }

  function prepareDirectConfirmation(applicationId: string) {
    const application = store.getAssociationRequest(applicationId);
    if (!application) throw new Error(`Association application not found: ${applicationId}`);
    if (application.status !== "PENDING") {
      throw new Error(`Association application is not PENDING: ${applicationId}`);
    }
    if (application.confirmationMethod !== "DIRECT_SIGNATURE") {
      throw new Error("Preparation is only available for DIRECT_SIGNATURE");
    }

    const prepared = application.preparedCredential;
    if (prepared !== null && typeof prepared === "object" && !Array.isArray(prepared)) {
      return {
        applicationId,
        credential: structuredClone(prepared),
        signingPayload: subjectConfirmationPayload(prepared as Record<string, unknown>),
      };
    }

    const currentTime = now();
    const context = buildCredentialDraft(application, currentTime);
    store.updateAssociationRequest({
      ...application,
      preparedCredential: context.credential as unknown as Record<string, unknown>,
      identityVerification: context.identity,
      relationshipVerification: context.relationship,
      updatedAt: currentTime,
    });
    return {
      applicationId,
      credential: structuredClone(context.credential),
      signingPayload: subjectConfirmationPayload(
        context.credential as unknown as Record<string, unknown>,
      ),
    };
  }

  function confirmAssociation(
    applicationId: string,
    input: Record<string, unknown>,
  ) {
    const application = store.getAssociationRequest(applicationId);
    if (!application) throw new Error(`Association application not found: ${applicationId}`);
    if (application.status !== "PENDING") {
      throw new Error(`Association application is not PENDING: ${applicationId}`);
    }

    const currentTime = now();
    const confirmationMethod = String(application.confirmationMethod);
    if (asString(input, "confirmationMethod") !== confirmationMethod) {
      throw new Error("confirmationMethod must match the association application");
    }

    let credential: AssociationCredential;
    let identity: unknown;
    let relationship: unknown;
    if (confirmationMethod === "ATTESTED_CONFIRMATION") {
      const context = buildCredentialDraft(application, currentTime);
      identity = context.identity;
      relationship = context.relationship;
      const attestation = attestationProvider.confirm({
        associationRequestId: applicationId,
        subjectId: context.credential.subjectId,
        agentId: context.credential.agentId,
        relationshipRole: String(context.credential.associationRole),
        purpose: context.credential.purpose,
        scope: context.credential.scope,
        now: currentTime,
      });
      credential = issueAttestedCredential({
        credential: context.credential,
        issuerPrivateKey: issuerKeys.privateKey,
      });
      application.attestation = attestation;
    } else if (confirmationMethod === "DIRECT_SIGNATURE") {
      const prepared = application.preparedCredential;
      if (prepared === null || Array.isArray(prepared) || typeof prepared !== "object") {
        throw new Error("DIRECT_SIGNATURE must be prepared before confirmation");
      }
      const subjectPublicKey = input.subjectPublicKey;
      if (subjectPublicKey === null || Array.isArray(subjectPublicKey)
        || typeof subjectPublicKey !== "object") {
        throw new Error("subjectPublicKey is required for DIRECT_SIGNATURE");
      }
      const submittedPublicKey = subjectPublicKey as unknown as PublicKeyReference;
      const trustedPublicKey = trustedSubjectPublicKey(
        String(application.subjectId),
        submittedPublicKey.keyId,
      );
      credential = issueDirectCredentialFromConfirmation({
        credential: prepared as unknown as AssociationCredential,
        subjectPublicKey: trustedPublicKey,
        subjectSignature: asString(input, "subjectSignature"),
        subjectSignatureAlgorithm: asString(input, "subjectSignatureAlgorithm"),
        issuerPrivateKey: issuerKeys.privateKey,
      });
      identity = application.identityVerification;
      relationship = application.relationshipVerification;
    } else {
      throw new Error(`Unsupported confirmation method: ${confirmationMethod}`);
    }

    store.saveCredential(credential as unknown as Record<string, unknown>);
    const statusBase: Omit<CredentialStatusRecord, "statusProof"> = {
      credentialId: credential.credentialId,
      status: "ACTIVE",
      statusVersion: 1,
      reasonCode: "ISSUED",
      effectiveAt: currentTime,
      updatedAt: currentTime,
    };
    const status: CredentialStatusRecord = {
      ...statusBase,
      statusProof: signCanonical(
        unsignedStatus(statusBase),
        issuerKeys.privateKey,
        issuerKeys.keyId,
      ),
    };
    store.saveCredentialStatus(status);
    store.updateAssociationRequest({
      ...application,
      status: "ACTIVE",
      credentialId: credential.credentialId,
      identityVerification: identity,
      relationshipVerification: relationship,
      updatedAt: currentTime,
    });

    return { applicationId, credential, status };
  }

  function getCredential(credentialId: string) {
    return store.getCredential(credentialId);
  }

  function getCredentialStatus(credentialId: string) {
    const status = store.getCredentialStatus(credentialId);
    if (status !== undefined && !credentialStatusProofIsValid(status)) {
      throw new Error("ASSOCIATION_PROOF_INVALID: credential status proof is invalid");
    }
    return status;
  }

  function changeCredentialStatus(
    credentialId: string,
    targetStatus: CredentialStatusRecord["status"],
    reasonCode: string,
  ) {
    const current = store.getCredentialStatus(credentialId);
    if (!current) throw new Error(`Credential not found: ${credentialId}`);
    if (!credentialStatusProofIsValid(current)) {
      throw new Error("ASSOCIATION_PROOF_INVALID: current status proof is invalid");
    }
    const transitioned = transitionStatus(current.status, targetStatus, now(), reasonCode);
    const nextBase: Omit<CredentialStatusRecord, "statusProof"> = {
      credentialId,
      status: transitioned.status,
      statusVersion: current.statusVersion + 1,
      reasonCode: transitioned.reasonCode ?? reasonCode,
      effectiveAt: transitioned.changedAt,
      updatedAt: transitioned.changedAt,
    };
    const next: CredentialStatusRecord = {
      ...nextBase,
      statusProof: signCanonical(
        unsignedStatus(nextBase),
        issuerKeys.privateKey,
        issuerKeys.keyId,
      ),
    };
    store.saveCredentialStatus(next);
    return next;
  }

  function changeCredentialStatusFromRequest(
    credentialId: string,
    targetStatus: CredentialStatusRecord["status"],
    input: Record<string, unknown>,
  ) {
    const request = validateStatusChangeRequest(input, now());
    if (request.credentialId !== credentialId) {
      throw new Error("credentialId must match the path");
    }
    if (request.targetStatus !== targetStatus) {
      throw new Error("targetStatus must match the operation");
    }
    const credentialRecord = store.getCredential(credentialId);
    if (credentialRecord === undefined) {
      throw new Error(`Credential not found: ${credentialId}`);
    }
    const credential = recordToCredential(credentialRecord);
    if (request.requestedBy !== credential.subjectId) {
      throw new Error("requestedBy must be the associated subject");
    }
    const replayKey = [
      request.requestedBy,
      request.requestId,
      request.antiReplay.nonce ?? "",
      request.antiReplay.idempotencyKey ?? "",
    ].join(":");
    const publicKey = trustedSubjectPublicKey(
      request.requestedBy,
      request.requestProof.keyId,
    );
    if (!verifyCanonicalSignature(
      requestSigningPayload(request as unknown as Record<string, unknown>),
      request.requestProof,
      publicKey,
    )) {
      throw new Error("REQUEST_PROOF_INVALID: status-change proof is invalid");
    }
    if (!store.consumeReplayKey("credential-status-change", replayKey)) {
      throw new Error("REPLAY_DETECTED: status-change request was already used");
    }
    return changeCredentialStatus(credentialId, targetStatus, request.reasonCode);
  }

  function createQueryAuthorization(input: Record<string, unknown>) {
    const frequencyLimit = optionalRecord(input, "frequencyLimit");
    const resultUseRestrictions = optionalRecord(input, "resultUseRestrictions");
    const suppliedProof = optionalRecord(input, "authorizationProof");
    if (suppliedProof === undefined) {
      throw new Error("authorizationProof is required");
    }
    const authorization = createAuthorization({
      authorizationId: asString(input, "authorizationId"),
      mode: asString(input, "mode") as "PER_REQUEST" | "PLATFORM_DELEGATED",
      subjectId: asString(input, "subjectId"),
      relyingPartyIds: Array.isArray(input.relyingPartyIds)
        ? asStringArray(input, "relyingPartyIds")
        : [asString(input, "relyingPartyId")],
      agentIds: asStringArray(input, "agentIds"),
      authorizationVersion: input.authorizationVersion === undefined
        ? "reference-v1"
        : asString(input, "authorizationVersion") as "reference-v1",
      verificationLevel: input.verificationLevel === undefined
        ? "ASSOCIATED_CREDIT"
        : asString(input, "verificationLevel") as "ASSOCIATED_CREDIT",
      purpose: asString(input, "purpose"),
      allowedDataItems: Array.isArray(input.allowedDataItems)
        ? asStringArray(input, "allowedDataItems")
        : asStringArray(input, "dataItems"),
      validFrom: asString(input, "validFrom"),
      expiresAt: typeof input.expiresAt === "string"
        ? input.expiresAt
        : asString(input, "validUntil"),
      frequencyLimit: frequencyLimit === undefined
        ? undefined
        : {
            maxRequestsPerWindow: Number(frequencyLimit.maxRequestsPerWindow),
            windowDurationSeconds: Number(frequencyLimit.windowDurationSeconds),
          },
      maxRequestsPerWindow: typeof input.maxRequestsPerWindow === "number"
        ? input.maxRequestsPerWindow
        : undefined,
      windowDurationSeconds: typeof input.windowDurationSeconds === "number"
        ? input.windowDurationSeconds
        : undefined,
      platformDelegateId: typeof input.platformDelegateId === "string"
        ? input.platformDelegateId
        : typeof input.platformAgentId === "string"
        ? input.platformAgentId
        : undefined,
      boundRequestId: typeof input.boundRequestId === "string"
        ? input.boundRequestId
        : typeof input.requestId === "string"
        ? input.requestId
        : undefined,
      resultUseRestrictions: resultUseRestrictions === undefined
        ? undefined
        : {
            mayStore: Boolean(resultUseRestrictions.mayStore),
            ...(typeof resultUseRestrictions.retentionSeconds === "number"
              ? { retentionSeconds: resultUseRestrictions.retentionSeconds }
              : {}),
            mayTransfer: Boolean(resultUseRestrictions.mayTransfer),
          },
      authorizationProof: suppliedProof as unknown as {
        signatureAlgorithm: string;
        signatureValue: string;
        keyId?: string;
      },
    });
    const proofKey = trustedSubjectPublicKey(
      authorization.subjectId,
      authorization.authorizationProof.keyId,
    );
    if (!verifyAuthorizationProof(authorization, proofKey)) {
      throw new Error("authorizationProof is invalid");
    }
    const currentTime = now();
    for (const agentId of authorization.agentIds) {
      if (!hasActiveCredential(authorization.subjectId, agentId, currentTime)) {
        throw new Error(
          `ACTIVE association credential is required for subject ${authorization.subjectId} and agent ${agentId}`,
        );
      }
    }
    store.saveAuthorization(authorizationToStored(authorization));
    return authorization;
  }

  function revokeQueryAuthorization(authorizationId: string) {
    const current = store.getAuthorization(authorizationId);
    if (!current) throw new Error(`Authorization not found: ${authorizationId}`);
    const revoked = revokeAuthorization(
      authorizationFromStored(current),
      now(),
    );
    store.saveAuthorization({
      ...authorizationToStored(revoked),
      usageTimestamps: [...current.usageTimestamps],
    });
    return authorizationFromStored(store.getAuthorization(authorizationId)!);
  }

  function revokeQueryAuthorizationFromRequest(
    authorizationId: string,
    input: Record<string, unknown>,
  ) {
    const request = validateAuthorizationRevocationRequest(input, now());
    if (request.authorizationId !== authorizationId) {
      throw new Error("authorizationId must match the path");
    }
    const current = store.getAuthorization(authorizationId);
    if (!current) throw new Error(`Authorization not found: ${authorizationId}`);
    if (String(current.subjectId) !== request.subjectId) {
      throw new Error("subjectId does not match the authorization");
    }
    const replayKey = [
      request.subjectId,
      request.requestId,
      request.antiReplay.nonce ?? "",
      request.antiReplay.idempotencyKey ?? "",
    ].join(":");
    const publicKey = trustedSubjectPublicKey(
      request.subjectId,
      request.requestProof.keyId,
    );
    if (!verifyCanonicalSignature(
      requestSigningPayload(request as unknown as Record<string, unknown>),
      request.requestProof,
      publicKey,
    )) {
      throw new Error("REQUEST_PROOF_INVALID: revocation proof is invalid");
    }
    if (!store.consumeReplayKey("authorization-revocation", replayKey)) {
      throw new Error("REPLAY_DETECTED: authorization revocation was already used");
    }
    return revokeQueryAuthorization(authorizationId);
  }

  function verify(input: Record<string, unknown>) {
    const generatedAt = now();
    const request = validateVerificationRequest(input, generatedAt);
    if (options.resolveRelyingPartyPublicKey === undefined) {
      throw new Error("REQUEST_PROOF_INVALID: trusted relying-party key resolver is required");
    }
    const publicKey = options.resolveRelyingPartyPublicKey(
      request.relyingPartyId,
      request.requestProof.keyId,
    );
    if (publicKey === undefined) {
      throw new Error("REQUEST_PROOF_INVALID: relying-party key was not resolved");
    }
    const proofResult = verifyVerificationRequest({
      request,
      relyingPartyPublicKey: publicKey,
      now: generatedAt,
      consumeAntiReplay: (key) => store.consumeReplayKey("verification", key),
    });
    if (!proofResult.valid) {
      throw new Error(`${proofResult.reasonCode}: verification request rejected`);
    }

    const requestRecord = request as unknown as Record<string, unknown>;
    const { credentialId, inlineCredential } = credentialInput(requestRecord);
    const credentialRecord = inlineCredential as unknown as Record<string, unknown>
      ?? store.getCredential(credentialId);
    const status = store.getCredentialStatus(credentialId);
    const verificationLevel = request.verificationLevel;

    if (!credentialRecord || !status) {
      throw new Error(`Association credential not found: ${credentialId}`);
    }
    if (!credentialStatusProofIsValid(status)) {
      throw new Error("ASSOCIATION_PROOF_INVALID: credential status proof is invalid");
    }

    const credential = recordToCredential(credentialRecord);
    const baseInput = {
      credential,
      issuerPublicKey: issuerKeys.publicKey,
      status: {
        credentialId: status.credentialId,
        status: status.status,
        changedAt: status.updatedAt,
      },
      agentId: request.agentId,
      purpose: request.purpose,
      requestedDataItems: request.requestedDataItems,
      now: generatedAt,
    };

    let result: Record<string, unknown>;
    if (verificationLevel === "CREDENTIAL") {
      result = verifyAssociationCredential(baseInput) as unknown as Record<string, unknown>;
    } else if (verificationLevel === "ASSOCIATED_CREDIT") {
      if (request.subjectCreditAssertionRef !== credential.subjectCreditAssertionRef) {
        throw new Error("subjectCreditAssertionRef does not match the credential");
      }
      const authorizationId = request.authorizationId;
      const authorization = authorizationId
        ? store.getAuthorization(authorizationId)
        : undefined;
      if (authorization) {
        const authorizationValue = authorizationFromStored(authorization);
        const authorizationKey = trustedSubjectPublicKey(
          authorizationValue.subjectId,
          authorizationValue.authorizationProof.keyId,
        );
        if (!verifyAuthorizationProof(authorizationValue, authorizationKey)) {
          throw new Error("AUTHORIZATION_REQUIRED: authorization proof is invalid");
        }
        const decision = evaluateAuthorization(
          authorizationValue,
          {
            requestId: request.requestId,
            relyingPartyId: request.relyingPartyId,
            agentId: request.agentId,
            verificationLevel: "ASSOCIATED_CREDIT",
            purpose: request.purpose,
            requestedDataItems: request.requestedDataItems,
            ...(request.platformDelegateId === undefined
              ? {}
              : { platformDelegateId: request.platformDelegateId }),
          },
          generatedAt,
          authorization.usageTimestamps.map((usedAt) => ({ usedAt })),
        );
        store.saveAuthorization({
          ...authorizationToStored(decision.authorization),
          usageTimestamps: [...decision.runtimeState.usageTimestamps],
        });
        if (!decision.allowed) {
          result = {
            result: "FAIL",
            reasonCode: decision.reasonCode,
            completedVerificationLevel: "CREDENTIAL",
            credentialStatus: status.status,
            scope: [...credential.scope],
          };
        } else {
          const creditAssertion = creditAssertionProvider.get(credential.subjectId);
          result = verifyAssociatedCredit({
            ...baseInput,
            authorization: decision.authorization,
            creditAssertionAvailable: creditAssertion !== undefined,
            creditAssertionValid: creditAssertion !== undefined
              && creditAssertion.subjectId === credential.subjectId
              && creditAssertion.assertionRef === credential.subjectCreditAssertionRef
              && isCreditAssertionCurrent(creditAssertion, generatedAt),
            mappingPolicySupported: credential.mappingPolicy.id === "mock-level-mapping",
          }) as unknown as Record<string, unknown>;
        }
      } else {
        result = {
          result: "FAIL",
          reasonCode: "AUTHORIZATION_REQUIRED",
          completedVerificationLevel: "CREDENTIAL",
          credentialStatus: status.status,
          scope: [...credential.scope],
        };
      }
    } else {
      throw new Error(`Unsupported verificationLevel: ${verificationLevel}`);
    }

    const record = createVerificationRecord({
      requestId: request.requestId,
      agentId: credential.agentId,
      verification: result as unknown as CoreVerificationResult,
      generatedAt,
      statusQuery: credential.statusQuery,
      responsePrivateKey: issuerKeys.privateKey,
      responseKeyId: issuerKeys.keyId,
    });
    store.saveVerificationRecord(record as unknown as Record<string, unknown>);
    return record;
  }

  function reset() {
    store.reset();
  }

  return {
    createAssociationRequest,
    prepareDirectConfirmation,
    confirmAssociation,
    getCredential,
    getCredentialStatus,
    changeCredentialStatusFromRequest,
    createQueryAuthorization,
    revokeQueryAuthorizationFromRequest,
    verify,
    reset,
    issuerPublicKey: issuerKeys.publicKey,
    protocolAssociationApplication,
    store,
  };
}

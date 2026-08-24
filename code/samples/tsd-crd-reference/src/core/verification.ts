import { randomUUID } from "node:crypto";

import { verifyCredentialProof } from "./association.ts";
import { evaluateAuthorization } from "./authorization.ts";
import { effectiveCredentialStatus } from "./lifecycle.ts";
import { mappingTraceFromCredential, validateMappingTrace } from "./mapping.ts";
import type {
  AssociationCredential,
  AuthorizationEvaluationRequest,
  CredentialStatus,
  CredentialStatusRecord,
  CreditQueryAuthorization,
  PublicKeyReference,
  ReasonCode,
  SignatureProof,
  VerificationRequest,
  VerificationResponse,
  VerificationResult,
} from "./types.ts";
import {
  signCanonical,
  type KeyMaterial,
  verifyCanonicalSignature,
} from "./crypto.ts";

export interface VerifyAssociationCredentialInput {
  credential: AssociationCredential;
  issuerPublicKey: PublicKeyReference | KeyMaterial;
  subjectPublicKey?: PublicKeyReference | KeyMaterial;
  status: CredentialStatus | CredentialStatusRecord;
  agentId: string;
  purpose: string;
  requestedDataItems?: string[];
  now?: string;
}

export interface CoreVerificationResult {
  result: VerificationResult;
  reasonCode: ReasonCode;
  completedVerificationLevel: "CREDENTIAL" | "ASSOCIATED_CREDIT";
  credentialStatus: CredentialStatus;
  scope: string[];
  creditSource?: "ASSOCIATED_CREDIT";
  associatedCreditValue?: AssociationCredential["associatedCreditValue"];
  subjectCreditAssertionValid?: boolean;
  mappingPolicy?: AssociationCredential["mappingPolicy"];
}

function result(
  input: VerifyAssociationCredentialInput,
  verificationResult: VerificationResult,
  reasonCode: ReasonCode,
  credentialStatus: CredentialStatus,
): CoreVerificationResult {
  return {
    result: verificationResult,
    reasonCode,
    completedVerificationLevel: "CREDENTIAL",
    credentialStatus,
    scope: [...input.credential.scope],
  };
}

function statusRecord(
  credential: AssociationCredential,
  status: CredentialStatus | CredentialStatusRecord,
  now: string,
): CredentialStatus {
  if (typeof status === "string") {
    return effectiveCredentialStatus(
      { credentialId: credential.credentialId, status, changedAt: now },
      credential.expiresAt,
      now,
    );
  }
  return effectiveCredentialStatus(status, credential.expiresAt, now);
}

export function verifyAssociationCredential(
  input: VerifyAssociationCredentialInput,
): CoreVerificationResult {
  const now = input.now ?? new Date().toISOString();
  const currentStatus = statusRecord(input.credential, input.status, now);
  if (input.credential.agentId !== input.agentId) {
    return result(input, "FAIL", "INVALID_REQUEST", currentStatus);
  }
  if (
    input.credential.purpose !== input.purpose
    || input.credential.scope.length === 0
  ) {
    return result(input, "FAIL", "INVALID_REQUEST", currentStatus);
  }
  if (
    Date.parse(now) < Date.parse(input.credential.validFrom)
    || currentStatus !== "ACTIVE"
  ) {
    return result(
      input,
      "FAIL",
      "ASSOCIATION_CREDENTIAL_NOT_ACTIVE",
      currentStatus,
    );
  }
  const trace = mappingTraceFromCredential(input.credential);
  if (trace === undefined || !validateMappingTrace(trace).valid) {
    return result(input, "FAIL", "INVALID_REQUEST", currentStatus);
  }
  if (!verifyCredentialProof(input)) {
    return result(input, "FAIL", "ASSOCIATION_PROOF_INVALID", currentStatus);
  }
  return result(input, "PASS", "VERIFIED", currentStatus);
}

export interface VerifyAssociatedCreditInput
  extends VerifyAssociationCredentialInput {
  authorization?: CreditQueryAuthorization;
  authorizationRequest?: AuthorizationEvaluationRequest;
  creditAssertionValid?: boolean;
  creditAssertionAvailable?: boolean;
  mappingPolicySupported?: boolean;
  reviewRequired?: boolean;
}

export function verifyAssociatedCredit(
  input: VerifyAssociatedCreditInput,
): CoreVerificationResult {
  const base = verifyAssociationCredential(input);
  if (base.result !== "PASS") return base;

  if (input.authorization === undefined) {
    return {
      ...base,
      result: "FAIL",
      reasonCode: "AUTHORIZATION_REQUIRED",
    };
  }
  const verificationNow = input.now ?? new Date().toISOString();
  if (input.authorization.status === "REVOKED") {
    return { ...base, result: "FAIL", reasonCode: "AUTHORIZATION_REVOKED" };
  }
  if (
    input.authorization.status === "EXPIRED"
    || Date.parse(verificationNow) < Date.parse(input.authorization.validFrom)
    || Date.parse(verificationNow) >= Date.parse(input.authorization.expiresAt)
  ) {
    return { ...base, result: "FAIL", reasonCode: "AUTHORIZATION_EXPIRED" };
  }
  if (
    input.authorization.subjectId !== input.credential.subjectId
    || !input.authorization.agentIds.includes(input.credential.agentId)
    || input.authorization.purpose !== input.purpose
  ) {
    return {
      ...base,
      result: "FAIL",
      reasonCode: "AUTHORIZATION_SCOPE_MISMATCH",
    };
  }
  if (input.authorizationRequest !== undefined) {
    const decision = evaluateAuthorization(
      input.authorization,
      input.authorizationRequest,
      input.now,
    );
    if (!decision.allowed) {
      return { ...base, result: "FAIL", reasonCode: decision.reasonCode };
    }
  }
  if (input.reviewRequired === true) {
    return { ...base, result: "REVIEW_REQUIRED", reasonCode: "REVIEW_REQUIRED" };
  }
  if (input.creditAssertionAvailable === false) {
    return {
      ...base,
      result: "INCONCLUSIVE",
      reasonCode: "CREDIT_ASSERTION_UNAVAILABLE",
    };
  }
  if (input.creditAssertionValid !== true) {
    return { ...base, result: "FAIL", reasonCode: "CREDIT_ASSERTION_INVALID" };
  }
  if (input.mappingPolicySupported !== true) {
    return {
      ...base,
      result: "INCONCLUSIVE",
      reasonCode: "MAPPING_POLICY_UNSUPPORTED",
    };
  }

  const allowedItems = new Set(input.authorization.allowedDataItems);
  const requestedItems = input.requestedDataItems ?? [];
  const mayDiscloseValue = requestedItems.includes("associatedCreditValue")
    && allowedItems.has("associatedCreditValue");
  const mayDisclosePolicy = allowedItems.has("mappingPolicy");
  if (!mayDiscloseValue || !mayDisclosePolicy) {
    return {
      ...base,
      result: "FAIL",
      reasonCode: "AUTHORIZATION_SCOPE_MISMATCH",
    };
  }

  return {
    ...base,
    result: "PASS",
    reasonCode: "VERIFIED",
    completedVerificationLevel: "ASSOCIATED_CREDIT",
    creditSource: "ASSOCIATED_CREDIT",
    subjectCreditAssertionValid: true,
    associatedCreditValue: structuredClone(input.credential.associatedCreditValue),
    mappingPolicy: structuredClone(input.credential.mappingPolicy),
  };
}

export function createVerificationRecord(input: {
  requestId: string;
  agentId: string;
  verification: CoreVerificationResult;
  generatedAt?: string;
  ttlSeconds?: number;
  statusQuery?: VerificationResponse["statusQuery"];
  responsePrivateKey: KeyMaterial;
  responseKeyId?: string;
}): VerificationResponse {
  const generatedAt = input.generatedAt ?? new Date().toISOString();
  const expiresAt = new Date(
    Date.parse(generatedAt) + (input.ttlSeconds ?? 300) * 1_000,
  ).toISOString();
  const unsigned: Omit<VerificationResponse, "responseProof"> = {
    requestId: input.requestId,
    verificationRecordId: `verification-${randomUUID()}`,
    agentId: input.agentId,
    completedLevel: input.verification.completedVerificationLevel,
    result: input.verification.result,
    reasonCode: input.verification.reasonCode,
    credentialStatus: input.verification.credentialStatus,
    scope: [...input.verification.scope],
    ...(input.verification.creditSource === undefined
      ? {}
      : { creditSource: input.verification.creditSource }),
    ...(input.verification.associatedCreditValue === undefined
      ? {}
      : { associatedCreditValue: structuredClone(input.verification.associatedCreditValue) }),
    ...(input.verification.subjectCreditAssertionValid === undefined
      ? {}
      : { subjectCreditAssertionValid: input.verification.subjectCreditAssertionValid }),
    ...(input.verification.mappingPolicy === undefined
      ? {}
      : { mappingPolicy: structuredClone(input.verification.mappingPolicy) }),
    generatedAt,
    expiresAt,
    ...(input.statusQuery === undefined ? {} : { statusQuery: input.statusQuery }),
    purposeLimited: true,
  };
  return signVerificationResponse(
    unsigned,
    input.responsePrivateKey,
    input.responseKeyId,
  );
}

export function verificationRequestSigningPayload(
  request: VerificationRequest,
): Record<string, unknown> {
  const payload = structuredClone(request) as unknown as Record<string, unknown>;
  delete payload.requestProof;
  return payload;
}

export interface VerifyVerificationRequestInput {
  request: VerificationRequest;
  relyingPartyPublicKey: PublicKeyReference | KeyMaterial;
  now?: string;
  maxClockSkewSeconds?: number;
  consumeAntiReplay?: (key: string) => boolean;
}

export function verifyVerificationRequest(
  input: VerifyVerificationRequestInput,
): { valid: boolean; reasonCode: ReasonCode } {
  const { request } = input;
  if (
    request.messageVersion !== "reference-v1"
    || request.requestId.trim() === ""
    || request.relyingPartyId.trim() === ""
    || request.agentId.trim() === ""
    || request.purpose.trim() === ""
    || request.requestedDataItems.length === 0
    || Object.keys(request.businessContext).length === 0
  ) {
    return { valid: false, reasonCode: "INVALID_REQUEST" };
  }
  if (
    request.verificationLevel === "ASSOCIATED_CREDIT"
    && (
      request.subjectCreditAssertionRef === undefined
      || request.authorizationId === undefined
    )
  ) {
    return { valid: false, reasonCode: "AUTHORIZATION_REQUIRED" };
  }
  const requestedAt = Date.parse(request.requestedAt);
  const currentTime = Date.parse(input.now ?? new Date().toISOString());
  const skewMilliseconds = (input.maxClockSkewSeconds ?? 300) * 1_000;
  if (
    Number.isNaN(requestedAt)
    || Number.isNaN(currentTime)
    || Math.abs(currentTime - requestedAt) > skewMilliseconds
  ) {
    return { valid: false, reasonCode: "REQUEST_EXPIRED" };
  }
  const nonce = request.antiReplay.nonce;
  const idempotencyKey = request.antiReplay.idempotencyKey;
  if (
    (nonce === undefined || nonce.length < 16)
    && (idempotencyKey === undefined || idempotencyKey.length < 8)
  ) {
    return { valid: false, reasonCode: "INVALID_REQUEST" };
  }
  if (!verifyCanonicalSignature(
    verificationRequestSigningPayload(request),
    request.requestProof,
    input.relyingPartyPublicKey,
  )) {
    return { valid: false, reasonCode: "REQUEST_PROOF_INVALID" };
  }
  const replayKey = [
    request.relyingPartyId,
    request.requestId,
    nonce ?? "",
    idempotencyKey ?? "",
  ].join(":");
  if (input.consumeAntiReplay !== undefined && !input.consumeAntiReplay(replayKey)) {
    return { valid: false, reasonCode: "REPLAY_DETECTED" };
  }
  return { valid: true, reasonCode: "VERIFIED" };
}

export function verificationResponseSigningPayload(
  response: Omit<VerificationResponse, "responseProof"> | VerificationResponse,
): Record<string, unknown> {
  const payload = structuredClone(response) as unknown as Record<string, unknown>;
  delete payload.responseProof;
  return payload;
}

export function signVerificationResponse(
  response: Omit<VerificationResponse, "responseProof">,
  privateKey: KeyMaterial,
  keyId?: string,
): VerificationResponse {
  const responseProof: SignatureProof = signCanonical(
    verificationResponseSigningPayload(response),
    privateKey,
    keyId,
  );
  return { ...structuredClone(response), responseProof };
}

export function verifyVerificationResponseProof(
  response: VerificationResponse,
  publicKey: PublicKeyReference | KeyMaterial,
): boolean {
  return verifyCanonicalSignature(
    verificationResponseSigningPayload(response),
    response.responseProof,
    publicKey,
  );
}

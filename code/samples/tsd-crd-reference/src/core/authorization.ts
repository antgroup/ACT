import {
  signCanonical,
  type KeyMaterial,
  verifyCanonicalSignature,
} from "./crypto.ts";
import type {
  AuthorizationEvaluation,
  AuthorizationEvaluationRequest,
  AuthorizationRuntimeState,
  AuthorizationUsage,
  CreditQueryAuthorization,
  PublicKeyReference,
  ResultUseRestrictions,
  SignatureProof,
} from "./types.ts";

export interface CreateAuthorizationInput {
  authorizationId: string;
  authorizationVersion?: "reference-v1";
  mode: "PER_REQUEST" | "PLATFORM_DELEGATED";
  subjectId: string;
  relyingPartyIds?: string[];
  relyingPartyId?: string;
  platformDelegateId?: string;
  platformAgentId?: string;
  agentIds: string[];
  verificationLevel?: "ASSOCIATED_CREDIT";
  purpose: string;
  allowedDataItems?: string[];
  dataItems?: string[];
  validFrom: string;
  expiresAt?: string;
  validUntil?: string;
  frequencyLimit?: {
    maxRequestsPerWindow: number;
    windowDurationSeconds: number;
  };
  maxRequestsPerWindow?: number;
  windowDurationSeconds?: number;
  resultUseRestrictions?: ResultUseRestrictions;
  boundRequestId?: string;
  requestId?: string;
  subjectPrivateKey?: KeyMaterial;
  subjectKeyId?: string;
  authorizationProof?: SignatureProof;
}

function assertNonEmpty(values: string[], field: string): void {
  if (values.length === 0 || values.some((value) => value.trim() === "")) {
    throw new TypeError(`${field} must contain non-empty values`);
  }
  if (new Set(values).size !== values.length) {
    throw new TypeError(`${field} must not contain duplicates`);
  }
}

function authorizationPayload(
  authorization: Record<string, unknown>,
): Record<string, unknown> {
  const copy = structuredClone(authorization) as unknown as Record<string, unknown>;
  delete copy.authorizationProof;
  delete copy.status;
  return copy;
}

export function createAuthorization(
  input: CreateAuthorizationInput,
): CreditQueryAuthorization {
  const relyingPartyIds = input.relyingPartyIds
    ?? (input.relyingPartyId === undefined ? [] : [input.relyingPartyId]);
  const allowedDataItems = input.allowedDataItems ?? input.dataItems ?? [];
  const expiresAt = input.expiresAt ?? input.validUntil;
  if (expiresAt === undefined) throw new TypeError("expiresAt is required");
  const platformDelegateId = input.platformDelegateId ?? input.platformAgentId;
  const boundRequestId = input.boundRequestId ?? input.requestId;
  const frequencyLimit = input.frequencyLimit
    ?? (
      input.maxRequestsPerWindow !== undefined
      && input.windowDurationSeconds !== undefined
        ? {
            maxRequestsPerWindow: input.maxRequestsPerWindow,
            windowDurationSeconds: input.windowDurationSeconds,
          }
        : undefined
    );

  for (const [field, value] of [
    ["authorizationId", input.authorizationId],
    ["subjectId", input.subjectId],
    ["purpose", input.purpose],
  ] as const) {
    if (value.trim() === "") throw new TypeError(`${field} is required`);
  }
  if (
    Number.isNaN(Date.parse(input.validFrom))
    || Number.isNaN(Date.parse(expiresAt))
  ) {
    throw new TypeError("validFrom and expiresAt must be RFC 3339 timestamps");
  }
  if (
    input.verificationLevel !== undefined
    && input.verificationLevel !== "ASSOCIATED_CREDIT"
  ) {
    throw new TypeError("verificationLevel must be ASSOCIATED_CREDIT");
  }
  if (
    input.authorizationVersion !== undefined
    && input.authorizationVersion !== "reference-v1"
  ) {
    throw new TypeError("authorizationVersion must be reference-v1");
  }

  assertNonEmpty(relyingPartyIds, "relyingPartyIds");
  assertNonEmpty(input.agentIds, "agentIds");
  assertNonEmpty(allowedDataItems, "allowedDataItems");
  if (Date.parse(input.validFrom) >= Date.parse(expiresAt)) {
    throw new TypeError("expiresAt must be after validFrom");
  }

  if (input.mode === "PER_REQUEST") {
    if (boundRequestId === undefined) {
      throw new TypeError("boundRequestId is required for PER_REQUEST");
    }
    if (boundRequestId.trim() === "") {
      throw new TypeError("boundRequestId must be non-empty");
    }
    if (platformDelegateId !== undefined || frequencyLimit !== undefined) {
      throw new TypeError(
        "PER_REQUEST forbids platformDelegateId and frequencyLimit",
      );
    }
  } else {
    if (platformDelegateId === undefined || frequencyLimit === undefined) {
      throw new TypeError(
        "PLATFORM_DELEGATED requires platformDelegateId and frequencyLimit",
      );
    }
    if (platformDelegateId.trim() === "") {
      throw new TypeError("platformDelegateId must be non-empty");
    }
    if (boundRequestId !== undefined) {
      throw new TypeError("PLATFORM_DELEGATED forbids boundRequestId");
    }
    if (
      !Number.isInteger(frequencyLimit.maxRequestsPerWindow)
      || frequencyLimit.maxRequestsPerWindow <= 0
      || !Number.isInteger(frequencyLimit.windowDurationSeconds)
      || frequencyLimit.windowDurationSeconds <= 0
    ) {
      throw new TypeError("frequencyLimit values must be positive integers");
    }
  }

  const restrictions = input.resultUseRestrictions ?? {
    mayStore: false,
    mayTransfer: false,
  };
  if (
    restrictions.mayStore
    && (!Number.isInteger(restrictions.retentionSeconds)
      || (restrictions.retentionSeconds ?? 0) <= 0)
  ) {
    throw new TypeError("retentionSeconds is required when mayStore is true");
  }

  const unsigned = {
    authorizationId: input.authorizationId,
    authorizationVersion: input.authorizationVersion ?? "reference-v1",
    mode: input.mode,
    subjectId: input.subjectId,
    relyingPartyIds: [...relyingPartyIds],
    ...(platformDelegateId === undefined ? {} : { platformDelegateId }),
    agentIds: [...input.agentIds],
    verificationLevel: "ASSOCIATED_CREDIT",
    purpose: input.purpose,
    allowedDataItems: [...allowedDataItems],
    validFrom: input.validFrom,
    expiresAt,
    ...(frequencyLimit === undefined ? {} : { frequencyLimit }),
    resultUseRestrictions: restrictions,
    status: "ACTIVE",
    ...(boundRequestId === undefined ? {} : { boundRequestId }),
  } satisfies Omit<CreditQueryAuthorization, "authorizationProof">;

  if (input.authorizationProof === undefined && input.subjectPrivateKey === undefined) {
    throw new TypeError("authorizationProof or subjectPrivateKey is required");
  }
  if (
    input.authorizationProof !== undefined
    && (
      input.authorizationProof.signatureAlgorithm !== "Ed25519"
      || input.authorizationProof.signatureValue.trim() === ""
    )
  ) {
    throw new TypeError("authorizationProof must use Ed25519 and be non-empty");
  }
  const proof = input.authorizationProof
    ?? signCanonical(
      authorizationPayload(unsigned as unknown as Record<string, unknown>),
      input.subjectPrivateKey!,
      input.subjectKeyId,
    );
  return { ...unsigned, authorizationProof: proof };
}

export function evaluateAuthorization(
  authorization: CreditQueryAuthorization,
  request: AuthorizationEvaluationRequest & { dataItems?: string[] },
  now = new Date().toISOString(),
  usage: AuthorizationUsage[] = [],
): AuthorizationEvaluation & { authorization: CreditQueryAuthorization } {
  const requestedDataItems = request.requestedDataItems ?? request.dataItems ?? [];
  const currentState: AuthorizationRuntimeState = {
    useCount: usage.length,
    usageTimestamps: usage.map((entry) => entry.usedAt),
  };
  const deny = (reasonCode: AuthorizationEvaluation["reasonCode"]) => ({
    allowed: false,
    reasonCode,
    authorizedDataItems: [],
    runtimeState: currentState,
    authorization: structuredClone(authorization),
  });

  if (authorization.status === "REVOKED") return deny("AUTHORIZATION_REVOKED");
  if (
    authorization.status === "EXPIRED"
    || Date.parse(now) < Date.parse(authorization.validFrom)
    || Date.parse(now) >= Date.parse(authorization.expiresAt)
  ) {
    return deny("AUTHORIZATION_EXPIRED");
  }
  if (
    request.verificationLevel !== "ASSOCIATED_CREDIT"
    || !authorization.relyingPartyIds.includes(request.relyingPartyId)
    || !authorization.agentIds.includes(request.agentId)
    || authorization.purpose !== request.purpose
    || requestedDataItems.some(
      (item) => !authorization.allowedDataItems.includes(item),
    )
    || (
      authorization.mode === "PER_REQUEST"
      && authorization.boundRequestId !== request.requestId
    )
    || (
      authorization.mode === "PLATFORM_DELEGATED"
      && authorization.platformDelegateId !== request.platformDelegateId
    )
  ) {
    return deny("AUTHORIZATION_SCOPE_MISMATCH");
  }

  if (authorization.mode === "PER_REQUEST" && currentState.useCount > 0) {
    return deny("AUTHORIZATION_SCOPE_MISMATCH");
  }
  if (authorization.frequencyLimit !== undefined) {
    const windowStart = Date.parse(now)
      - authorization.frequencyLimit.windowDurationSeconds * 1_000;
    const recentUses = usage.filter(
      (entry) => Date.parse(entry.usedAt) > windowStart && Date.parse(entry.usedAt) <= Date.parse(now),
    );
    if (recentUses.length >= authorization.frequencyLimit.maxRequestsPerWindow) {
      return deny("AUTHORIZATION_SCOPE_MISMATCH");
    }
  }

  return {
    allowed: true,
    reasonCode: "VERIFIED",
    authorizedDataItems: [...requestedDataItems],
    runtimeState: {
      useCount: currentState.useCount + 1,
      usageTimestamps: [...currentState.usageTimestamps, now],
    },
    authorization: structuredClone(authorization),
  };
}

export function revokeAuthorization(
  authorization: CreditQueryAuthorization,
  _revokedAt = new Date().toISOString(),
): CreditQueryAuthorization {
  return {
    ...structuredClone(authorization),
    status: "REVOKED",
  };
}

export function authorizationSigningPayload(
  authorization: CreditQueryAuthorization,
): Record<string, unknown> {
  return authorizationPayload(authorization as unknown as Record<string, unknown>);
}

export function verifyAuthorizationProof(
  authorization: CreditQueryAuthorization,
  subjectPublicKey: PublicKeyReference | KeyMaterial,
): boolean {
  return verifyCanonicalSignature(
    authorizationSigningPayload(authorization),
    authorization.authorizationProof,
    subjectPublicKey,
  );
}

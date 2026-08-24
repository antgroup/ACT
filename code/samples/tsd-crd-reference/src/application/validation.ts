import type {
  AntiReplay,
  SignatureProof,
  VerificationRequest,
} from "../core/index.ts";

function requiredString(
  value: Record<string, unknown>,
  field: string,
): string {
  const candidate = value[field];
  if (typeof candidate !== "string" || candidate.trim() === "") {
    throw new Error(`${field} must be a non-empty string`);
  }
  return candidate;
}

function requiredRecord(
  value: Record<string, unknown>,
  field: string,
): Record<string, unknown> {
  const candidate = value[field];
  if (candidate === null || Array.isArray(candidate) || typeof candidate !== "object") {
    throw new Error(`${field} must be an object`);
  }
  return candidate as Record<string, unknown>;
}

function requiredStringArray(
  value: Record<string, unknown>,
  field: string,
): string[] {
  const candidate = value[field];
  if (!Array.isArray(candidate) || candidate.length === 0
    || candidate.some((entry) => typeof entry !== "string" || entry === "")) {
    throw new Error(`${field} must be a non-empty string array`);
  }
  if (new Set(candidate).size !== candidate.length) {
    throw new Error(`${field} must not contain duplicates`);
  }
  return [...candidate];
}

function requiredIsoDate(value: Record<string, unknown>, field: string): string {
  const candidate = requiredString(value, field);
  if (Number.isNaN(Date.parse(candidate))) {
    throw new Error(`${field} must be an RFC 3339 timestamp`);
  }
  return candidate;
}

export type ValidAssociationApplication = {
  applicationId: string;
  messageVersion: "reference-v1";
  subjectId: string;
  agentId: string;
  associationRole: string;
  relationshipEvidenceRefs: string[];
  confirmationMethod: "ATTESTED_CONFIRMATION" | "DIRECT_SIGNATURE";
  issuerId: string;
  purpose: string;
  scope: string[];
  authorizationMode: "PER_REQUEST" | "PLATFORM_DELEGATED";
  requestedAt: string;
  validFrom: string;
  expiresAt?: string;
  antiReplay: Record<string, unknown>;
};

export function validateAntiReplay(value: unknown): AntiReplay {
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error("antiReplay must be an object");
  }
  const record = value as Record<string, unknown>;
  const allowed = new Set(["nonce", "idempotencyKey"]);
  if (Object.keys(record).some((key) => !allowed.has(key))) {
    throw new Error("antiReplay contains unsupported fields");
  }
  const nonce = record.nonce;
  const idempotencyKey = record.idempotencyKey;
  if ((typeof nonce !== "string" || nonce.length < 16 || nonce.length > 256)
    && (typeof idempotencyKey !== "string" || idempotencyKey.length < 8
      || idempotencyKey.length > 256)) {
    throw new Error("antiReplay requires nonce or idempotencyKey");
  }
  return {
    ...(typeof nonce === "string" ? { nonce } : {}),
    ...(typeof idempotencyKey === "string" ? { idempotencyKey } : {}),
  };
}

export function validateProof(value: unknown, field = "requestProof"): SignatureProof {
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${field} must be an object`);
  }
  const record = value as Record<string, unknown>;
  const allowed = new Set(["signatureAlgorithm", "signatureValue", "keyId"]);
  if (Object.keys(record).some((key) => !allowed.has(key))) {
    throw new Error(`${field} contains unsupported fields`);
  }
  const signatureAlgorithm = requiredString(record, "signatureAlgorithm");
  if (signatureAlgorithm !== "Ed25519") {
    throw new Error(`${field}.signatureAlgorithm must be Ed25519`);
  }
  const signatureValue = requiredString(record, "signatureValue");
  return {
    signatureAlgorithm,
    signatureValue,
    ...(record.keyId === undefined ? {} : { keyId: requiredString(record, "keyId") }),
  };
}

function assertFresh(requestedAt: string, now: string, maxClockSkewSeconds = 300): void {
  const requestTime = Date.parse(requestedAt);
  const currentTime = Date.parse(now);
  if (
    Number.isNaN(requestTime)
    || Number.isNaN(currentTime)
    || Math.abs(currentTime - requestTime) > maxClockSkewSeconds * 1_000
  ) {
    throw new Error("REQUEST_EXPIRED: requestedAt is outside the allowed time window");
  }
}

export function validateVerificationRequest(
  input: Record<string, unknown>,
  now: string,
): VerificationRequest {
  const messageVersion = requiredString(input, "messageVersion");
  if (messageVersion !== "reference-v1") {
    throw new Error("messageVersion must be reference-v1");
  }
  const verificationLevel = requiredString(input, "verificationLevel");
  if (verificationLevel !== "CREDENTIAL" && verificationLevel !== "ASSOCIATED_CREDIT") {
    throw new Error("Unsupported verificationLevel");
  }
  const requestedAt = requiredIsoDate(input, "requestedAt");
  assertFresh(requestedAt, now);
  const businessContext = requiredRecord(input, "businessContext");
  if (Object.keys(businessContext).length === 0) {
    throw new Error("businessContext must not be empty");
  }
  if (Object.values(businessContext).some((entry) => ![
    "string",
    "number",
    "boolean",
  ].includes(typeof entry))) {
    throw new Error("businessContext values must be scalar");
  }
  const credential = requiredRecord(input, "credential") as VerificationRequest["credential"];
  requiredString(credential as unknown as Record<string, unknown>, "credentialId");
  const authorizationId = input.authorizationId === undefined
    ? undefined
    : requiredString(input, "authorizationId");
  const subjectCreditAssertionRef = input.subjectCreditAssertionRef === undefined
    ? undefined
    : requiredString(input, "subjectCreditAssertionRef");
  if (
    verificationLevel === "ASSOCIATED_CREDIT"
    && (authorizationId === undefined || subjectCreditAssertionRef === undefined)
  ) {
    throw new Error(
      "ASSOCIATED_CREDIT requires authorizationId and subjectCreditAssertionRef",
    );
  }
  return {
    requestId: requiredString(input, "requestId"),
    messageVersion,
    relyingPartyId: requiredString(input, "relyingPartyId"),
    agentId: requiredString(input, "agentId"),
    verificationLevel,
    ...(subjectCreditAssertionRef === undefined ? {} : { subjectCreditAssertionRef }),
    ...(authorizationId === undefined ? {} : { authorizationId }),
    ...(input.platformDelegateId === undefined
      ? {}
      : { platformDelegateId: requiredString(input, "platformDelegateId") }),
    purpose: requiredString(input, "purpose"),
    businessContext: structuredClone(businessContext) as VerificationRequest["businessContext"],
    requestedDataItems: requiredStringArray(input, "requestedDataItems"),
    credential: structuredClone(credential),
    requestedAt,
    antiReplay: validateAntiReplay(input.antiReplay),
    requestProof: validateProof(input.requestProof),
  };
}

export type ValidStatusChangeRequest = {
  requestId: string;
  credentialId: string;
  targetStatus: "ACTIVE" | "SUSPENDED" | "REVOKED";
  reasonCode: string;
  requestedBy: string;
  requestedAt: string;
  antiReplay: AntiReplay;
  requestProof: SignatureProof;
};

export function validateStatusChangeRequest(
  input: Record<string, unknown>,
  now: string,
): ValidStatusChangeRequest {
  const targetStatus = requiredString(input, "targetStatus");
  if (!(["ACTIVE", "SUSPENDED", "REVOKED"] as const).includes(targetStatus as never)) {
    throw new Error("Unsupported targetStatus");
  }
  const requestedAt = requiredIsoDate(input, "requestedAt");
  assertFresh(requestedAt, now);
  return {
    requestId: requiredString(input, "requestId"),
    credentialId: requiredString(input, "credentialId"),
    targetStatus: targetStatus as ValidStatusChangeRequest["targetStatus"],
    reasonCode: requiredString(input, "reasonCode"),
    requestedBy: requiredString(input, "requestedBy"),
    requestedAt,
    antiReplay: validateAntiReplay(input.antiReplay),
    requestProof: validateProof(input.requestProof),
  };
}

export type ValidAuthorizationRevocationRequest = {
  requestId: string;
  authorizationId: string;
  subjectId: string;
  reasonCode: string;
  requestedAt: string;
  antiReplay: AntiReplay;
  requestProof: SignatureProof;
};

export function validateAuthorizationRevocationRequest(
  input: Record<string, unknown>,
  now: string,
): ValidAuthorizationRevocationRequest {
  const requestedAt = requiredIsoDate(input, "requestedAt");
  assertFresh(requestedAt, now);
  return {
    requestId: requiredString(input, "requestId"),
    authorizationId: requiredString(input, "authorizationId"),
    subjectId: requiredString(input, "subjectId"),
    reasonCode: requiredString(input, "reasonCode"),
    requestedAt,
    antiReplay: validateAntiReplay(input.antiReplay),
    requestProof: validateProof(input.requestProof),
  };
}

export function validateAssociationApplication(
  input: Record<string, unknown>,
): ValidAssociationApplication {
  const messageVersion = requiredString(input, "messageVersion");
  if (messageVersion !== "reference-v1") {
    throw new Error("messageVersion must be reference-v1");
  }

  const confirmationMethod = requiredString(input, "confirmationMethod");
  if (confirmationMethod !== "ATTESTED_CONFIRMATION"
    && confirmationMethod !== "DIRECT_SIGNATURE") {
    throw new Error("Unsupported confirmationMethod");
  }

  const authorizationMode = requiredString(input, "authorizationMode");
  if (authorizationMode !== "PER_REQUEST"
    && authorizationMode !== "PLATFORM_DELEGATED") {
    throw new Error("Unsupported authorizationMode");
  }

  const antiReplay = validateAntiReplay(input.antiReplay);

  const expiresAt = input.expiresAt === undefined
    ? undefined
    : requiredIsoDate(input, "expiresAt");

  return {
    applicationId: requiredString(input, "applicationId"),
    messageVersion: "reference-v1",
    subjectId: requiredString(input, "subjectId"),
    agentId: requiredString(input, "agentId"),
    associationRole: requiredString(input, "associationRole"),
    relationshipEvidenceRefs: requiredStringArray(input, "relationshipEvidenceRefs"),
    confirmationMethod,
    issuerId: requiredString(input, "issuerId"),
    purpose: requiredString(input, "purpose"),
    scope: requiredStringArray(input, "scope"),
    authorizationMode,
    requestedAt: requiredIsoDate(input, "requestedAt"),
    validFrom: requiredIsoDate(input, "validFrom"),
    ...(expiresAt ? { expiresAt } : {}),
    antiReplay: structuredClone(antiReplay) as Record<string, unknown>,
  };
}

export function antiReplayValue(antiReplay: Record<string, unknown>): string {
  if (typeof antiReplay.nonce === "string") return `nonce:${antiReplay.nonce}`;
  return `idempotency:${String(antiReplay.idempotencyKey)}`;
}

export function asString(value: Record<string, unknown>, field: string): string {
  return requiredString(value, field);
}

export function asStringArray(value: Record<string, unknown>, field: string): string[] {
  return requiredStringArray(value, field);
}

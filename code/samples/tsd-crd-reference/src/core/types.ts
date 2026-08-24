export type JsonPrimitive = null | boolean | number | string;

export type JsonValue =
  | JsonPrimitive
  | JsonValue[]
  | { [key: string]: JsonValue };

export const CONFIRMATION_METHODS = [
  "DIRECT_SIGNATURE",
  "ATTESTED_CONFIRMATION",
] as const;
export type ConfirmationMethod = (typeof CONFIRMATION_METHODS)[number];

export const CREDENTIAL_STATUSES = [
  "PENDING",
  "ACTIVE",
  "SUSPENDED",
  "REVOKED",
  "EXPIRED",
] as const;
export type CredentialStatus = (typeof CREDENTIAL_STATUSES)[number];

export const VERIFICATION_LEVELS = [
  "CREDENTIAL",
  "ASSOCIATED_CREDIT",
] as const;
export type VerificationLevel = (typeof VERIFICATION_LEVELS)[number];

export const VERIFICATION_RESULTS = [
  "PASS",
  "FAIL",
  "INCONCLUSIVE",
  "REVIEW_REQUIRED",
] as const;
export type VerificationResult = (typeof VERIFICATION_RESULTS)[number];

export const REASON_CODES = [
  "VERIFIED",
  "INVALID_REQUEST",
  "REQUEST_PROOF_INVALID",
  "REQUEST_EXPIRED",
  "REPLAY_DETECTED",
  "AUTHORIZATION_REQUIRED",
  "AUTHORIZATION_EXPIRED",
  "AUTHORIZATION_REVOKED",
  "AUTHORIZATION_SCOPE_MISMATCH",
  "AGENT_NOT_REGISTERED",
  "ASSOCIATION_CREDENTIAL_NOT_FOUND",
  "ASSOCIATION_CREDENTIAL_NOT_ACTIVE",
  "ASSOCIATION_PROOF_INVALID",
  "CREDIT_ASSERTION_UNAVAILABLE",
  "CREDIT_ASSERTION_INVALID",
  "MAPPING_POLICY_UNSUPPORTED",
  "INCONCLUSIVE",
  "REVIEW_REQUIRED",
] as const;
export type ReasonCode = (typeof REASON_CODES)[number];

export interface PublicKeyReference {
  keyId: string;
  format: "pem-spki";
  value: string;
}

export interface SignatureProof {
  signatureAlgorithm: "Ed25519" | string;
  signatureValue: string;
  keyId?: string;
}

export interface Ed25519KeyPair {
  algorithm: "Ed25519";
  keyId: string;
  publicKey: PublicKeyReference;
  privateKey: string;
}

export interface MappingPolicyReference {
  id: string;
  version: string;
}

export interface MappingTrace {
  subjectCreditAssertionRef: string;
  associatedCreditValue: JsonValue;
  mappingPolicy: MappingPolicyReference;
  creditSource: "ASSOCIATED_CREDIT";
}

export interface StatusQueryReference {
  uri: string;
  method?: "GET" | "POST";
}

export interface AssociationCredential {
  credentialId: string;
  credentialVersion: string;
  associationApplicationId: string;
  agentId: string;
  subjectId: string;
  associationRole?: string;
  issuerId: string;
  relationshipEvidenceRef: string;
  confirmationMethod: ConfirmationMethod;
  subjectCreditAssertionRef: string;
  associatedCreditValue: JsonValue;
  creditSource: "ASSOCIATED_CREDIT";
  mappingPolicy: MappingPolicyReference;
  confirmationStatement: string;
  purpose: string;
  scope: string[];
  associationApplicationRequestedAt?: string;
  associationApplicationAntiReplay?: AntiReplay;
  subjectPublicKey?: PublicKeyReference;
  subjectSignature?: string;
  subjectSignatureAlgorithm?: string;
  issuedAt: string;
  validFrom: string;
  expiresAt?: string;
  statusQuery: StatusQueryReference;
  previousCredentialRef?: string;
  issuerSignature: string;
  issuerSignatureAlgorithm: string;
}

export type UnsignedAssociationCredential = Omit<
  AssociationCredential,
  | "subjectSignature"
  | "subjectSignatureAlgorithm"
  | "issuerSignature"
  | "issuerSignatureAlgorithm"
> & {
  subjectSignature?: never;
  subjectSignatureAlgorithm?: never;
  issuerSignature?: never;
  issuerSignatureAlgorithm?: never;
};

export interface CredentialStatusRecord {
  credentialId: string;
  status: CredentialStatus;
  changedAt: string;
  reasonCode?: string;
  previousStatus?: CredentialStatus;
}

export const AUTHORIZATION_MODES = ["PER_REQUEST", "PLATFORM_DELEGATED"] as const;
export type AuthorizationMode = (typeof AUTHORIZATION_MODES)[number];

export const AUTHORIZATION_STATUSES = ["ACTIVE", "REVOKED", "EXPIRED"] as const;
export type AuthorizationStatus = (typeof AUTHORIZATION_STATUSES)[number];

export interface FrequencyLimit {
  maxRequestsPerWindow: number;
  windowDurationSeconds: number;
}

export interface ResultUseRestrictions {
  mayStore: boolean;
  retentionSeconds?: number;
  mayTransfer: boolean;
}

export type BusinessContext = Record<string, string | number | boolean>;

export interface CreditQueryAuthorization {
  authorizationId: string;
  authorizationVersion: "reference-v1";
  mode: AuthorizationMode;
  subjectId: string;
  relyingPartyIds: string[];
  platformDelegateId?: string;
  agentIds: string[];
  verificationLevel: "ASSOCIATED_CREDIT";
  purpose: string;
  allowedDataItems: string[];
  validFrom: string;
  expiresAt: string;
  frequencyLimit?: FrequencyLimit;
  resultUseRestrictions: ResultUseRestrictions;
  status: AuthorizationStatus;
  boundRequestId?: string;
  authorizationProof: SignatureProof;
}

export type QueryAuthorization = CreditQueryAuthorization;

export type UnsignedCreditQueryAuthorization = Omit<
  CreditQueryAuthorization,
  "authorizationProof" | "status"
> & {
  authorizationProof?: never;
  status?: never;
};

export type UnsignedQueryAuthorization = UnsignedCreditQueryAuthorization;

export interface AuthorizationEvaluationRequest {
  requestId: string;
  relyingPartyId: string;
  agentId: string;
  verificationLevel: VerificationLevel;
  purpose: string;
  requestedDataItems: string[];
  platformDelegateId?: string;
}

export interface AntiReplay {
  nonce?: string;
  idempotencyKey?: string;
}

export interface AuthorizationUsage {
  usedAt: string;
}

export interface AuthorizationRuntimeState {
  useCount: number;
  usageTimestamps: string[];
}

export interface AuthorizationEvaluation {
  allowed: boolean;
  reasonCode: ReasonCode;
  authorizedDataItems: string[];
  runtimeState: AuthorizationRuntimeState;
}

export interface CredentialReferenceInput {
  credentialId: string;
  uri?: string;
}

export type CredentialInput = AssociationCredential | CredentialReferenceInput;

export interface VerificationRequest {
  requestId: string;
  messageVersion: string;
  relyingPartyId: string;
  agentId: string;
  verificationLevel: VerificationLevel;
  subjectCreditAssertionRef?: string;
  authorizationId?: string;
  platformDelegateId?: string;
  purpose: string;
  businessContext: BusinessContext;
  requestedDataItems: string[];
  credential: CredentialInput;
  requestedAt: string;
  antiReplay: AntiReplay;
  requestProof: SignatureProof;
}

export interface VerificationResponse {
  requestId: string;
  verificationRecordId: string;
  agentId: string;
  completedLevel: VerificationLevel;
  result: VerificationResult;
  reasonCode: ReasonCode;
  credentialStatus: CredentialStatus;
  creditSource?: "ASSOCIATED_CREDIT";
  associatedCreditValue?: JsonValue;
  subjectCreditAssertionValid?: boolean;
  mappingPolicy?: MappingPolicyReference;
  scope: string[];
  generatedAt: string;
  expiresAt: string;
  statusQuery?: StatusQueryReference;
  purposeLimited: true;
  responseProof: SignatureProof;
}

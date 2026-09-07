import type {
  AssociationCredential,
  PublicKeyReference,
  SignatureProof,
} from "./types.ts";
import {
  signCanonical,
  type KeyMaterial,
  verifyCanonicalSignature,
} from "./crypto.ts";
import { mappingTraceFromCredential, validateMappingTrace } from "./mapping.ts";

type CredentialDraft = Omit<
  AssociationCredential,
  | "issuerSignature"
  | "issuerSignatureAlgorithm"
  | "subjectSignature"
  | "subjectSignatureAlgorithm"
  | "subjectPublicKey"
  | "confirmationMethod"
> & Record<string, unknown>;

export interface IssueAttestedCredentialInput {
  credential: CredentialDraft | AssociationCredential;
  issuerPrivateKey: KeyMaterial;
  issuerKeyId?: string;
}

export interface IssueDirectCredentialInput {
  credential: CredentialDraft | AssociationCredential;
  subjectPrivateKey: KeyMaterial;
  subjectPublicKey?: PublicKeyReference;
  subjectKeyId?: string;
  issuerPrivateKey: KeyMaterial;
  issuerKeyId?: string;
}

export interface IssueDirectCredentialFromConfirmationInput {
  credential: CredentialDraft | AssociationCredential;
  subjectPublicKey: PublicKeyReference;
  subjectSignature: string;
  subjectSignatureAlgorithm: string;
  issuerPrivateKey: KeyMaterial;
  issuerKeyId?: string;
}

function withoutKeys<T extends Record<string, unknown>>(
  value: T,
  keys: readonly string[],
): Record<string, unknown> {
  const copy = structuredClone(value);
  for (const key of keys) delete copy[key];
  return copy;
}

function assertCredentialBase(value: Record<string, unknown>): void {
  const required = [
    "credentialId",
    "credentialVersion",
    "associationApplicationId",
    "agentId",
    "subjectId",
    "issuerId",
    "relationshipEvidenceRef",
    "subjectCreditAssertionRef",
    "associatedCreditValue",
    "creditSource",
    "mappingPolicy",
    "confirmationStatement",
    "purpose",
    "scope",
    "issuedAt",
    "validFrom",
    "statusQuery",
  ];
  for (const field of required) {
    if (value[field] === undefined || value[field] === "") {
      throw new TypeError(`${field} is required`);
    }
  }
  if (value.credentialVersion !== "reference-v1") {
    throw new TypeError("credentialVersion must be reference-v1");
  }
  const stringFields = required.filter(
    (field) => !["associatedCreditValue", "mappingPolicy", "scope", "statusQuery"].includes(field),
  );
  for (const field of stringFields) {
    if (typeof value[field] !== "string" || value[field].trim() === "") {
      throw new TypeError(`${field} must be a non-empty string`);
    }
  }
  if (
    !Array.isArray(value.scope)
    || value.scope.length === 0
    || value.scope.some((entry) => typeof entry !== "string" || entry.trim() === "")
    || new Set(value.scope).size !== value.scope.length
  ) {
    throw new TypeError("scope must be a non-empty set of strings");
  }
  const statusQuery = value.statusQuery as Record<string, unknown>;
  if (
    statusQuery === null
    || typeof statusQuery !== "object"
    || typeof statusQuery.uri !== "string"
    || statusQuery.uri.trim() === ""
  ) {
    throw new TypeError("statusQuery.uri is required");
  }
  for (const field of ["issuedAt", "validFrom", "expiresAt"] as const) {
    if (value[field] !== undefined && Number.isNaN(Date.parse(String(value[field])))) {
      throw new TypeError(`${field} must be an RFC 3339 timestamp`);
    }
  }
  if (
    value.expiresAt !== undefined
    && Date.parse(String(value.expiresAt)) <= Date.parse(String(value.validFrom))
  ) {
    throw new TypeError("expiresAt must be after validFrom");
  }
  if (value.creditSource !== "ASSOCIATED_CREDIT") {
    throw new TypeError("creditSource must be ASSOCIATED_CREDIT");
  }
  if (value.confirmationMethod === "DIRECT_SIGNATURE") {
    if (
      typeof value.associationApplicationRequestedAt !== "string"
      || Number.isNaN(Date.parse(value.associationApplicationRequestedAt))
    ) {
      throw new TypeError(
        "associationApplicationRequestedAt is required for DIRECT_SIGNATURE",
      );
    }
    const antiReplay = value.associationApplicationAntiReplay;
    if (antiReplay === null || Array.isArray(antiReplay) || typeof antiReplay !== "object") {
      throw new TypeError(
        "associationApplicationAntiReplay is required for DIRECT_SIGNATURE",
      );
    }
    const record = antiReplay as Record<string, unknown>;
    const nonce = record.nonce;
    const idempotencyKey = record.idempotencyKey;
    if (
      (typeof nonce !== "string" || nonce.length < 16)
      && (typeof idempotencyKey !== "string" || idempotencyKey.length < 8)
    ) {
      throw new TypeError(
        "associationApplicationAntiReplay requires nonce or idempotencyKey",
      );
    }
  }

  const trace = mappingTraceFromCredential(value as unknown as AssociationCredential);
  if (trace !== undefined) {
    const result = validateMappingTrace(trace);
    if (!result.valid) throw new TypeError(result.errors.join("; "));
  }
}

export function subjectConfirmationPayload(
  credential: AssociationCredential | Record<string, unknown>,
): Record<string, unknown> {
  const payload = withoutKeys(credential as Record<string, unknown>, [
    "subjectPublicKey",
    "subjectSignature",
    "subjectSignatureAlgorithm",
    "issuerSignature",
    "issuerSignatureAlgorithm",
    "previousCredentialRef",
  ]);
  payload.confirmationMethod = "DIRECT_SIGNATURE";
  return payload;
}

export function issuerCredentialPayload(
  credential: AssociationCredential | Record<string, unknown>,
): Record<string, unknown> {
  return withoutKeys(credential as Record<string, unknown>, [
    "issuerSignature",
    "issuerSignatureAlgorithm",
    "statusQuery",
    "previousCredentialRef",
  ]);
}

export function createDirectConfirmation(input: {
  credential: AssociationCredential | Record<string, unknown>;
  subjectPrivateKey: KeyMaterial;
  subjectKeyId?: string;
}): SignatureProof {
  return signCanonical(
    subjectConfirmationPayload(input.credential),
    input.subjectPrivateKey,
    input.subjectKeyId,
  );
}

export function issueAttestedCredential(
  input: IssueAttestedCredentialInput,
): AssociationCredential {
  const base = withoutKeys(input.credential as Record<string, unknown>, [
    "subjectPublicKey",
    "subjectSignature",
    "subjectSignatureAlgorithm",
    "issuerSignature",
    "issuerSignatureAlgorithm",
  ]);
  const credential = {
    ...base,
    confirmationMethod: "ATTESTED_CONFIRMATION",
  } as unknown as AssociationCredential;
  assertCredentialBase(credential as unknown as Record<string, unknown>);
  const proof = signCanonical(
    issuerCredentialPayload(credential),
    input.issuerPrivateKey,
    input.issuerKeyId,
  );
  return {
    ...credential,
    issuerSignature: proof.signatureValue,
    issuerSignatureAlgorithm: proof.signatureAlgorithm,
  };
}

export function issueDirectCredential(
  input: IssueDirectCredentialInput,
): AssociationCredential {
  const suppliedPublicKey = input.subjectPublicKey
    ?? (input.credential as AssociationCredential).subjectPublicKey;
  if (suppliedPublicKey === undefined) {
    throw new TypeError("subjectPublicKey is required for DIRECT_SIGNATURE");
  }

  const base = withoutKeys(input.credential as Record<string, unknown>, [
    "subjectSignature",
    "subjectSignatureAlgorithm",
    "issuerSignature",
    "issuerSignatureAlgorithm",
  ]);
  const unsigned = {
    ...base,
    confirmationMethod: "DIRECT_SIGNATURE",
    subjectPublicKey: structuredClone(suppliedPublicKey),
  } as unknown as AssociationCredential;
  assertCredentialBase(unsigned as unknown as Record<string, unknown>);

  const subjectProof = createDirectConfirmation({
    credential: unsigned,
    subjectPrivateKey: input.subjectPrivateKey,
    subjectKeyId: input.subjectKeyId ?? suppliedPublicKey.keyId,
  });
  const subjectSigned: AssociationCredential = {
    ...unsigned,
    subjectSignature: subjectProof.signatureValue,
    subjectSignatureAlgorithm: subjectProof.signatureAlgorithm,
    issuerSignature: "",
    issuerSignatureAlgorithm: "",
  };
  const issuerProof = signCanonical(
    issuerCredentialPayload(subjectSigned),
    input.issuerPrivateKey,
    input.issuerKeyId,
  );
  return {
    ...subjectSigned,
    issuerSignature: issuerProof.signatureValue,
    issuerSignatureAlgorithm: issuerProof.signatureAlgorithm,
  };
}

/**
 * Issuer-side DIRECT_SIGNATURE flow. The subject signs locally and submits
 * only its public key and inner signature. The issuer verifies that proof
 * before adding the outer signature.
 */
export function issueDirectCredentialFromConfirmation(
  input: IssueDirectCredentialFromConfirmationInput,
): AssociationCredential {
  const base = withoutKeys(input.credential as Record<string, unknown>, [
    "subjectPublicKey",
    "subjectSignature",
    "subjectSignatureAlgorithm",
    "issuerSignature",
    "issuerSignatureAlgorithm",
  ]);
  const subjectSigned = {
    ...base,
    confirmationMethod: "DIRECT_SIGNATURE",
    subjectPublicKey: structuredClone(input.subjectPublicKey),
    subjectSignature: input.subjectSignature,
    subjectSignatureAlgorithm: input.subjectSignatureAlgorithm,
    issuerSignature: "",
    issuerSignatureAlgorithm: "",
  } as unknown as AssociationCredential;
  assertCredentialBase(subjectSigned as unknown as Record<string, unknown>);
  const subjectValid = verifyCanonicalSignature(
    subjectConfirmationPayload(subjectSigned),
    {
      signatureAlgorithm: input.subjectSignatureAlgorithm,
      signatureValue: input.subjectSignature,
      keyId: input.subjectPublicKey.keyId,
    },
    input.subjectPublicKey,
  );
  if (!subjectValid) throw new Error("ASSOCIATION_PROOF_INVALID");

  const issuerProof = signCanonical(
    issuerCredentialPayload(subjectSigned),
    input.issuerPrivateKey,
    input.issuerKeyId,
  );
  return {
    ...subjectSigned,
    issuerSignature: issuerProof.signatureValue,
    issuerSignatureAlgorithm: issuerProof.signatureAlgorithm,
  };
}

export interface VerifyCredentialProofInput {
  credential: AssociationCredential;
  issuerPublicKey: PublicKeyReference | KeyMaterial;
  subjectPublicKey?: PublicKeyReference | KeyMaterial;
}

export function verifyCredentialProof(input: VerifyCredentialProofInput): boolean {
  const { credential } = input;
  if (credential.issuerSignatureAlgorithm !== "Ed25519") return false;
  const issuerValid = verifyCanonicalSignature(
    issuerCredentialPayload(credential),
    {
      signatureAlgorithm: credential.issuerSignatureAlgorithm,
      signatureValue: credential.issuerSignature,
    },
    input.issuerPublicKey,
  );
  if (!issuerValid) return false;

  if (credential.confirmationMethod === "ATTESTED_CONFIRMATION") {
    return credential.subjectPublicKey === undefined
      && credential.subjectSignature === undefined
      && credential.subjectSignatureAlgorithm === undefined;
  }
  if (
    credential.confirmationMethod !== "DIRECT_SIGNATURE"
    || credential.subjectPublicKey === undefined
    || credential.subjectSignature === undefined
    || credential.subjectSignatureAlgorithm !== "Ed25519"
  ) {
    return false;
  }
  return verifyCanonicalSignature(
    subjectConfirmationPayload(credential),
    {
      signatureAlgorithm: credential.subjectSignatureAlgorithm,
      signatureValue: credential.subjectSignature,
    },
    input.subjectPublicKey ?? credential.subjectPublicKey,
  );
}

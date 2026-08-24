import type {
  CredentialStatus,
  CredentialStatusRecord,
} from "./types.ts";

const ALLOWED_TRANSITIONS: Readonly<Record<CredentialStatus, readonly CredentialStatus[]>> = {
  PENDING: ["ACTIVE", "REVOKED", "EXPIRED"],
  ACTIVE: ["SUSPENDED", "REVOKED", "EXPIRED"],
  SUSPENDED: ["ACTIVE", "REVOKED", "EXPIRED"],
  REVOKED: [],
  EXPIRED: [],
};

export function canTransitionStatus(
  current: CredentialStatus,
  target: CredentialStatus,
): boolean {
  return ALLOWED_TRANSITIONS[current].includes(target);
}

export function transitionStatus(
  current: CredentialStatus,
  target: CredentialStatus,
  changedAt: string,
  reasonCode?: string,
  credentialId = "",
): CredentialStatusRecord {
  if (!canTransitionStatus(current, target)) {
    throw new Error(`Invalid credential status transition: ${current} -> ${target}`);
  }
  if (Number.isNaN(Date.parse(changedAt))) {
    throw new TypeError("changedAt must be an RFC 3339 timestamp");
  }
  return {
    credentialId,
    previousStatus: current,
    status: target,
    changedAt,
    ...(reasonCode === undefined ? {} : { reasonCode }),
  };
}

export function effectiveCredentialStatus(
  record: CredentialStatusRecord,
  expiresAt: string | undefined,
  now: string,
): CredentialStatus {
  if (
    record.status !== "REVOKED"
    && expiresAt !== undefined
    && Date.parse(now) >= Date.parse(expiresAt)
  ) {
    return "EXPIRED";
  }
  return record.status;
}

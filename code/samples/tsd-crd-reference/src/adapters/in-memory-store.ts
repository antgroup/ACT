export type StoredAssociationRequest = {
  applicationId: string;
  status: "PENDING" | "ACTIVE" | "REVOKED" | "EXPIRED";
  antiReplay: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  [key: string]: unknown;
};

export type StoredAuthorization = {
  authorizationId: string;
  status: "ACTIVE" | "REVOKED" | "EXPIRED";
  usageTimestamps: string[];
  [key: string]: unknown;
};

export type CredentialStatusRecord = {
  credentialId: string;
  status: "PENDING" | "ACTIVE" | "SUSPENDED" | "REVOKED" | "EXPIRED";
  statusVersion: number;
  reasonCode?: string;
  effectiveAt: string;
  updatedAt: string;
  statusProof: {
    signatureAlgorithm: string;
    signatureValue: string;
    keyId?: string;
  };
};

const ALLOWED_STATUS_TRANSITIONS: Readonly<Record<
  CredentialStatusRecord["status"],
  ReadonlySet<CredentialStatusRecord["status"]>
>> = {
  PENDING: new Set(["ACTIVE", "REVOKED", "EXPIRED"]),
  ACTIVE: new Set(["SUSPENDED", "REVOKED", "EXPIRED"]),
  SUSPENDED: new Set(["ACTIVE", "REVOKED", "EXPIRED"]),
  REVOKED: new Set(),
  EXPIRED: new Set(),
};

export class InMemoryStore {
  readonly associationRequests = new Map<string, StoredAssociationRequest>();
  readonly credentials = new Map<string, Record<string, unknown>>();
  readonly credentialStatuses = new Map<string, CredentialStatusRecord>();
  readonly authorizations = new Map<string, StoredAuthorization>();
  readonly verificationRecords = new Map<string, Record<string, unknown>>();
  readonly replayKeys = new Set<string>();

  consumeReplayKey(namespace: string, value: string): boolean {
    const key = `${namespace}:${value}`;
    if (this.replayKeys.has(key)) {
      return false;
    }
    this.replayKeys.add(key);
    return true;
  }

  saveAssociationRequest(request: StoredAssociationRequest): void {
    if (this.associationRequests.has(request.applicationId)) {
      throw new Error(`Association request already exists: ${request.applicationId}`);
    }
    this.associationRequests.set(request.applicationId, structuredClone(request));
  }

  getAssociationRequest(applicationId: string): StoredAssociationRequest | undefined {
    const value = this.associationRequests.get(applicationId);
    return value ? structuredClone(value) : undefined;
  }

  updateAssociationRequest(request: StoredAssociationRequest): void {
    if (!this.associationRequests.has(request.applicationId)) {
      throw new Error(`Association request not found: ${request.applicationId}`);
    }
    this.associationRequests.set(request.applicationId, structuredClone(request));
  }

  saveCredential(credential: Record<string, unknown>): void {
    const credentialId = String(credential.credentialId ?? "");
    if (!credentialId) {
      throw new Error("credentialId is required");
    }
    if (this.credentials.has(credentialId)) {
      throw new Error(`Credential already exists and is immutable: ${credentialId}`);
    }
    this.credentials.set(credentialId, structuredClone(credential));
  }

  getCredential(credentialId: string): Record<string, unknown> | undefined {
    const value = this.credentials.get(credentialId);
    return value ? structuredClone(value) : undefined;
  }

  listCredentials(): Record<string, unknown>[] {
    return [...this.credentials.values()].map((value) => structuredClone(value));
  }

  saveCredentialStatus(status: CredentialStatusRecord): void {
    if (
      status.statusProof.signatureAlgorithm !== "Ed25519"
      || status.statusProof.signatureValue.trim() === ""
    ) {
      throw new Error("A non-empty Ed25519 statusProof is required");
    }
    const current = this.credentialStatuses.get(status.credentialId);
    if (current === undefined) {
      if (status.statusVersion !== 1) {
        throw new Error("Initial credential statusVersion must be 1");
      }
    } else {
      if (status.statusVersion !== current.statusVersion + 1) {
        throw new Error("Credential statusVersion must increase by exactly one");
      }
      if (!ALLOWED_STATUS_TRANSITIONS[current.status].has(status.status)) {
        throw new Error(
          `Invalid credential status transition: ${current.status} -> ${status.status}`,
        );
      }
      if (Date.parse(status.updatedAt) < Date.parse(current.updatedAt)) {
        throw new Error("Credential status updatedAt must be monotonic");
      }
    }
    this.credentialStatuses.set(status.credentialId, structuredClone(status));
  }

  getCredentialStatus(credentialId: string): CredentialStatusRecord | undefined {
    const value = this.credentialStatuses.get(credentialId);
    return value ? structuredClone(value) : undefined;
  }

  saveAuthorization(authorization: StoredAuthorization): void {
    const current = this.authorizations.get(authorization.authorizationId);
    if (current !== undefined) {
      if (current.status !== "ACTIVE" && authorization.status !== current.status) {
        throw new Error(`Authorization ${current.status} status is terminal`);
      }
      if (authorization.usageTimestamps.length < current.usageTimestamps.length) {
        throw new Error("Authorization usage history must not shrink");
      }
    }
    this.authorizations.set(
      authorization.authorizationId,
      structuredClone(authorization),
    );
  }

  getAuthorization(authorizationId: string): StoredAuthorization | undefined {
    const value = this.authorizations.get(authorizationId);
    return value ? structuredClone(value) : undefined;
  }

  saveVerificationRecord(record: Record<string, unknown>): void {
    const recordId = String(record.verificationRecordId ?? "");
    if (!recordId) {
      throw new Error("verificationRecordId is required");
    }
    this.verificationRecords.set(recordId, structuredClone(record));
  }

  reset(): void {
    this.associationRequests.clear();
    this.credentials.clear();
    this.credentialStatuses.clear();
    this.authorizations.clear();
    this.verificationRecords.clear();
    this.replayKeys.clear();
  }
}

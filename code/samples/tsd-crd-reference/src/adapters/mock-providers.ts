export type IdentityVerification = {
  verified: boolean;
  subjectId: string;
  assuranceLevel: string;
  verifiedAt: string;
};

export type RelationshipVerification = {
  verified: boolean;
  verifierId: string;
  evidenceRef: string;
  assuranceProfile: string;
  verifiedAt: string;
};

export type CreditAssertion = {
  assertionRef: string;
  subjectId: string;
  valid: boolean;
  lifecycleStatus: "ACTIVE" | "REVOKED" | "CORRECTED" | "REPLACED";
  level: string;
  status: string;
  validFrom: string;
  validUntil: string;
};

export function isCreditAssertionCurrent(
  assertion: CreditAssertion,
  now: string,
): boolean {
  const currentTime = Date.parse(now);
  const validFrom = Date.parse(assertion.validFrom);
  const validUntil = Date.parse(assertion.validUntil);
  return assertion.valid
    && assertion.lifecycleStatus === "ACTIVE"
    && !Number.isNaN(currentTime)
    && !Number.isNaN(validFrom)
    && !Number.isNaN(validUntil)
    && currentTime >= validFrom
    && currentTime < validUntil;
}

const DEMO_SUBJECTS = new Set(["subject-demo-alice", "subject-demo-company"]);

const DEMO_RELATIONSHIPS = new Map([
  ["relationship-demo-alice-shopping-agent", {
    subjectId: "subject-demo-alice",
    agentId: "agent-demo-shopping",
    role: "OPERATOR",
  }],
  ["relationship-demo-company-service-agent", {
    subjectId: "subject-demo-company",
    agentId: "agent-demo-service",
    role: "CONTROLLER",
  }],
]);

const DEMO_ASSERTIONS = new Map<string, CreditAssertion>([
  ["subject-demo-alice", {
    assertionRef: "urn:acp:credit-assertion:subject-demo-alice:v1",
    subjectId: "subject-demo-alice",
    valid: true,
    lifecycleStatus: "ACTIVE",
    level: "A",
    status: "GOOD_STANDING",
    validFrom: "2026-01-01T00:00:00.000Z",
    validUntil: "2030-01-01T00:00:00.000Z",
  }],
  ["subject-demo-company", {
    assertionRef: "urn:acp:credit-assertion:subject-demo-company:v1",
    subjectId: "subject-demo-company",
    valid: true,
    lifecycleStatus: "ACTIVE",
    level: "AA",
    status: "GOOD_STANDING",
    validFrom: "2026-01-01T00:00:00.000Z",
    validUntil: "2030-01-01T00:00:00.000Z",
  }],
]);

export class MockIdentityProvider {
  verify(subjectId: string, now: string): IdentityVerification {
    return {
      verified: DEMO_SUBJECTS.has(subjectId),
      subjectId,
      assuranceLevel: "MOCK_SUBSTANTIAL",
      verifiedAt: now,
    };
  }
}

export class MockRelationshipVerifier {
  verify(input: {
    subjectId: string;
    agentId: string;
    relationshipRole: string;
    relationshipEvidenceRef: string;
    now: string;
  }): RelationshipVerification {
    const relationship = DEMO_RELATIONSHIPS.get(input.relationshipEvidenceRef);
    const verified = relationship !== undefined
      && relationship.subjectId === input.subjectId
      && relationship.agentId === input.agentId
      && relationship.role === input.relationshipRole;

    return {
      verified,
      verifierId: "mock-relationship-registry",
      evidenceRef: input.relationshipEvidenceRef,
      assuranceProfile: "MOCK_REGISTRY_V1",
      verifiedAt: input.now,
    };
  }
}

export class MockAttestationProvider {
  confirm(input: {
    associationRequestId: string;
    subjectId: string;
    agentId: string;
    relationshipRole: string;
    purpose: string;
    scope: string[];
    now: string;
  }): Record<string, unknown> {
    return {
      confirmationMethod: "ATTESTED_CONFIRMATION",
      confirmationProviderId: "mock-attestation-provider",
      subjectId: input.subjectId,
      associationRequestId: input.associationRequestId,
      confirmedAgentId: input.agentId,
      confirmedRole: input.relationshipRole,
      confirmedPurpose: input.purpose,
      confirmedScope: [...input.scope],
      confirmationResultRef: `urn:acp:mock-attestation:${input.associationRequestId}`,
      assuranceLevel: "MOCK_SUBSTANTIAL",
      confirmedAt: input.now,
    };
  }
}

export class MockCreditAssertionProvider {
  get(subjectId: string): CreditAssertion | undefined {
    const assertion = DEMO_ASSERTIONS.get(subjectId);
    return assertion ? structuredClone(assertion) : undefined;
  }
}

export function demoAssociationRequest(): Record<string, unknown> {
  return {
    applicationId: "association-application-demo-001",
    messageVersion: "reference-v1",
    subjectId: "subject-demo-alice",
    agentId: "agent-demo-shopping",
    associationRole: "OPERATOR",
    relationshipEvidenceRefs: ["relationship-demo-alice-shopping-agent"],
    confirmationMethod: "ATTESTED_CONFIRMATION",
    issuerId: "issuer-demo-reference-suite",
    purpose: "DEMO_TRUST_CHECK",
    scope: ["shopping-assistant"],
    authorizationMode: "PER_REQUEST",
    requestedAt: "2026-01-01T00:00:00.000Z",
    validFrom: "2026-01-01T00:00:00.000Z",
    expiresAt: "2030-01-01T00:00:00.000Z",
    antiReplay: { nonce: "demo-association-nonce-001" },
  };
}

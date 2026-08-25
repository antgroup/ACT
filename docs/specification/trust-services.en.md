# ACT 2.1 Trust Services Domain

[中文](trust-services.md) | English

> **Chinese source publication: ACT 2.1 Specification / Final / Normative**
> **The protocol content is final. Conformance with this specification requires independent conformance evidence.**
> **Version baseline: 2026-08-11 (UTC+8).**
> **Translation status: Official English translation / Informative. If a translation discrepancy is found, the Chinese ACT 2.1 publication remains controlling until the discrepancy is resolved through project governance.**

The Trust Services Domain (TSD) provides verifiable, traceable, and reviewable trust support for cross-domain ACT facts. It contains two parallel parts: Trusted Attestation and Credit Association.

This document is the official informative English translation of the normative ACT 2.1 Trust Services Domain text in this release. The [ACT Protocol Trust Services page](https://www.act-protocol.com/documentation/trust) is an unversioned informative reference.

## 1. Relationship and boundaries of the two parts

| Part | Problem addressed | Components |
|---|---|---|
| Trusted Attestation | How critical business events form off-chain evidence, on-chain anchors, verification results, and dispute-handling chains | `TSD-ATT-EVT`, `TSD-ATT-OFF`, `TSD-ATT-OCA`, `TSD-ATT-SVF`, `TSD-ATT-DSP` |
| Credit Association | When an Agent lacks sufficient independent credit, how it can reference the credit of an associated subject within a restricted scope while keeping source, authorization, and state verifiable | `TSD-CRD-ASC`, `TSD-CRD-MAP`, `TSD-CRD-LCM`, `TSD-CRD-VER`, `TSD-CRD-AUTH` |

Trusted Attestation is only one part of TSD and is not equivalent to the whole domain. Credit Association specifies associated subjects, credentials, declarations and mapped values, query-authorization modes, the `ASSOCIATED_CREDIT` source marker, confirmation methods, and responsibility boundaries.

Trusted Attestation does not specify the internal implementation of an underlying blockchain, timestamp service, database, or third-party evidence facility. Credit Association does not specify credit-scoring models, credit-granting rules, payment-risk decisions, cross-institution conversion rules, or independent Agent credit or reputation mechanisms. Product logs, payment receipts, or credit results do not automatically become TSD-conforming protocol objects merely because they exist.

# Part I: Trusted Attestation

## 2. Architecture and cross-domain relationship

Trusted Attestation uses a two-layer architecture of **complete off-chain record plus on-chain digest anchoring**. Participants retain event plaintext and signing material off-chain. Only the minimum necessary digest and index are written on-chain; complete business plaintext is not stored on-chain. An on-chain anchor proves that a digest was anchored earlier and does not replace the original off-chain evidence.

TSD centrally maintains the registry of attestation event types. ADD, CID, and PSD reference event identifiers without redefining event structures or attestation governance. Cross-domain evidence chains primarily correlate `intent_id`, `delegation_id`, merchant order transaction number, payment transaction number, and the attestation record's unique identifier.

Attestation MUST occur asynchronously after the business event completes and SHOULD NOT block the main transaction flow or affect online payment latency.

## 3. `TSD-ATT-EVT`: event-type registry

The event namespace is `act:<domain>:<event>`. The current standard set is:

| Event identifier | Trigger semantics |
|---|---|
| `act:delegation:intent-created` | The user confirms intent and a result available for authorization processing is formed |
| `act:delegation:delegation-issued` | An IAC is issued and enters `Active` |
| `act:delegation:delegation-suspended` | An IAC is suspended |
| `act:delegation:delegation-resumed` | An IAC returns from suspension to active use |
| `act:delegation:delegation-revoked` | An IAC is revoked |
| `act:delegation:delegation-expired` | An IAC expires |
| `act:commerce:decision-logged` | The Buyer Agent completes candidate comparison or records a decision |
| `act:commerce:cart-confirmed` | Transaction confirmation completes and the transaction may enter payment |
| `act:payment:transaction-completed` | Payment completes and produces a payment result |
| `act:commerce:fulfillment-completed` | Merchant-order fulfillment completes |

This component currently freezes only event identifiers and basic trigger semantics. It does not define a complete `event_body`, field-level validation, signature envelope, or on-chain format for each event type.

## 4. `TSD-ATT-OFF`: off-chain attestation record

### 4.1 Record composition

An off-chain record has six parts: basic metadata, end-to-end correlation and provenance identifiers, privacy and inference-resistance elements, participant list, `event_body`, and digital signatures.

| Part | Minimum semantics |
|---|---|
| Basic metadata | Unique attestation-record identifier, event type, business-event time, record-creation time, and structure version |
| Chain identifiers | Required `intent_id`; conditionally required `delegation_id` in delegated scenarios; conditionally required merchant order number after confirmation; conditionally required payment transaction number after payment; optional upstream-record reference |
| Privacy and digest | An independent high-entropy random salt for each record, payload hash, and hash-algorithm identifier |
| Participant list | At least one participant identifier and role; the represented principal MAY also be recorded when acting by proxy |
| `event_body` | Necessary business plaintext for the current event, or privacy-processed business facts |
| Digital signature | Signer, algorithm, Base64url signature value, and signed scope |

Business-event time and record-creation time MUST be recorded separately and SHOULD use ISO 8601 UTC. Once created, a record MUST NOT be structurally changed without a new version.

### 4.2 Privacy, hashing, and signatures

- Every record MUST use an independent, cryptographically secure random salt with an original length of at least 128 bits. Salts MUST NOT be reused across records.
- Canonicalize `event_body` and the participant list with RFC 8785 JCS, concatenate the canonical byte sequence with the original salt bytes, then hash with SHA-256 or SM3 and store the digest as Base64url.
- `event_body` MUST NOT contain high-sensitivity plaintext such as real names, identity-document numbers, contact details, bank-card numbers, or payment-account numbers. Fields that cannot be recorded in plaintext SHOULD store a digest with explicit semantics.
- The signature MUST cover at least `event_body`, participant list, random salt, unique attestation-record identifier, and business-event time. Every record MUST contain at least the initiator's signature and MAY contain joint signatures.
- Historical records MUST NOT be rewritten because of a protocol upgrade. A parser selects compatible logic using the record structure version.

## 5. `TSD-ATT-OCA`: on-chain attestation anchor

An on-chain anchor and its off-chain record have a one-to-one mapping through the unique record identifier and payload hash. The anchor SHOULD use JWS Compact Serialization. Its header MUST at least express the algorithm and key reference. Its payload expresses:

- unique record identifier, protocol or structure version, event type, and business-event time;
- JWT issuance or anchor-submission time;
- `intent_id` and, when applicable, `delegation_id`, order number, and payment transaction number;
- submitter identity, payload hash, hash algorithm, and ACT Trust Chain privacy-channel identifier;
- optional extensions that contain no business plaintext or sensitive identity or payment-account information.

Submitting the same unique record identifier is idempotent: a node MUST reject duplicate anchoring and return the existing block height or equivalent location. An anchor MUST NOT be overwritten after being written. Later supplements use a new record or a compatible extension.

ACT 2.1 identifies ACT Trust Chain as the anchoring infrastructure but does not define a directly implementable public node interface, network parameters, authentication, JWS field names, or Schema. These are future implementation or later-version work and MUST NOT be invented by this repository.

## 6. `TSD-ATT-SVF`: signature verification

Verification follows **off-chain before on-chain, digest before signature, current record before upstream chain**:

1. Retrieve the complete off-chain record by its unique identifier.
2. Obtain the public key that was valid at the business-event time from a DID document, ACT Trust Chain trust registry, or another trusted source. If unavailable, return `PUBLIC_KEY_UNAVAILABLE`.
3. Recompute the payload hash using the same JCS, salt, and algorithm. On mismatch, return `PAYLOAD_HASH_MISMATCH`.
4. Verify each declared signed scope. On invalid signature, return `SIGNATURE_INVALID`.
5. Query the on-chain anchor and compare the hash. If absent, return `ANCHOR_NOT_FOUND`; if different, return `CHAIN_HASH_MISMATCH`. The source recommends a 30-second timeout and at most three retries, returning `ANCHOR_QUERY_TIMEOUT` after the final timeout.
6. If an upstream-record reference exists, the causal chain MAY be verified recursively.
7. Return `VERIFIED` after all required checks pass.

Temporary unavailability of an external dependency does not mean the record was tampered with. `VERIFIED` means only that cryptographic checks and on-chain/off-chain consistency pass; it is not a final no-dispute conclusion for contractual, regulatory, or arbitration purposes.

## 7. `TSD-ATT-DSP`: dispute handling

Dispute handling is organized as **application, evidence submission, verification, and disposition**. A disputing party submits the dispute type, correlation identifiers, and description. Each party submits its off-chain records. The processor runs `TSD-ATT-SVF`. An arbitrator or processor makes a disposition based on the evidence and verification results.

This component defines only the workflow framework. The arbitrating body, evidence-submission deadline, evidence priority, supplemental-evidence rules, and final-decision rules are determined by network agreements, governance documents, or legal arrangements and are not conclusions of the current TSD specification.

# Part II: Credit Association

## 8. Principles, objects, and components

An associated subject may be a natural person, legal entity, or organization with a verified development, deployment, operational, controlling, or other relationship to the Agent. Associated credit is only a supplemental risk reference for an explicit purpose, scope, and validity period:

- the source MUST be marked `ASSOCIATED_CREDIT`;
- it MUST NOT be represented as the Agent's independent credit, independent reputation, credit rating, or credit capacity;
- it MUST NOT expand or replace an IAC authorization boundary;
- it MUST NOT replace payment authorization, account validation, anti-fraud, anti-money-laundering, or other independent controls;
- a verification result does not directly constitute transaction admission, credit granting, or payment approval.

| Component | Purpose |
|---|---|
| `TSD-CRD-ASC` | Establish the association and issue a Credit Association Credential |
| `TSD-CRD-MAP` | Map the associated subject's credit declaration into an Agent associated-credit declaration |
| `TSD-CRD-LCM` | Manage credential suspension, resumption, revocation, expiration, replacement, and reassessment |
| `TSD-CRD-VER` | Verify the credential itself or further verify current associated-credit information |
| `TSD-CRD-AUTH` | Constrain the subject, purpose, data items, and frequency of associated-credit queries |

Core objects include a Credit Association Application, Credit Association Credential, associated-subject credit declaration, Agent associated-credit declaration, associated-credit mapped value, credit-query authorization, and credit-verification record.

## 9. `TSD-CRD-ASC`: establishing credit association

### 9.1 Flow

1. The associated subject submits the Agent identifier, association evidence, role, purpose, scope, and replay-resistance elements.
2. The credit service provider verifies subject identity, association, and role match, and obtains confirmation of the Agent, purpose, scope, validity, query authorization, and revocation method.
3. The credit service provider creates an Agent associated-credit declaration according to `TSD-CRD-MAP`.
4. The Credit Association Credential issuer creates and signs the credential. Its state after issuance is `ACTIVE`.

### 9.2 Credential semantics

The credential MUST at least express credential, application, Agent, associated-subject, and issuer identifiers; association-evidence reference; confirmation method; associated-credit mapped value; `ASSOCIATED_CREDIT` source marker; mapping rule and version; association-confirmation statement; applicable purpose and scope; issuance and effective time; state-query information; and issuer signature. A reference to the associated-subject credit declaration is conditionally required when associated-credit information is provided.

The declaration reference, mapped value, and mapping-rule identifier and version form a three-part traceability set. If any element is missing, the mapped value MUST NOT be independently interpreted, compared, or used.

The confirmation method is one of:

- `DIRECT_SIGNATURE`: the associated subject signs the application and critical confirmation content as an inner signature; after verification, the issuer adds an outer signature, producing two signature layers.
- `ATTESTED_CONFIRMATION`: the associated subject completes identity verification and interactive confirmation through the credit service provider; the credential contains only the issuer's outer signature.

The association-confirmation statement MUST explicitly state role, scope, purpose, and responsibility boundary. It proves only the subject's confirmation of the association and permitted use; it does not guarantee the Agent's transaction, payment, or fulfillment result. A confirmation MUST NOT be reused for another Agent, subject, role, purpose, scope, or application.

When a core field changes materially, a new credential MUST be issued and related through a predecessor-credential reference. The old credential MUST NOT be overwritten.

## 10. `TSD-CRD-MAP`: associated-credit mapping

The associated-subject credit declaration is an independent object and SHOULD include a declaration identifier or version, credit service provider, issuance time, validity period, and signature or equivalent proof. The Credit Association Credential references it rather than directly carrying its original credit content.

The credit service provider determines the concrete score, level, and mapping model. TSD requires only that:

- every mapping rule has a unique identifier and version;
- results from different rules or versions MUST NOT be directly compared or converted without rule information;
- the declaration reference, mapped value, and rule version are retained and verified together;
- the mapped result has an upper bound and usage boundary independent of the associated subject's own credit;
- the Agent MUST NOT directly inherit all credit permissions, limits, lending capacity, or business qualifications of the associated subject.

A mapped value MAY be a level, interval, state, limit, multidimensional attribute, or another structured form. The source does not freeze a common data structure.

## 11. `TSD-CRD-LCM`: lifecycle

| State | Semantics |
|---|---|
| `PENDING` | Application created; confirmation, mapping, or issuance incomplete |
| `ACTIVE` | Credential valid and available for in-scope verification |
| `SUSPENDED` | Suspended; MUST NOT produce new passing results |
| `REVOKED` | Irreversibly revoked; terminal |
| `EXPIRED` | Validity period exceeded; terminal |

Allowed transitions are `PENDING → ACTIVE/REVOKED/EXPIRED`, `ACTIVE → SUSPENDED/REVOKED/EXPIRED`, and `SUSPENDED → ACTIVE/REVOKED/EXPIRED`. The associated subject MAY suspend or revoke voluntarily. The credit service provider MAY trigger suspension or revocation because of anomalies in a declaration, association, evidence, or risk. The issuer applies and records the state change.

A change to the associated-subject credit declaration, mapping rule, supporting evidence, role, purpose, scope, or another core field triggers reassessment. First suspend the old credential and recompute the declaration and mapping. If a core field changed, issue a new credential and move the old credential to `REVOKED` after the new credential becomes effective. If there is no material change and the old credential has not expired, it MAY be restored. Historical verification records retain the state at the time, but a relying party MUST be able to identify a later revocation.

## 12. `TSD-CRD-VER`: associated-credit verification

Verification has two levels:

1. **Credit Association Credential verification:** check the request, replay protection, requester identity, outer signature, and inner signature when necessary; then verify subject, Agent, role, purpose, scope, the three mapping elements, and current `ACTIVE` state. This level does not retrieve the associated subject's original credit information and therefore does not require credit-query authorization.
2. **Associated-credit information verification:** after level one passes, verify credit-query authorization, current validity of the associated-subject credit declaration, mapping-rule version, and current state of the Agent associated-credit declaration; return only authorized data under data minimization.

A request MUST at least express the request identifier and version, credit relying party, Agent, verification level, business purpose or context, requested data items, credential, request time, replay-resistance elements, and request proof. Level two also requires the associated-subject credit-declaration reference.

A response expresses the verification record, level actually completed, `PASS` / `FAIL` / `INCONCLUSIVE` / `REVIEW_REQUIRED`, reason code, credential state, applicable scope, result time and expiration time, purpose restriction, and response proof. Only when level two passes and is authorized MAY the response return `ASSOCIATED_CREDIT`, mapped value, declaration validity, and mapping-rule version.

A critical failure MUST NOT return `PASS`. Insufficient evidence or an unavailable dependency returns `INCONCLUSIVE`. Reassessment in progress or a need for a higher assurance level returns `REVIEW_REQUIRED`. Standard reason-code categories include request, proof, freshness, replay, missing or expired authorization, revoked or out-of-scope authorization, unresolvable Agent, missing or inactive credential, invalid proof, unavailable or invalid credit declaration, and unsupported mapping rule.

## 13. `TSD-CRD-AUTH`: credit-query authorization

Credit-query authorization permits only querying or verifying associated-credit information. It does not authorize a transaction, payment, fulfillment, or other commercial action. Authorization MUST bind the credit relying party, optional platform proxy, Agent scope, verification level, business purpose, requested data items, validity period, and result-use restrictions. Platform-proxy queries MUST also have a machine-readable frequency limit such as `max_requests_per_window` and `window_duration`.

Two authorization modes exist:

- **Per-query authorization:** every level-two verification notifies the associated subject for confirmation and independently binds requester, Agent, purpose, data items, request identifier, and validity time.
- **Platform-proxy query:** the associated subject authorizes an explicit platform subject in advance to query within a restricted scope and period without per-query participation. The platform proxy MUST NOT delegate that authority or use results outside the authorized purpose.

Every verification MUST check authorization state and request scope. After revocation, a new valid level-two verification result MUST NOT be produced. Responses MUST follow data minimization.

## 14. Current machine-contract and implementation boundary

The two source documents provide complete semantics, field presence, states, and reason codes, but the following have not become public machine contracts that can establish formal compatibility:

- English wire field names, JSON Schemas, version negotiation, and error envelopes for common TSD objects;
- public ACT Trust Chain network, node interface, authentication, privacy channels, and formal JWS payload Schema;
- field-level Schema and submission or query interface for each `event_body`;
- formal envelopes and algorithm suites for Credit Association Credentials, credit declarations, query authorizations, and verification requests and responses;
- protocols for identity resolution, historical public-key retrieval, state queries, and mapping-rule registration.

The repository therefore does not generate fictional TSD Schemas, node implementations, credit models, or an “on-chain sandbox.”

## 15. Sources

- Related TSD website reference: [Trust Services Domain](https://www.act-protocol.com/documentation/trust); content not labeled ACT 2.1 is not a normative source for this release
- ADD: [Authorization & Delegation Domain](https://www.act-protocol.com/documentation/delegation)
- Cross-domain scenarios: [Scenarios and business flows](https://www.act-protocol.com/documentation/scenarios)

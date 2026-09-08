# ACT 2.1 Authorization & Delegation Domain

[中文](authorization-delegation.md) | English

# Scope
## Domain Positioning
Authorization & Delegation Domain (Authorization & Delegation Domain, ADD) provides the expression, confirmation, structured constraints of user intent, authorization credential issuances and their life-cycle management rules that provide an expressionable, binding, verifiable and retroactive basis of authorization for Agent representing User commercial activities.

## Domain Responsibilities
This domain covers the following:

+ User's original intentAccess, clarification, confirmation and structured expression;
+ Intent Structuring Result (ISR) generation and reference;
+ Intent Authorization Credential (IAC) construction, issuance and sealing;
+ IAC Life cycle state and its visible semantics.

The following are not regulated in this domain:

+ Front-end interactive styles, hint engineering, model reasoning processes and multi-modular bottom recognition algorithms;
+ Specific identity infrastructure, private key hosting and signature services internalization;
+ Commodity discovery, transaction negotiation, Cart Confirmation, payment channel communication, settlement of funds.

# The list of components and relationships in this field
## Component Overview
Authorization & Delegation Domain consists of three protocol components, which together complete the available links from User's original intent to authorization credential. The functional position of the components is as follows:

+ **ADD-INT-ICS: Intentional and structured expression.** Be responsible for receiving User's original intent, completing the necessary semantic clarifications, User confirmation and structured expression, resulting in Intent Structuring Result to be quoted in the subsequent authorization process.
+ **ADD-IAC-ISS: Intent Authorization Credential for issuance.** Be responsible for encapsulating the structured intent as authorization credential as cross-domain verifiable and completing the necessary signature or issuance actions.
+ **ADD-IAC-LCM: Intent Authorization Credential Life cycle management.** Responsible for defining and managing IAC changes in state and their visible semantics during the life of the period.

## Core Object & Identification
To maintain consistency in internal and cross-domain processing, ADD uses a set of standard core objects and identification keys to describe the critical state in the User authorized link. The core objects of this domain and their effects can be summarized as follows:

|** Object or Identification**|** Meaning**|** Mainly Generate Location**|** Main Use Location**|
| --- | --- | --- | --- |
|User's original intent|User Original commercial intent expressed in natural language or other type of input.|ADD-INT-ICS|ADD-INT-ICS, and relevant processing elements for ex post verification, as necessary.|
|`intent_id`|user intent logo for cross-intention confirmation, structured expression and subsequent cross-domain reference|ADD-INT-ICS|ADD Internal domain, and other fields Intent Context that need to be quoted|
|Intent Structuring Result<br/> (Intent Structured Research, ISR)|Expression of structured rules for User commercial objectives, constraints and boundaries|ADD-INT-ICS|ADD-IAC-ISS, and other fields where reference to the rule is required|
|Intent Authorization Credential (Intent Assessment Credit, IAC)|authorization credential Object after ISR can be verified|ADD-IAC-ISS|ADD-IAC-LCM, Payment Services Domain, Trust Services Domain|
|`delegation_id`|IAC unique sign for the life cycle to mark a formal authorization credential|ADD-IAC-ISS|ADD-IAC-LCM, Payment Services Domain, Trust Services Domain|
|Authorized Status|IAC Current available status, e.g. Active, Suspended, Revoked, Expired|ADD-IAC-LCM|Payment Services Domain, and other elements that need to be judged on the validity of the delegation of authority|

## Dependence and Cross-domain Reference
ADD-INT-ICS forms the basis for the issuance of ADD-IAC-ISS. ADD-IAC-ISS forms IAC and `delegation_id` form the subject of ADD-IAC-LCM, and the state of authorization given ADD-IAC-LCM will affect the subsequent acceptance of authorization credential.

Commerce Interaction Domain primarily references ISR and the relevant constraint context to support product discovery, intent transmission, and transaction confirmation. Payment Services Domain primarily references IAC, `delegation_id`, and authorization status results to support authorization verification in payment requests. The trusted attestation subsection of Trust Services Domain centrally maintains the relevant event types and attestation governance rules; this domain does not redefine them.

# ADD-INT-ICS: Intentional acquisition and structured expression
## Overview
Intent to obtain and structured expression (Intent Capture and Structured Exchange, ADD-INT-ICS) provides for User's original intent acquisition, semantic clarification, User confirmation and structured expression processing requirements.

The objective of this component is to translate User original commercial intent, expressed in natural language or other input, into Intent Structuring Result that can be quoted and validated by a follow-up authorization process (Intent Processed Research, ISR).

This component does not regulate specific human interfaces, hint engineering, model reasoning processes and multi-modular bottom recognition algorithms.

## Participants and prefix
This component covers the following Participants: User and the User side Agent to receive, interpret, clarify, confirm and generate ISR.

Before entering this component, SHALL satisfies the following preconditions:

+ An effective interactive context with User has been established on User side Agent.
+ User is capable of expressing commercial intent in such a way as to achieve party-supported input.
+ User side Agent has the capability to retain original intent and output ISR locally.

## Data structure and field tables
Two core objects are involved in the treatment of this component: User original intent (`conversation_history`) and Intent Structuring Result (ISR).

Of these, `conversation_history` is used to carry User's original intent and its original context references; ISR is used to carry the structured expression resulting from clarification, confirmation and as a basis for ADD-IAC-ISS input.

### User's original intent
`conversation_history` is the structure carrying User's original intent for recording the original content expressed in this intent link User or its verifiable summary and context references.

|** Field name**|** Type**|** Existence**|** Conditions of restraint**|** Annotations**|
| --- | --- | --- | --- | --- |
|`user_intent_raw`|string or array [object]|Conditionally required|Exists with `user_intent_raw_digest` at least one|User original intent Content. This can be in the form of dialogue log arrays (objects with `role`, `content`, `create_time`, or in the form of pure text strings.|
|`user_intent_raw_digest`|string|Conditionally required|Exists with `user_intent_raw` at least one|User's original intent Summary values. This applies to the presence of multi-modular information such as voice, pictures, interactive cards in Intent Context, which does not allow for direct transmission of the full original intent content.|
|`input_mode`|array[string]|Optional|Numerical elements SHALL be input mode count values|User enters to support a mix of multiple modes of input.|
|`context_ref`|string|Conditionally required|must exist when `user_intent_raw_digest` exists|Reference pointing to the relevant session, local record or external storage location; the corresponding original content SHALL allow the calculation of summary values consistent with `user_intent_raw_digest`.|

Of which:

+ The examples of `user_intent_raw` are as follows.

```plain
"user_intent_raw": [
  {
    "role": "USER",
    "content": "Please secure me a second-class ticket to Harbin on January 20.",
    "create_time": "2025-12-23T10:28:00Z"
  },
  {
    "role": "ASSISTANT",
    "content": "Train G123 still has tickets at CNY 600. Would you like me to monitor availability and place the order automatically?",
    "create_time": "2025-12-23T10:28:05Z"
  },
  {
    "role": "USER",
    "content": "Yes. Keep the limit under CNY 600 and check several times each day.",
    "create_time": "2025-12-23T10:29:00Z"
  }
]
```

+ Input_mode count values as follows
    - `TEXT`: text input;
    - `VOICE`: voice input;
    - `IMAGE`: photo input;
    - `INTERACTIVE_CARD`: Interactive cards;
    - `OTHER`: Other inputs.

This allows you to expand other input mode count values, but SHALL NOT changes the basic semantics of the above field.

### Intent Structuring Result (ISR)
ISR is the core output object of this component, which is used to express the result of a structured intent resulting from semantic understanding, clarification and confirmation of User. This section defines ISR as a data dictionary, with only the name of the field, the type of field and the semantic of the field, and does not agree on the conditions for the existence of the field in this section. The specific existence of the field requirements is further regulated by the subsequent scenario rules, IAC issuance rules and sections of the relevant components.

#### Basic fields
|** Field name**|** Type**|** Binding statements**|** Annotations**|
| --- | --- | --- | --- |
|`conversation_history`|object|SHALL meeting 3.3.1 definitions|Object User's original intent|
|`intent_id`|string|The only one in this chain of intent.|Mark user intent|
|`delegation_mode`|string|Enumeration values: `SPECIFIED`/ `BOUNDED`|Commission Mode|
|`validity_start_time`|string|ISO 8601 UTC|Start of commission|
|`validity_end_time`|string|ISO 8601 UTC, SHALL later than `validity_start_time`|Mandate end time|
|`max_total_amount`|number|SHALL greater than or equal to 0, keep 2 decimal places accurate|Maximum total amount authorized|
|`currency`|string|ISO 4217|Currency|
|`allowed_payment_methods`|array[string]|There's at least one way of allowing it.|Allowed List payment method|
|`agent_id`|string|SHALL be an identifiable Agent identifier|Implementation of Agent markings|
|`user_confirmation_method`|string|Defined by Accelerator|User Confirmation|
|`user_confirmation_timestamp`|string|must exist when `user_confirmation_method` exists; ISO 8601 UTC|Confirmation time User|
|`ext`|object|SHALL meeting 3.3.3 definitions|Standard extension field and private extension field namespace.|

Delegation_mode extracts:

|** Enumeration values**|** Semantic**|** Applicability**|
| --- | --- | --- |
|`SPECIFIED`|Targeted commissioning, authorization Scope is locked within a specified purchase target, Merchant or a clearer transaction boundary|User Invisible and Target-Specified|
|`BOUNDED`|Boundary commissioning, authorization to set mission objectives and behavioural boundaries only, with the option of Agent autonomous decision-making within the boundary|User Unaccompanied and autonomous decision-making within the border Agent|

#### Standard Extension Fields
Includes three standard extensions: `ext.commerce`, `ext.agent_behavior` and `ext.fulfillment`. These extensions are used to carry goods and Merchant binding, Agent behavioural strategies and compliance requirements.

`ext.commerce` field table:

|** Field name**|** Type**|** Conditions of restraint**|** Annotations**|
| --- | --- | --- | --- |
|`max_single_amount`|number|SHALL greater than or equal to 0; SHALL NOT greater than `max_total_amount`|Single maximum amount|
|`min_single_amount`|number|SHALL greater than or equal to 0; SHALL NOT greater than `max_single_amount`|Single minimum amount|
|`allowed_categories`|array[string]|Element values defined by the achiever|The White List.|
|`forbidden_categories`|array[string]|Element values defined by the achiever|Class blacklist|
|`allowed_merchants`|array[string]|Element value SHALL be identifiable as Merchant|Merchant White List|
|`forbidden_merchants`|array[string]|Element value SHALL be identifiable as Merchant|Merchant Blacklist|

`ext.agent_behavior` field table:

|** Field name**|** Type**|** Conditions of restraint**|** Annotations**|
| --- | --- | --- | --- |
|`price_deviation_tolerance`|number|Percentage difference|Percentage change in price|
|`price_deviation_action`|string|Enumeration values: `PAUSE_AND_NOTIFY`/ `AUTO_CANCEL`|Handle actions when price differentials are exceeded|
|`on_payment_failure`|string|Enumeration values: `AUTO_RETRY`/ `CANCEL`|Payment Failed Method|
|`max_retry_count`|integer|SHALL greater than or equal to 0|Maximum number of retries|

`ext.fulfillment` field table:

|** Field name**|** Type**|** Conditions of restraint**|** Annotations**|
| --- | --- | --- | --- |
|`delivery_time_requirement`|string|Accomplishment-defining format|Time limits for distribution or performance|
|`delivery_address`|string|SHALL Reference for parsable or structured addresses|Distribution Address|

#### Private extension
Except for standard extension fields, this protocol supports the carrying of private extension fields by `ext.vendor_private` as their logo. Private expansion fields may not change the existing semantics of ISR core fields or standard extension fields.
For unidentifiable private extension fields, the receiving party may ignore those parts of the core constraint understanding, but SHALL NOT changes the interpretation of ISR core semantics.

## Processing of requests
### original intentAccess
User sideagent SHALL receives User original commercial intent and forms `conversation_history` object.

Agent Records directly and transmits the full user_intent_raw. Agent calculates `user_intent_raw_digest` and points `context_ref` to relevant sessions or local records in situations where voice, pictures, interactive cards, etc. are not available to directly record and transmit the full original intent conversation.
If this input contains multiple modes of input, Agent can record the hybrid mode in `input_mode`.

### Preliminary understanding and structured draft generation
After obtaining original intent, the User side Agent should be given a preliminary semantic understanding and extract the core elements related to commercial commissioning. These elements may include, but are not limited to, commissioning objectives, monetary boundaries, time boundaries, payment method limits, Merchant or class restraints, compliance requirements and Agent behavioural strategies. On this basis, Agent SHALL generate drafts ISR.

### Intended clarifications and draft updates
When original intent is ambiguous, key constraints are missing, conditions are incomplete or there is a clear conflict, the User sideagent SHALL initiate clarification to User. The clarification process may be a single or multiple round; the specific interaction is determined by the party who achieved it and does not belong to the norm of this protocol Scope.

After each valid clarification, the draft ISR should be updated so that it is gradually reduced to a structured outcome that expresses the true intent and border conditions of User.

### Confirmation User
Once the draft ISR has reached an understandable and identifiable level, the User side agent SHOULD display the structured summary to User in an understandable manner and is confirmed by User. The confirmation SHALL be sufficient to reflect the core objectives of this mandate and the main boundary.

### ISR Output
User Upon confirmation, User sideagent SHALL generate the final ISR. If subsequent issuance is required Intent Authorization Credential, ADD-IAC-ISS SHALL be used as the basis for the entry ISR.

### Retention original intent
At User sideagent SHOULD, original records relating to this intent link or their verifiable references are kept locally to support subsequent dispute resolution, manual review or audit.
The duration of the retention period SHOULD be not less than the duration of the reasonable dispute resolution period following the completion of the mission.

# Signature ADD-IAC-ISS: Intent Authorization Credential
## Overview
User Intent Authorization Credentialissuance (Intent Cooperation Central Insurance, ADD-IAC-ISS) on how to translate the final ISR into commerce interaction, payment execution and trusted attestation User Intent Authorization Credential (IAC) to be followed up by commerce interaction, trusted attestation Intent Authorization Credential.

This component defines the business semantics of IAC, the boundary of the pending signature load, the sealing requirements of the voucher and the process of issuance.

IAC is entered for the final ISR but ultimately ISR does not necessarily have all the contents in the IAC to be signed; only fields that constitute the basis for the authorized boundary, enforcement constraints and subsequent verifications will SHALL be included in the IAC signature Scope.

## Participants and prefix
This component involves the following Participants: Principal, entrusted with Agent, and the realization component or service that provides signature, key call or document seal support.
In practical terms, the issuance process can be carried out in conjunction with security capabilities such as identity verification, protected interaction, key access control and control certificates, but the related security capabilities can be provided by external security support protocols.

Before entering this component, SHALL satisfies the following preconditions:

+ The final ISR has been formed and has entered the confirmation chain for User. User confirmation actions for the final ISR can be triggered directly by the authorization issued IAC.
+ The designation Agent of the mandate has been clarified, along with the modalities of the mandate, its duration and the main binding boundaries.
+ The achiever has the capacity to generate `delegation_id`, construct IAC to be signed, implement normative processing and output ultimately IAC.
+ IAC The signature private key SHALL be hosted by the controlled key management capability and signed in a credible execution environment or an equivalent controlled signature environment; the business application shall not disclose or hold the signature key for IAC issuance in an explicit manner. When ASL is used by the implementer as a security support protocol, the issuer ' s identification, key call, signature generation, control certificate and related status queries can be completed by ASL-IDN, ASL-INF-KMS and ASL-INF-SEE, respectively.

## Data structure and field tables
### IAC to be signed load
The IAC to be signed payload is based on the final ISR screening and reorganization of authorized business subjects to express “who authorizes which Agent within what boundaries to act on its behalf”. IAC to be signed payload SHOULD be defined as follows:

|** Field name**|** Type**|** Existence**|** Binding statements**|** Annotations**|
| --- | --- | --- | --- | --- |
|`delegation_id`|string|Required|Only identifier for this IAC|The only mark of this IAC is also the primary mark of this authorized life cycle|
|`intent_id`|string|Optional|ISR Upstream when the mark is generated|Corresponding user intent sign(s); can be used to establish IAC correspondence with ISR upstream when ISR has been generated|
|`conversation_history`|object|Conditionally required|When `intent_id` is not generated and the achiever carries the object original intent directly; if available, SHALL meets the definition of 3.3.1.|When `intent_id` is not generated, `conversation_history` can directly serve as the basis for upstream input for this mandate; this approach is more appropriate for the smaller byte scenario User's original intent|
|`delegator_identity`|string|Required|Authorisation of the issuer identifier, i.e. the client identifier|Authorization of the issuer ' s identifier, usually corresponding to Principal or the subject identifier initiated on behalf of Principal|
|`agent_id`|string|Required|Trusted identification Agent|Identification of Agent authorized for follow-up actions|
|`delegation_mode`|string|Optional|Enumeration values: `SPECIFIED` / `BOUNDED`, default value when not completed `SPECIFIED`|Commission Mode|
|`validity_start_time`|string|Required|ISO 8601 UTC|Time of validity of authorization|
|`validity_end_time`|string|Required|ISO 8601 UTC, SHALL later than `validity_start_time`|Time of expiry of authorization|
|`max_total_amount`|number|Required|SHALL greater than or equal to 0, keep 2 decimal places accurate|Maximum total amount authorized|
|`currency`|string|Optional|ISO 4217; Default for unfilled `CNY`|Currency|
|`allowed_payment_methods`|array[string]|Optional|If entered Scope for signature, SHALL remain consistent with the semantics of the field ISR|Allowed List payment method|
|`user_confirmation_method`|string|Optional|Defined by Accelerator|User Confirmation or nuclei|
|`user_confirmation_timestamp`|string|Conditionally required|SHALL Sync presence when `user_confirmation_method` exists; ISO 8601 UTC|User Time of completion of confirmation or nuclei|
|`source_isr_digest`|string|Optional|Excerpt values used to express upstream ISR or their agreed summary Scope|Fill in if the achiever needs a more stable cross-domain verification anchor|
|`ext`|object|Optional|ISR Extension bounds to IAC, SHALL directly follow the `ext` structure and field syntax of ISR|Expand Field Naming Space|

Treatment of `ext`:

+ IAC If you need to carry the extension restriction in ISR, SHALL simply follow the namespace and field syntax of `ext` in ISR.
+ Whether or not to include an extension field in the signature of IAC is determined by the fulfilment party on the basis of whether or not it affects the subsequent authorization; no requirement to sign all of the extensions in ISR together with IAC.

### Eventually IAC
Ultimately IAC is a verifiable authorization credential object formed by the completion of the signature, encapsulation and addition of the necessary metadata on the basis of IAC signature loads. This chapter defines only its components and its semantic boundaries in the final IAC without specifying a specific field-level structure to be achieved in a format compatible with the different document envelopes.

Ultimately IAC may include the following components:

+ `protected_header` or equivalent encapsulation metadata for the expression of algorithm identification, type of encapsulation, key location information and necessary configuration identifiers.
+ `credential_metadata` for the expression of underlying metadata such as the issuer, the trustee, the time of issuance, the time of entry into force, the time of expiry and the certificate identifier.
+ `credential_subject` or equivalent service load area to carry the IAC signature load as defined in 4.3.1.
+ `proof` for the purpose of expressing a certificate of signature generated for the agreed signature Scope.
+ `status_reference` to support follow-up status queries, life-cycle management or related verification links.
+ `control_proof_ref` is an optional component; in a high-risk issuance scenario, it can be used to refer to a control certificate or a summary thereof in relation to the current call for the signature.

## Processing of requests
### ISR Integrity check and confirmation trigger
Trusted to receive agent SHALL final ISR and to check that it has reached the status of confirmation and issuance of User, has a clear commissioning model, Agent marking, validity period and primary authorized boundary. In the event that ISR ultimately lacks the key authorization information necessary to constitute IAC, SHALL NOT enters the formal issuance process.

User Confirmation actions for the final ISR may be issued directly as trigger actions for IAC. SHOULD NOT Compulsory confirmation of User on the same authorized matter due to design Protocol Flow.

### IAC to be signed load construction
agent SHALL be entrusted with the construction of the IAC to be signed payload based on the final ISR and the identification of fields into this IAC signature Scope. SHALL be then based on the principle of “based ISR filtering and reorganization” and SHALL NOT will eventually be ISR as a whole. IAC

### Normative treatment
Before entering the signature, the achiever shall perform a definitive normative treatment of IAC to be performed in the agreed signature Scope to ensure consistency between cross-domain signatures and abstracts. The issuer in the same deployment will keep the field name, regularize rules and the signature entered into the boundary by the certifying party SHALL, otherwise the signature or summary verification will fail.

If JSON is used as a payload expression, SHOULD applies the regulatory treatment of JSON Canonicalization Scheme (JCS) as defined by RFC 8785.

### Signature Generation
After the formalization has been completed, the achieving party should enter the agreed signature into the executed signature, generating `proof` of IAC.

### Certificate Envelope
When the result of the signature is obtained, the person SHALL assemble the pending signature load, certificate metadata, signature certificate and necessary references to information as final IAC. The sealed IAC SHALL be able to express the issuer, be trusted Agent, authorized boundaries, validity period and signature certificate, and will support subsequent independent verification.

## Seal and signature requirements
This component uses a non-encapsulation rule for IAC; it achieves a mapable cover of a certificate type, a JWS type envelope or other equivalent to validate expression, but the selected envelope SHALL be able to stabilize the carrier ' s issuer, trustee, time limit, IAC pending signature load and signature certificate. This version uses W3C VC-JWT as one of the recommended means of realization, but is not the only cover format.

Signature Scope SHALL be clearly stated by the implementer and is consistent within the same deployment. By default, the signature input SHALL be a IAC to be signed or its equivalent normative expression in the agreed signature Scope, rather than a full ISR original text. In the context of the JSON regularization, SHALL retains the original name of the field, SHALL NOT changes the synonym of the signature input due to the style of automatic transformation of the serial framework field.

When the implementer uses ASL as a security support protocol, normative references can be made in the following manner:

+ The signature generation of IAC can be `Sign` completed by reference to ASL-INF-KMS, matching the signature key use SHALL with the signature use authorization credential, SHALL NOT with other uses.
+ User recognition, local sensitive interaction and signature call under a high-risk authorization scenario, SHOULD combined with ASL-INF-SEE protected interactive capability and ASL-INF-KMS control certification capability.
+ SHOULD refers to ASL-INF-KMS control certification capabilities when the signature is required to record evidence calling for access control strategies, and carries `control_proof_ref` or equivalent references in IAC at the end.

# ADD-IAC-LCM: Intent Authorization Credential Life cycle management
## Overview
Intent Authorization Credential Lifecycle Management (Intent Autoration Central Life Cycle Management, ADD-IAC-LCM) defines IAC legal status, status migration rules and treatment requirements.

This component applies to the status management, authentication and related certificate processing of IAC issued.

## Definitions State Machine
IAC The rules of legality and flow within their life cycle are as follows.

|** Status Value**|** Semantic**|** Trigger Condition**|** Restorability**|
| --- | --- | --- | --- |
|`Active`|Valid, available at commerce interaction and payable.|IAC Completed and not suspended or cancelled during its validity|—|
|`Suspended`|Pause, temporarily unavailable.|Principal or risk control system initiated temporary suspension, and the voucher has not been terminated|Restoreable|
|`Expired`|Expired, not available|`validity_end_time` Arrival, system automatically activated|Unrecoverable.|
|`Revoked`|Cancelled, permanently unusable|Principal or entrusted Agent to initiate a permanent revocation|Unrecoverable.|

## Status migration rules
The IAC status migration rules are as follows.

|** Current Status**|** Target Status**|** Trigger Condition**|** Is it counterproductive?**|
| --- | --- | --- | --- |
|`Active`|`Suspended`|Principal or risk control system initiating temporary hangup|Yes.|
|`Suspended`|`Active`|Principal or risk control system unmounted|Yes.|
|`Active`|`Revoked`|Principal or commissioned Agent to initiate the revocation|Yes|
|`Suspended`|`Revoked`|Principal or commissioned Agent to initiate the revocation|Yes|
|`Active`|`Expired`|Arrival at `validity_end_time`|Yes|
|`Suspended`|`Expired`|`validity_end_time`Arrivals|Yes|

Of which `Revoked` and `Expired` are final. IAC may not be restored to Active or Suspended. Suspended is temporarily restricted and can only be lifted and returned to Active under clearly defined restoration conditions.

## Processing of requests
### Effective status
IAC Upon issuance, if the current time has entered its active time window and it has not been suspended or revoked, the status SHALL be `Active`. The IAC status of `Active` may be followed by commerce interaction, payment execution and authorization of verification is routinely quoted.

### Suspend
Principal or a risk control system may be temporarily suspended for the duration of IAC. After that, the state of IAC shall be changed to `Suspended`. IAC in `Suspended` status shall not continue to be used for commerce interaction, payment execution or authorization verification.
agent SHOULD Step to Report `act:delegation:delegation-suspended` Testimony Event.

### Unstagger
IAC, in `Suspended` state, can be removed from operation by Principal or by the risk control system. After release, IAC state SHALL be restored to `Active`.
agent SHOULD Step to Report `act:delegation:delegation-resumed` Testimony Event.

### Cancel
After cancellation, the status of IAC shall be changed to `Revoked`. IAC in `Revoked` status shall not continue to be used for commerce interaction, payment for execution or authorization of verification.
agent SHOULD Step to Report `act:delegation:delegation-revoked` Testimony Event.

### Autoprocessing due
When `validity_end_time` arrives, IAC status SHALL be automatically changed to `Expired`. IAC in `Expired` status shall not continue for commerce interaction, payment for execution or authorization of verification.
agent SHOULD Step to Report `act:delegation:delegation-expired` Testimony Event.

## Authentication status verification
In the follow-up, when citing IAC, SHALL confirms at least the following:

+ Whether IAC is in a valid time window.
+ IAC Whether the current status is `Active`.
+ IAC Whether there are known suspensions, revocations or expirys.

The processor can obtain the current status by `status_reference` before making a final authorization validity judgement. When the status service is temporarily unavailable, the process can perform interim risk control based on the last local successful query and `validity_end_time`.

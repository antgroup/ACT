# ACT 2.1 Trust Services Domain

[中文](trust-services.md) | English

# First: trusted attestation

# Scope
## Subdomain Positioning
trusted attestation (Trusted Attestation) is one of the sub-sections of Trust Services Domain. This sub-section provides for a unified record, reference and certification of key business events in the ACT protocol, which provides a trusted basis for authorization, commerce interaction, payment of performance and performance-related facts, which are traceable, verifiable and subject to review.

## Subdomain Scope and Boundaries
This sub-section covers the following:

+ (a) Types of incidents documented and their marking rules;
+ Standard load structure and minimum required elements for the certificated event;
+ Rules for the submission, signature, anchor reference and status indication of the event attestation;
+ (b) Basic verification rules for reference, validation and dispute resolution of the certificate results;
+ Cross-domain incident reference relationships and their consistency requirements;
+ The sub-section provides for ACT Trust Chain as a chain anchoring infrastructure to carry summary anchors for key business events and to support unmistakable verifications in the cross-agency context.

The following are not regulated in this sub-section:

+ Internal realization of specific bottom books, block chains, time stamp services, databases or third-party documentation infrastructure;
+ The internal audit platforms Participants, the legal processing system and the operational operating system were implemented.

## 1.3 trusted attestation Value statement
The sub-chapter uses a two-tiered certificate structure, “Current full record-up + summary anchoring on the chain”: under the chain, complete business events are maintained with explicit and signed material and only protected summary anchors are included in the chain to satisfy operational verifiability, privacy protection and cross-agency Trust Requirements.

The central objective of this design is not to centralize the original business data for third-party preservation, but to establish a minimum level of trust that is necessary and mutually verifiable, provided that each party has the maximum degree of autonomy to keep the original data. When a dispute, audit or compliance verification occurs, the relevant Participants presents the original records retained by the party on demand and compares them with the pre-enclosed summary of the chain, thereby proving that the record has not been tampered with subsequently.

Since the chain only preserves a light quantitative summary without a full-volume business statement, the book enables the retention of the critical certification capacity required for cross-agency validation while controlling storage costs and reducing the risk of spills of sensitive information. At the same time, the chain anchor is maintained by a multi-party consensus and does not rely on any single platform or a single Participants log endorsement, making it more neutral and credible than a single-point log system. Based on this mechanism, trusted attestation serves not only historical memory, but also serves as a common basis for subsequent signature verification, causal chain traceability and dispute resolution.

# List of sub-components and relation
## Component Overview
The sub-section trusted attestation consists of five protocol components that jointly complete the full chain from the definition of critical business events, the production of chain-based certificate records, the chain-based summary anchoring, to ex post facto verification and dispute resolution support.

The functional positioning of the components is as follows.

+ **TSD-ATT-EVT: Definition of the type of event to be documented.** Responsible for defining key event types and their standard semantics that can be included at ACT throughout the business chain as a single entry for the processing of subsequent certificates in the sub-chapter.
+ **TSD-ATT-OFF: Sub-chain record-keeping.** It is responsible for regulating the requirements of Participants for the generation, preservation and management of complete documentation at the local level so that key business events can form a retroactive and verifiable first-hand evidence vehicle.
+ **TSD-ATT-OCA: Certificate anchors on the chain.** Regulates the extraction of the minimum summary information necessary from the chain record and the inclusion of the requirement of ACT Trust Chain in order to create a time anchor and cross-institutional basis for validation of the chain that cannot be altered.
+ **TSD-ATT-SVF: Sign verification process.** Responsible for regulating the standard steps for consistent verification of record-keeping, signature material and chain anchorages under the chain in the context of dispute resolution, audit or compliance verification.
+ **TSD-ATT-DSP: Dispute process.** Regulate the process framework for each Participants certificate of proof based on chain record, chain anchors and verification findings.

## Core Object & Identification
In order to maintain consistency between the internal processing of the sub-section and the citation relationships with other domains, the sub-section uses a set of standard core objects and identifiers to describe key messages in the trusted attestation link. The core object of the sub-section and its role can be summarized as follows.

|** Object or Identification**|** Meaning**|** Mainly Generate Location**|** Main Use Location**|
| --- | --- | --- | --- |
|Testified Events|Standardized event expression for ACT key business node of the full chain to clarify what is to be documented and the unified semantic of the event|TSD-ATT-EVT|TSD-ATT-OFF, TSD-ATT-OCA, and associated processes in other domains when referring to the deposition event identifier|
|Only identifier for record-keeping|For the sole identification of the record of the certificate under a chain and as the main key to stabilize the link between the record under the chain and the anchor point on the chain|TSD-ATT-OFF|TSD-ATT-OCA、TSD-ATT-SVF、TSD-ATT-DSP|
|Underlink record.|A complete record of events generated by Participants and kept locally, usually containing the content of events, Participants information, summary value and signature material, as a first-hand object of evidence in the handling of disputes|TSD-ATT-OFF|TSD-ATT-OCA、TSD-ATT-SVF、TSD-ATT-DSP|
|Store anchor on the chain|Light Quantified Summary Certificate taken from the chain record to create unmovable anchor record on ACT Trust Chain|TSD-ATT-OCA|TSD-ATT-SVF, TSD-ATT-DSP and cross-agency verification scenes|
|Validate conclusion|Standard results resulting from consistent verification of chain records, signature materials and chain anchors to determine whether the records are complete, authentic and unmistakable|TSD-ATT-SVF|TSD-ATT-DSP, and follow-up on audit, compliance verification, etc.|
|Requests for settlement of disputes|A request for evidence or processing initiated by a disputing party in relation to a particular chain of transactions, usually relating to a specific business event, a transaction identifier and a description of the dispute|TSD-ATT-DSP|TSD-ATT-DSP and related arbitration, verification and processing|

## Dependence and Cross-domain Reference
TSD-ATT-EVT is the logical starting point for this sub-section to define which key business nodes can be included in trusted attestation and the unified semantics of these events.

TSD-ATT-OFF Generates under-chain documentation according to the type of event defined by TSD-ATT-EVT and forms the subject of evidence relied upon for anchoring and ex post verification in the subsequent chain.

TSD-ATT-OCA Further references to core summary information in the chain certificate record, completing the chain anchoring, thus providing a cross-institutionally verifiable basis for tampering with the chain record.

TSD-ATT-SVF also relies on the chain record and chain anchor to perform consistency verifications in order to arrive at a standardized verification conclusion.

TSD-ATT-DSP is based on chain records, chain anchors and verification findings to organize evidence, verification and processing processes in the context of the dispute.

Together, these relationships constitute a closed ring link to the “definition of the event — scarring under the chain — anchoring on the chain — ex post facto verification — dispute resolution”.

trusted attestation sub-sections maintain a unified register of the type of event for which the certificate is filed; Authorization & Delegation Domain, Commerce Interaction Domain and Payment Services Domain refer only to the event identifier in the relevant components and do not repeat the structure of the event or the certificate governance rules within their respective domains.

On cross-domain links, the sub-chapters create a link of evidence across the entire chain from authorization, confirmation of transactions, payment execution to dispute resolution, mainly through the `intent_id`, `delegation_id`, Merchant side order transaction number, payment transaction flow and unique identification of certificate records.

# TSD-ATT-EVT: Definition of the type of certificated event
## Overview
TSD-ATT-EVT (Attestation event) is used to define the standard storage event type in the ACT trusted attestation system and to harmonize the incident identifiers and basic semantics on key operational nodes Authorization & Delegation Domain, Commerce Interaction Domain and Payment Services Domain.
This component performs the role of a global event type registration form in the system, and includes trusted attestationScope for key events, SHALL for which registration and reference is consolidated in this component.

This component defines only the type of key event that can be documented and does not define the temporary state of operation within each business area, the step of realization or the private intermediate event of the manufacturer.

The current protocol specifies only the standard certificate type of event and its underlying trigger semantics, and does not specify the complete `event_body` structure of each event, field level verification rules, signature sealing or chain anchoring formats.

## Participants and prefix
Participants includes Authorization & Delegation Domain, Commerce Interaction Domain and Payment Services Domain related to the generation of critical business events, as well as the manager responsible for maintaining registration information on the type of documented event.

Before entering this component, SHALL satisfies the following preconditions.

+ The relevant business area SHALL have been identified for inclusion in the key business nodes at trusted attestation Scope and their completion conditions.
+ The relevant Participants SHALL be able to provide stable business linkages markers to support chain-based records, chain anchors and cross-domain links in dispute resolution.
+ The above-mentioned associated identification SHOULD includes at least `intent_id` and may further include `delegation_id` and each business area transaction identifier, depending on the specific scene.

## Basic requirements
The standard event-type naming space in this component is in the form of `act:<domain>:<event>`, where `domain` indicates the business field to which the event belongs, and `event` indicates the specific critical business event within that domain.

The standard event type SHALL have a stable, enumerable, cross-domain-referenced character, SHALL NOT changing its basic semantics due to a single difference. The same business event can be documented separately at Participants, but Participants at the time of reference uses the same standard event identifier and is understood in a consistent trigger syntax.

SHOULD reports of documented events that take place at the end of the business event, SHOULD NOT takes over the main business process path, and SHOULD NOT affects the processing of online transactions.

## Standard type of event
The standard type of event included in the current version TSD-ATT-EVT is as follows.

|Event type identification|Own Field|Trigger Time|
| --- | --- | --- |
|`act:delegation:intent-created`<br/>|ADD|user intent Trigger when confirmation is completed and the result of intent is available for subsequent authorization|
|`act:delegation:delegation-issued`<br/>|ADD|Intent Authorization Credential Trigger when issuance is completed and active|
|`act:delegation:delegation-suspended`<br/>|ADD|Intent Authorization Credential Trigger when hung|
|`act:delegation:delegation-resumed`<br/>|ADD|Intent Authorization Credential Triggered when restored to Active status by Suspended|
|`act:delegation:delegation-revoked`<br/>|ADD|Intent Authorization Credential Trigger when revoked|
|`act:delegation:delegation-expired`<br/>|ADD|Intent Authorization Credential Trigger when expiry|
|`act:commerce:decision-logged`<br/>|CID|Buyer Agent Trigger when candidate comparison or decision is completed|
|`act:commerce:cart-confirmed`<br/>|CID|Cart Confirmation Trigger when transaction confirmation is completed and entered for start-up payment|
|`act:payment:transaction-completed`<br/>|PSD|Trigger when payment transactions are completed and form payment result|
|`act:commerce:fulfillment-completed`<br/>|CID|Merchant Trigger when performance of the side order is completed|

These events constitute the standard set of events in the current version trusted attestation, covering key nodes such as mandate formation and change of status, business confirmation, performance completion and payment completion.

# TSD-ATT-OFF: Subchain record-keeping
## Overview
The standard structure, method of generation, preservation requirements and cross-domain chain rules for recording under the chain in the ACT system are the basic components of Participants for local credible trails of critical business events.

This component carries elements such as the statement of business event to be certified, Participants identification, link identification, load of Hashi and digital signatures, which are used to provide a verifiable original basis for anchoring, signature verification and dispute resolution on the subsequent chain, without explicitly placing the business on the chain.

##  Participants and prefix
Participants includes Participants related to the generation of critical business events and documentary responsibility in Authorization & Delegation Domain, Commerce Interaction Domain and Payment Services Domain, as well as a depository service provider who can be entrusted with record-keeping or search services.

Before entering this component, SHALL satisfies the following preconditions.

+ The relevant operational event SHALL have met the trigger conditions for the corresponding standard type of event in TSD-ATT-EVT, and the initiating or record generator SHALL be able to obtain a stable business connection sign, including at least `intent_id`, and may further include `delegation_id`, Merchant side order transaction and payment trade stream water.
+ The record generator also has SHALL available signature private keys, decryptionable identifiers, recognized time expressions, and local secure storage capacity or fiduciary storage arrangements that meet the requirements before the record is stored under the creation chain.

## Basic requirements
Under-chain certificate record SHALL be generated by structured data models and can be stabilized by subsequent loads of Hashi calculations, digital signatures, chain anchoring and verification processes, so that records cannot undergo structural changes without version numbers once they are generated.

Under-chain certificate record SHALL adhere to the principle of “business completion, proof-of-assist reporting” and the actual time of occurrence of an operational event is recorded separately from the time of creation of the certificate record SHALL to clarify the difference between the time of completion of the business and the time of deposit.

The CSR SHALL support the four capabilities of cross-domain chain, privacy protection, protection from tampering and accountability, i.e., ability to restore the chain, avoid sensitive explicit leaks, detect subsequent modifications through Hashi and signatures, and identify who is responsible for the authenticity of the record.

## Underlink recorder structure
Under-chain documentation records consist of six parts: basic metadata, full-chain links and tracer identification, privacy and inference elements, Participants list, event load `event_body`, digital signature; to achieve the addition of an extended field without compromising compatibility.

In addition to expanding fields, the core field SHALL in each part has a stable semantic and SHALL have a consistent naming or one-map relationship with the relevant fields TSD-ATT-EVT, TSD-ATT-OCA, TSD-ATT-SVF to avoid ambiguity at the bottom of the chain and at the verification stage.

### Basic metadata
Basic metadata are used to identify “what this record is, what version it belongs to, when the business occurs, when the record is generated” as the only identification for each record, ensuring that the record is accurately located and analysed across versions.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Only identifier for record-keeping|Required|The value given by the record generator at the time of creation, as soon as SHALL NOT changes|
|Event type identification|Required|SHALL be the registered number of entries in TSD-ATT-EVT|
|Business event time|Required|Actual occurrence of business events (non-documented record creation time) recorded by the sponsor at the completion of the event|
|Certificate record creation time|Required|Certificate record creation time, later than business event time, reflecting anecdotal reporting|
|Certificate record structure version number|Required|For future versions to be compatible|

The record generator SHALL record the time of the business event and the time of the creation of the record of the record of the record of the record of the record of the record of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction, and the time of the creation of the record of the record of the record of the record of the record of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the business of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the record of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the record of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the transaction of the record of the record of the record of the record of the transaction

### Full link and trace identification
The full chain link and the tracer mark are used to record “what business link this matter belongs to” and to provide a complete end-to-end causal chain of evidence at different Participants points of time, ensuring that the complete picture of the transaction can be restored in the event of a dispute.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Intentional markings|Required|Global business process master key, all certificates of the same business process SHALL carry the same intent identification|
|Delegated identification|Conditionally required|Carrying SHALL commission payment scene|
|Merchant side order transaction number|Conditionally required|Events after Cart Confirmation SHALL carry|
|Pay the Trade Stream.|Conditionally required|Pays for events following execution SHALL carried, corresponding to PSP return value|
|References to upstream certificates|Optional|Unique identification of the record of evidence pointing to a related upstream event; SHOULD carried when there is a specified upstream event, which can be used to construct the end-to-end causal chain of evidence|

The intended identification (`intent_id`) SHALL be used as a global lead chain that crosses ADD, CID, PSD, and TSD, while the other identifiers are used as auxiliary strings at different stages of the operation.
When there is a clear causal link between the current event and the critical upstream event, the record generator SHOULD fills in the reference to the upstream certificate record to support TSD-ATT-SVF in the implementation of a back-to-back upstream chain check, if necessary.

### Privacy and inference-proof elements
The privacy and inference elements are used to address the “how to ensure that records are not tampered with without explicit exposure” and to reduce the risk of inversion of certificate content through known operational data by introducing random salinity values that make the summary values of each record unique and unpredictable.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Random salt value|Required|Each certificate record SHOULD contain an independent high entropy random salt value of not less than 128 bit in original length and is generated using a password safe random number generator.|
|Load Hash|Required|The event load and the Participants list are treated in a standardized manner and the password summary values obtained are calculated in conjunction with random salinity values; SHOULD be stored in Base64url code.|
|Hash algorithm identifier|Required|The current version supports SHA-256 or SM3; if subsequent versions support other algorithms, SHALL adopt the explicit statement of the field.|

The steps in the calculation of the load of Hashi are as follows.

+ Deals with the event load with the Participants list field by the RFC 8785 JSON Regularization Program (JCS) as a byte sequence.
+ Collapse the byte sequence with the original byte of the random salt value, in the order of " Regulate the byte series ∥ salt value byte ".
+ Performs SHA-256 or SM3 calculations for collage results.
+ Stores the calculation with the Base64url encoding as a load of Hash.

The record generator SHALL ensure that a separate random salt value is used for each chain under the certificate, and SHALL NOT repeats the same salt value between multiple records.
When the event load is identical, but with a different random salt value, the recalculated load Hash value is also SHALL different, a feature that is part of this component's insulation design.

### Participants List
The list Participants records the identity of the parties involved in this business event, specifying “who is involved in this business and who is involved in what role” so that the attribution of responsibility can be clearly established when the dispute arises.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Mark Participants|Required|Who confirmed the incident?|
|Role Participants|Required|In what capacity the incident was confirmed; the list may include: the payer Agent, the payee Agent, Merchant, Payment Service Provider, Principalagent, the provider of the certificate|
|Agency identification|Optional|When Participants is acting on behalf of other entities (e.g. Agent platform type User completed on behalf of a specific User), record the identity of the Agent|

The list Participants of each record includes at least one role to ensure that each record has a clear responsibility to initiate in order to be traced. The list of roles may include participants identified by the protocol, such as the payer Agent, the payee Agent, Merchant, Payment Service Provider, Principal Agent, the certificated service provider.

The list Participants may contain more than Participants entries when multiple joint certificates exist, but its role SHALL remain clear and non-duplicable.

The Participants logo SHALL be able to be adapted to the system ' s identity mechanism or to the external lettered identity mechanism, thereby supporting subsequent public key acquisition and accountability judgement.

### Event Load
The event load (`event_body`) carries “what exactly happened in this matter” as a central part of the chain-based certificate record to preserve key explicits and business elements of the current business node and as a direct basis for reconciling transaction details in the handling of disputes.

The collection of event loads is determined by the type of event, and this component only defines the location, existence and privacy of this part in the chain-based certificate record, and does not list all exclusive fields of different type of event in this section.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Event Load|Required|Operations that carry current critical business events are explicit and essential business elements whose fields are determined by events-type dynamics|
|Preset Extension Fields|Optional|For carrying additional information that does not affect core authentication; SHOULD NOT contains sensitive data such as sensitive personal information or original payment account numbers|

The event load SHALL NOT contains the following sensitive information: Principal complete identity information, such as real name, document number, contact information, and original payment account number, such as bank card number, payment account number, etc.

The event load may contain non-sensitive business elements such as amounts, currencies, commodity snapshots, time stamp; for fields that cannot be explicitly recorded due to privacy requirements, SHOULD be replaced by a Hashi summary of the corresponding field and is identified with a “summary” or “Hashi” suffix in the synonym of the field.

### Organisation
A digital signature is used to answer “who is responsible for the authenticity of the record”, to bind Participants identification and the contents of the record through a password signature, to ensure that anything can be discovered by tampering with it, and to provide an irrefutable evidentiary basis for the record under the chain.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Signing party identifier|Required|Format with Participants Identification|
|Signing algorithm identifier|Required|A signature algorithm value supported by this protocol|
|Sign Value|Required|Base64url Encoding|
|The signature overwrites the description Scope|Required|Overwrite: Event load, Participants list, random salt values, unique identifier for record-keeping, five fields of business event time|

Each certificate record SHALL contain at least one signature generated by the sponsor of the record and other Participants joint signatures may be attached to enhance the evidentiary effect.

The signer's public key SHOULD be obtained from the identity document to which it corresponds or from the letter-registry information to support the subsequent TSD-ATT-SVF signing process.

## Load Hash calculation requirements
In order to avoid a difference in achieving inconsistent summaries due to the serialization differences of JSON, the record generator should regulate the use of RFC 8785 JCS for the object in calculating the load of Hashi and executing the digital signature.

The minimum input set SHALL for the load Hashi includes the list of `event_body` and the list of Participants and SHALL participate in the operation with the independent random salt carried by this record to ensure the sole binding relationship and re-placement feature between the chain record and the chain anchor.

The same entry records complete consistency of the result of the double calculation of the load Hashi SHALL without changes to the business content, Participants list and salinity values, otherwise it is deemed not to meet the requirements of this component.

## Storage and retention requirements
Under-chain certificate records may be stored autonomously by each Participants or may be commissioned to be stored on behalf of the provider of the certificate, but irrespective of who keeps them, the responsibility for the authenticity of the content of the record remains with the originator or signatory of the record, and the provider of the certificate does not acquire the power to modify the original record by proxy.

Under-chain record SHOULD be maintained for a period of time in accordance with applicable laws and regulations, the dispute resolution cycle and the operational risk exposure period, and during the retention period SHALL be guaranteed as searchable, exportable, verifiable and capable of removing, covering and back-up recovery.

When the protocol version is upgraded, the structure of the generated record and the verifiable content SHALL NOT is rewritten and the solver SHALL selects the corresponding resolution logic based on the structure version number in the record to ensure that the historical evidence is valid for the long term.

# TSD-ATT-OCA: Certificate anchor on the chain
## Overview
TSD-ATT-OCA (On-Chain Actation Anchor) sets the standard structure, submission requirements and chain writing rules for ACT trusted attestation proof anchors in the chain, which are standard components of the chain record entry into ACT Trust Chain. The chain anchor is a light quantitative metadata document derived from the chain certificate record, which does not contain full business specifications, but carries the minimum required index, summary and signature information to provide a non-falterable cross-agency authentication on the multi-consensual ledger.

Any unilateral modification of the original text at the bottom of the chain, which is the only link between the chain-based proof anchor and the corresponding chain-based record, would result in the recalculated Hashi values not being consistent with the chain-based anchor, thus preventing subsequent verification.

## Participants and prefix
Participants includes Participants areas responsible for the generation and submission of anchors in the chain, certificate service providers who can be trusted to submit anchors, and ACT Trust Chain node operators responsible for the capacity to write and search anchors.

Before entering this component, SHALL satisfies the following preconditions.

+ The standard type of event has been determined in SHALL for the relevant operational event, and its chain-based record SHALL have been generated in accordance with TSD-ATT-OFF requirements, with the only basic fields for the record-keeping, the type of event, the time of the business event, the intention to mark and the load of the Hash value.
+ If the certification service provider is acting as the anchor of the chain, the certificate service provider is only responsible for submitting or searching on behalf, and does not acquire the right to modify or authenticate the contents of the original record under the chain by writing by the Chargé d ' affaires.

## Basic requirements
The chain proof anchor SHALL follows the Design Principles under the "Current preservation of complete clear and minimal summary on the chain" to ensure inter-agency validation while preserving commercial privacy and storage costs on the chain of control.

The chain anchor SHALL be capable of establishing a stable one-simulation relationship with the corresponding chain bottom certificate record, in which the sole identifier of the record is used for record-level binding, and the carrying Hash value is used for content-level binding, which together support subsequent chain bottom consistency verification.

The chain anchor SHOULD be submitted by step after the completion of the business event and the production of the chain-based certificate record, SHALL NOT obstructs the original main business process and SHOULD NOT affects the processing of online transactions.

The chain anchor SHALL serves as a credible index of proof rather than a complete body of evidence and, in the event of a dispute or audit, continues to SHALL to be a source of original evidence using the chain-based evidence record, which is then combined with the chain anchor to complete the integrity and unmovable verification.

## Validation anchor structure
The chain proof anchor uses a two-tiered data model, i.e. the base field layer and the extended field layer, where the base field layer is the core element for all anchor points SHALL and the extended field layer is used to fit the additional properties of a given deployment scenario.

The anchor SHOULD be encapsulated in the form of JWS Compact Management and is written at ACT Trust Chain, the head of the encapsulation SHALL contain the signature algorithm and signature key reference and the load section carries the anchor field as defined by this component.

### Head request
JWS head SHALL contain at least the signature algorithm and signature key reference to support the source identification and subsequent signature processing of the chain anchor.

The specific naming and coding of the head field can be determined by achieving layers compatible with JWS Compact Management, but SHALL NOT affects the stable resolution and cross-institutional recognition of anchor loads.

### Load Fields
The JWT payload contains the following fields.

|** field syntax**|** Existence**|** Annotations**|
| --- | --- | --- |
|Only identifier for record-keeping|Required|Strictly consistent with the sole marking of the chain-based record-keeping, achieving the only binding of the two|
|protocol version number|Required|Certificate record structure version number|
|Event type identification|Required|SHALL be the registered number of entries in TSD-ATT-EVT|
|Business event time|Required|Consistent with the time of the business event recorded under the chain, use ISO 8601 UTC at SHOULD|
|JWT issuance time|Required|Time of submission of this anchor point to the chain|
|Intentional markings|Required|Global business process tracking marker|
|Delegated identification|Conditionally required|Carrying SHALL commission payment scene|
|Merchant side order transaction number|Conditionally required|Events after Cart Confirmation SHALL carry|
|Pay the Trade Stream.|Conditionally required|Transport of payment type event SHALL|
|Submitting party identifier|Required|Submit Participants identification for this anchor|
|Load Hash|Required|Fully consistent with the loading of the Hash in the chain certificate record, SHOULD using the Base64url code is the only coded basis for the binding of the two|
|Hash algorithm identifier|Required|Current version supports SHA-256 or SM3 and aligns SHALL with the Halshi algorithm statement in the chain record|
|Privacy Channel Identification|Required|ACT Trust Chain's privacy channel identifier for multiple data isolation|
|Preset Extension Fields|Optional|Additional attributes used to fit specific scenes, SHOULD NOT containing business specifications or personal identity information|

## Structure Map Requirements
The unique identification of the certificate record in the chain anchor, the protocol version number, the event type identification, the time of the business event, the intent marking, the commissioning identification, the order transaction number, the payment transaction flow and the load of the Hashi value, SHALL be consistent with or can be mapped at the relevant field in the corresponding chain certificate record.

The submitting identifier is used to mark “who submitted the anchor point to the chain” and is not, of course, equivalent to the full collection of Participants in the chain record, so that the Participants list and digital signature information in the backlink record is fully verified at the time of the dispute.

The introduction of the extended field SHALL NOT destroys the stable semantics of the base field layer and has led to different interpretations of the core of the same anchor point by different institutions.

## Technical requirements
ACT Trust Chain Node Operator SHOULD provide a standard chain anchoring interface for submission of requests in the form of JWS Compact Security and for return to the chain where the results can be used for subsequent inquiries and verification.

The only identified anchor in the same certificate record requests SHALL to be considered as an operation, etc., and node SHALL refuses to duplicate and, in response, returns information on the height or equivalent chain of blocks where the anchor already exists, in order to prevent a repetition of anchoring of the same event.

The chained data structure SHOULD NOT contains sensitive elements such as explicit, sensitive personal information or original payment account numbers, SHOULD contain only deminious Hashi, anonymous indexing and extension without sensitive content, in order to perpetuate the privacy protection principle of the system's “clear and chain-based summary”.

When an extension of the protocol level occurs in the Hashi algorithm, version number or associated identifier recorded under the chain, the chain anchor achieves SHALL the ability to maintain compatible resolution of the existing version, SHALL NOT destroying the validity of the historical anchor as the new version is online.

Once the chain anchor has been written, the SHALL NOT is overwritten; if subsequent linkage information is required for business replenishment, SHOULD be achieved by the compatibility of the new chain recording or extension fields, while SHALL NOT returns the existing core anchor content.

# TSD-ATT-SVF: Sign verification process
## Overview
TSD-ATT-SVF (Signature Verification Flow) is used to specify standard steps for ex post-cipheral verification of documented event records in the ACT trusted attestation system for uniform call in dispute processing, compliance audit and inter-agency verification scenarios.
This component is used to verify the integrity, validity of the signature and consistency of the record under the chain, thus determining whether a record of the certificate can be considered as credible evidence that has not been tampered with and is imputable.

## Participants and prefix
Participants includes the initiating business Participants, the record holder responsible for the provision of the chain certificate record, the depository service provider for the provision of a surrogate or search service, and the operator of the chain anchor search ACT Trust Chain node.

Before entering this component, SHALL satisfies the following preconditions.

+ Verify that the initiating party SHALL be able to obtain the full text of the certificate under the chain to be verified, or at least the sole identifier of the certificate record and the corresponding complete record through a local storage or certificate service provider search interface.
+ The initiating party can also SHALL acquire the signature party's identifier for the current valid public key or historical valid public key and the ability to access the anchor points on the search chain, otherwise the complete authentication closure loop cannot be completed.

## Basic requirements
The signature verification SHALL follows the sequenced approach of “first, second, first summary, then signature, first current record, then upstream chain” in order to avoid moving directly into higher-cost or more complex subsequent verification steps in the absence of confirmation of base consistency.

When recalculating the load of Hashi during the verification process, SHALL recalculates the summary values in accordance with the established algorithm using the same normative rule as TSD-ATT-OFF, i.e. following the regularization of the event load and the Participants list with the RFC 8785 JCS.

If either step is reached with a clear failure conclusion that would negate the credibility of the record, the verification process can be terminated and the corresponding error code returned without the need to proceed with the subsequent steps.

If the verification cannot be completed simply because external dependence is unavailable, e.g. the chain search time-out or the current valid public key is not available, SHALL return the result of the “summary not available” or “public key not available”, while SHALL NOT miscalculates the record.

## Checking steps
### Step 1: Retrieval of the record under the chain
Verify that the originator SHALL retrieves the full certificate from the chain storage based on the unique identifier of the certificate record; if the record is held by the certificate provider, SHALL be obtained through the certificate provider search interface.

The bottom record SHALL of the recovered chain contains at least the core elements required for verification of basic metadata, full chain links and tracer identification, Participants lists, event loads, loads of Hashi values and digital signatures, otherwise the conditions for entering the follow-up verification process are not met.

### Step 2: Obtaining the public key for signature
Verify the signature party identifier corresponding to each signature element in the digital signature array of the originator SHALL and obtain its public key material for signing.

For the DID format identification, the public key SHOULD be obtained from the DID document corresponding to that identifier; for the institutional identifier registered in the ACT Trust Chain Trust Register, the public key SHOULD be retrieved from the Trust Register.

Approving party SHOULD further validates the validity of the public key acquired at the time of the business event, including whether it has rotated, is invalid and is still within Scope the time available for historical signature verification.

If it is not possible to obtain the current valid public key of the signatory or a valid public key that can be used for historical verification, SHALL terminates the password check and returns `PUBLIC_KEY_UNAVAILABLE`.

### Step 3: Recalculating and comparing the load of Hashi
Checks that the incident load in the chain response certificate record and the Participants list are recalculated with the random salt value stored in the record in accordance with the algorithm TSD-ATT-OFF.

Recalculated loads of SHALL be consistent bytes with the loads stored in the bottom certificate record; if not, indicate that the content of the local record or its structured elements may have been changed.

The verification process SHALL terminates and returns `PAYLOAD_HASH_MISMATCH` when the local recalculation results are inconsistent with the summary kept in the record.

### Step four: Password checking
The approving party SHALL performs a password-checking each signature element in the digital signature array using the corresponding public key obtained in the second step.
At the time of the examination, SHALL ensure that the signature covers Scope consistent with the covered object stated in TSD-ATT-OFF, including at least the event load, Participants list, random salinity values, unique identification of the record and the time of the operational event.

If any signature element fails to verify, SHALL return `SIGNATURE_INVALID` and SHOULD with the signature identifier corresponding to the failed signature in order to subsequently locate the subject of the responsibility or screen for the difference.

If the record contains multiple signatures, the certifying authority will decide, in accordance with the operational rules, whether to require a successful verification of all signatures, but at least SHALL ensure that the collection of signatures deemed valid meets the minimum credible requirements of the scene.

### Step 5: Chain anchor verification
Approving party SHALL search ACT Trust Chain for the sole identification of the chain anchor in the certificate record and confirm the existence of the anchor.
If the anchor is present, the verification also compares SHALL the loads in the chain anchors to the full consistency of the loads in the 3rd local recalculations.

The chain query SHOULD sets a time limit of 30 seconds and SHOULD retrys up to 3 times after the time has elapsed; if the time is still exceeded, SHALL return `ANCHOR_QUERY_TIMEOUT` and SHALL NOT determines it to be `VERIFIED` or `CHAIN_HASH_MISMATCH`.

If anchors exist but there is a discrepancy between the Hashi values in the chain, then SHALL return `CHAIN_HASH_MISMATCH`; if no corresponding anchor points exist in the chain, SHALL return `ANCHOR_NOT_FOUND`.

### Step six: Continuous validation of the upstream causal chain
If the reference field to the upstream certificate record is present in the current bottom-chain record, the verification should be carried out step 1 to step 5 of the upstream link certificate record to which it is directed, so that the complete end-to-effect chain of evidence can be constructed step by step.

This step is optional, but of high value in cross-domain dispute resolution, as it supports the overall consistency review of key nodes such as authorization, confirmation, payment, performance by extending the verification of single-point events to a chain-level fact.

### Step seven: Return to check.
Upon completion of the above-mentioned steps, the Approving Party returns the Standardized Validation Conclusions SHALL to ensure consistency of understanding of the results between the different institutions and the different achievements.

The verification conclusion SHALL NOT is defined freely, while SHALL gives priority to the use of standard count values specified in this component to support subsequent dispute management, audit trails and automated inter-system interfaces.

## Validate conclusion
|** Validate conclusion**|** Meaning**|
| --- | --- |
|`VERIFIED`<br/>|The signature is valid, the chain is consistent and the record is intact.|
|`PAYLOAD_HASH_MISMATCH`<br/>|The local recalculated summary is not consistent with the summary stored in the certificate record, which may have been tampered with.|
|`SIGNATURE_INVALID`<br/>|The signature authentication failed and SHOULD was accompanied by a failed signature party identifier.|
|`CHAIN_HASH_MISMATCH`<br/>|An anchor in the chain exists, but the chain summary is not consistent with the local recalculation results, and there may be tampering on or under the chain.|
|`ANCHOR_NOT_FOUND`<br/>|Corresponding anchors do not exist on the chain, and the evidence may not have succeeded in uplinking.|
|`ANCHOR_QUERY_TIMEOUT`<br/>|The chain search is timed out and no final check can be concluded at this time.|
|`PUBLIC_KEY_UNAVAILABLE`<br/>|Could not get the signatory's current valid public key or a valid public key for historical verification, and there may be key rotation or failure to resolve it.|

When the result is `VERIFIED`, merely indicating that the record has been verified at the level of passwords and in the context of chain consistency is not automatically equivalent to business conduct that has been finally confirmed as uncontested in the sense of a contract, regulatory or controversial decision.

When the result is not `VERIFIED`, the successor SHOULD takes measures such as additional evidence, re-examination, request for a return to the record or access to the dispute process in combination with the type of failure, while SHOULD NOT treats all failures in the same way.

## Technical requirements
The verification of data-processing rules consistent with SHALL and TSD-ATT-OFF and TSD-ATT-OCA, particularly with regard to JCS standardization, Hashi algorithm selection, Base64url coding and field mapping, SHALL NOT resulted in different validations of the same records in different institutions as a result of the discrepancy.

For chain anchors with JWS Compact Regulation, the achieving party corrects the separation and verification of the head, payload and signature parts at SHALL during the decomposition and signature, and ensures that the algorithm statement is consistent with the actual signature algorithm to reduce the risk of the algorithm replacing or defusing the ambiguity.

The verification system SHOULD retains the process audit log, including the timing of the verification, the verification of the sponsor, the source of the public key used, the results of the chain search and the final verification findings, with a view to restoring the validation process in the subsequent dispute resolution.

When the signatory rotates the key, SHALL be verified by comparing the time of the business event with the time of validity of the key and continues to be allowed to complete the historical signature check using the old key when the business event time falls within the validity of the old key to ensure long-term validation of historical evidence.

# **TSD-ATT-DSP: Dispute process**
## Overview
TSD-ATT-DSP (Dispute Resolution) is used to define the process framework in the event of a dispute in the ACT protocol transaction, specifying how each Participants evidence, verification and disposal is based on a chain record and chain anchor.

This component is an important application export of the trusted attestation system, and the practical value of the certification mechanism is realized mainly through the dispute management landscape.

This component defines only the process framework and basic requirements; the attribution of decision-making authority to final arbitration, such as the Platform ' s arbitration, industry arbitration committee or judicial body, as otherwise agreed by Participants in an access protocol or related legal arrangement, does not belong to this protocol norm Scope.

## Participants and prefix
Participants includes the applicant for the dispute, the respondent or other relevant transactions Participants, the processor or arbiter responsible for receiving and organizing the verification, the provider of the certificate of storage or authentication services for the chain record, and the operator of the ACT Trust Chain node providing the chain anchor search capability.

Before entering this component, SHALL satisfies the following preconditions.

+ The disputed matter SHOULD already has associated markings that can be used to locate the business link, such as intent identification, commissioning identification, Merchant side order transaction number or one or more of the payment transaction flow numbers, to support the retrieval and chaining of relevant documentary records.
+ The relevant Participants SHALL be capable of providing a complete chain record of certificates retained by the parent, or of extracting the corresponding records from a local storage or certificate service provider search interface based on the unique identifier of the record.
+ The processor also has SHALL capability to search for anchor points on the ACT Trust Chain chain and to obtain valid public key material corresponding to the signatory ' s identifier to complete the bottom chain consistency check and signature validity check.
+ If it is not possible to obtain the necessary public key material for the chain record, chain anchor or signature verification, this component may enter the admissibility and evidence phase, but may not be able to complete the full standardized closure loop.

## Basic processes
The handling of the dispute SHOULD follows the order in which the “claim in dispute—the parties provide evidence—the documentary examination—forms a disposition” in order to ensure a clear course of processing, a clear boundary of responsibility and a uniform basis for verification.

The SHALL disputing party submits the type of dispute, the associated identification and description of the dispute for the location of the business link; the relevant Participants SHALL submits the certificate record under the chain within the prescribed time limit; the processing party shall perform the TSD-ATT-SVF verification of the documentary record of the link to the dispute and use the verification findings as an important basis for disposal.

The decision of the arbitrator or the processing party, after combining the parties' evidentiary material with the findings of verification, shall be considered as one of the grounds of the presumption against the party if a Participants fails to provide the documentary record within a specified time limit or if its documentary record confirms the conclusion that it is not `VERIFIED`.

|** Process phase**|** Main requirements**|
| --- | --- |
|Dispute application|Submission by the disputing party of the type of dispute, associated identification to locate the business link and description of the dispute|
|Evidence by the parties|Relevant Participants certificates submitted under the chain within the prescribed time limit|
|Certificate Validation|Processors carry out TSD-ATT-SVF verifications of the supporting records on the chain of dispute, with findings as an important basis|
|Disposed conclusions|Processor ' s decision to dispose of consolidated evidentiary material and verification findings|

## Processing of requests
The dispute management SHALL insists on the basic principle of “based on the original record, based on a password check, and based on a chain anchor as a basis for protection against tampering”, avoiding relying only on unilateral oral statements, logshots of platforms or non-validable secondary compilations to reach conclusions.

In the course of processing, the chain record is the source of the original evidence, the chain anchor is used to prove that the summary has been pre-established and cannot be tampered with, and the signature verification process is used to confirm the integrity of the record, the validity of the signature and the consistency of the chain.

Detailed classification of disputes, time limits for proof, mechanisms for recognizance, evidentiary priorities and rules for final adjudication could be further refined in subsequent versions of the protocol or accompanying governance documents, and it is sufficient that this chapter maintains a lightweight process design.

# Part Two: credit association

# Scope
## Subdomain Positioning
credit association(Credit Association) is one of the sub-sections of Trust Services Domain. This sub-section provides for the establishment of a Agent relationship between credit association and its associated subject, Agent associated credit statements generation, life cycle management, query authorization and certification rules to provide verifiable reference to Agent related credit in the event of insufficient credit data.

Related subjects may be natural persons, legal persons or other organizations that have a development, deployment, operation, control or other empirical link to Agent. credit association By establishing a verifiable credit association certificate, the associated subject ' s credit information can be invoked within the explicit application of Scope and form an associated credit statement to the designated Agent.

> Note: Linked credit is a different source of credit than Agent independent credit or independent reputation. Linked credit is used to express a restricted credit reference to the designation Agent under a valid credit association relationship with the associated subject credit information; Agent Independent credit or independent reputation is used to express Agent its own historical performance in commerce interaction. Associated credit may not be expressed directly as Agent its own credit rating, reputation or creditworthiness.
>

## Subdomain Scope and Boundaries
This sub-section covers the following:

+ Application, confirmation, issuance and structural regulation of credit association certificates between related subjects and Agent;
+ Mapping rules, source tags and version management for associated subject credit statements to Agent associated credit statements and associated credit map values;
+ Life cycle management such as credit association vouchers and Agent associated credit statements entry into force, suspension, revocation, expiry, replacement and reassessment;
+ (a) A mechanism for authorization of inquiries by associated subjects for credit validation, including sub-authorizations and platform proxy queries;
+ Mechanisms for standardized verification of credit association relationships and associated credit information by third parties.

The following are not regulated in this sub-section:

+ Credit evaluation models, Agent reputation scoring formulas, rules for the award of transactions, rules for the decision-making of payment risks or rules for the conversion of credit across institutions;
+ Agent Mechanisms to create an independent credit or an independent reputation based on its own conduct, performance, dispute or other historical record;
+ Internal realization of any manufacturer, platform, Identity Service Provider, credit information provider, credit provider, payment agency or other Participants.

## Value statement credit association
When doing business on behalf of User or an organization, the counterparty to the transaction, platform, and risk management system usually need to refer to its identity, behavioral records, and credit information. However, the newly created Agent or an insufficient Agent of behavioural data may not have created a referenceable reputation of its own credit or independence, creating a trust gap.

credit association By establishing a credit association relationship between a verifiable related subject and Agent, the credit-dependent party is able to provide a supplementary credit reference to Agent associated credit statements, based on the credit information of the associated subject, for a clear purpose, Scope and for a period of time.

The value of this mechanism is reflected in three main areas:

+ For Agent, associated credit can provide a complementary reference to trust for their involvement in business collaboration when their own credit data are insufficient.
+ For trading opponents, platforms and credit-dependent parties, the verifiable credit association relationship and Agent associated credit statements provide a standardized risk reference base that helps them to make business judgements in the context of their own strategies.
+ For ecology Participants, credit association may be traced to an identifiable associated subject so that linkages, sources of credit, application of Scope and state changes can be recorded, verified and audited.

credit association values depend on associated relationships, Agent associated credit statements, search authorizations and verifiable results for verifiable, retroactive, revocable and independent review.

# List of sub-components and relation
## Component Overview
The sub-section credit association consists of five protocol components, which together complete the full link established at credit association, associated credit generation, life cycle management, search authorization and independent validation.

The functional positioning of the components is as follows.

+ **TSD-CRD-ASC: credit association Create.** The mechanism for establishing the relationship credit association between the related subject and Agent, including the associated prefix, the credit association voucher structure and the associated subject identification and issuance process.
+ **TSD-CRD-MAP: Associated credit mapping.** Regulates mapping rules, source tags and version management between associated body credit statements, credit association vouchers and Agent associated credit statements.
+ **TSD-CRD-LCM:credit association Life cycle management.** Responsible for regulatory mechanisms such as credit association vouchers and Agent associated credit statements, state flow, and suspension, revocation, expiry, replacement and reassessment.
+ **TSD-CRD-VER: Associated credit certification.** Regulate the level of certification, information structure, certification process and cause code for the standardized certification of credit association relationships and associated credit information by third parties.
+ **TSD-CRD-AUTH: Credit search authorization.** Responsible for regulating the authorization mechanisms of associated subjects for the certification of associated credit, including sub-authorizations and platform agency queries.

## Core Object & Identification
credit association uses a standard core set of objects and identifiers to describe key information in the credit association link. The core objects of the subtext and their effects are as follows.

|Object or Identification|Meaning|Mainly Generate Location|Main Use Location|
| :--- | :--- | :--- | :--- |
|Application credit association|Pending confirmation request by associated subject and Agent before credit association|TSD-CRD-ASC|TSD-CRD-ASC|
|Certificate credit association|Proof of credit association relation, association Scope, confirmation mode and status information between associated subject and Agent|TSD-CRD-ASC|TSD-CRD-MAP、TSD-CRD-LCM、TSD-CRD-VER|
|Associated Subject Credit Declarations|Statements of credit ratings, compartmentalities, status or other credit information issued by credit service guidelines to related subjects|Credit providers|TSD-CRD-MAP、TSD-CRD-VER|
|Agent Linked Credit Statement|Validable credit statements issued by a credit provider against a designation Agent based on valid credit association vouchers, associated subject credit statements and map rules|TSD-CRD-MAP|TSD-CRD-LCM、TSD-CRD-VER|
|Associated Credit Map Values|Credit content expressed externally in Agent associated credit statements may be in the form of ratings, compartments, status, limits, multi-dimensional attributes or other structured form|TSD-CRD-MAP|TSD-CRD-VER|
|Credit query authorization|The associated subject allows a specific requesting party or Agent of the Platform to certify the associated credit information within the limits of Scope|TSD-CRD-AUTH|TSD-CRD-VER|
|Credit verification records|Record of results after validation of credit association vouchers, Agent associated credit statements, search authorization and status|TSD-CRD-VER|Credit-dependent parties, follow-up certificates and dispute resolution|

Of these, credit association vouchers are used to demonstrate the link between the related subject and Agent; the associated subject credit statements are used to express the credit information of the related subject; and Agent associated credit statements are used to express the relevant credit information based on the association and the related subject's credit information Agent.

The associated credit map SHALL clearly marks its credit source `ASSOCIATED_CREDIT` and may not be expressed as Agent its own independent credit or reputation.

## Dependence and Cross-domain Reference
credit association sub-sections can be quoted as required by Authorization & Delegation Domain, Commerce Interaction Domain and Payment Services Domain. Commerce Interaction Domain may refer to the results of the associated credit certification at the point of entry to the transaction, the choice of the counterparty, and Payment Services Domain may refer to the results of the associated credit certification at its risk management, level strategy or unusual treatment.

Linked credit certification results are entered only as risk reference or business decision-making, and may not be extended, modified, covered or replaced by Authorization & Delegation Domain authorized boundaries, nor may they be a substitute for the payment authorization, account verification, anti-fraud, anti-money-laundering or other independent risk control required by Payment Services Domain.

# TSD-CRD-ASC: credit association Create
## Overview
TSD-CRD-ASC Establishment to define the relationship between the related subject and Agent, including the associated pre-condition, the standard structure of credit association vouchers and the associated subject identification and issuance process.

This component is the logical starting point for sub-section credit association. Once the associated subject has completed the identification, relationship verification and confirmation through this component, the issuer of credit association produces a certified credit association certificate, which provides the basis for subsequent associated credit mapping, life-cycle management and independent validation.

## Participants and prefix
This component covers the following Participants: associated subject, Agent, credit provider and credit association certificate issuer.

+ The subject of association is a natural person, legal person or other organization having a development, deployment, operation, control, liability or other empirical link to Agent;
+ Credit service providers assume responsibility for the identification of related subjects, the verification of relationships and related credit services;
+ The issuer of credit association certificate is responsible for the generation and issuance of credit association certificate;
+ The credit provider and the issuer of the credit association certificate may be the same entity or may be borne separately by different entities.

Before entering this component, SHALL satisfies the following preconditions:

+ The identity of the subject concerned can be verified by the credit provider;
+ (a) Agent with a decipherable identifier, as well as identification documents, control materials or equivalents that can be used to verify the connection;
+ The subject(s) can provide evidence of their association with Agent;
+ credit association in the application SHALL identifies the relevant subject, Agent, the relevant role, the applicable purpose, the application of Scope and other necessary restrictions.

SHALL provide control material or equivalent proof that matches its control Scope when the associated subject declares that the associated actor is the controller, operator or other actor involved in physical control. SHALL provide evidence that matches its declared role when the associated subject is the developer, the deployer or other non-controlled actor.

## Process Steps
**Step 1: Initiate credit association application**

Associated entities initiate credit association applications to credit providers and submit identifications, relevant identification documents or supporting material, associated roles, purpose of use, application of Scope and re-entry elements to be associated with Agent.

The credit provider performs a preliminary verification of the application, confirms that the application is complete, that the request has not been re-issued, and generates credit association applications pending confirmation.

**Step II: Verification of the identity and relation of the relevant subject**

The credit provider carries out an identification check of the applicant at credit association to confirm that his/her identity is consistent with the alleged affiliation.

Credit providers SHALL further verify the connection of the related subject to Agent, including but not limited to the associated role of development, deployment, operation, control or other declaration. After the linkage verification, the associated subject SHALL further confirms the information to be associated with Agent, the associated role, the applicable purpose, the application of Scope, the validity period, the means of searching for authorization and the manner of revocation.

**Step 3: Generate credit association certificates to be issued**

The credit service provider produces the associated credit statement in relation to Agent in accordance with the associated credit map rules specified in `TSD-CRD-MAP`, based on the credit association application verified and confirmed by the related subject.

The credit provider SHALL shall notify the issuer of credit association certificates of the resulting Agent associated credit statements, as well as of the confirmed related subject ' s association information with Agent, the applicable purpose, the application of Scope, the confirmation of the relationship statement and the confirmation material, for the production and issuance of credit association certificates.

**Step 4: credit association Certificates issued**

credit association certificate issuer SHALL produces credit association certificate according to the certificate structure defined in Section 3.4, based on the certified credit association application, the associated entity confirmation results and the associated credit statement Agent generated by the credit provider.

credit association The issuer of the certificate shall sign the key field of the certificate. The reference to the associated subject ' s credit statement, the associated credit map value, the map rule identifier and version of the certificate, SHALL be consistent with the Agent associated credit statement generated by the credit provider.

Upon the issuance of the credit association certificate, it will be placed in the state of `ACTIVE`. credit association certificate issuer SHALL provide credit association valid certificate to Agent or its trustee for subsequent associated credit mapping and associated credit validation scenes.

## credit association voucher structure
The credit association voucher contains the following fields.

|field syntax|Existence|Annotations|
| --- | --- | --- |
|Certificate Identification|Required|credit association certificate unique identification|
|Certificate Version|Required|Document structure version currently in use|
|credit association Request for identification|Required|credit association application pointing to this document|
|Mark Agent|Required|Mark the current credit association corresponding to Agent|
|Associated Subject Identification|Required|Identify the relevant subject of the current credit association|
|Associated roles|Optional|The role of the associated subject in relation to Agent, such as the developer, the deployer, the operator, the controller, the responsible subject or other defined role|
|Issuer identifier|Required|Current identity of issuer of credit association|
|Reference to Agent|Required|Identification document, control material, supporting documents or references to equivalent material to verify the connection between the subject and Agent|
|Related Subject Recognition|Required|`DIRECT_SIGNATURE` or `ATTESTED_CONFIRMATION`|
|Associated Subject Credit Statement Reference|Conditionally required|Need to provide associated credit information, pointing to the related subject ' s credit statements|
|Associated Credit Map Values|Required|Linked credit expression after mapping to Agent, which may take the form of ranking, partition, state, limit, multi-dimensional properties or other structured form|
|Associated credit source tags|Required|Identification of associated credit sources, with value `ASSOCIATED_CREDIT`|
|Map rule identifier and version|Required|Map rules and versions used to identify associated credit mapping values|
|Statement of confirmation of association|Required|Confirmation of the connection of the subject to the designation Agent, the associated role, the purpose of application, the application of Scope and the boundary of responsibility|
|Purpose of application|Required|credit association Allowed for business purposes|
|Application Scope|Required|credit association Applicable scene, type of transaction, type of requesting party or other restriction|
|Public key controlled by associated subject|Conditionally required|The confirmation method is `DIRECT_SIGNATURE` required to verify the inner layer signature of the associated subject|
|Associated body signature value|Conditionally required|Confirmation by `DIRECT_SIGNATURE` required, i.e. associated body inner layer signature value|
|Associated Subject Signing algorithm|Conditionally required|Identification by means of `DIRECT_SIGNATURE`, identifying algorithms and versions of signatures in the inner layer|
|Time of issue|Required|Document Generation Time|
|Entry into force time|Required|Validation time of document|
|Expiry Time|Optional|Validation time of certificate|
|Status Query Information|Required|Quoted or Equivalent Information for Querying the Current Status of the Document|
|Presequenced voucher references|Optional|Forward sequence when association replaces, renews or association supports rotates|
|Signing value of certificate issuer|Required|External signature value of credit association certificate issuer to key field of certificate|
|Credential issuer signature algorithm|Required|Identifies the algorithm and version used for the outer signature|

Of these, the associated subject credit statements, the associated credit map value, the map rule identifier and the version constitute the three traceable elements of the associated credit map.

### Related Subject Recognition
The two approaches SHALL have the same core semantics: the associated entity clearly knows and agrees to establish credit association with the designation Agent, confirming that the results may not be diverted to other Agent, other associated subjects, other purposes, Scope or other credit association applications.

+ **DIRECT_SIGNATURE**: The associated entity uses its controlled private signature key to sign credit association directly to the key element. credit association The issuer of the certificate verifies the internal signature of the associated subject and then signs the credit association certificate externally with its own private signature key. In this way the certificate has two layers of signature.
+ **ATTESTED_CONFIRMATION**: The related subject completes the identification and cross-identification by the credit provider, and the certificate is issued by the credit association issuer on the basis of the credit provider's confirmation.

### Signature data Scope
Under `DIRECT_SIGNATURE` confirmation, the associated subject shall sign the credit association application and its confirmation at the inner level.

+ Internal signatures SHALL cover, at a minimum: credit association application marking, Agent identification, associated subject identification, associated role, references to association evidence, association confirmation statements, associated credit mapping information, applicable purpose, application Scope, validity period, issuer identification and re-discharge protection elements.

Regardless of the means of confirmation, the issuer of the credit association certificate shall sign the document at the outer level.

+ The external signature SHALL cover the identification of the certificate, the version of the document, the issuer ' s identifier, the identification of the associated subject, and all core fields in the credit association certificate except for status information, signature information and the reference to the pre-certificate; and SHALL also covers the public key information required for the internal signature of the associated subject and its authentication under `DIRECT_SIGNATURE`.

The certificate ' s current status, status query information, pre-certificate references, external signature values and outer signature algorithms do not participate in the outer signature data Scope. The current status SHALL be maintained separately by the State Machine system referred to in the status query information; the state flow SHALL NOT invalidates the certificate signature and SHALL corresponds to the status management mechanism `TSD-CRD-LCM`.

## Processing of requests
The credit provider SHALL certifies the validity of the material in relation to the related subject and Agent and prevents another person from initiating an application credit association on the basis of unauthorized Agent identity, controlled material, associated role or subject.

The correlation certification includes the following scenarios:

+ **Initial Authentication** At credit association application stage, the applicant is identified as true and relevant, and there is a correlation between the applicant and Agent that matches his declared role; only after certification can the relevant subject confirm and issue the certificate.
+ **Continuous revalidation** SHALL triggers a re-certification when the associated certifying material is rotated, controlled material changes, key leak signs are identified, Agent operating subject is changed, the associated subject is in an abnormal state of identity or has reached the pre-set re-certification cycle.
+ **Unusual disposal**: credit association certificate SHALL transferred to `SUSPENDED` or `REVOKED` at `SUSPENDED` or at `REVOKED` when a re-certification has not been made, or when a credit provider finds that the association is likely to lapse, is forged or exceeds the declared Scope.

The results of the confirmation by the associated subject may not be diverted to other Agent, other related subjects, other associated roles, other purposes, other applicable Scope or other credit association applications.

The link in the certificate confirms the associated role, link SHALL identified by the related subject, the purpose of application and the application of the boundary, and may not be empty or use vague and potentially misleading statements. The link confirmation statement is used only to prove that the relevant subject ' s confirmation of the credit association relationship and its use Scope does not constitute a commitment to the result of the transaction, payment, performance or other business conduct Agent.

SHALL issues new credit association certificates and establishes a link by reference to prior documents when the related subject, Agent, associated role, supporting information, confirmation of association, associated subject credit statements, associated credit map values, mapping rules, applicable purpose, application of Scope or a material change of validity.

# TSD-CRD-MAP: Associated credit mapping
## Overview
TSD-CRD-MAP (Associated Credit Mapping) is used to specify map rules for associated subject credit statements to Agent associated credit statements.

This component sets out the requirements for standardization of the associated credit mapping process and the expression of Agent associated credit statements and associated credit mapping values; it does not specify the specific mapping rules themselves. The specific mapping rules are self-fulfilled by credit providers according to their credit model, risk strategy and business requirements.

This component is quoted in the credit association voucher issuance process at `TSD-CRD-ASC`. The credit provider converts the associated subject's credit statement to Agent associated credit statements in accordance with applicable map rules, and provides the associated credit map value and associated map information to credit association certificate issuer as the basis for the generation of the relevant credit information in credit association certificate.

## Participants and prefix
This component involves the following Participants: credit provider, and credit association certificate issuer.

Before entering this component, SHALL satisfies the following preconditions:

+ The associated subject has completed the identification check and confirmed the application credit association;
+ The link between the subject and Agent has been verified by the credit provider;
+ A credit service provider has obtained a credit statement of the relevant subject or a verifiable reference;
+ The necessary information has been identified in the application credit association, related subjects, associated roles, applicable purposes, application Scope and duration.

The credit provider SHALL completes the associated credit map before the credit association certificate is issued and provides the results to the credit association certificate issuer.

## Associated Subject Credit Declarations
The associated subject credit statement is the credit information statement provided by the credit service approach to the related subject and is the input basis for the associated credit map.

Credit services are able to determine the content of the related subject’s credit statements, the manner of disclosure and access controls based on applicable data protection, privacy protection and business rules.

The associated subject credit statement SHOULD contain the following metadata:

+ (b) Declaration marking;
+ (a) The version of the declaration;
+ (b) Credit service provider identification;
+ (a) The time of issue;
+ (a) Duration;
+ Signature or equivalent.

The credit content of the credit statements of associated subjects, such as rank, spacing, amount, state, multi-dimensional rating or other credit attributes, is issued by the credit service provider in accordance with its credit model.

## Associated Credit Map Rules
This sub-section does not prescribe rules for a specific associated credit mapping.

The associated credit mapping process SHALL meets the following standardization requirements.

**Map rule identification and version:**

+ Each associated credit mapping rule SHALL have a uniquely identifiable rule identifier and version within Scope management of the credit provider.
+ The map rule identifier and version SHALL be carried on credit association vouchers to identify which map value is generated by. When the map rule is iterative, adjusted or replaced, SHALL update the rule version. The associated credit map values generated by different rules or versions are not directly compared, converted or explained without the rule identifier and version information.

**Retroactive:**

+ The associated subject credit statement quotes, the associated credit map value, the map rule identifier and the version together constitute the three traceable elements of the associated credit map.
+ The associated credit map value SHALL be the result of a specified map rule and version that acts on a given associated subject's credit statement. The three elements SHALL be able to be traced back to be saved and validated with credit association vouchers, without which the associated credit map value may not be used as a relevant credit information that can be interpreted, compared or used independently.
+ credit association The issuer of the certificate, when issuing the certificate, verifies the integrity and consistency of the three elements retroactively.

**Limitations on credit privileges:**

+ Associated credit may not directly inherit Agent the full credit authority, credit line, creditworthiness or other business qualification of the related subject.
+ Credit service providers should set a ceiling or boundary for the use of the associated credit map that is independent of the related subject ' s own credit, and identify the relevant credit information that can be consulted at Scope, taking into account the associated role, the applicable purpose, the application of Scope, the duration of the period and other risk limits.

## Agent Associated credit statements and associated credit mapping values
Agent Associated Credit Statements are credit statements generated by credit providers against designated Agent based on valid credit association applications, associated subject credit statements and associated credit mapping rules.

Agent Linked credit statements are expressed by associated credit mapping values, source information, map basis and use of boundaries.

+ **Associated Credit Map Values**: Generated by this component to express the results of the credit mapping associated with the designation Agent, which may be in the form of ranking, partition, state, limit, multi-dimensional properties or other forms.
+ **Source Information**: Includes references to related subject credit statements and associated credit source tags. The associated credit source tag SHALL be `ASSOCIATED_CREDIT` and may not be labelled Agent as independent credit or independent reputation.
+ **Map Source**: Includes map rule identifiers and versions, which are used to identify the mapping rules used to generate associated credit map values.
+ **Use boundary**: Includes the purpose of application, the application of Scope, the duration of application and other necessary restrictions.

The specific data structure of the associated credit map value is defined by the credit provider according to its credit model. The sub-section does not provide for a uniform data structure. The associated credit map value, regardless of the expression, is SHALL to meet the three retroactivity limits and cannot be interpreted independently from the reference and map rule logo and version of the related subject ' s credit statement.

# TSD-CRD-LCM:credit association Life cycle management
## Overview
TSD-CRD-LCM (Credit Association Lifecycle Management) is used to specify the life cycle of credit association vouchers State Machine, state flow rules, and regulatory mechanisms such as suspension, revocation, expiry, replacement and reassessment.

This component ensures that the associated subject can revoke credit association and that credit services can trigger suspension and reassessment in the event of a change in the credit statements of the related subject, change in the association relationship, or risk event. credit association When the core field of the voucher changes, SHALL NOT covers the original document, while SHALL issues a new credit association certificate and establishes a prior certificate reference to ensure that the process is retroactive, auditable and subject to review.

The status of the credit association certificate determines whether the associated credit information it carries can be used for subsequent association credit certification.

## Participants and prefix
This component involves the following Participants: related subject, credit provider, credit association certificate issuer and credit certification service provider.

Before entering this component, SHALL satisfies the following preconditions:

+ credit association application created or credit association certificate issued;
+ credit association The issuer of the certificate is capable of maintaining or searching for the state of the certificate;
+ Credit service providers are able to identify changes in the credit statements, affiliations or other relevant information of related subjects.

## Life cycle state
The credit association certificate has the following life-cycle status.

|Status|Meaning|
| --- | --- |
|`PENDING`|credit association application has been created, but the identification of the associated subject, the associated credit map or the issuance of the certificate has not yet been completed|
|`ACTIVE`|credit association vouchers are valid and can be used for associated credit authentication in Scope applicable|
|`SUSPENDED`|credit association vouchers are temporarily suspended and may not result in a new valid associated credit certification result|
|`REVOKED`|The certificate credit association has been revoked and may not be restored to its state of validity|
|`EXPIRED`|credit association certificate is no longer valid and may no longer be used for associated credit certification|

Of these, `SUSPENDED` may be distinguished by the cause of the trigger as the active suspension of the associated subject, the suspension of the risk to the credit provider, or other suspension.

## State flow rules
```plain

                  ┌─────────────┐
                  │   PENDING   │
                  └──────┬──────┘
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        ┌────────┐  ┌──────────┐ ┌─────────┐
        │ ACTIVE │  │ REVOKED  │ │ EXPIRED │
        └───┬────┘  └──────────┘ └─────────┘
            │  ▲
            │  │
            ▼  │
      ┌───────────┐
      │ SUSPENDED │
      └─────┬─────┘
            ├──────────────► REVOKED
            └──────────────► EXPIRED
```

The permitted state flow is as follows:

+ `PENDING → ACTIVE`: credit association application has completed the identification of the associated subject, the associated credit map and the issuance of the certificate, and the certificate is valid;
+ `PENDING → REVOKED`: credit association application withdrawn or terminated;
+ `PENDING → EXPIRED`: credit association The application exceeds the validity period but does not complete the issuance of the certificate;
+ `ACTIVE → SUSPENDED`: credit association vouchers are temporarily suspended;
+ `ACTIVE → REVOKED`: credit association vouchers have been withdrawn or replaced with new documents as a result of a material change in the associated credit information, association or other core field;
+ `ACTIVE → EXPIRED`: credit association certificate is beyond the validity period;
+ `SUSPENDED → ACTIVE`: return to effect after the reasons for the suspension have been removed;
+ `SUSPENDED → REVOKED`: Confirmation of SHALL withdrawal during suspension, or replacement of original documents with new documents;
+ `SUSPENDED → EXPIRED`: The suspension period exceeds the validity period.

`REVOKED` and `EXPIRED` shall be final and shall not be transferred to another state.

## Suspension and restoration
`SUSPENDED` states can be initiated by:

+ **Associated Subject Active Pause** The associated entity can request the suspension of the credit association voucher for its own needs.
+ **Credit provider risk paused**: The credit service may notify the issuer of the certificate of credit association to suspend the certificate, on the basis of an abnormal credit statement of the related subject, an abnormal association relationship, an abnormal behaviour Agent, failure to certify the association, failure to verify the control material or other risk judgement.
+ **credit association Certificate issuer ' s performance status change** credit association The issuer of the certificate executes the suspension, reinstatement or revocation of the change of status and maintains a record of the change of status in accordance with a valid order of the credit provider or related subject.

During `SUSPENDED`, a credit certification service provider may not produce a new pass result on the basis of the certificate.

## Re-evaluation and replacement of vouchers
The credit provider SHALL triggers a reassessment when the associated subject ' s credit statements, the associated credit mapping rules, the supporting material, the associated role, the applicable purpose, the application of Scope or other core fields have changed that may affect the validity of the associated credit information.

The reassessment process is as follows:

1. The credit service provider identifies changes in the credit statements, affiliations or other relevant information of the related subject and advises the issuer of credit association to suspend the original credit association certificate;
2. Agent Linked credit statements and associated credit mapping values are regenerated by credit service providers based on changed information and applicable map rules;
3. Credit providers judge whether the reassessment results in a change in the core field in the original credit association voucher;
4. If the core field changes, SHALL generate new credit association vouchers as specified in `TSD-CRD-ASC` and quotes the associated document through a pre-certificate;
5. After the entry into force of the new document, the original document SHALL was converted to `REVOKED` status;
6. The original certificate may be restored to `ACTIVE` only if it is re-evaluated that the information on which the original document is based has not changed substantially and the original document has not exceeded the validity period.

The reference to the associated subject ' s credit statement in credit association certificate, the associated credit map value, the map rule identifier and version, the link certificate, the associated role, the purpose of application, the application of Scope and the validity period are all core fields.

During the reassessment period, the original certificate is in `SUSPENDED` state and the credit certification service may not produce a new `PASS` certification result on the basis of the certificate.

## Undo
A credit provider or a credit association issuer of a certificate may revoke credit association documents at any time.

The revocation is the irreversible act of the certificate level. After the revocation, the certificate SHALL enters the state `REVOKED` and may not be restored to the state of validity.

After the original certificate has been withdrawn, the associated subject may re-initiate the application credit association; when re-established credit association, SHALL generate a new credit association voucher and can be quoted as having been withdrawn by reference to the previous document.

After the revocation takes effect, the credit certification service may no longer produce a new `PASS` authentication result based on the certificate. The resulting historical certification record SHALL retains the certificate status and authentication results at the time of its creation, but the searcher SHALL be able to recognize that the document has been revoked at a later point.

# TSD-CRD-VER: Associated credit certification
## Overview
TSD-CRD-VER (Associated Credit Assistance) provides a mechanism for credit relying parties to perform standardized verification of agentcredit association relationships and associated credit information, including certification levels, certification processes, certification requests and responses to submissions and standard cause codes.

Validation is divided into two levels:

+ **Association Relationship Verification:** Validate the integrity of the credit association credential's signature, the associated subject's confirmation, and the validity of its current status;
+ **Association Credit Information Validation**: Further query and verify the current validity of the associated subject's credit statements and associated credit mapping information on the basis of credit association certificate authentication.

Credit association credential verification does not involve querying the associated subject's credit information and therefore does not require credit query authorization. Verification of associated credit information involves querying or confirming the associated subject's credit statement and SHALL obtain valid credit query authorization from the associated subject; see `TSD-CRD-AUTH` for the specific authorization rules.

A credit-dependent party SHALL make business decisions independently of its own rules.

## Participants and prefix
This component involves the following Participants: credit relying party, credit certification service party, credit association certificate issuer, credit service provider.

Before entering this component, SHALL satisfies the following preconditions:

+ credit association vouchers issued;
+ Credit-dependent parties are able to provide Agent identification to be validated and credit association vouchers or their references;
+ The credit certification service provider is able to obtain authentication material and status information from the issuer of the credit association certificate;
+ When performing the authentication of the associated credit information, the credit-dependent party has obtained a valid credit search authorization for the related subject.

## Validation process
### Credit Association Credential Verification
Credit certification service providers SHALL perform the following:

1. (b) Validation of the version of the request, the required fields, the marking of the request, the time of the request and the elements of protection against redundancies;
2. Validation of the identity of the party relying on credit and proof of claim;
3. Obtaining credit association certificates to verify the validity of credit association signatures issued at the outer level;
4. Validation of the inner layer signature of the associated subject under `DIRECT_SIGNATURE` confirmation;
5. Validate the Agent identifier in the credit association certificate, the associated subject identifier, the associated role, the purpose of application and the application of Scope for consistency with the present request;
6. (a) Query the certificate status query and confirm that credit association the certificate is in `ACTIVE`;
7. Validates the integrity of the associated credit map information, such as references to associated subject credit statements, associated credit map values, map rule identifiers and versions, and is consistent with the records in credit association vouchers.

The credit association certificate certification does not require the credit certification service provider to recalculate the internal mapping model of the credit provider, nor does it require it to obtain the original content of the associated subject credit statement.

credit association Certificates shall not return to `PASS` and shall not enter the associated credit information authentication if any critical step fails.

### **Association Credit Information Validation**
The associated credit information verification SHALL be implemented after the certification of credit association certificates.

1. Validation of credit query authorization is currently valid;
2. (a) To inquire of credit service providers or confirm that the related subject ' s credit statements are currently valid and have not been revoked, corrected, replaced or marked as invalid;
3. (a) Verifying that the map markings and versions recorded in credit association certificates are still identifiable and applicable;
4. Confirms that Agent associated credit statements and associated credit map values remain operational;
5. (b) The content of the response is tailored in accordance with the minimum disclosure principle and authorized data items and returns only those data items that are necessary and mandated for this validation;
6. Generates a certificate of response to the certification results and keeps a record of the certification.

No key step shall be returned `PASS` if it fails.

SHALL return `INCONCLUSIVE` and cannot be substituted by default when insufficient evidence is available or it is not possible to determine clearly whether the certification has been passed.

SHALL return `REVIEW_REQUIRED` when the credit association voucher is in the process of reassessment, the associated credit information needs to be reconfirmed, or the related subject confirms that the strength does not match the strength required by the business.

## Authentication request
The certification request contains the following fields.

|field syntax|Existence|Annotations|
| --- | --- | --- |
|Request for identification|Required|For processing ethos and correlation of results|
|Request for text version|Required|Request for text structure version|
|Credit-dependent party identifier|Required|Credit-dependent party initiating certification|
|Mark Agent|Required|Verified Agent|
|Verification level|Required|Credit Association Credential Verification or Associated Credit Information Verification|
|Associated Subject Credit Statement Reference|Conditionally required|Associated credit information validation required|
|Operational purpose|Required|Purpose for which validation results are used|
|Operational context|Required|Minimum correlation information for order, commission, transaction or risk decisions|
|Data requested entry|Required|Pool of fields, declarations or validation conclusions expected to return|
|Certificate credit association|Required|credit association certificate to be validated or references thereto|
|Request Time|Required|Request generation time|
|Element of protection against redundancies|Required|Random number, quail etc. or equivalent|
|Proof of request|Required|Overwrite signature or equivalent certificate for requested key fields|

## Verify Response
The validation response contains the following fields.

|field syntax|Existence|Annotations|
| --- | --- | --- |
|Request for identification|Required|Correspond to original authentication request|
|Validation record identifier|Required|The only mark on this validation.|
|Mark Agent|Required|Verified Agent|
|Validation level completed|Required|The highest level of authentication actually completed, with a value of credit association certificate authentication or associated credit information authentication|
|Authentication Results|Required|`PASS`, `FAIL`, `INCONCLUSIVE` or `REVIEW_REQUIRED`|
|Reason code|Required|Explanation of validation results|
|Support status credit association|Required|Document 's Current Life Cycle Status|
|Associated credit source tags|Conditionally required|Linked credit information validated and returned with a value of `ASSOCIATED_CREDIT`|
|Associated Credit Map Values|Conditionally required|Linked credit information validation required for authorized return of relevant credit information|
|Validity of associated subject credit statements|Conditionally required|Revert the current validity of the related subject 's credit statement when the associated credit information is verified|
|Map rule identifier and version|Conditionally required|Linked credit information verified and required to return associated credit information|
|Application Scope|Required|This validation is allowed at Scope|
|Result generation time|Required|Validation completion time|
|Due Expiry|Required|Re-validate SHALL beyond that time|
|Status Query Information|Optional|For checking the follow-up status of credit association vouchers or validation results|
|Purpose Limiting Tags|Required|Mark the results of this validation only for specified business purposes|
|Response certificate|Required|Overwrite signature or equivalent proof for key fields|

Response SHALL follows the minimum disclosure principle:

+ credit association voucher validates response SHALL NOT to the original content of the associated subject ' s credit statement or associated credit map value;
+ The associated credit information authentication does not default on the return of the associated subject ' s original identity information, the original content of the related subject ' s credit statement or the internal map basis of the credit service;
+ Fields that exceed the Scope search authorization or the requested data entry Scope are cropped and not returned.

## Standard reason code
|Reason code|Meaning|
| --- | --- |
|`VERIFIED`|The specified authentication level has been passed|
|`INVALID_REQUEST`|Invalid request structure, version or mandatory field|
|`REQUEST_PROOF_INVALID`|The request signature or equivalent proof failed verification|
|`REQUEST_EXPIRED`|Request to exceed allowed time window|
|`REPLAY_DETECTED`|Request for marking or weighting elements have been used|
|`AUTHORIZATION_REQUIRED`|Linked credit information authentication lacked valid credit search authorization|
|`AUTHORIZATION_EXPIRED`|Credit search authorization expired|
|`AUTHORIZATION_REVOKED`|Credit search authorization revoked.|
|`AUTHORIZATION_SCOPE_MISMATCH`|Credit relying party, Agent, certification level, business purpose or data item exceeding delegated authority Scope|
|`AGENT_NOT_REGISTERED`|The Agent identity cannot be resolved or verified|
|`ASSOCIATION_CREDENTIAL_NOT_FOUND`|No credit association credential was found|
|`ASSOCIATION_CREDENTIAL_NOT_ACTIVE`|credit association certificate pending confirmation, suspension, revocation or expiry|
|`ASSOCIATION_PROOF_INVALID`|The credential signature, associated subject's inner signature, or other association proof failed verification|
|`CREDIT_ASSERTION_UNAVAILABLE`|Unable to obtain associated subject credit statements or validity information for authentication of associated credit information|
|`CREDIT_ASSERTION_INVALID`|The associated subject ' s credit statements are invalid, expired, revoked, corrected or invalidated|
|`MAPPING_POLICY_UNSUPPORTED`|Unidentifiable, unsupported or unable to apply map rule identifiers and versions|
|`INCONCLUSIVE`|Insufficient evidence or necessary reliance not available for the time being|
|`REVIEW_REQUIRED`|Need for manual or higher level of assurance|

# TSD-CRD-AUTH: Credit search authorization
## Overview
TSD-CRD-AUTH (Credit Query Assessment) is used to provide a search authorization mechanism for associated subjects for the authentication of associated credit, and only to limit the information search and authentication required for the authentication of associated credit to Scope, which does not constitute an authorization for Agent transactions, payments, performance or other commercial acts.

When a credit relying party performs the authentication of associated credit information, the current validity of the associated subject’s credit statements and associated credit mapping information needs to be sought or confirmed by the credit service provider. The process may involve the related subject’s credit information, so SHALL obtains a valid credit search authorization from the related subject.

## Participants and prefix
This component covers the following Participants: related subjects, credit-dependent parties, credit providers, credit-certification service providers and platform agents.

Of which:

+ The related subject is the authorized person for the credit search;
+ The credit relying party is the subject of a request for the use of associated credit certification results;
+ The credit provider is responsible for maintaining the credit statements of the related subject, the status of authorization or the related search capability;
+ Credit certification services are responsible for verifying authorization and producing certification results during the certification process;
+ The Agent body of the Platform is the subject of the performance or assistance in the execution of the credit query under the Platform proxy query model, with the prior authorization of the associated entity and within the limits of Scope.

Before entering this component, SHALL satisfies the following preconditions:

+ credit association vouchers have been issued and are in `ACTIVE` status;
+ Associated subjects can be validated and have the capacity to make authorization confirmations;
+ The credit relying party has clearly linked the business purpose of the credit certification, the requested data item and the relevant business context;
+ Under the Platform proxy query model, the Platform proxy body has been clearly identified and authorized by the associated subject.

## Elements of a mandate
The credit search authorization SHOULD specifies the following elements:

+ (b) Credit relying party identity: credit relying party identifier allowing requests or the use of associated credit certification results;
+ (a) Platform proxy body identity: the identification of the Platform Agent who is allowed to perform the query or confirmation on behalf of the Platform Agent when using the Platform proxy query model;
+ agentScope: allowed to be marked Agent or Agent Scope;
+ Level of certification: the level of certification to which this authorization applies and the default is the authentication of the relevant credit information;
+ Business purpose: the business purpose for which the results of the associated credit validation are permitted;
+ Data requested: fields, declarations or a collection of validated conclusions that allow search, validation or return;
+ Duration: the time of validity and expiry of the credit search authorization;
+ Frequency limit: the maximum frequency allowed to perform a query or validation during the validity of the authorization; necessary under the Platform proxy query model;
+ Limitations on the use of results: Validation of the result to allow preservation, duration of storage, transmission to other subjects and other necessary limitations.

The credit query authorization SHALL be clearly linked to the related subject, Agent, the level of certification, the purpose of the business and the requested data item and may not be reused beyond the subject, Agent, purpose or data item of the authorization Scope.

## Delegation of authority model
Credit query authorization is divided into sub-authorizations and platform proxy queries. Both models meet the requirements of authorization SHALL to be clear, authorization is verifiable, results are restricted and authorization can be revoked.

### Sub-authorizations
Under the sub-authorization model, each time a credit-dependent party initiates a request for the authentication of a related credit information, the credit-servicing party or the credit-certification service party SHALL notifys the related subject of a sequential confirmation.

The delegation of authority and associated credit information validation was completed in the same interaction and the process was as follows:

1. (b) The initiation by credit-dependent parties of requests for the authentication of related credit information;
2. (b) The credit provider or the credit certification service provider notifys the related subject for authorization confirmation;
3. The associated entity identifies the credit-dependent party, Agent, the business purpose, the requested data item and the time of validity of the inquiry;
4. Credit certification services perform the authentication of associated credit information and return the certification results.

Sub-delegation applies to situations where ad hoc inquiries, high-sensitive inquiries or related subjects need to be informed on a case-by-case basis.

The authorization shall not be diverted to other credit-dependent parties, other Agent, other business purposes, other requests or other authentication scenes.

### Platform Agent Query
In the Platform proxy query mode, the associated entity pre-authorizes the designation of the Agent of the Platform to perform or assist in the performance of the associated credit query on behalf of Scope and within a limited period of time.

The associated subject SHALL explicitly authorizes the following:

+ (a) Acting body of the Platform;
+ Verifiable agentScope;
+ Validation level, default for associated credit information authentication;
+ Credit-dependent parties or permitted credit-dependent parties Scope;
+ Operational purpose;
+ Data items requested;
+ Frequency limits;
+ (a) Duration;
+ Restrictions on the use of validation results.

The frequency limit SHALL be expressed in machine-readable measurements such as `max_requests_per_window` and `window_duration` to avoid any ambiguity as to whether the number or frequency of queries exceeds the authorized Scope.

Each time a Platform Agent executes or assists in carrying out a query, SHALL carries the operational context and validates the identity of the Platform Agent, the status of the authority, the authority Scope and the consistency of the request.

A Platform Agent may no longer perform a new valid associated credit information authentication based on the associated entity’s withdrawal of the authorization. A Platform Agent may not use search capabilities, validation results or authorization to quote scenes other than those used for the purpose of the authorization, or transfer authorization to an unauthorized third party or provide information beyond the authorization Scope.

## Processing of requests
Credit queries are authorized to process SHALL the following requirements:

+ The credit provider or credit certification service SHALL maintain the authorized status and verifies that the authorization is currently valid and covers the current certification request at each time the relevant credit information is validated;
+ SHALL Identify the Agent of the Platform, the credit-dependent party Scope, Agent Scope, the business purpose, the requested data item, frequency limits, the validity period and the limitations on the use of the results; the Agent of the Platform SHALL verify that the request is not in excess of the authorization Scope at each query or validation;
+ The credit provider SHALL return only the associated credit information in the authorized Scope and necessary to satisfy the purpose of the business, in accordance with the minimum disclosure principle;
+ Credit relying parties, credit providers, credit certification service providers and Platform agents shall not use the results of the certification for scenarios other than the authorized purposes or disclose information beyond the authorized Scope to an unauthorized third party.

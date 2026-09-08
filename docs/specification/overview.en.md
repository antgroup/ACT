# ACT 2.1 Protocol Overview

[中文](overview.md) | English

# Introduction
In the Internet business phase, which is dominated by information retrieval and page browsing, User is the direct implementer of business decision-making and payment. The transaction takes place between User and the business platform, User in real-time viewing of the goods, clicking on the list, and confirming payments on a case-by-case basis through interface. This premise is changing with the deep penetration of AI Agent technology. Agent Starts on behalf of User service discovery, commodity price, transaction negotiation and even payment execution, User from "real-time operator" to "target setr and authorized person".

While bringing about efficiency gains, this change has also brought about confidence challenges that traditional business and payment systems need to face and address:

+ First, in agentic commerce, the subject of the transaction is separated. User is responsible for proposing objectives and constraints, Agent is responsible for implementing decision-making and operations, Merchant and Payment Service Provider are seen as proxy requests for transactions; “who wishes, who operates, who is responsible” is no longer as natural as traditional e-commerce.
+ Second, the transaction is based on a change from User real-time confirmation to User ex post facto authorization, Agent ex post facto execution. This means that the system not only answers whether a transaction has been successful, but also whether it is within the original authorized boundary User, whether it has been faithfully implemented user intent, and whether the results of the execution can be traced and explained.
+ Finally, the efficiency of implementation Agent may result in a significant increase in transaction numbers and transaction complexity, with corresponding disputes, audits, and risk-control pressures being magnified simultaneously. Traditional manual review-by-hand processing will make it difficult to adapt to scalable Agent transactions, and commercial systems will require standardized recording and certification mechanisms that can be automated.

In any case, agentic commerce does not create a single chain of security, but rather an overall migration of the basis of trust in transactions: trust is no longer based on the natural premise of “real-time human presence”, but must be clearly established through a mechanism of protocols that can be expressed, communicated, verified and traced.

ACT (Agentic Commerce Trust Protocol, Agentic Commerce Trust Protocol) is a set of application-level trust protocols designed to address the above-mentioned challenges, covering the full commercial chain from user intent expression, authorization and delegation, commerce interaction payment execution to trusted attestation. ACT does not replace the existing payment network, Merchant system or identity infrastructure, but rather provides a layer of trust organization for the agentic commerce scene, enabling each Participants to achieve delegation of authority, consistency of transactions, payment control and enforceability within the framework of a unified protocol.

This document, which is the ACT protocol outline, defines the protocol ' s Scope boundary, birth background needs, Design Goals and Principles, Overall Framework, Participants role and terminology system and is the top reference document for each domain specification document.

# Scope
This Protocol is directed towards the scenario of Agent engaging in commercial transactions and regulates the level of trust and collaboration between User, Agent, Merchant, Payment Service Provider and related Trust Service Provider for the completion of authorized, enforceable and verifiable commercial transactions.

This Protocol regulates, inter alia, the following four types of protocol activities:

+ authorization and delegation: an act of protocol formed around the boundaries of expression, delegation of enforcement powers and their effects user intent.
+ commerce interaction: The act of protocol that occurs around the discovery of goods or services, the confirmation of terms of trade and the commercial consensus before payment.
+ Payment execution: an act of protocol occurring around payment evidence use, payment request initiation, payment result return and its alignment with upstream authorization and transaction confirmation.
+ trusted attestation: Actions in support of protocols that occur around the recording of key business events, the execution of fact-checks and subsequent disputes.

This Protocol does not regulate the following:

+ Specific interactive experiences between Agent and User are achieved, including the front-end interface, the natural language dialogue approach, the introduction project and the tasking strategy.
+ Commercial Participants own operating regulations, including commodity pricing, inventory management, order performance, after-sale processing and other operational details.
+ Rules for the liquidation and settlement of funds for the base payment infrastructure.
+ The internal risk control model, the anti-fraud algorithm and the internal audit strategy within the participating agencies.
+ Details on the realization of technologies that are not directly part of the application layer of confidence and collaboration, such as ground-level communications transmission, infrastructure deployment, system transportation and other technologies.

# Trust Requirements for Agentic Commerce
The core needs in ACT are grouped into four categories: authorization and delegation (R1), commerce interaction (R2), payment services(R3) and trust services (R4). The four categories of needs correspond to Agent, respectively, why they represent User actions, how to develop a common understanding of transactions, how to complete payment implementation and how to validate implementation results.

Together, these four types of requirements form the basis of the design of the protocol ACT and delineate the four subsequent capability areas.

![](../assets/specification/act-2.1-trust-requirements.png)

**authorization and delegation Requirements (R1)**

+ The need for authorization and delegation addresses how user intent can be reliably expressed and serves as a uniform basis for subsequent business behaviour.
+ Under User real-time presence, a structured expression of intent helps to support subsequent commodity matching, transaction negotiation and confirmation of payment; under User non-real-time presence, this expression further forms the basis of the mandate Agent for self-execution. The core consists of two points: user intent authorization and delegation per se SHALL be credible, and SHALL intent and authorized boundary SHALL be able to be structured to support transmission, understanding and validation of the follow-up.

**commerce interaction Requirement (R2)**

+ The need for commerce interaction addresses how Agent can efficiently and accurately match and interface user intent with goods or services.
+ This could be achieved by providing structured catalogues of goods or services to Agent, Agent passing Intent Context to Merchant side, or by combining them with more effective matching mechanisms. On this basis, there could also be interaction between Agent and Merchant around the process of asking for quotations, inventory confirmation, confirmation of terms and synergy of services.

**payment services Requirement (R3)**

+ The need for payment services addresses how the transaction results are translated into payments that meet the intent of User and that can be confirmed in User authorized Scope.
+ This category covers both the recognition of payments in real-time presence at User and the recognition of payments at User, initiated within the pre-established authorized boundary at Agent. At the same time, as collaboration between Agent increases, protocols also need to fit new payment scenarios such as Agent high frequency, autonomous small payments, etc.

**Trust service requirements (R4)**

+ Trust service requirements are directed towards confidence-building, certification and governance-related matters in agentic commerce, which may include, inter alia, transaction certificates, identity management, reputation management, and credit association.

# Protocol Design Goals and Principles
## Design Goals
Based on the analysis of Trust Requirements in Chapter 3, ACT is expected to achieve the following objectives at the level of protocol.

+ **user intent may be expressed:** User Objectives, constraints and preferences in commercial activities can be expressed in a structured manner and serve as a common basis for follow-up commerce interaction, implementation of payments and validation of results.
+ **The authorized borders may specify:** The authority Agent to act User can be clearly defined and communicated, identified and verified in the follow-up process to avoid the implicit extension or abuse of the authorization Scope.
+ **The transaction process can be linked to:** From user intent, commerce interaction to payment execution, key links in the chain of transactions can be kept consecutively, enabling Participants to form a common understanding of the same transaction.
+ **Payable to implement appropriate:** The protocol supports payment requirements in different scenarios, such as User presence, User absence and Agent autonomous payment between Agent, and enables payment result compliance with User payment intent and authorization Scope.
+ **Key results can be validated by:** Critical events in business activities can provide a verifiable and retroactive record that provides a basis for dispute resolution, audit and subsequent governance.

Together, these objectives form the overall orientation of the design of the ACT protocol, starting with user intent, subject to authorized boundaries, with trade links and payment execution as the main link, with the result being validated as a trust loop.

## Design Principles
ACT for the Protocol Design Principles as follows.

+ **Compatibility:** The protocol takes fully into account compatibility with existing commercial and payment infrastructure and prioritizes the use of designs coordinated with existing standards, interfaces and security mechanisms to reduce access and eco-refitting costs.
+ **Progressive evolution:** Given that agentic commerce is still in the process of sustainable development, protocol-building does not require a step-by-step approach, but a step-by-step refinement and upgrading based on industrial practices and landscape needs to avoid excessive advance design.
+ **Open:** The protocol does not bind a particular manufacturer, platform or technology warehouse, supports multiple modes of realization and multiple types of service provider access, and guarantees different ecological Participants interfaces under open conditions.
+ **Inclusiveness:** The protocol may refer to, absorb or accommodate other mature open protocols on specific modules, avoid duplication of construction and avoid creating a fragmented system of protocols.
+ **Portability:** The protocol maintains a combination of modular design features and minimizes unnecessary hidden reliance to support flexible combinations and independent evolution in different scenarios.
+ **Security and privacy priorities:** The protocol is designed to take fully into account security controls and privacy protection mechanisms, including, but not limited to, minimum privileges, access controls, encrypted transmissions, identification requirements, etc.
+ **Separation of entity from role:** By virtue of their role in the abstract of functions and responsibilities, a specific operational entity may assume one or more roles according to its own circumstances, thus enhancing the adaptability of the protocol to different business organizational patterns.

# Overall Protocol Framework
## Overall Architecture Diagram
The ACT protocol framework uses the protocol stack structure of the sub-domain organization, consisting of Authorization & Delegation Domain, Commerce Interaction Domain, Payment Services Domain and Trust Services Domain. The domain contains several protocol modules that together support the full chain of expression, trade negotiation, and payment execution and results validation from user intent. The modules are interconnected, and they can evolve independently and be flexible, so ACT is not a single protocol, but a system of protocols for sustainable expansion.

The modules listed in the figure below are the overall component view of the current version of the protocol. The official component name, number, object definition and cross-domain reference relationships for each domain are based on the corresponding domain specification document; the typical use scene for which the protocol is currently oriented can be found in the " Typical scene and business process " document.

![](../assets/specification/act-2.1-protocol-framework.png)

## Four Capability Domains and Primary Protocol Modules
### Authorization & Delegation Domain
**Positioning:** Authorization & Delegation DomainGuidance Principal (i.e. User where the intent is presented in the specific scene and the authority is granted) confers its commercial intent and operational authority on the complete process of Agent in a verifiable manner. It covers the period from Scope to Principal the expression of natural language intent, to Agent the holding of complete validity User Intent Authorization Credential and, accordingly, to represent Principal action in subsequent commerce interaction and payment execution.

**Key protocol modules:**

+ **Intentional acquisition and structured expression:** Regulates the process of receiving, semantic clarification, confirmation and structured expression of Principaloriginal intent, resulting in the Intent Structuring Result that can be cited in the subsequent authorization process.
+ **Issued User Intent Authorization Credential** Regulates the transformation of structured intent into a cross-domain verifiable process of issuance and signature authorization credential.
+ **Intent Authorization Credential Life cycle management** Code authorization credential for full life-cycle flow mechanisms from entry into force, temporary suspension, release from suspension, active revocation to expiry.

### Commerce Interaction Domain
**Positioning**: Commerce Interaction DomainOrdinance Agent and Merchant, Merchant-side Agent or other Agent rules of interaction around the discovery, transmission of intent, content consultation, Payment Capability Negotiation and Cart Confirmation of goods or services. The goal is to achieve an efficient and accurate match and interface between user intent and goods services in a variety of interactive ways.

**Key protocol modules:**

+ **Merchant Catalog Interface**: Regulates Merchant the opening of interfaces to Agent structured goods or service catalogues to support Agent efficient access to information on goods or services.
+ **Intent Context Passage** Code Buyer Agent transmits Intent Context relevant to the current mandate to Merchant or to the platform to support more precise candidate, matching and dynamic pathways.
+ **Cart Confirmation**• Regulate the interactive process between buyers and sellers of confirmation of final commodity lists, amounts and the state of the transaction and preparation for the payment phase.
+ **Interaction between consultations and collaboration on services**: Code Agent interacts with Merchant, Merchant-side Agent or other counterparty regarding consultations and collaboration on transactions. In the current version, this module is reduced to Payment Capability Negotiation, and primarily regulates the ability of buyers and sellers to declare, match and consult with payment method, Payment Service Provider, interface end points and related load modes before payment is made.

### Payment Services Domain
**Positioning** The main interactive process of payment is initiated to Payment Service Provider upon completion of Cart Confirmation. It covers payment request the structure, authorization of verification, execution of transactions, return of results and related status management to support uniform synonyms in different payment scenarios.

**Key protocol modules:**

+ **Payment Method Binding**: Guideline Principal to complete Payment Service Provider capacity to pay and to establish a process for Agent for the use of payment marks or other equivalent payment instrument quotations.
+ **Agent-specific Sub-account Management** Regulates the opening of an exclusive sub-account for a specific Agent and manages its accompanying authentication key and life cycle.
+ **Instant User Payment:** The process of prompt payment, completion of confirmation of payment and receipt of payment result is initiated in Principal real-time presence.
+ **User-directed Delegated Payment:** Code Principal for non-real-time presence, Buyer Agent is based on a valid Intent Authorization Credential process for initiating and accepting Payment Service Provider targeted commissioning.
+ **Autonomous Delegated Payment:** Regulation Principal Unaccompanied scene Buyer Agent for the autonomous conduct of multiple rounds of commercial decision-making and payment under Intent Authorization Credential within the authorized boundary.
+ **Payment access based on HTTP 402 (A402 payment process)** A universal payment access interface based on HTTP 402 between Buyer Agent the seller's service provider and Payment Service Provider can serve as a single access point to the above-mentioned payment scenario components.

### Trust Services Domain
**Positioning:** Trust Services Domain is the confidence infrastructure level of the ACT protocol, which provides confidence services such as trusted attestation, agentcredit association, Agent identity management, Agent reputation management for agentic commerce ecological agentic commerce. Its role is to provide a common trust base for cross-institutional, cross-subject business collaboration and to support dispute management, risk identification and subsequent governance. The current version of the Focus Regulation trusted attestation is related to agentcredit association components, Agent identity management, reputation management, etc., can serve as an extension of the subsequent version.

**Main Protocol Subsections:**

+ **agentic commercetrusted attestation** Regulates the preservation of the record and long-term retention of key node information during agentic commerce interaction to provide an objective and verifiable factual basis for dealing with transactions disputes.
+ **agentcredit association:** The establishment of a Agent relationship with its associated subject credit association, the generation and mapping of associated credit statements, life-cycle management, search authorization and standardized certification provide a verifiable associated-credit reference for Agent when its own credit data are insufficient.
+ **Agent Identity management** Agent capacity for registration, authentication and analysis of identity for participation at commerce interaction, supporting the verification of identity and legality of the transaction at Participants.
+ **Agent Honorary management** To regulate the multi-dimensional evaluation and ongoing tracking of historical behaviour in Agent, provide a searchable basis for the credibility of the transaction Participants and support governance and restraint of the breach Agent.

# Protocol Participants
## Primary Participants
### Principal
Principal is the author of the commercial intent and the authorized source of Agent commercial activity on its behalf.
Principal is responsible for expressing its own transaction objectives, constraints and preferences, and for confirming the intent or result, if necessary. Principal may also be directly involved in key points such as confirmation of payment in a real-time scenario.

### Agent
Agent is the core executive role in the protocol to receive the intent and authorization of Principal and to complete subsequent business operations on behalf of Principal in the authorization Scope.
Depending on their location and responsibilities, Agent may be shown as Agent side Agent, Merchant-side Agent or as an automated executive with other Agent directly interacting in a given scene.
Agent may be involved in the process of interpretation of intent, transmission of information, matching of goods or services, negotiation of transactions, Cart Confirmation, initiation of payments and return of results.

### Merchant or Service Provider
Merchant or Service Provider is the provider of goods, services or performance capacity and the provider of business in interaction agentic commerce.
Its main functions include opening the catalogue of goods or services, responding to Intent Context, participating in transaction consultations, confirming the outcome of the transaction and fulfilling the corresponding service or delivery obligations upon completion of the transaction.
In part achieved, Merchant or Service Provider could also deploy its own Merchant-side Agent to participate in automated interactive processes.

### Payment Service Provider
Payment Service Provider is Participants for capacity to pay to provide and execute transactions for the purpose of carrying payment request, completing authorization to verify, executing payments and returning payment result. Its duties may include Payment Method Binding, immediate payment processing, commissioning payment processing, Agent payment support and related status management.
Payment-related payment proof, special sub-accounts or other payment base capabilities may be provided either by Payment Service Provider itself or by the associated professional service module.

### Trust Service Provider
Trust Service Provider is Participants to provide identification, documentation, certification and related governance support capacity.
In the current version of the protocol, the focus of its responsibilities is on key event certificates, signature verification, chain anchoring inquiries and dispute resolution support.
Given the wide coverage of this type of service Scope, the current version of the protocol describes it as a uniform classification. As the protocol evolves and the industry division of labour is refined, the capacity can then be further broken down into more detailed service roles or types.

## Participant Relationships
In a typical scenario, Principal first expresses its intent and completes its authorization to Agent, then commerce interaction undertakes commerce interaction with Merchant or Service Provider and initiates payment request with Payment Service Provider when payment conditions are in place; the key results can be Trust Service Provider to provide documentation, validation or other trust support services. This relationship reflects the basic synergy links from ACT, authorization and delegation, commerce interaction, payment implementation to trust service support.

It should be noted that each Participants in this protocol is based on an abstract function and responsibility and does not foresee a correspondence between it and a specific operational entity. The same entity may assume one or more of the agreed roles under the operational model, and the same agreed roles may be assumed by different entities. Protocol Participants The division is mainly used to clarify the functional positioning, interaction and boundaries of responsibility of the parties in the ACT link, rather than to define the way in which the specific organization operates.

# Terms and Normative Language
This chapter provides a uniform description of the core terms and normative expressions used in the ACT protocol, with a view to reducing differences in understanding between the different chapters and providing a consistent language base for the subsequent domain-specific rule descriptions.

## Terminology
This chapter defines only the basic terms used for cross-domain overlap, with more detailed fields, status and reporting terms, which can be further refined in the corresponding domain document.

|Terminology in Chinese|Terminology English|Explanation of terms|
| :--- | :--- | :--- |
|user intent|User Intent|Principal Objectives, conditions, preferences and related binding information in a business activity.|
|authorization credential|Authorization Credential|Proof used to carry and express the authorized relationship and its boundaries and for subsequent identification and verification.|
|commerce interaction|Commerce Interaction|Interactive process around the discovery of goods or services, transmission of intent, negotiation of transactions, Cart Confirmation, etc.|
|Transaction confirmation|Transaction Confirmation|(b) The process by which the buyer and the seller agree on the list of goods or services, the amount of money and the terms of the related transactions.|
|Payment execution|Payment Execution|(c) Initiate a process of payment request, complete authorization to verify, execute payments and return to payment result where payment conditions are in place.|
|trusted attestation|Trusted Attestation|The recording, validation and retention of critical events or results in a business activity in support of dispute resolution, audit and ex post facto traceability.|
|Cross-domain operational information|Cross-Domain Business Information|Business information transmitted, quoted or validated on an ongoing basis between authorization and delegation, commerce interaction, payment services and trust services.|

## Normative Language
This Protocol adopts the following Normative Language:

+ “SHALL (SHALL)” denotes a requirement that must be met;
+ “SHALL NOT (SHALL NOT)” denotes requirements that must be avoided;
+ “SHOULD (SHOULD)” indicates the recommended requirements;
+ “SHOULD NOT(SHOLD NOT)” indicates the requirement to be avoided;
+ “may” indicates an optional requirement.

Existing protocol on the field:

+ The word “necessary” indicates that the field must exist and have a valid value;
+ (a) “Conditions must” means that they must exist and have a valid value at the time the particular condition is established;
+ “Optional” indicates that the field is allowed to exist and that the value must be valid at the time of its existence.

## Editorial Conventions
In order to maintain consistency throughout the text, this Protocol provides for the following common formulations in part:

+ In the overview section of the protocol, use such role expressions as “Principal “Agent” “Merchant or Service Provider” “Payment Service Provider” “Trust Service Provider”.
+ In the context of the specific domain rule, a formulation such as “Buyer Agent” “Merchant-side Agent” “Payment Service Provider” may be used, but its meaning is consistent with the definition in this chapter.
+ SHALL Supplementary provisions apply when the specific domain document provides a more detailed description of a term, without conflict with the basic definition in this chapter.

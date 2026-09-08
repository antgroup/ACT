# ACT 2.1 Typical Scenarios and Business Processes

[中文](scenarios.md) | English

# Overview
This section uses typical commercial scenarios supported by the ACT Protocol to explain how delegation authorization, commerce interaction, payment execution, and trust services connect across end-to-end processes, providing scenario-based implementation references for protocol adopters. This document focuses on the applicable conditions, key business steps, and cross-domain interface relationships in each scenario.

# Scenario Classification Framework
Payment scenarios in agentic commerce are abstracted into three levels based on the principal's presence and the Agent's autonomy in commercial decision-making:

+ **L1 User Instant Payment**: The principal participates in the purchase decision loop in real time. AI participates in intent understanding and product matching, but the principal must complete identity verification and confirmation for every payment before funds are debited, and the principal retains payment decision authority. This level does not require an Intent Authorization Credential (IAC) to be issued in advance; the principal's real-time confirmation for the current transaction serves as the basis for payment authorization.
+ **L2 User-Specified Delegated Payment**: The principal is not present in real time, and the purchase target has already been specified during the initial interaction. The principal issues an Intent Authorization Credential in advance, authorizing the Agent to execute programmatically toward the specified purchase target within defined boundaries. In general, the principal does not need to intervene again for each transaction during execution.
+ **L3 Autonomous Delegated Payment**: The principal is not present in real time, and the specific purchase target is determined autonomously by the Agent during execution within the authorization boundaries. The principal issues an Intent Authorization Credential in advance and sets only the task objective and boundary conditions, such as the total budget cap, category scope, and task validity period. Within those boundaries, the Agent autonomously completes task decomposition, service discovery, multi-round negotiation, commercial decision-making, and multiple autonomous payments.

The core basis of the three-level classification is the combination of two dimensions: "principal presence" and "Agent autonomy in commercial decision-making." The former distinguishes between the principal being present in real time (Human-Present) and the principal not being present (Human-Not-Present); the latter distinguishes between directed execution toward a specified objective and autonomous decision-making by the Agent within authorization boundaries. L1 corresponds to "real-time presence + principal decision-making," L2 to "absence + directed execution," and L3 to "absence + autonomous decision-making." Based on these two dimensions, ACT defines four typical scenarios, as shown in the following table.

| **Scenario** | **Level** | **Principal Presence** | **Dependency on Intent Authorization Credential (IAC)** | **Agent Autonomy in Commercial Decision-Making** |
| --- | --- | --- | --- | --- |
| Scenario 1: User Instant Payment | L1 | Present in real time | No IAC needs to be issued in advance | The principal confirms and makes key decisions in real time |
| Scenario 2: Specified Delegated Payment (Platform Agent) | L2 | Not present | Depends on an IAC, with delegation mode set to SPECIFIED | The Agent performs programmatic, directed execution toward the objective already specified by the principal |
| Scenario 3: Specified Delegated Payment (Dedicated Agent) | L2 | Not present | Depends on an IAC, with delegation mode set to SPECIFIED | The Agent performs programmatic, directed execution toward the objective already specified by the principal |
| Scenario 4: Autonomous Delegated Payment | L3 | Not present | Depends on an IAC, with delegation mode set to BOUNDED | The Agent autonomously conducts multiple rounds of commercial decision-making and payment within the authorization boundaries |

The following sections describe the key processes and differentiated requirements for each scenario.

# ACT Protocol Component List
| **Protocol Domain** | **Protocol ID** | **Protocol Name** | **Protocol Description** |
| --- | --- | --- | --- |
| Authorization & Delegation Domain<br/>(ADD) | ADD-INT-ICS | Intent Capture and Structured Expression | Captures, normalizes, and structures the user's delegation intent |
| | ADD-IAC-ISS | Intent Authorization Credential Issuance | Generates and issues an IAC authorization credential based on the structured user intent |
| | ADD-IAC-LCM | Intent Authorization Credential Life Cycle Management | Manages the activation, suspension, resumption, revocation, and expiration states of an IAC |
| Commerce Interaction Domain<br/>(CID) | CID-MER-CAT | Catalog Interface | Provides standardized access to product, service, and merchant catalogs |
| | CID-INT-XFR | Intent Context Transfer | Transfers intent context to appropriate merchants and obtains matching product and service recommendations |
| | CID-PCA-NEG | Payment Capability Negotiation | Negotiates available payment methods, PSPs, payment endpoints, and other payment capability information |
| | CID-CART-CFM | Cart Confirmation | Performs final confirmation of an order, cart, or transaction details before payment |
| Payment Services Domain<br/>(PSD) | PSD-PMT-BND | Payment Method Binding | Binds available payment methods as the basis for subsequent payment processes |
| | PSD-AGT-SUB | Agent-Dedicated Sub-Account Management | Manages dedicated sub-accounts for Agent operations and the related payment control capabilities |
| | PSD-PAY-A402 | HTTP 402-Based Payment Process | Specifies a general HTTP 402-based payment access and interaction mechanism among the buyer Agent, seller service provider, and payment service provider, which can serve as a unified access point for payment scenario components |
| | PSD-PAY-INS | User Instant Payment | Completes payment processing in real time and produces a payment completion result. |
| | PSD-PAY-DEL | User-Specified Delegated Payment | Based on an Intent Authorization Credential in SPECIFIED mode, enables an Agent to initiate a specified delegated payment while the principal is not present and accept verification by the payment service provider |
| | PSD-PAY-AUP | Autonomous Delegated Payment | Based on an Intent Authorization Credential in BOUNDED mode, enables an Agent to autonomously conduct multiple rounds of commercial decision-making and payment within the authorization boundaries |
| Trust Services Domain<br/>(TSD) | TSD-ATT-EVT | Attestation Event | Defines the recording unit for attestation events covering key cross-domain actions and state changes |
| | TSD-ATT-OFF | Offline Attestation Record | Creates standardized attestation records that can be stored, transmitted, and verified offline |
| | TSD-ATT-OCA | On-Chain Attestation Anchor | Anchors attestation digests to the ACT Trust Chain to enhance verifiability and tamper resistance |
| | TSD-ATT-SVF | Signature Verification Flow | Defines the consistency verification process for attestation records, digests, on-chain anchors, and signatures |
| | TSD-ATT-DSP | Dispute Resolution | Supports dispute handling and adjudication |
| | TSD-CRD-ASC | Credit Association Establishment | Specifies the mechanism for establishing credit associations between an associated entity and an Agent, and for issuing credentials |
| | TSD-CRD-MAP | Associated Credit Mapping | Specifies mapping rules and version management from the associated entity's credit claims to the Agent's associated credit claims |
| | TSD-CRD-LCM | Credit Association Lifecycle Management | Specifies the state machine for credit association credentials and mechanisms for suspension, revocation, expiration, reassessment, and other lifecycle operations |
| | TSD-CRD-VER | Associated Credit Verification | Specifies standardized verification of credit associations and associated credit information by third parties |
| | TSD-CRD-AUTH | Credit Query Authorization | Specifies the associated entity's authorization mechanism for associated credit verification queries |

# Scenario 1: User Instant Payment
## Scenario Description
This scenario applies when the principal is present in real time and the purchase target has been specified during the current interaction. The principal confirms the product and authorizes payment in real time during the current interaction, without requiring an IAC to be issued in advance.

**Typical example:** The principal tells the Agent, "Order these headphones for me." After the Agent discovers the product, the principal confirms it on the spot and completes the payment.

## Main Business Process

![](../assets/specification/act-2.1-scenario-1-immediate-payment.png)

**Step 1: The principal expresses a purchase intent.**
The principal submits a purchase request to the Agent in natural language.

**Step 2: Intent structuring and intent confirmation.**
With reference to ADD-INT-ICS, the Agent may convert the natural-language intent into standardized, structured constraint information and present it to the principal in a readable form for confirmation. Constraints that may be specified include the purchase category, amount cap, validity period, payment method constraints, fulfillment timing requirements, and other key conditions.

**Step 3: Product discovery or merchant routing.**
When obtaining product details or screening candidate products, the Agent may obtain a merchant's structured product catalog with reference to CID-MER-CAT, or transfer intent context to a merchant or platform with reference to CID-INT-XFR to obtain more precise candidate results.

**Step 4: The principal confirms the product and willingness to pay in real time.**
The Agent presents candidate products to the principal, who selects the transaction target on the spot and confirms the willingness to pay. This step is an application-layer internal interaction, and its result serves as a direct prerequisite for initiating the subsequent payment.

**Step 5: Payment capability negotiation (optional).**
The Agent may read the payment capability information declared by the merchant with reference to CID-PCA-NEG to confirm the payment method and payment service provider to be used for this payment.

**Step 6: Payment initiation and PSP verification.**
The Agent should construct a payment request based on PSD-PAY-INS and initiate an instant payment with the PSP. The PSP verifies the payment request, including at least replay protection checks and validation of the Agent's signature, and may initiate a principal identity verification challenge as needed. If verification fails, the PSP should reject the payment and return the corresponding error result. After all checks pass, the PSP returns the payment authorization result.

**Step 7: Merchant fulfillment.**
After confirming payment authorization, the merchant fulfills the order. This is an internal merchant business process and falls outside the scope of this protocol specification.

**[Attestation] Attestation of the payment completion event (optional).**
Implementers may asynchronously attest the `act:payment:transaction-completed` event. Such attestation may provide factual evidence of payment completion for subsequent dispute resolution and create a traceable historical record of the Agent's behavior.

# Scenario 2: Specified Delegated Payment (Platform Agent)
## Scenario Description
This scenario applies to specified delegation where the principal is not present and the purchase target has already been specified during the initial interaction. The principal must issue a SPECIFIED IAC in advance, authorizing the platform Agent to complete subsequent commercial discovery, transaction confirmation, and programmatic payment within defined boundaries. In general, the principal does not need to intervene again in real time during execution.

A platform Agent typically uses a multi-tenant shared architecture, meaning that multiple principals share the same platform Agent identity. Therefore, payment verification in this scenario should also consider the binding between the platform Agent identity and the specific principal identity, reducing the risks of cross-principal overreach and identity confusion.

**Typical example:** The principal tells the platform Agent, "Book me a flight to Beijing tomorrow morning for no more than CNY 1,200." After identity verification and credential issuance, the Agent completes the search, comparison, ordering, and payment within the authorization boundaries.

## Main Business Process

![](../assets/specification/act-2.1-scenario-2-platform-delegated-payment.png)

### Phase 1: Intent Structuring and Credential Issuance
**Step 1: The principal expresses an intent.**
The principal expresses the purchase request in natural language.

**Step 2: Intent structuring and intent confirmation.**
With reference to ADD-INT-ICS, the Agent may convert the natural-language intent into standardized, structured constraint information and present it to the principal in a readable form for confirmation.

**Step 3: Issue the IAC.**
After the principal confirms the intent rules, the Agent should complete principal identity verification and execute the signature in a secure environment with reference to ADD-IAC-ISS, with the delegation mode set to `SPECIFIED`. The credential and its unique identifier generated in this step will be continuously referenced in subsequent commerce interactions, payment execution, and attestation to maintain information consistency across the full process.

**[Attestation] Attestation of the credential issuance event (optional).**
After the IAC is issued, implementers may asynchronously submit the `act:delegation:delegation-issued` attestation event.

### Phase 2: Commerce Interaction
**Step 1: Product discovery or merchant routing.**
The Agent may obtain a merchant's structured product catalog with reference to CID-MER-CAT, or transfer intent context to a merchant or platform with reference to CID-INT-XFR.

**Step 2: Product comparison and decision-making.**
The Agent compares candidate results based on the structured intent constraints and makes a purchase decision. This reasoning process is an internal application-layer implementation, but the Agent may generate a structured decision summary locally to explain the basis for its selection afterward.

**[Attestation] Attestation of the Agent decision event (optional).**
Implementers may asynchronously submit the `act:commerce:decision-logged` attestation event to provide evidence of the Agent's decision for subsequent dispute resolution.

**Step 3: Cart confirmation and rule self-check.**
Before submitting the cart, the Agent should perform a rule self-check based on CID-CART-CFM to confirm that the transaction complies with all authorization boundaries and constraints defined in the IAC. After all checks pass, the Agent submits the cart and obtains an order transaction number. If any constraint is not satisfied, the Agent follows the boundary-handling strategy predefined in the IAC, such as notifying the principal for renewed confirmation or automatically canceling the transaction.

**[Attestation] Attestation of the cart confirmation event (optional).**
After cart confirmation is completed, implementers may asynchronously submit the `act:commerce:cart-confirmed` attestation event to provide transaction confirmation evidence for subsequent dispute resolution.

### Phase 3: Payment Execution
**Step 1: Payment capability confirmation (optional).**
With reference to CID-PCA-NEG, the Agent may confirm the payment method and payment service provider to be used for the payment.

**Step 2: Payment initiation and PSP verification.**
The Agent should construct a delegated payment request based on PSD-PAY-DEL. The request should carry the IAC and order transaction number, be signed by the Agent, and then be submitted to the PSP. The PSP should perform replay protection checks, Agent signature verification, IAC validity verification, consistency verification between the principal identity and payment credentials, and consistency verification between the order transaction parameters and the authorization boundaries. If verification fails, the PSP should reject the payment request and return the corresponding error result. After all checks pass, the PSP returns the payment result.

The process and diagram above use a traditional merchant-platform ordering and payment process for illustration. The buyer Agent may also initiate payment using the PSD-PAY-A402 payment process.

**[Attestation] Attestation of the payment completion event (optional).**
After payment is completed, implementers may asynchronously submit the `act:payment:transaction-completed` attestation event to provide factual payment evidence for subsequent dispute resolution.

**Step 3: Merchant fulfillment.**
After confirming payment authorization, the merchant completes fulfillment. This is an internal merchant business process and falls outside the scope of this protocol specification.

**[Attestation] Attestation of the fulfillment completion event (optional).**
After merchant fulfillment, implementers may asynchronously submit the `act:commerce:fulfillment-completed` attestation event to provide fulfillment status evidence for subsequent dispute resolution.

# Scenario 3: Specified Delegated Payment (Dedicated Agent)
## Scenario Description
This scenario also applies to specified delegation where the principal is not present and the purchase target has already been specified during the initial interaction, but the executing entity is a dedicated Agent strongly bound to the principal's device, account, or runtime environment.

Unlike the multi-tenant platform Agent in Scenario 2, a dedicated Agent has an independent and unique dedicated identity, and payment verification can be anchored directly to that dedicated Agent identity. When supported by the payment service provider, this scenario may also establish an independent sub-account for the dedicated Agent, isolating the risk of the Agent's payment behavior from the principal's primary account.

**Typical example:** Through their dedicated Agent, the principal says, "Buy me the book *Artificial Intelligence: A Modern Approach* for no more than CNY 150." After identity verification and credential issuance, the dedicated Agent completes the search, comparison, ordering, and payment.

## Main Business Process

![](../assets/specification/act-2.1-scenario-3-dedicated-agent-payment.png)

This scenario is generally consistent with Scenario 2 in the fundamental processes of intent structuring and credential issuance, commerce interaction, cart confirmation, delegated payment execution, and asynchronous attestation. These processes are not repeated in this section. Only the substantive differences from Scenario 2 are highlighted below.

**Difference 1: Dedicated Agent identity initialization**

When a dedicated Agent first establishes a secure binding with the principal's device or runtime environment, it should complete registration and verification with the relevant identity service and obtain a unique identity identifier that can be recognized and verified within the ACT ecosystem. This initialization is generally performed only once upon initial binding. When the same dedicated Agent subsequently initiates another commercial delegation, it may directly reuse the existing identity.

**Difference 2: Delegate identifier in the IAC and signature verification method**

In this scenario, the delegate identifier in the IAC should contain the dedicated Agent's unique Agent identifier. When verifying the payment request, the PSP should verify the signature of the Agent initiating the payment request using the public key material corresponding to that Agent ID.

**Difference 3: Dedicated sub-account support**

If the principal has enabled an independent sub-account for the dedicated Agent, the Agent and the payment service provider may establish the dedicated sub-account, bind its identifier, and manage its lifecycle with reference to PSD-AGT-SUB. For a specific payment, the payment request should carry the corresponding sub-account identifier. During verification, the PSP should also verify the sub-account balance or limit status and debit funds or reserve the limit according to the applicable rules. If no independent sub-account is enabled, the transaction may instead be processed using payment credential separation and risk-control mechanisms.

# Scenario 4: Autonomous Delegated Payment
## Scenario Description
This scenario applies when the principal is not present and the specific purchase target is determined autonomously by the Agent during execution within the authorization boundaries. Unlike the specified delegation in Scenarios 2 and 3, the principal does not need to specify a particular transaction target during the initial stage and only needs to set the task objective and boundary conditions, such as the total budget cap, service category scope, and task validity period. Within these authorization boundaries, the Agent may autonomously complete task decomposition, service discovery, multi-round negotiation, and multiple autonomous payments, without the principal intervening in each transaction throughout the process.

To control the risk of high-frequency machine-to-machine transactions, this scenario generally requires the buyer Agent to use a dedicated independent sub-account, isolating risk from the principal's primary account.

**Typical example:** The principal asks a dedicated Agent to prepare a research report. The Agent autonomously purchases capabilities or data in sequence from a data service Agent, a literature retrieval Agent, and others, then delivers the result to the principal after all subtasks have been completed.

## Main Business Process

![](../assets/specification/act-2.1-scenario-4-autonomous-payment.png)

### Phase 1: Task Delegation and Credential Issuance
**Step 1: The principal expresses an autonomous delegation task.**
The principal expresses the task objective and boundary constraints to the buyer Agent, such as the permitted service category scope, total budget cap, and task deadline.

**Step 2: Structured intent and rule confirmation.**
With reference to ADD-INT-ICS, the buyer Agent may express the task objective and constraints in a structured form and present the key constraints to the principal for confirmation.

**Step 3: Issue an autonomous delegation IAC.**
After the principal confirms, the buyer Agent should complete identity verification and signing with reference to ADD-IAC-ISS, with the delegation mode set to `BOUNDED`. After credential issuance, the principal generally does not need to reconfirm each of the subsequent autonomous payments initiated by the buyer Agent within the boundaries.

**Step 4: Prepare the dedicated sub-account (optional).**
The buyer Agent checks the balance or available limit of the dedicated independent sub-account. If it is insufficient, the Agent may remind the principal to add funds or adjust the budget cap.

**[Attestation] Attestation of the credential issuance event (optional).**
After the IAC is issued, implementers may asynchronously submit the `act:delegation:delegation-issued` attestation event.

### Phase 2: Task Decomposition and Service Discovery
**Step 1: Task decomposition.**
The buyer Agent decomposes the overall task into several subtasks and plans the execution path. This process is internal Agent reasoning and falls outside the scope of this protocol specification.

**Step 2: Service discovery.**
Through a service marketplace or another discovery mechanism, the buyer Agent may screen service provider Agents that satisfy the intent constraints and form a candidate list. When screening service provider Agents, the buyer Agent may reference the Agent's associated credit claims from the Trust Services Domain, as described in the Credit Association sub-specification, as auxiliary inputs for evaluating the trustworthiness of service providers.

**Step 3: Payment capability negotiation (optional).**
With reference to CID-PCA-NEG, the buyer Agent may negotiate payment capabilities with the selected service provider Agent and confirm a matching payment method and payment service provider.

### Phase 3: Multi-Round Agent-to-Agent Autonomous Payments
The following process describes a single autonomous payment. It may be repeated multiple times during a complete task execution cycle.

**Step 1: Real-time rule self-check.**
Before initiating each autonomous payment, the buyer Agent should verify whether the current time is within the credential validity period, whether the sum of the cumulative payment amount and the current amount exceeds the total cap, whether the service provider and service category satisfy the constraints, and whether the payment method falls within the authorization scope. If any condition is not met, the Agent should terminate the current payment and handle it according to the predefined strategy. When the remaining limit or validity period approaches a predefined threshold, the Agent may proactively send an alert to the principal.

**Step 2: Payment trigger and message construction.**
After receiving a service request from the buyer Agent, the service provider Agent may request payment by returning `HTTP 402 Payment Required` with reference to PSD-PAY-A402, and state the payment amount, payment method, payee identifier, and other necessary payment parameters for the service in the response. After receiving the payment request, the buyer Agent constructs an autonomous delegated payment request message based on PSD-PAY-AUP, carries the BOUNDED IAC and the current payment parameters, and signs the message. The buyer Agent should submit the payment request message directly to the agreed PSP to request payment authorization for the service.

The process and diagram above use the PSD-PAY-A402 payment process for illustration. The buyer Agent may also initiate payment through a traditional merchant-platform ordering and payment process.

**Step 3: PSP verification and payment authorization.**
After receiving the payment request, the PSP performs scenario-specific verification for autonomous delegated payment based on PSD-PAY-AUP, including replay protection checks, buyer Agent signature verification, BOUNDED IAC validity verification, verification of the current amount and cumulative limit boundaries, and verification of the dedicated sub-account balance or available limit.

The verification requirements above are independent of the payment access method. Whether PSD-PAY-A402 or a traditional merchant-platform ordering and payment process is used, the PSP should perform these scenario-specific checks. If verification fails, the PSP should reject the payment and return a failure result or the corresponding error information to the buyer Agent. If all checks pass, the PSP should return a successful payment result, or a payment authorization result and credential that can be referenced and verified during subsequent service delivery. The buyer Agent may proceed to the subsequent service request stage only after receiving a successful payment result.

**Step 4: Service delivery and continuation of subtasks.**
After receiving another service request from the buyer Agent, the service provider Agent should verify the payment result, payment credential, or payment-related identifier carried in the request, and verify the payment status with the payment service provider using the verification method agreed with the payment service provider, to confirm that the payment corresponding to the request has been completed or that the related payment authorization is valid. The service provider Agent may deliver the corresponding data or service result only after confirming that payment has been completed, or that the related payment authorization is valid and acceptable.

The buyer Agent continues with the next subtask until all subtasks are completed.

**[Attestation] Attestation of a single payment completion event (optional).**
After each autonomous payment is completed, implementers may asynchronously submit the `act:payment:transaction-completed` attestation event. Multiple payment records under the same delegated task may be further aggregated into a complete task bill to support auditing and dispute resolution after task completion.

### Phase 4: Task Completion and Bill Review
**Step 1: Task completion and result delivery.**
After all subtasks are completed, the buyer Agent aggregates the results and delivers the task output to the principal.

**Step 2: Credential revocation (optional).**
If the credential has not expired when the task is completed, the buyer Agent may proactively trigger credential revocation with reference to ADD-IAC-LCM to terminate possible subsequent payment activity.

**Step 3: Bill review.**
The principal may review all payment records initiated by the buyer Agent during task execution and the related result summaries.

**[Attestation] Attestation of the credential revocation or expiration event (optional).**
If the credential is proactively revoked, implementers may asynchronously submit the `act:delegation:delegation-revoked` attestation event. If the credential becomes invalid upon expiration, they may asynchronously submit the `act:delegation:delegation-expired` attestation event.

# General Notes on Asynchronous Attestation Processing
All steps marked [Attestation] in the scenarios in this document are asynchronous, non-blocking operations. Their execution timing should not block or affect the normal progression of the main commerce interaction and payment processes.

Whether related attestation events are submitted, and which participant is responsible for submitting them, may be determined based on the business risk level, dispute resolution requirements, and implementation architecture. However, for attestation events that have been submitted, their event types, payload structures, signature verification methods, and subsequent verification rules should comply with the unified requirements of the Trust Services Domain.

In the current protocol version, typical attestable events include credential issuance, Agent decision logging, cart confirmation, payment completion, fulfillment completion, and credential revocation or expiration. Together, these events form an important factual basis for subsequent dispute resolution, auditing, and retrospective tracing.

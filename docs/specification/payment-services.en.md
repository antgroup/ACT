# ACT 2.1 Payment Services Domain

[中文](payment-services.md) | English

# Scope
## Domain Positioning
Payment Services Domain (Payment Services Domain, PSD) provides for Agent to initiate interactive rules for payment, acceptance of payment verification, acquisition of payment result and treatment of the related state after completion of the pre-payment commercial confirmation, providing a uniform, verifiable, compatible payment services synonym for the payment execution phase in agentic commerce.

## Domain Responsibilities
This domain covers the following:

+ Payment Method Binding and payment instrument Reference management;
+ Agent-specific Sub-account and its associated certification capacity management;
+ Universal payment access interactive (PSD-PAY-A402) based on HTTP 402;
+ Three types of payment scenarios under different attendance and autonomy: Instant User Payment, User-directed Delegated Payment and Autonomous Delegated Payment;
+ payment request Structure, payment instrument citation, authorization to verify, payment execution and status return;
+ Pays the critical objects, state semantics and cross-domain reference relationships required for the implementation phase.

The following are not regulated in this domain:

+ Merchant Internal order performance, inventory disposal and business systems achieved;
+ (b) Information on the ground liquidation network, the processing of funds for settlement and the internal mechanisms of the corridor;
+ Payment Service Provider Internal risk control strategy achieved, routed strategy and account core system achieved.

# The list of components and relationships in this field
## Component Overview
Payment Services Domain consists of six protocol components, divided into payment access programme components and payment scene components, which together complete the full chain from payment instrument readiness, account segregation and payment authorization to payment implementation and outcome status management.

Payment scenario component:

+ **PSD-PMT-BND: Payment Method Binding.** Responsible for regulating Principal the process of completing Payment Service Provider capacity to pay and establishing Agent payment marks or equivalent payment instrument quotations.
+ **PSD-AGT-SUB: Agent-specific Sub-account Management.** Responsible for regulating the opening of an exclusive sub-account with a financial isolation capability for a specific Agent and managing its accompanying authentication key and life cycle process.
+ **PSD-PAY-INS: Instant User Payment.** Responsible for regulating the process of prompt payment, completion of confirmation of payment and receipt of payment result in real-time presence.
+ **PSD-PAY-DEL: User-directed Delegated Payment.** Responsible for regulating the process in which Buyer Agent initiates directed delegated payment based on a SPECIFIED mode IAC and accepts PSP verification when Principal is not present in real time.
+ **PSD-PAY-AUP: Autonomous Delegated Payment.** Responsible for regulating the process in which Buyer Agent autonomously conducts multiple rounds of commercial decision-making and payment within the authorization boundary based on a `BOUNDED` mode IAC when Principal is not present in real time.

Payment access programme components:

+ **PSD-PAY-A402: payment access based on HTTP 402.** General payment access based on HTTP 402 status code is interactive and can be quoted as required by each payment scenario component.

## Core Object & Identification
Payment Services Domain uses a standard core set of objects and identifiers to describe key information for the payment implementation phase. The core objects of the field and their roles can be summarized as follows.

|** Object or Identification**|** Meaning**|** Mainly Generate Location**|** Main Use Location**|
| --- | --- | --- | --- |
|payment instrument Reference|Available references to the payment instrument used to identify payment instruments at the time of payment may be shown as proof of payment mark, sub-account mark or other equivalent payment instrument|PSD-PMT-BND、PSD-AGT-SUB|PSD-PAY-INS、PSD-PAY-DEL、PSD-PAY-AUP、PSD-PAY-A402|
|Merchant side order number|Order-level confirmation result from Commerce Interaction Domain; the order number identifies the product information, amount, and other information for the current transaction.|CID-CART-CFM|Payment Services Domain Payment execution components|
|Results Payment Capability Negotiation|Pre-payment capability alignment results from Commerce Interaction Domain to determine the payment method, Payment Service Provider interface endpoint and load mode used for this payment|CID-PCA-NEG|PSD-PAY-A402, PSD-PAY-DEL, PSD-PAY-AUP and, if necessary, PSD-PAY-INS|
|User Intent Authorization Credential(IAC)|Intent Authorization Credential issued Authorization & Delegation Domain for the expression of authorized boundaries for commissioning or autonomous payment|ADD-IAC-ISS|PSD-PAY-DEL、PSD-PAY-AUP|
|`delegation_id`|authorization and delegation voucher life-cycle markers for stable association with the same authorization chain in payment execution, authorization verification and subsequent certificates|ADD-IAC-ISS|PSD-PAY-DEL、PSD-PAY-AUP|
|payment request|Buyer Agent Standardized payment execution request for the construction of Payment Service Provider to carry transaction confirmation information, payment instrument reference, time stamp, request unique identification and necessary signature material.|PSD-PAY-INS、PSD-PAY-DEL、PSD-PAY-AUP|PSP or related payment recipient|
|payment result|Payment Service Provider Returned payment execution results, usually including trade flow numbers, associated order markings, trade status and transaction time information|PSD-PAY-INS、PSD-PAY-DEL、PSD-PAY-AUP|Buyer Agent, Merchant side and follow-up certificate processing|

## Dependence and Cross-domain Reference
PSD-PMT-BND and PSD-AGT-SUB provide the basis of payment instrument for the payment of implementation, respectively: the former provides payment instrument quotations for Principal main account, and the latter provides a specific Agent financial segregation account and its authentication key.

Before initiating payment, PSD-PAY-INS, PSD-PAY-DEL, and PSD-PAY-AUP reference the transaction confirmation result produced by Commerce Interaction Domain; PSD-PAY-DEL and PSD-PAY-AUP additionally reference User Intent Authorization Credential provided by Authorization & Delegation Domain.

When the counterparty is the seller Agent or payment method to be consulted dynamically, PSD-PAY-DEL and PSD-PAY-AUP may also refer to Payment Capability Negotiation resulting from CID-PCA-NEG to determine payment method, Payment Service Provider and interface endpoints.

PSD-PAY-A402 as a universal payment access option can be cited as required by PSD-PAY-INS, PSD-PAY-DEL, PSD-PAY-AUP.

Under the scenario Agent-specific Sub-account, the generation, authentication key binding and key failure processing of payment authorizations can be achieved by relying on the key management and security enforcement capabilities provided by ASL.

Trust Services Domain Harmonized rules for maintaining the governance of the type and certificate of events related to payments; Payment Services Domain used only the incident identifier in the relevant components and did not define the structure of the event or the governance mechanism in its own domain.

# PSD-PMT-BND: Payment Method Binding
## Overview
Payment Method Binding (Payment Method Binding, PSD-PMT-BND) provides for Principal completion of capacity to pay at Payment Service Provider or account service and establishment of basic processes and requirements for Agent to be quoted at payment instrument.

The objective of this component is to enable Agent to complete the payment using the authorized payment instrument in the execution of subsequent payments while avoiding direct exposure to Agent of the original payment account information.

In the Agent payment scenario, agent SHALL NOT holds directly or has access to Principal original payment account information.

## Participants and prefix
This component involves the following Participants: Principal, Buyer Agent and Payment Service Provider or account service providers that provide Payment Method Binding services.

Before entering this component, SHALL satisfies the following preconditions.

+ Effective interaction with Buyer Agent has been established and there is a clear desire to open up capacity to pay for Agent.
+ Buyer Agent SHALL have an identification that can be identified and bound by Payment Service Provider or account service.
+ Payment Service Provider or account service SHALL have the capability of Principal identification, payment instrument reference generation, binding relationship management and validity verification.

## Basic processes
Payment Method Binding SHOULD was activated by Principal. Principal Following the launch of the Agent platform, the SHOULD platform directed the request to Payment Service Provider or the account service side to complete identification and binding confirmation.

**The first step is identification and confirmation of will.** Payment Service Provider or account service provider should verify Principal identification and binding willingness, which may include biometric recognition, payment passwords, dynamic authentication codes or other means of realizing support. During the verification process, Payment Service Provider or account service provider SHALL clearly shows Principal this binding fiduciary Agent identification and associated authorization Scope to ensure that the binding is based on an informed confirmation.

**The second step is to generate and release payment instrument references** Payment Service Provider or the account service generate a payment mark or other equivalent payment instrument quotation and bind it to Principal real funds accounts, Agent fiduciary identification and related restrictions. The relevant restrictions may include the validity period, monetary ceiling and other restrictions on the use of the party ' s definition. Once the attachment is completed, Payment Service Provider or the account service will send it to Buyer Agent under payment instrument quotation for use as a payment tool in payment request.

## Processing of requests
The payment instrument citation (payment mark), SHALL formed by this component, stabilizes the association with the following information: Principal true financial account, Agent fiduciary identifier, and the subject ' s own state of validity.

Payment Service Provider or the account service provider can verify the validity of the payment instrument reference and its consistency with the identity of Buyer Agent for initiating the payment at subsequent payment request.

If the reference to payment instrument is expired, expired, or does not match the current identity of Agent, Payment Service Provider or the account server SHALL NOT continues to accept payment request.

## Failed to process
Payment Service Provider or account service SHALL rejects this binding request and returns the identifiable failure result if the identification, payment instrument reference generation or binding relationship has failed.

The semantic SHOULD of the cause of the failure covers at least the failure of identification, the failure of Agent identification, the excess of account amount and other anomalies that make payment instrument citation impossible.

The failure of binding SHALL NOT gives rise to valid payment instrument quotations that can continue to be paid for.

The established binding relationship is also recognized as not available in the subsequent payment verification if it has lapsed, frozen or cancelled.

# PSD-AGT-SUB: Agent-specific Sub-account Management
## Overview
Agent-specific Sub-account Management (Agent-Dedicated Sub-Account Management, PSD-AGT-SUB) provides for the opening of an exclusive sub-account with financial isolation capability for a specific Agent, along with its accompanying certification key binding and life-cycle management requirements.
The objective of this component is to provide a mechanism of account-level risk segregation for Agent, which is more autonomous, so that Principal main account is not directly exposed to the payment risk of Agent autonomous execution.

## Participants and prefix
This component covers the following: Participants: Principal, Buyer Agent and Payment Service Provider for the opening, validation and management of sub-accounts.

Before entering this component, SHALL satisfies the following preconditions.

+ Principal has clearly expressed a desire to establish separate payment boundaries for specific Agent funds.
+ Buyer Agent SHALL already has a stable identifier that can be identified and bound; under the exclusive Agent scenario, the identity is usually more closely tied to Principal equipment, account number or operating environment.
+ Payment Service Provider SHALL have basic managerial capacity for the opening, filling, freezing, unfrozen, write-off and status queries of sub-accounts.

## Sub-account management requirements
An Agent-specific Sub-account SHOULD be opened at the Principal's initiative.

Payment Service Provider complete SHALL identification and establish a binding relationship between sub-account, trusted Agent identification and associated authentication keys during opening.

Once a sub-account has been opened, Principal may be recharged or made available to enable Agent to be paid within the established balance or amount Scope.

In the follow-up payment process, the Buyer Agent portable sub-account identification and the corresponding authorization of payment is initiated, while Payment Service Provider is verified and processed on the basis of the binding relationship and the status of the account.

Payment Service Provider SHALL support freezing or write-off of sub-accounts when wind abnormality triggers, Principal voluntary application or Agent identity lapses.

After the sub-account has been cancelled or invalidated, the relevant authentication key is also SHALL synchronized to expire and SHALL NOT continues to be used for subsequent payments.

## Exclusive Key Tie
The sub-account SHOULD contain an exclusive authentication key to support a valid authentication of the authorization of payment to the sub-account. The authentication key may be an asymmetric or symmetrical program; it may only be achieved by selecting the applicable mode in accordance with security requirements and conditions of deployment.

When the sub-account is opened, the relevant key or authentication material SHOULD be generated in a protected enforcement environment and is bound to the sub-account identifier for registration as the basis for subsequent validation.

In the subsequent payment process, Buyer Agent may be based on the authentication key to generate a message authorizing payment, Payment Service Provider to verify that payment request is consistent with the current sub-account and its binding Agent.

When the sub-account is frozen or cancelled, the authentication key associated with the sub-account is also disabled by SHALL; after the sub-account has lapsed, Payment Service Provider SHALL NOT continues to receive payment request.

For the bottom security mechanism for key generation, call for protection and disablement, this component is not repeatedly defined for practical realization; the capability can be supported by the ASL security enforcement and key management capability, with corresponding modules `ASL-INF-SEE` and `ASL-INF-KMS`.

## **Processing requests and failures**
The sub-accounts managed by this component are at least SHALL capable of stabilizing the information associated with the sub-account identifier, the fiduciary Agent identifier, the current state of the account and the authentication key status associated with it.

The achievement of such limitations as maximum balances, single amounts, cumulative amounts, validity periods or the application of mission Scope may require further allocation of sub-accounts, depending on the operation, to support risk segregation for more finer particles.

Payment Service Provider SHALL be able to identify the basic life cycle state of the sub-account, including, at a minimum, the state of availability, freezing and cancellation, and decide whether to accept subsequent payment request.

When a sub-account is not opened, the balance is insufficient, the state is abnormal, the binding relationship is inconsistent or the authentication key is invalid, Payment Service Provider SHALL rejects the related payment or management operation and returns the identifiable failure result.

The semantic SHOULD of the cause of the failure covers at least the failure to verify the identity, the failure to open the sub-account, the freezing of the sub-account, the cancellation of the sub-account, the insufficient balance and the invalidation of the authentication key.

# PSD-PAY-A402: Payment Process Based on HTTP 402
## Overview
This component definition is Buyer Agent, Merchant/resource service provider interacts with a generic payment access line based on the HTTP 402 status code (Payment Required): Buyer Agent access to paid resources or services, and the seller ' s service returns 402 status code and bill when no valid proof of payment is found; the buyer completes payment that meets the requirements of the payment scene; the seller certifies the delivery of resources and completes the confirmation of performance.

This component may be referenced as needed by `PSD-PAY-INS`, `PSD-PAY-DEL`, and `PSD-PAY-AUP`. When referenced, it carries only the payment access interaction mechanism and does not replace other specific requirements of each scenario component, such as IAC constraints, cumulative amount boundaries, or sub-account management.

## Participants and prefix
This component involves the following Participants:

+ **Buyer Agent** Request for seller ' s resources or services, analysis of claims for payment, performance of authorized verification Principal, acquisition and submission of proof of payment.
+ **Seller's services** The seller's side may be Merchant, platform, seller Agent or its proxy interface, which is referred to as the seller's service provider in this component.
+ **Payment Service Provider (PSP)**: To receive payments under specific payment methods, to generate proof of payment, to provide certification of payment and to receive the required confirmation of performance.
+ **Principal**: confirm payments in real time in `PSD-PAY-INS` scenes; predefined authorized boundaries in `PSD-PAY-DEL` and `PSD-PAY-AUP` scenes by Intent Authorization Credential or sub-accounts, etc.
+ **Merchant or resource provider**: may be the same subject as the seller's service provider, or the seller's service provider may provide it with the resources to access and pay access capacity.

Before entering this component, SHALL satisfies the following conditions:

+ The seller ' s service provider SHALL be able to identify steadily the resources, services or orders to be charged and has the capacity to generate the only `resource_id` and `out_trade_no`.
+ Buyer Agent SHALL have the capability to identify HTTP 402 status code, to interpret Base64URL code Header, to select `method_id` supported and to verify Principal enabling rules.
+ Between Participants it has been determined that `CID-PCA-NEG` or the equivalent mechanism is available at payment method.

## Interactive flow
The following process describes the single payment access process, which can be repeated many times during a full mission implementation cycle.

**Step 1: Request for fee-paying resources**

The request may be `GET`, `POST` or other HTTP method defined by the seller’s provider.

Buyer Agent The initial request is usually not accompanied by `Payment-Proof`; if carried, the seller ' s services SHALL verify its format, duration, binding of the transaction and whether it has been repeated.

**Step 2: Return to payment claims**

If the current request is not supported by proof of payment, or if the proof of payment is not certified, the seller ' s serviceer SHALL return HTTP `402 Payment Required` and carries a payment bill coded Base64URL on `Payment-Needed` Header.

```plain
HTTP/1.1 402 Payment Required
Payment-Needed: <Base64URL-encoded payment invoice>
Content-Type: application/json

{
  "error": "Payment Needed",
  "message": "Please pay CNY 0.01 to access this resource",
  "resource_id": "RES_1739836600000_abc123"
}
```

Response is used only for debugging, logs and human readable tips; Buyer Agent payment information for machine processing SHALL be based on `Payment-Needed` Header.

**Step 3: Buyer undertakes scene verification and payment**

After the Buyer Agent resolution `Payment-Needed`, SHALL performs the pre-judgement of the scene:

+ In the `PSD-PAY-INS` scene, SHALL leads Principal to real-time payment confirmation.
+ In the `PSD-PAY-DEL` scenario, SHALL verify the validity of the SPECIFIED mode IAC, amount, cumulative amount, Merchant Scope, and allowed payment methods.
+ In the `PSD-PAY-AUP` scenario, SHALL verify the validity of the `BOUNDED` mode IAC, task Scope, cumulative budget, resource category, and Agent-specific Sub-account status.

If either condition is not met, Buyer Agent SHALL NOT continues to initiate payment and SHALL terminates the transaction in accordance with the pre-set strategy, switchs the counterparty or informs Principal processing.

After the validation, Buyer Agent SHALL initiate payment to PSP or method-designated endpoints under the corresponding payment method norm `method_id` and obtains a certificate of the results of payment authorization. payment method, payment instrument, funds deduction, IAC verification and risk control strategy remains defined by the corresponding PSD scenario component and payment method component, A402 without repetition.

**Step 4: Retry visits with payment certificates**

After payment has been successful, Buyer Agent shall initiate a new request for the original resource or service and carry in `Payment-Proof` Header information such as payment certificates, PSP Trade Stream and buyer session identification.

```plain
GET /market/XXXX/trend HTTP/1.1
Payment-Proof: <Base64URL-encoded payment proof>
```

**Step 5: Seller certifying payment**

The seller ' s service provider SHALL interprets `Payment-Proof` and uses the PSP or letter-certification service according to the corresponding methodological norm `method_id` to verify the proof of payment as follows:

+ **Validity of documents** Check the signature, validity period, revocation status, etc. of `payment_proof` and confirm that the certificate itself is valid.
+ **Responsiveness** Check whether the certificate has been duplicated and prevent the same payment certificate from being used for multiple resource visits.
+ **Coherence**: Verify that the paragraphs `trade_no` and `resource_id` in the certificate are consistent with the current request for resource visits and confirm that the certificate corresponds to the resources requested for payment.

If any verification is not made, the seller's service SHALL refuses to pay for access to the resources and returns the wrong semantics that can be identified by Buyer Agent.

**Step 6: Delivery of resources and recognition of performance**

The seller’s services can then return to the machine’s readable certification and performance by `Payment-Validation` Header in a successful response.

```plain
HTTP/1.1 200 OK
Payment-Validation: <Base64URL-encoded validation result>
Content-Type: application/json

{
  "status": "PAYMENT_VALIDATED",
  "trade_no": "2026040900828111317760000001xxxx",
  "resource_id": "RES_1739836600000_abc123",
  "resource": "XXXXXXXXXXXX"
}
```

After completing the delivery of resources or the performance of services, the seller ' s service provider initiated a confirmation of performance to the PSP in accordance with the specific method of payment.

Upon completion of the payment transaction, PSP SHOULD be reported as `act:payment:transaction-completed` certificated events providing a factual basis for subsequent audits, dispute processing and task billings.

## HTTP Header Extension Field
This component uses the following three types of HTTP Header fields. Three Header Value SHALL use Base64URL-coded format UTF-8 JSON.

|Header Name|User|Time to use|
| --- | --- | --- |
|`Payment-Needed`|Seller's services|`HTTP 402` for the statement of payment claims and core parameters.|
|`Payment-Proof`|Buyer Agent|The buyer used it again when requesting resources or services with proof of the payment of the result of the authorization.|
|`Payment-Validation`|Seller's services|The seller returns after the results of the payment warrant have been certified.|

## Method of payment (metal_id)
This component identifies the specific method of payment through `method_id`, and the corresponding method regulates the independent maintenance of the relevant rules in the document.

Each payment method regulates the documentation of the independent method used to define the method ' s request construction, the extension field requirements, the signature algorithm, the PSP verification logic, the method of return of the certificate of payment result and the rules for allocation of error codes.

Before entering this component, the buyers and sellers may consult and confirm `method_id`, `psp_id`, `endpoint` and `method_schema_url` as direct inputs for subsequent payment request construction and execution.

## Payload Structure
The payment load is structured into two levels: the base load field and the payment method extension field. The base load field is used to define a set of standard elements shared by each payment method to ensure interoperability between different realizations. The payment method extension field is used to carry business parameters specific to the specific payment method, but does not change the standard semantic of the base load field.

Each of the three Header payloads uses two layers of `Protocol + method` (pre-Base64URL code).

### Baseload field
|Fields|Type|Annotations|
| --- | --- | --- |
|`method_id`|string|The payment method identifier is used to identify the specific method of payment used in the transaction.|
|`out_trade_no`|string|External order numbers, used for control, etc., of transactions.|
|`amount`|string|Payments, SHOULD in string format to avoid floating point accuracy problems.|
|`currency`|string|The currency of the transaction, SHOULD be expressed in the standard currency code.|
|`resource_id`|string|Resource identifiers to bind payments and resource access to prevent misappropriation of vouchers.|
|`pay_before`|string|The payment deadline is used to limit the time window for payment and reduce the risk of readmission.|
|`seller_unique_id`|string|The sole identifier of the seller ' s service provider.|
|`buyer_unique_id`|string|Buyer Agent Unique identifier.|
|`payment_proof`|string|A certificate of payment of the results of the authorization is used to mark the successful outcome of the authorization of payment.|
|`trade_no`|string|Trade stream number or trade unique identification number, generated by PSP and used for transaction tracking.|
|`expires_at`|string|(c) The deadline for the payment of certificates of authorized results.|
|`signer_id`|string|The only signer ' s identifier is used to identify the person that generated the signature of the message.|
|`signature_content`|string|Signing value to be used to ensure the integrity of the message and the verifiability of the source.|
|`signature_type`|string|The type of signature algorithm used to indicate the algorithm identifier required for the authentication of the signature of the message.|

### Payment Method Extension Fields
The payment method extension field is used to fit the business scenario of the specific payment method, and the buyer and seller and the PSP may allow the addition of specific parameters to the method Scope in the methodological specifications. Such extension parameters may include the account identifier map key, commodity information, signature over the Scope declaration, or other payment-method-specific attributes.

The definition, restraint and use of the extended field is defined by the corresponding payment method to regulate the independent description of the document.

### Example of payload Payment-Needed
Using two layers of `Protocol + method` (before Base64URL code):

```json
{
  "protocol": {
    "out_trade_no": "ORDER_1739836600000_abc123",
    "amount": "0.01",
    "currency": "CNY",
    "resource_id": "RES_1739836600000_abc123",
    "pay_before": "2026-03-25T12:00:00+08:00",
    "seller_signature": "YYYYxxxx=",
    "seller_sign_type": "RSA2",
    "seller_unique_id": "2088xxxxxxxx"
  },
  "method": {
    "seller_name": "Test Merchant",
    "seller_id": "2088xxxxxxxx",
    "seller_app_id": "app_123456",
    "goods_name": "Test Product",
    "seller_unique_id_key": "seller_id",
    "service_id": "xxxx_12344"
  }
}
```

### Example of payload Payment-Proof
Using two layers of `Protocol + method` (before Base64URL code):

```json
{
  "protocol": {
    "payment_proof": "7cf8a6a93c924e13eaa4bf20c3a487f30d1fbdb759a1f229b4091b7d0158xxxx",
    "trade_no": "2026040900828111317760000001xxxx"
  },
  "method": {
    "client_session": "xxxxxxxxxxxxxsCiAgICAic2Vzc2lvbklkIjogInh4IiwKICAgICJzaWduYXR1cmUiOiAi5Yqg562+5ZCO57uT5p6c77yM6YCa6L+HY3JlZGVudGlhbElk5Yqg562+YWdlbnRUb2tlbiArIHNlc3Npb25JZCkiCn0="
  }
}
```

## Transaction Status
This component defines the state of the transaction described below, and the internal state of each payment method SHALL be mapped to the state below and then exported externally.

|Status Code|Status Name|Annotations|Transferable to Status|
| --- | --- | --- | --- |
|`CREATE`|Create|Initial Status|`WAIT_BUYER_PAY`|
|`WAIT_BUYER_PAY`|Waiting for the buyer to pay.|The buyer has not yet completed payment|`WAIT_SELLER_FULFILLMENT`、`TRADE_CLOSED`|
|`WAIT_SELLER_FULFILLMENT`|Waiting for the seller to perform|The buyer paid for the performance of the seller ' s services|`WAIT_BUYER_RECEIPT`、`TRADE_CLOSED`|
|`WAIT_BUYER_RECEIPT`|Waiting for the buyer to write back.|The seller performed the contract, awaiting confirmation from the buyer|`TRADE_FINISHED`、`TRADE_CLOSED`|
|`TRADE_FINISHED`|The deal is done.|Final|None|
|`TRADE_CLOSED`|Transactions closed|Final, applicable to closed status after refund or cancellation|None|

## Error Response
An error response SHOULD cover the semantic categories of signature verification, request parameters, identification, amount and asset, risk control, trading status, payment certificate certification and system anomalies. Buyer Agent and the seller's services may decide to retry, switch payment method, change the counterparty or terminate the transaction in accordance with the wrong synonym.

|Semantic Category|Annotations|Retry proposal|
| --- | --- | --- |
|Signature verification error|Signature verification failed or the signature type is unsupported|Direct retry is generally not recommended; first check the signature material, signer identifier, and algorithm configuration|
|Request parameter error|Parameters are invalid, amount format error, time format error, or request expired|Once the submission has been amended, it may be re-examined; if it has expired, re-acquire the claim for payment SHALL|
|Protocol verification error|The protocol does not exist, the protocol is invalid, or the methodological norm does not match|Direct retry is not recommended, SHALL pre-validation of payment method configuration and protocol version|
|Agent identity verification error|Buyer Agent or seller service identity verification failed|Direct retry is not recommended; first check identity documents, public-key material, and binding relationships|
|Quantities and asset verification errors|Insufficient amount, insufficient balance or failure to verify asset accounts|It can be repeated after the balance has been filled, the amount adjusted or the payment instrument replaced|
|Restraint and Wind Control Error|User restricted, stroke control strategy, or authorized boundaries not satisfied|It is generally not recommended to try again immediately, SHALL pending release of the risk control or re-authorization. ]|
|Transaction status error|The transaction does not exist, or the current transaction is not allowed to proceed|Do not recommend a direct retry, SHALL first query the transaction status and do some sort of processing|
|Refund error|Excess of amount of refund or failure to process refunds|Subject to the cause of failure; transfer of personnel as necessary or follow-up reimbursement process|
|Performance reply error|Failure to perform, or abnormality in the return of performance results|You can decide whether or not to try again in conjunction with policy and compliance query results, etc.|
|Payment authorization result credential verification error|The credential is empty, expired, missing, invalid, or inconsistent with the current subject, transaction, or resource|Direct retry is generally not recommended; obtain a valid credential or initiate payment again|
|System error|Intra-system anomalies or downstream service failures|A limited number of re-tests by index exit strategy, manual transfer or alarm after crossing the threshold|

# PSD-PAY-INS: Instant User Payment (L1 scene)
## Overview
Instant User Payment (Instant Payment,PSD-PAY-INS) applies to Principal real-time presence and prompt confirmation of the purchase to complete the payment.

In that scenario, Principal participation in the closed circle of purchasing decisions in their entirety, and therefore no pre-issuance of Intent Authorization Credential; Principal prompt confirmation completed at Payment Service Provider cashier is in itself the legal basis for authorization of this payment.

In this component, AI participates in the transaction, but a human ultimately makes and executes the decision. Payment decision authority remains with the User. Before debiting funds, the Payment Service Provider SHALL verify the User for each payment (for example, by face, fingerprint, QR-code scan, password, or verification code); the Agent's role is to place the order and initiate the payment request on the User's behalf. From a payment-security and risk-control perspective, this is the L1 scenario.

> Note: The current protocol only defines the model payment request initiated from Agent to Payment Service Provider, which will be followed by an extension of support for the model payment request initiated from Merchant to Payment Service Provider.
>

## Preconditions
This component covers the following: Participants: Principal, Buyer Agent, seller or Merchant side system, and Payment Service Provider for the payment of payments for receipt, verification and processing of funds.

Before entering this component, SHALL satisfies the following preconditions.

+ Principal has expressed a real-time purchase intention to Buyer Agent and Buyer Agent has pre-screened the rule with Cart Confirmation process to obtain information on Merchant-side orders to be paid.
+ Buyer Agent SHALL holds valid payment instrument references in `PSD-PMT-BND` for this payment scene.
+ Payment Service Provider SHALL be capable of verifying the validity of payment instrument references, verifying the integrity of Buyer Agent identifications and requests, and initiating a payment counter or confirmation interface for Principal upon completion of the examination.
+ The payment interaction process may be based on `PSD-PAY-A402` processes, or on the traditional Merchant process under the Merchant platform; the interface may be achieved through the MCP interface, the API interface, etc., and determined by Participants in consultation with the scene based on capacity.

## Process Steps
The following process describes the single, instant payment process. Buyer Agent enforces the corresponding rules of interaction with Payment Service Provider SHALL on the basis of the established payment interaction process (`PSD-PAY-A402` or traditional Merchant under platform) and the manner in which the corresponding interface is achieved (MCP interface, API interface, etc.).

**Step 1: Pre-payment**

Buyer Agent After completing commerce interaction with the seller’s service provider or Merchant side system, SHALL obtains the transaction identifier information necessary to connect the front-end commercial intent to the back-end settlement of funds.

+ Buyer Agent SHALL completes the rule pre-check with Cart Confirmation process and obtains Merchant side order number when using the Merchant sub-payment process.
+ When the `PSD-PAY-A402` access process is used, Buyer Agent may be responded to by the seller ' s services by `HTTP 402 Payment Required` and by `Payment-Needed` returning the corresponding order or resource identifier (e.g. `out_trade_no`, `resource_id`, etc.) for the current payment.

**Step 2: Construct and send immediate payment request**

Buyer Agent At the launch of Payment Service Provider, the request SHOULD contain at least the following core elements.

+ This request is for the sole global identifier to be used for weight proofing.
+ Merchant side order number to be used for product information consistency verification.
+ payment instrument Quoted for prior binding.
+ This payment is in the amount and in the currency of the payment.
+ Time stamp requested for the timescale verification of Payment Service Provider.
+ Buyer Agent Identity and signature of key elements of this request.

**Step 3: Payment Service Provider Basic verification**

Payment Service Provider After receiving immediate payment request, the basic verification, which includes, at a minimum, a request for a single marking to protect against re-entry, a request for a time stamp to be time-barred, a Buyer Agent signature validity check, and a payment instrument reference validity check, is completed.

For payment instrument quotation, Payment Service Provider SHALL confirms that it is unexpired, unexpired and consistent with the Buyer Agent identity binding that initiated this payment request.

If either of these checks is not passed, Payment Service Provider SHALL NOT continues to enter the register confirmation process and SHALL directly returns the corresponding failure result.

**Step 4: Call up the cashier and Principal for immediate confirmation**

After all basic verifications have been completed, Payment Service Provider SHALL calls to Principal the cashier or confirmation window.

At least SHALL display the amount of the payment and the currency, the name of the receipt Merchant and the corresponding field in payment request.

Principal Upon completion of the confirmation by means of biometric recognition, payment password, dynamic authentication code or other Payment Service Provider support, Payment Service Provider SHALL record the nuclei used for this confirmation and the confirmation time stamp as evidence of authorization for this payment.

This step is the core feature of the L1 scenario: Payment Service Provider SHALL complete User identity verification and confirmation for each payment before funds are debited. The identity verification method (e.g., facial recognition, fingerprint, QR-code scanning, password, or verification code) is determined by Payment Service Provider based on its risk-control strategy and terminal environment; this protocol does not prescribe a specific method.

**Step 5: Pay execution and status returns.**

Upon immediate confirmation Principal, Payment Service Provider SHALL interpret payment instrument references to the corresponding true payment account and effect the deduction or amount freeze.

The Payment Service Provider SHALL synchronously return the payment result to the Buyer Agent. The response SHOULD include at least the Payment Service Provider transaction identifier, Merchant order number, transaction status, and transaction timestamp.

The Payment Service Provider SHOULD also notify the Merchant-side system of the payment result to support order-status updates and subsequent fulfillment.

Upon completion of the payment transaction, Payment Service Provider SHOULD anecdotal events are reported at `act:payment:transaction-completed` to support subsequent dispute resolution and audit retroactive.

> **Notes:** Upon completion of payment, Buyer Agent may be used to access paid resources or services and trigger compliance:
>
> + When the `PSD-PAY-A402` access process is used, Buyer Agent may carry `Payment-Proof` another access to the paid resources or services, and the seller ' s service provider certifies the release of the resources or initiates performance, as defined by `PSD-PAY-A402`.
> + Resource access and compliance are defined by the interface corresponding to the Merchant platform when the Merchant platform line payment process is used.
>
> Regardless of the payment interaction process, the interface is available through the MCP interface, the API interface, etc.
>

## Processing of requests
+ Buyer Agent When constructed immediately payment request, SHALL to ensure consistency in the amount paid, currency and order information on side Merchant, and SHALL NOT to modify the identified core elements of the transaction without permission.
+ Payment Service Provider complete all basic verifications before the register is called; unverified request SHALL NOT enters the register confirmation process.
+ Payment Service Provider Shows payment information for Principal that is strictly consistent with the corresponding field in the request to ensure that Principal is confirmed with full knowledge.
+ In the L1 scenario, Payment Service Provider SHALL complete User identity verification and confirmation before funds are debited; a payment request for which identity verification and confirmation have not been completed SHALL NOT enter the funds-debiting stage. The identity verification method is determined by Payment Service Provider based on its risk-control strategy and terminal environment.

## Error Response
Error response in instant payment, SHOULD overwrites the following semantic categories.

|** Semantic Category**|** Annotations**|** Retry proposal**|
| --- | --- | --- |
|Request repeated.|The only marking requested has been used and the attack is suspected to be repeated.|SHALL NOT Directly retrying; SHALL replacement request only marked and restarted.|
|Expiry of request|The time stamp requested exceeds the valid window Payment Service Provider accepted.|The test may be repeated after the time stamp is regenerated and after confirmation that the request is still valid.|
|Invalid Agent signature|Buyer Agent signature verification failed|SHALL NOT retry directly; first correct the signature material or verify the identity binding relationship.|
|Invalid quote payment instrument|payment instrument Quotes do not exist, are no longer valid, expired or not available.|SHALL NOT Directly retry; SHALL may be rebound or replaced at payment instrument.|
|payment instrument citation does not match Agent identity|The current reference to payment instrument does not correspond to the identity binding of Buyer Agent for initiating the request.|SHALL NOT Directly retry; SHALL amend the binding relationship or replace the legitimate sponsor.|
|Confirm failure User|Principal Failed, cancelled or not confirmed within a specified time frame.|Re-launch confirmation may be permitted on the basis of operational strategy.|
|Payment execution failed|Following the adoption of the basic verification and confirmation User, the transfer of funds, the freeze of amounts or access to roads have failed by stage.|A decision may be made whether to allow a re-test based on the reasons for failure; the tunnel can be re-tried at short notice, and account or risk control abnormalities usually re-try directly at SHOULD NOT.|

# PSD-PAY-DEL: User-directed Delegated Payment (L2 scene)
## Overview
User-directed Delegated Payment (Delegated Payment, PSD-PAY-DEL) applies in the absence of Principal and is Intent Authorization Credential pre-issued on the basis of Principal and autonomously completes the scenario of procedural payments within the authorized boundary.

Unlike `PSD-PAY-INS`, the basis of authorization for this component is not Payment Service Provider real-time confirmation, but Principal pre-issued and valid at the time of payment. The scenario described in this component is also referred to as the L2 scenario in terms of security risk protection.

> Note: The current protocol only defines the model payment request initiated from Agent to Payment Service Provider, which will be followed by an extension of support for the model payment request initiated from Merchant to Payment Service Provider.
>

## Apply scene and prefix conditions
This component applies to User alibi (Human-Not-Present) and the object of the purchase is clearly defined in the initial interaction and directed commissioning scenario.

In the platform Agent scenario, in order to prevent User excesses and confusion with identity, payment of SHALL be made with attention to the binding of the platform Agent identity with the specific Principal identity; in the exclusive Agent scenario, payment is usually made directly by anchoring the exclusive Agent identity and may be further sequestered with the exclusive sub-account.

From the point of view of the payment interaction, the L2 scenario usually uses the traditional Merchant platform line payment process (Principal for pre-defined purchases, Agent for completion of orders and payments on the side of Merchant; when the subject of Agent access is provided in the form of a fee-paying resource or service, the PSD-PAY-A402 access process may also be used, with the seller's service initiating a payment claim through HTTP 402. Two payment interactions can be achieved through the MCP interface, the API interface, etc.

Before entering this component, SHALL satisfies the following preconditions.

+ Principal SHALL Completed intent and issued valid Intent Authorization Credential (IAC); Buyer Agent pre-checked with Cart Confirmation for Merchant outstanding order information.
+ At the level of payment instrument, Buyer Agent SHALL be either available for payment instrument or available for Agent-specific Sub-account and its payment authorization.
+ For requests for signature protection, identity binding, authorization credential verification and bottom key call mechanisms, this component does not repeat the definition of its security achievement, and the relevant capabilities can be supported by ASL identity, connection, authorization and key management capabilities.

## Process Steps
The following process describes the single-directed commissioning process. Buyer Agent and Payment Service Provider SHALL implement the corresponding interactive rules based on the defined payment interaction process and the manner in which the corresponding interface is achieved.

**Step 1: Agent end-end rule self-check**

Buyer Agent Before the tectonic commission payment request, SHALL to perform local pre-screening in conjunction with the currently held IAC, at least: IAC is valid, the current period falls within IAC the authorized period Scope, the current amount of payment does not exceed the maximum amount of a single amount, the sum of this amount and the cumulative amount of the locally saved deduction does not exceed the total authorized amount, the target Merchant is within Scope allowed, and the proposed use of payment method is in the permitted list payment method.

Local pre-screening is a pre-filtration mechanism of Buyer Agent; if the pre-screening is not passed, Buyer Agent SHALL NOT continues to initiate commissioning payment request.

**Step 2: Construct and send the commission payment request**

Buyer Agent When initiating the commission payment request to Payment Service Provider, the request SHOULD includes, at a minimum, the unique identification requested, the Merchant side order number, the full Intent Authorization Credential and its commissioning identifier, the amount and currency of the current payment, payment instrument certificates, the time stamp requested, and the Buyer Agent identification and signature of key elements.

When the exclusive sub-account is not used, payment instrument is usually payment instrument quoted in the output `PSD-PMT-BND`; when the exclusive sub-account is used, payment instrument is SHALL a secret of payment authorization generated by the sub-account identifier and its exclusive key.

The signature covers Scope SHOULD at least the unique identification, commissioning mark, Merchant side order number, payment amount, currency and time stamp of the request to ensure that the key elements are not tampered with.

**Step 3: Payment Service Provider side authorization verification**

Payment Service Provider After receiving the commission payment request, SHALL completes the rectification, Buyer Agent signature verification, IAC validity verification, IAC financial binding verification and, if necessary, semantic binding verification.

+ Validity verification IAC includes, at a minimum, verification of validity of signature IAC, IAC unexpired unsuspensed, Agent fiduciary identification in IAC consistent with the identification Buyer Agent in the request, and the commissioning mode is a valid enumeration value as defined in this protocol.
+ The financial layer binding verification includes at least single-value, cumulative and payment method matching verifications.
+ Semantic binding may be performed as required by achievement, e.g. to verify whether the receipt Merchant is in the permitted Merchant Scope or to compare the requested element to User original intent.
+ If an exclusive sub-account is used, Payment Service Provider shall also verify the authorization of payment generated by the exclusive key of the sub-account.

If any verification is not made, Payment Service Provider SHALL rejects the request and returns the corresponding failure semantic.

**Step 4: Payment execution and status returns**

After all verifications have been completed, the deductions or amounts of funds have been frozen at Payment Service Provider SHALL; when the exclusive sub-account has been used, the funds SHALL have been transferred or frozen directly from that sub-account.

The Payment Service Provider SHALL synchronously return the payment result to the Buyer Agent. The response SHOULD include at least the globally unique transaction identifier generated by the Payment Service Provider, the delegation identifier associated with the payment, the Merchant order number, transaction status, and transaction timestamp.

After receiving a successful response, the Buyer Agent SHALL update its local cumulative-debit cache using the successful transaction amount confirmed by the Payment Service Provider.

The Payment Service Provider SHOULD also notify the Merchant-side system of the payment result to support order-status updates and subsequent fulfillment.

Upon completion of the payment transaction, Payment Service Provider SHOULD anecdotal events are reported at `act:payment:transaction-completed` to support subsequent dispute resolution and audit retroactive.

> Note: Upon completion of payment, Buyer Agent may be used to access paid resources or services and trigger performance:
>
> + When the `PSD-PAY-A402` access process is used, Buyer Agent may carry `Payment-Proof` another access to the paid resources or services, and the seller ' s service provider certifies the release of the resources or initiates performance, as defined by `PSD-PAY-A402`.
> + Resource access and compliance are defined by the interface corresponding to the traditional Merchant platform line payment process.
>
> Regardless of the payment interaction process, the interface is available through the MCP interface, the API interface, etc.
>

## Processing of requests
+ Buyer Agent Before initiating commissioning, local pre-screening is completed and SHALL NOT requests that clearly exceed the authorized boundary continue to be sent to Payment Service Provider.
+ Buyer Agent SHALL ensure that the payment amount, payment currency, and Merchant-side order number in the delegated payment request are consistent with the preceding Cart Confirmation result.
+ Payment Service Provider Completing the validity verification and binding verification of IAC, and SHALL NOT continuing the non-approval request at the withholding stage, pending the processing of funds.
+ When the exclusive sub-account model is used, Payment Service Provider, in addition to verifying IAC, verify the validity of the sub-account status and its payment authorization secret and confirm its validity in relation to the current Buyer Agent identity and sub-account binding.
+ Payment Service Provider The determination of the cumulative amount is based on the amount of historical successful transactions that it has identified, while SHALL NOT relies only on Buyer Agent local statements.
+ The authorizing effect of commissioning payments SHALL be strictly limited to the boundary as defined in IAC, SHALL NOT exceeding the original authorization Scope by being procedurally implemented payment request.

## Error Response
Based on the syntax of the error response of the `PSD-PAY-INS` component definition, this section primarily expands the syntax of the error response associated with the use of Intent Authorization Credential (IAC) and the level boundary.

|** Semantic Category**|** Annotations**|** Retry proposal**|
| --- | --- | --- |
|IAC Expired|Intent Authorization Credential has exceeded its validity and cannot continue to be the basis of authorization for this commission.|SHALL NOT Directly retry; SHALL re-enactment of valid authorization.|
|IAC Cancelled|Intent Authorization Credential has been revoked and cannot continue to be paid for.|SHALL NOT Directly retry.|
|IAC Paused|Intent Authorization Credential is currently suspended and not available for new payment request.|Normally SHALL NOT is to be retried directly; SHALL be to be restored or reauthorized.|
|Unmatched identity Agent|The Buyer Agent identifier in IAC is not consistent with the Buyer Agent identifier in the request.|SHALL NOT Directly retry; SHALL Amend binding relationships or replace legitimate sponsors.|
|Single amount exceeding limit|This payment exceeds the single amount ceiling set at IAC.|SHALL NOT Directly retry; SHALL adjustment of amounts or reauthorization.|
|Cumulative amount exceeded|The sum of the current payment and the cumulative amount confirmed exceeds the total authorized amount of IAC.|SHALL NOT Directly retry; SHALL Adjustments or reauthorizations.|
|Insufficient balance|The debit account or the exclusive sub-account balance is insufficient to complete the current payment.|The operational strategy can be used to determine whether to try again after the balance has been replenished.|
|Merchant Not in Scope|Collections Merchant are not in the permitted Merchant Scope.|SHALL NOT Directly retry; SHALL Replace Merchant or reauthorize.|

# PSD-PAY-AUP: Autonomous Delegated Payment (L3 scene)
## Overview
Autonomous Delegated Payment (autonomous Delegad Payment, AUP) applies in the absence of Principal and is based on `BOUNDED` pre-issued `BOUNDED` model Intent Authorization Credential for the autonomous conduct of multiple rounds of commercial decision-making and payments within the authorized boundary.

As in `PSD-PAY-DEL`, the basis of authorization for this component is not Principal real-time confirmation on Payment Service Provider cashier, but Principal pre-issued and still valid at the time of payment Intent Authorization Credential. The difference is that the object of purchase for the `PSD-PAY-DEL` scenario is clearly identified in the initial interaction, Buyer Agent the payment is executed in accordance with the directive, and Buyer Agent the scenario is autonomous within the authorized boundary to determine the object of the transaction, the time of the transaction and the path of execution, and can initiate multiple payments within a mission cycle.

## Participants and prefix
This component covers Buyer Agent, the seller's service provider, Payment Service Provider PSP, and the ability to provide the upstream authorization base Authorization & Delegation Domain if required.

In the platform Agent scenario, in order to prevent User excesses and confusion with identity, payment of SHALL be made with attention to the binding of the platform Agent identity with the specific Principal identity; in the exclusive Agent scenario, payment is usually made directly by anchoring the exclusive Agent identity and may be further sequestered with the exclusive sub-account.

From the point of view of the payment interaction process, L3 under the scenario Buyer Agent usually uses `PSD-PAY-A402` access (a payment claim is initiated by the seller's service provider through HTTP 402); it may also use the traditional Merchant platform under-list payment process or other access option. Both types of payment interaction can be achieved through the MCP interface, the API interface, etc.

Before entering this component, SHALL satisfies the following preconditions.

+ Principal has completed and has been issued a valid `BOUNDED` model Intent Authorization Credential.
+ Buyer Agent has completed the task of dismantling and obtaining resources or service targets to be visited.
+ Buyer Agent Available at payment instrument; under an autonomous commissioning scenario, SHOULD completes the payment authorization in combination with Agent-specific Sub-account and its accompanying proprietary key capability.
+ If necessary, the buyer and seller can complete Payment Capability Negotiation on the basis of `CID-PCA-NEG`, specifying the method of payment for subsequent payments, Payment Service Provider, the target interface address and the corresponding payload structure description.
+ For requests for signature protection, identity binding, authorization credential verification and bottom key call mechanisms, this component does not repeat the definition of its security achievement, and the relevant capabilities can be supported by ASL identity, connection, authorization and key management capabilities.

## Process Steps
The following process describes the single Autonomous Delegated Payment process; the process can recur over a full mission implementation cycle. The process involves steps that interact with the payment access option, Buyer Agent with the seller's SHALL based on the payment interaction process (`PSD-PAY-A402` or the traditional Merchant single payment process under the platform) and how the corresponding interface is achieved (MCP interface, API interface, etc.).

**Step 1: Return of the seller ' s service provider ' s claim for payment**

Buyer Agent When requesting resources or services from a seller's service provider for which payment is required, the seller's service provider SHALL return the claim for payment according to the payment interaction process adopted. When using `PSD-PAY-A402` access, the seller service provider SHALL return the `HTTP 402 Payment Required` status code and declares the core parameters of this payment through `Payment-Needed` response head; SHALL return the claim for payment for the equivalent price in accordance with the corresponding process. Merchant This response was used to clarify to Buyer Agent the corresponding payment request for the visit, the payment time window and the basis for the subsequent request.

**Step 2: Buyer Agent Implementation of the rules on self-inspection in real time**

Buyer Agent Before deciding whether to continue paying, SHALL in conjunction with the currently held `BOUNDED` model Intent Authorization Credential and local task status implementation rules, self-checks include, at a minimum:

+ (a) Whether the current period is still in the validity of the mandate IAC;
+ Whether the sum of the cumulative amount paid and the current amount exceeds the total authorized amount of IAC;
+ Whether the current payment exceeds the maximum amount of IAC;
+ Whether the counterparty and the type of service meet the constraints IAC;
+ To be used payment method in the list of payment method allowed;
+ Whether payment instrument (including exclusive sub-accounts) is available.

Local cache cumulative payment recognition SHALL be calculated as the amount of the successful payment transaction returned by PSP; the default is zero before the first payment.

If either condition is not met, Buyer Agent SHALL NOT continues to initiate payment and SHALL terminates the transaction in accordance with the pre-set strategy, switchs the counterparty or informs Principal processing.

**Step 3: Buyer Agent Submitted payment request**

If self-checked, Buyer Agent SHALL be bound by this component scenario and the normative structure of the access programme payment request and submitted to PSP for processing.

SHALL in payment request includes the `BOUNDED` model on which this payment is based and its commissioning identifier, transaction identifier information, payment amount and currency, payment instrument certificate, request time information, and Buyer Agent signature for key elements.

When the exclusive sub-account is not used, payment instrument is payment instrument quoted in the output `PSD-PMT-BND`, and when the exclusive sub-account is used, payment instrument is SHALL be the document generated by the sub-account SHALL and its exclusive key to authorize payment, consistent with payment instrument for `PSD-PAY-DEL`.

**Step 4: PSP Verification**

After receiving payment request, SHALL completes the following in turn:

+ (b) Validation of the weight check, Buyer Agent signature;
+ Validity of `BOUNDED` model Intent Authorization Credential (valid signature, unexpired unsuspensed, entrusted Agent identifier consistent with Buyer Agent identifier in request, valid list value);
+ Financial-level binding verification (single cap, cumulative cap, payment method matching);
+ Semantic binding verification (receipt Merchant in IAC permitted Scope and consistency of request elements with User's original intent);
+ Audit of account status, balance and risk control strategy.

If an exclusive sub-account is used, PSP also SHALL validates the validity of the payment authorization message generated by the exclusive key to the sub-account and verifies the balance or amount available for the sub-account. If any verification is not made, the PSP SHALL rejects the request and returns the corresponding failure syntax.

**Step 5: Payment execution and status returns**

The PSP returns to Buyer Agent a certificate of the results of the payment, which includes at least SHOULD the only global trade flow code generated by Payment Service Provider, the commissioning identifier for this payment connection, the status of the transaction and the time stamp.

Upon receipt of a successful response, SHALL updates the local cumulative debit cache with PSP recognition of successful transaction amounts. The PSP SHOULD sync will notify payment result side system Merchant to support order status updates and subsequent performance processing.

Upon completion of the payment transaction, PSP SHOULD be reported as `act:payment:transaction-completed` certificated events providing a factual basis for subsequent audits, dispute processing and task billings.

> Note: Resource visits, certificate validation and performance delivery after payment is completed, implemented on the basis of the payment interaction process used:
>
> + When the `PSD-PAY-A402` access process is used, Buyer Agent carries the `Payment-Proof` re-access to the resource at the head of the request; the seller ' s service is directed to verify the validity, non-repetition and consistency of the PSP certificate with the current resource access request, returning the validation results through `Payment-Validation` response head and releasing the resource or initiating performance. Specific interactive details are defined by `PSD-PAY-A402`.
> + When a traditional Merchant platform line payment process is used, resource access, certification and performance delivery are defined by the interface to which the process corresponds.
>
> The specific interactive mechanisms for service performance, compliance buy-back and archiving confirmation are defined by the rules of the access programme and the corresponding payment methods used.
>

## Processing of requests
+ Buyer Agent Before initiating Autonomous Delegated Payment, SHALL complete the local rule self-check and SHALL NOT continue to send requests that clearly exceed the authorized boundary in `BOUNDED` mode IAC to PSP.
+ Buyer Agent SHALL ensure that the payment amount, payment currency, and Merchant-side order number in the payment request are consistent with the preceding commercial confirmation result.
+ The PSP completes the validity verification and binding verification of IAC pending the processing of funds, and SHALL NOT continues the non-approval request to the deduction phase.
+ When the exclusive sub-account model is used, the PSP, in addition to verifying IAC, verifys the validity of the sub-account status and its payment authorization secret and confirms its validity in relation to the current Buyer Agent identity and sub-account binding.
+ PSP's assessment of the cumulative amount is based on the amount of historical successful transactions that it has identified, while SHALL NOT relies only on Buyer Agent local statements.
+ The validity of the authorization Autonomous Delegated Payment is strictly limited to the boundary defined in the `BOUNDED` model IAC, and SHALL NOT is exceeded by the procedural implementation of payment request the original mandate Scope.

## Error Response
Based on the `PSD-PAY-DEL` definition of error response syntax, the wrong response of this component is mainly related to the `BOUNDED` model IAC and the autonomous entrusting boundary. The wrong response of the access program (e.g. payment authorization certificate certification error) is defined by `PSD-PAY-A402` or the corresponding access program regulation by `PSD-PAY-A402`.

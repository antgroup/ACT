# ACT 2.1 Commerce Interaction Domain

[中文](commerce-interaction.md) | English

> **Status: ACT 2.1 Specification / Final / Informative English Translation**
> **Translation status: Official English translation / Informative**
> **This English edition is a complete translation of the finalized Chinese specification published on 2026-08-11. The Chinese edition is authoritative if the two editions differ.**
> **The Chinese ACT 2.1 publication remains controlling if the two editions differ.**

# Scope
## Domain Positioning
Commerce Interaction Domain (Commerce Interaction Domain, CID) provides for a uniform, citation and commerce interaction synonym between Agent and Merchant, Merchant-side Agent or other Agent for the pre-payment identification of goods or services, Intent Context transmission, alignment of capacity to pay and transaction recognition.

## Domain Responsibilities
This domain covers the following:

+ (b) Minimum information requirements for the discovery of goods and services;
+ Organization, transmission and return of candidate results Intent Context;
+ Payment Capability Advertisement, capacity recognition and capacity consultation;
+ Cart Confirmation, pre-checking of rules and confirmation of transactions;
+ Pre-payment business consensus to form key objects, state semantics and cross-domain reference relationships.

The following are not regulated in this domain:

+ Agent Internal decision algorithms, ranking strategies, preference extrapolations and model reasoning processes;
+ Merchant In-house operations processing, stock deductions, order management and performance systems achieved;
+ Generic multi-operative Agent collaboration protocols, tasking and service discovery protocols;

# The list of components and relationships in this field
## Component Overview
Commerce Interaction Domain consists of four protocol components that jointly complete the full chain from the discovery of goods or services, Intent Context transfer and pre-payment capacity, to the completion of the transaction and the beginning of the payment phase.

The functional positioning of the components is as follows.

+ **CID-MER-CAT: Merchant Catalog interface.** Regulates the minimum information requirements when opening the catalogue of goods or services in structured form to Merchant to support machine-readable goods or services.
+ **CID-INT-XFR: Intent Context Passage.** Responsible for regulating the Buyer Agent transmission of Intent Context to Merchant or to the platform in relation to the current mandate, and for receiving requests/responses to the outcome of the candidate goods or services.
+ **CID-PCA-NEG: Payment Capability Negotiation.** It is responsible for regulating the process of capacity statements and consultations between buyers and sellers before payments can be made, using payment method, Payment Service Provider, interface endpoints and associated load modes.
+ **CID-CART-CFM: Cart Confirmation.** Be responsible for regulating the process of final confirmation and pre-checking of rules on the subject matter of the transaction, the amount, conditions of performance and related constraints before entering the payment process Buyer Agent.

## Core Object & Identification
Commerce Interaction Domain uses a standard core set of objects and identifiers to describe key information at the pre-payment stage. The core objects of the domain and their role can be summarized as follows.

|** Object or Identification**|** Meaning**|** Mainly Generate Location**|** Main Use Location**|
| --- | --- | --- | --- |
|Intent Context|Buyer Agent Structured Intent Information around Current Tasks, Carrying Needs, Constraints and Necessary Backgrounds, and Upstream Inputs as Commodity Screening, Matching and Transaction Recognition|ADD-INT-ICS, also constructed locally by Buyer Agent based on upstream intent objects, if necessary|Candidate matching process CID-INT-XFR, CID-CART-CFM, and Merchant or platform|
|Results of candidate goods or services|Merchant, platform or selleragent returned the structured candidate results for the pre-screening, comparison and follow-up rule test at Buyer Agent|CID-MER-CAT、CID-INT-XFR|CID-CART-CFM and Buyer Agent local decision-making processes|
|Transaction confirmation result|The final confirmation of the order as a result of phase Cart Confirmation typically includes the subject matter of the transaction, the amount, Merchant identification, the order transaction number and related confirmation time information|CID-CART-CFM|Payment Services Domain, and trusted attestation with ex post facto dispute resolution support|
|Results Payment Capability Negotiation|Convergence between buyers and sellers on the use of payment method, Payment Service Provider, interface endpoints and methodological models|CID-PCA-NEG|payment request Construction and implementation of subsequent Payment Services Domain|

## Dependence and Cross-domain Reference
Both CID-MER-CAT and CID-INT-XFR may be used as upstream sources for candidate products or service outcomes to provide subsequent Cart Confirmation input.

The role of CID-PCA-NEG occurs primarily in the pre-payment phase and is used to determine, if necessary, the payment method, Payment Service Provider and interface endpoints used for the transaction, thus providing the basis for the subsequent payment request construction.

CID-CART-CFM is the key component in the field for pre-discovering, screening, negotiating and forming the final confirmation of the order level, the output of which will have a direct impact on whether the subsequent Payment Services Domain can initiate payment execution.

Authorization & Delegation Domain provides the domain primarily with ISR and the context of the relevant constraints; Payment Services Domain refers primarily to the transaction confirmation results, order transaction numbers, Payment Capability Negotiation results; Trust Services Domaintrusted attestation sub-sections harmonize the maintenance of the type of relevant event and certificate governance rules, and do not repeat the definition. Agent credit association statements defined in sub-section credit association can be used to assist judgement of the local domain ' s authorized link, such as the identification and screening of goods or services, and the transmission of Intent Context, but may not replace the inspection, confirmation and consultation rules prescribed by the components of this domain.

# CID-MER-CAT: Merchant Catalog Interface
## Overview
Merchant Catalog Interface (Catalog Interface, CID-MER-CAT) sets the minimum information requirements for Merchant opening a structured catalogue of goods or services to Agent to support machine-readable discovery of goods or services. The candidate goods or services output of this component may serve as upstream input for Buyer Agent subsequent comparative decision-making and Cart Confirmation.

The current version of this component does not define a uniform catalogue protocol for the time being, but provides for the minimum information requirements to be met by SHALL before commerce interaction enters the follow-up.

This component does not regulate the sorting logic of cataloguing, recommended algorithms, Merchant internal commodity modelling, and internal processing Merchant such as stock deductions, price calculations and order performance.

## Participants and prefix
This component involves the following Participants: Merchant or platform for providing information on goods or services, and Buyer Agent for initiating cataloguing visits and consuming returns.

Before entering this component, SHALL satisfies the following preconditions.

+ Merchant or the platform already has the capacity to provide external information on structured goods or services.
+ Buyer Agent The basic commercial context relevant to the current mission has been established and allows for local screening, comparison or subsequent confirmation of return results.
+ When the subsequent link needs to be tested under user intent against the binding enforcement rules, Buyer Agent SHALL be able to link the directory back to the relevant Intent Context provided by Authorization & Delegation Domain.

## Minimum return information requirement
Merchant returned catalogue data for goods or services SHALL meet the minimum information availability requirement to ensure that follow-up commerce interaction and confirmation before payment can proceed normally.

For each item of goods or services available for Buyer Agent consumption, the return result SHALL contain the following information.

+ Goods or services identification, SHALL, is the only globally or in the Merchant domain that can be deciphered.
+ Trade name or service name, SHALL may support Buyer Agent and subsequent processing to identify the subject of the transaction.
+ Commodity group or service category, SHALL support subsequent alignment with user intent binding.
+ Clear pricing and currency units, SHALL support value comparisons, rule pre-tests and pre-payment confirmations.

In addition to the minimum information required above, the return result on the side of Merchant SHOULD further contains the following information.

+ Current stock, marketable status or service availability.
+ The price is valid at the deadline or the price update.
+ Anticipated delivery times, time limits for performance or service delivery.
+ Merchant Identification, Merchant Reference Address or Trade Details Reference Address.

Buyer Agent SHOULD NOT is used directly for Cart Confirmation or for payment of pre-connection when the results of the directory cannot be satisfied. When the return result is only shown and is not sufficient to support the pre-checking of the rules, the achiever SHOULD supplements the necessary fields before entering CID-CART-CFM.

> The current version of ACT does not provide for uniform access paths, request methods, authentication mechanisms and page breaks for the directory interface.
>

## Statement of compatibility
This may be achieved in conjunction with existing industry protocols, Merchant open interfaces or existing catalogue services of the platform, as long as its return results meet the minimum information requirements specified in this component.

# CID-INT-XFR: Intent Context Passage
## Overview
Intent ContextTransfer, CID-INT-XFR provides for Buyer Agent transmission to Merchant or to the platform of Merchant and receives a request/response process for the results of the candidate goods or services. Intent Context used for this component may be quoted as ISR and associated binding syntax, and may be entered upstream as a follow-up candidate selection, pre-test and Cart Confirmation.

This component deals with the matching of intent transmission with candidate at the pre-payment stage and does not regulate internal intent understanding, preference extrapolation and decision algorithms Buyer Agent.

## Participants and prefix
This component involves the following Participants: Buyer Agent for initiating the intended request, and Merchant for receiving the request and returning the candidate results, the platform or its proxy interface.

Before entering this component, SHALL satisfies the following preconditions.

+ Buyer Agent The basic commercial context relevant to the current mission has been established and can be constructed to transmit Intent Context.
+ Merchant or the platform already has the capacity to receive intended requests and return to structured candidate results.
+ When the subsequent link needs to be tested against User objectives and binding enforcement rules, Buyer Agent SHALL be able to connect Intent Context to the relevant binding synonyms provided by Authorization & Delegation Domain.

## Composition Intent Context
Buyer Agent Passes Intent Context SHALL organize around current tasks and can support Merchant or platform matching. Intent Context typically include the following.

+ Visible intent demand, i.e. User clearly expressed purchase target or service demand.
+ Implicit intent needs, i.e. Buyer Agent supplementary needs based on the context of the current mandate, User confirmed information or continuous interactive content.
+ Limitations, i.e., amount, category, Merchant, time for performance, etc., relevant to the task.
+ The necessary background information, i.e. the additional context required to complete the candidate matching.
+ Preferable information that may be transmitted with the permission of the realizing party and subject to the applicable conditions.

Visible intent needs and constraints SHOULD be the main components of Intent Context. Implicit intent needs and preferences can be transmitted as optional messages that conflict with the authorized boundary as expressed in ISR/ IAC by User explicitly identified binding conditions or Authorization & Delegation Domain.

When transmitting information about hidden intent needs or preferences, the achiever SHALL processes the relevant informed consent and data protection requirements on its own.

## Requests and responses
Buyer Agent When initiating a request for intent, SHALL constructs can be analysed by Merchant or the Platform. The request contains the following key elements.

+ Request for marking to be used only to mark the current request and to support a response link.
+ Intent Context related to current mandate.
+ Link identifiers used when cross-domain linkages are required.
+ Required binding conditions and responsiveness to formal requirements.
+ Request for authentication information from sources.

At least SHALL contain details of the goods or services that can be selected for subsequent screening and confirmation. When Merchant or the platform is unable to return the valid candidate, SHALL return the wrong response and gives the wrong synonym that can be identified by Buyer Agent.

## Dynamic Update and Wrong Semantics
Buyer Agent SHALL Supports the dynamic update of Intent Context in multiple rounds of interaction. Each dynamic update generates a new request identifier and links it to the previous request. The dynamic update request SHOULD carries only the intended content of this change.

When Merchant or the platform is unable to process the request normally, the wrong synonym SHOULD cover the categories of error in format, lack of matching results, restricted access, restricted conflicts and excessive frequency of requests. Buyer Agent Depending on the type of error, retrying, switching Merchant, adjustment request or notification User.

## Multiple Merchant route
In the actual business network, Buyer Agent can be accompanied by a request for intent to multiple Merchant or platforms and a summary of the results of each party’s return. The comparison of the results with the final decision is Buyer Agent local processing, which is not part of this component instruction Scope.

> Note: Where key business nodes need to be recorded, this will be achieved before the `act:commerce:decision-logged` event marker is used for follow-up certificate processing after the decision is completed.
>

# CID-PCA-NEG: Payment Capability Negotiation
## Overview
Payment Capability Negotiation (Payment Capitalisation, CID-PCA-NEG) provides for a process of capacity statement and consultation between buyers and sellers on the use of payment method, Payment Service Provider, interface endpoints and related load modalities before entering payment execution.

This component applies mainly to multiple agentic commerce interactive scenarios in which the seller Agent participates, as well as to other scenarios where capacity to pay needs to be aligned before payment is made. The output of this component Payment Capability Negotiation can be used as a follow-up Payment Services Domain construct payment request and input to choose the payment path.

This component does not define common service discovery, information exchange, tasking and collaborative interaction protocols, but only regulates the semantics of Payment Capability Advertisement and Payment Capability Negotiation required to pay for the pre-connection.

## Participants and prefix
This component involves the following: Participants: Buyer Agent initiating Payment Capability Negotiation, and Merchant external declaration of capacity to pay and return to the results of the consultations, Agent seller or its proxy interface.

Before entering this component, SHALL satisfies the following preconditions.

+ The buyer and the seller have developed a basic commercial context in which to enter the pre-payment phase.
+ Buyer Agent already identifies the amount of the transaction, the currency, the subject of the transaction and other necessary transaction parameters.
+ The seller ' s side has the capability to publish Payment Capability Advertisement or respond to Payment Capability Negotiation requests.
+ When the transaction is subject to user intent or authorized boundaries, Buyer Agent SHALL be able to determine the availability of the candidate payment method according to the relevant binding syntax.

## Payment Capability Advertisement
### Declaration Mode
The seller's side can make its Payment Capability Advertisement public through a standardized path. Under the seller's Agent scene, Payment Capability Advertisement can be published through `capabilities` node in its Agent Card, with a statement of the mode of consultation supported by the seller and the corresponding interface address.

Payment Capability Advertisement SHALL be able to convey the following message.

+ Modalities for consultations supported by this party.
+ The list of payment methods supported by this side.
+ Each corresponding Payment Service Provider identifier.
+ Each corresponding payment interface endpoint payment method.
+ Each corresponding load mode or description of the payload structure payment method.

When the seller's side supports the one-way declaration model, SHALL in its public capability description is able to provide `capability_url` or equivalent capability statement portals, for example, Agent Card:

```plain
{
  "agent_id": "did:act:alipay.com/Agent-alice-001",
  "capabilities": {
    "act:payment:negotiation": {
      "mode": "one-way",
      "capability_url": "https://merchant.com/.well-known/act-payment-capability.json"
    }
  }
}
```

When the seller's side supports the two-way negotiation model, SHALL of its public capability description provides `negotiation_endpoint` or the interface portal for the equivalent, for example, Agent Card:

```plain
{
  "agent_id": "did:act:enterprise.com/premiumbot-02",
  "capabilities": {
    "act:payment:negotiation": {
      "mode": "two-way",
      "negotiation_endpoint": "https://api.enterprise.com/act/payment/negotiate"
    }
  }
}
```

### One-way declaration mode
The one-way declaration model applies to a scenario where the seller side is fully open Payment Capability Advertisement, Buyer Agent which is directly accessible without additional consultation and interaction. Under this model, Buyer Agent SHALL reads Payment Capability Advertisement which is publicly available on the seller side and selects payment method from `supported_methods` the candidate matching the terms of the transaction.

When Buyer Agent is bound by payment method from an upstream intention or authorized boundary, SHALL be chosen only from a candidate payment method that meets the relevant restriction.

Buyer Agent After the screening has been completed, SHALL extracts the corresponding `method_id`, `psp_id`, `endpoint` and `method_schema_url` for subsequent payment request construction input.

If there is no available match in the public statement payment method, Buyer Agent SHALL NOT continues to be paid.

Examples of the format of the capacity to pay document (`act-payment-capability.json`) are as follows:

```plain
{
  "version": "1.0",
  "role": "payee",
  "agent_id": "did:act:merchant.com/servicebot-01",
  "supported_methods": [
    {
      "method_id": "urn:act:payment:alipay",
      "psps": [
        {
          "psp_id": "urn:act:psp:alipay-official",
          "endpoint": "https://openapi.alipay.com/act-psp/v1",
          "method_schema_url": "https://alipay.com/act/schemas/payment-payload.json"
        }
      ]
    }
  ]
}
```

### Two-way consultation model
The two-way consultation model applies to situations where the seller ' s side needs to match payment method with the context of the buyer ' s request. Under this model, Buyer Agent SHALL initiate a request for consultation with `negotiation_endpoint` declared to the seller ' s side.

The request SHOULD contain at least the following elements.

+ `agent_id`, to mark Buyer Agent for initiating consultations.
+ `buyer_supported_methods` for a list of payment method acceptable to the buyer at present.
+ `currency`, to be used to declare the currency of the transaction.
+ `estimated_amount`, to be used to state the estimated amount of the transaction.

Upon receipt of the request by the seller, SHALL return the result of capacity to pay that matches the current terms of the transaction. `supported_methods` SHOULD in the response contains at least the following elements.

+ `method_id` for marking success payment method.
+ `psp_id` for marking Payment Service Provider corresponding to payment method.
+ `endpoint`, to identify the target interface address for follow-up payment request.
+ `method_schema_url` to identify the corresponding payment load description for payment method.

When `supported_methods` is empty, SHALL be deemed to have failed to complete the matching of capacity to pay. In that case, Buyer Agent SHALL NOT continues to enter the payment phase and SHALL decides whether to replace payment method, replace the counterparty or terminate the transaction in accordance with the business strategy.

The examples are as follows:

**First step (buyer initiated)**: Buyer Agent Send HTTP POST request to `negotiation_endpoint` declared by seller Agent containing a list of payment method intended items supported by buyer, currency and estimated amount:

```plain
{
  "agent_id": "did:act:platform.com/Agent-alice-001",
  "buyer_supported_methods": ["urn:act:payment:alipay", "urn:act:payment:credit_card"],
  "currency": "CNY",
  "estimated_amount": 500.00
}
```

**Second step (seller response)** The seller Agent returns the matching payment method and the corresponding PSP information:

```plain
{
  "supported_methods": [
    {
      "method_id": "urn:act:payment:alipay",
      "psp_id": "urn:act:psp:alipay-official",
      "endpoint": "https://openapi.alipay.com/act-psp/v1",
      "method_schema_url": "https://alipay.com/act/schemas/payment-payload.json"
    }
  ]
}
```

If the response `supported_methods` is empty, it indicates that the parties have no available common payment method and that the transaction cannot continue, Buyer Agent SHALL suspends the process and gives feedback to Principal.

## Outcome of the consultations
The final output of Payment Capability Negotiation aligns a set of capabilities available for subsequent payment. The result is at least SHALL to specify four parameters: `method_id`, `psp_id`, `endpoint` and `method_schema_url`.

Where there are multiple optional outcomes, the selection logic is Buyer Agent locally and this component is not specified.

## Security Considerations
Buyer Agent Before using Payment Capability Advertisement (`act-payment-capability.json`), the source should be verified and the statement confirmed as having been issued by the business's stated capability address (`capabilityurl`).

Buyer Agent In the analysis of `supported_methods`, the paragraphs `pspid`, `endpoint`, and `methodschemaurl` are checked consistently to avoid Payment Service Provider unauthorized access due to the falsification, alteration or replacement of a capability statement.

Payment Capability Advertisement for failure to confirm the source or key fields, Buyer Agent may not continue to use its initiation of a subsequent capacity to pay matching or payment process.

# CID-CART-CFM: Cart Confirmation
## Overview
Cart Confirmation(Cart Regulation, CID-CART-CFM) requires Buyer Agent to enforce the treatment requirements for final confirmation of the subject matter, amount, terms of performance and related constraints of the transaction before entering the payment process.

This component assumes the responsibility for order-level confirmation in the pre-payment phase, which is used to anchor the results of front-line goods or services discovery, candidate screening, matching of conditions and matching of capacity to pay into the confirmation of transactions that can be entered into payment execution.

This component does not regulate internal candidate comparison algorithms, ranking strategies and decision logic Buyer Agent or internal order management, inventory deductions and compliance systems.

## Participants and prefix
This component involves the following Participants: Buyer Agent for initiating the confirmation of the transaction, and Merchant for receiving the confirmation request and generating the order-level result, platform, seller Agent or its proxy interface.

Before entering this component, SHALL satisfies the following preconditions.

+ Buyer Agent Candidatures for identifiable goods or services have been obtained.
+ The subject matter of the transaction, the amount, currency and necessary performance information are clearly identified.
+ When the transaction is controlled by User objectives, bounds or authorized borders, Buyer Agent can be quoted in the relevant meanings of intent and constraint provided by Authorization & Delegation Domain.

## Pre-test for rules
Cart Confirmation Before formally submitting Cart Confirmation to the counterparty and obtaining the order transaction number, Buyer Agent SHALL pre-tests the rules for enforcement of the transaction to be confirmed, based on the relevant intent and binding information of the current mission. Buyer Agent SHALL When the transaction involves commissioning payments, further verification is performed in conjunction with the language of the authorized boundary provided by Authorization & Delegation Domain.

The pre-check SHOULD of the rules covers the following dimensions.

+ The amount test, including whether the single sum exceeds the permitted amount Scope and whether the cumulative amount boundary is exceeded at the time of the cumulative constraint.
+ The category Scope test, i.e. whether the goods or services to be purchased meet the permitted category or do not trigger the prohibited category restriction.
+ MerchantScope test, i.e. whether the counterparty meets the permitted Merchant or does not trigger the ban Merchant.
+ The time limit test for performance, i.e. whether the expected delivery, delivery or service performance time meets the established requirements.
+ The price tolerance test, i.e. the final confirmation that the price falls within Scope permitted price fluctuations.

Additional tests may also be added to the above when the realizing party has other business-related necessary verification items, but SHALL NOT weakens the basic verification semantics of this component definition.

## Treatment when the test is failed
Buyer Agent SHALL NOT goes directly to the payment stage when either rule pre-checks are not passed.

+ Buyer Agent SHALL be implemented in accordance with the intended or authorized transboundary disposal strategy in the border.
+ If the transboundary disposal strategy is suspended and notified, Buyer Agent SHALL suspends the current confirmation process and waits for User recertification or adjustment of the constraints.
+ If the cross-border treatment strategy is automatically cancelled, Buyer Agent SHALL terminates the current commerce interaction and records the reasons for the cancellation.
+ If no clear transboundary treatment strategy is foreseen, Buyer Agent SHOULD defaults on a suspended and notified treatment.

## Submit lock and order generation
When the pre-rule test is passed, Buyer Agent may be submitted to the counterparty with a request Cart Confirmation. The confirmation request SHOULD includes, at a minimum, the details of the goods or services to be identified, the final price, the currency, the performance requirements and the relevant context as necessary.

After accepting a request for confirmation, the counterparty should lock the relevant price, inventory or service capacity to the order level and generate the order transaction number back to Buyer Agent. The order transaction number returned by the counterparty SHALL be able to be consistently quoted at the subsequent payment execution stage.

When the counterparty is unable to complete the order locking, SHALL return a clear failure or incorrect semantic, and Buyer Agent SHALL NOT the confirmation is considered successful.

## Transaction confirmation result
Upon completion of Cart Confirmation, Buyer Agent SHALL forms the confirmation of the transaction.

The transaction confirmation results SHOULD include at least the following.

+ Details of goods or services identified.
+ Final recognition of the amount and currency.
+ Counterpart identification.
+ Order trade number.
+ Confirm time information.
+ Link identifiers used when cross-domain linkages are required.

> Note: When key commercial nodes need to be recorded, this will be achieved in order to use the `act:commerce:cart-confirmed` event marker for follow-up certificate processing after Cart Confirmation completion.
>

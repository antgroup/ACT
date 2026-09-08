# ACT 2.1 Documentation

This directory is the human-readable ACT 2.1 documentation set. ACT 2.1 is published in Chinese with an official informative English translation. If a translation discrepancy is found, the Chinese publication remains controlling until the translation is corrected in a subsequent repository release.

| Document | English | 中文 |
|---|---|---|
| Specification overview | [English](specification/overview.en.md) | [中文](specification/overview.md) |
| Authorization & Delegation Domain | [English](specification/authorization-delegation.en.md) | [中文](specification/authorization-delegation.md) |
| Commerce Interaction Domain | [English](specification/commerce-interaction.en.md) | [中文](specification/commerce-interaction.md) |
| Payment Services Domain | [English](specification/payment-services.en.md) | [中文](specification/payment-services.md) |
| Trust Services Domain | [English](specification/trust-services.en.md) | [中文](specification/trust-services.md) |
| Scenarios and Business Flows (non-normative) | [English](specification/scenarios.en.md) | [中文](specification/scenarios.md) |

Non-normative Alipay integration guides: [A402 payment access](../integrations/alipay/a402.en.md) / [中文](../integrations/alipay/a402.md), and [commerce-to-payment connection](../integrations/alipay/commerce-payment-negotiation.en.md) / [中文](../integrations/alipay/commerce-payment-negotiation.md).

- [Glossary](glossary.md)
- [FAQ](faq.md)
- [TSD-CRD Reference Implementation guide](../integrations/tsd-crd/README.md)

Protocol requirements are defined only by the overview and four domain specifications. The scenario guide and integration guides are non-normative. Runnable artifacts are under [`code/`](../code/README.md), while reference implementation guidance and product-specific implementations are under [`integrations/`](../integrations/README.md).

TSD-CRD is a normative subprotocol of the ACT 2.1 Trust Services Domain. Its optional `reference-v1` machine profile and runnable reference implementation are under [`code/schemas/tsd-crd/`](../code/schemas/tsd-crd/README.md) and [`code/samples/tsd-crd-reference/`](../code/samples/tsd-crd-reference/README.md); human-readable implementation guidance is centralized under [`integrations/tsd-crd/`](../integrations/tsd-crd/README.md).

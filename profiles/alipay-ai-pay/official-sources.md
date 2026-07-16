# Official product sources

> Status: Active source registry  
> Snapshot date: 2026-07-16

Alipay AI Pay public documentation is the product fact source. ACT documentation links to these pages instead of copying onboarding, sandbox or API tutorials.

## Source registry

| Source ID | Public source | Scope | Used for |
|---|---|---|---|
| AP-SRC-001 | [Alipay AI Pay overview](https://aipay.alipay.com/docs/overview.html) | Product selection and public install prompts | Scope and developer routing |
| AP-SRC-002 | [Agent Payment product page](https://aipay.alipay.com/agentpay) | Agent wallet and payment product positioning | Agent Payment overview |
| AP-SRC-003 | [AI wallet guide](https://aipay.alipay.com/wallet-guide) | Skill installation, wallet application, authorization and binding | Agent Payment journey |
| AP-SRC-004 | [Official Payment Skills repository](https://github.com/alipay/payment-skills) | Public Skill packages and supported payment scenarios | Skill/CLI Binding |
| AP-SRC-005 | [AI Metered Payment product page](https://aipay.alipay.com/callpay) | HTTP 402 and paid API/MCP/Skill positioning | Metered Payment overview |
| AP-SRC-006 | [AI Metered Payment integration guide](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | `Payment-Needed`, `Payment-Proof`, signing, verification and fulfillment | HTTP 402 provider alignment |
| AP-SRC-007 | [Payment verification API](https://ideservice.alipay.com/cms/site/0j7uot) | `alipay.aipay.agent.payment.verify` request, response and errors | Verification and error mapping |
| AP-SRC-008 | [Fulfillment confirmation API](https://ideservice.alipay.com/cms/site/0j7sw0) | `alipay.aipay.agent.fulfillment.confirm` request, response and errors | Fulfillment and error mapping |
| AP-SRC-009 | [Official AI Pay 402 example](https://github.com/alipay/ai/tree/main/code_example/aipay-402-example) | Provider-side example code | Validation reference, not normative source |
| AP-SRC-010 | [Traditional merchant Skill payment guide](https://aipay.alipay.com/docs/skillpay.html) | Merchant order Skill and cashier link handoff | Cashier payment boundary |
| AP-SRC-011 | [Machine-readable documentation index](https://aipay.alipay.com/docs/llms.txt) | Public documentation discovery | Weekly source drift check |

## Source precedence

When public materials differ, use the following review order:

1. Current Alipay Open Platform API documentation for exact API parameters and error codes.
2. Current Alipay AI Pay integration guide for the product flow.
3. Official Alipay open-source Skill or example for executable behavior.
4. Product and marketing pages for product positioning.

A difference between sources must be recorded as `PRODUCT-REVIEW`; example code must not silently decide the profile requirement.

## Weekly drift check

Until the conference release, the profile owner checks these sources once per week and records:

- page availability and URL changes;
- page update timestamps;
- install command or package changes;
- Header, field, API and error-code changes;
- sandbox and onboarding changes;
- changes in the declared support for API, MCP Tool or Skill.

The 2026-08-28 release candidate must record its final product source snapshot date.

## Public-only rule

- Internal documents may identify a question but cannot be the sole evidence for a public requirement.
- If a product behavior cannot be supported by a public source, label it `PRODUCT-REVIEW` and exclude it from conference conformance until confirmed publicly.
- Do not copy credentials, private test data, internal URLs or internal operating procedures into this directory.

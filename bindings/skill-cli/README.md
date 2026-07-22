# Skill/CLI Binding

> Status: Preview / Non-normative

The conference buyer baseline uses the official Alipay wallet and payment skills. It is a workflow-level Binding: a command or skill turn may package wallet readiness, user authorization, payment execution, status query, proof submission, original-request retry, and result delivery.

The host Agent must still preserve:

- the user's original intent;
- a comprehensible transaction summary;
- the original paid-resource request;
- the distinction between pending, successful, failed and authorization-required results;
- enough non-sensitive evidence to resume or audit the task.

The host must not extract secrets from logs, manufacture `Payment-Proof`, or treat a locally mocked result as payment success.

Official installation and behavior are maintained by [alipay/payment-skills](https://github.com/alipay/payment-skills). Runnable entry: [Agent Payment Quickstart](../../quickstarts/alipay/agent-payment/README.md).

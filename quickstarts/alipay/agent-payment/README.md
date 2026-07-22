# Agent Payment Quickstart

> Scope: buyer Agent, L1 `PSD-PAY-INS` + candidate `PSD-PAY-A402` through the official Skill/CLI Binding

This Quickstart installs no private ACT payment implementation. It verifies the local prerequisites and then hands payment to the public Alipay package.

## 1. Run the local preflight

Requires Node.js 18 or newer.

```bash
cd quickstarts/alipay/agent-payment
npm run preflight
```

The check does not download software or ask for credentials. It prints the official next command and reports whether `alipay-bot` is already available.

## 2. Install the official payment capability

Run the command currently published by [alipay/payment-skills](https://github.com/alipay/payment-skills):

```bash
npx -y @alipay/agent-payment@latest install
```

If only the CLI is needed, the official repository currently documents:

```bash
npx -y @alipay/agent-payment@latest install-cli
```

Package contents and commands can change independently of ACT. Recheck the official repository before a release snapshot.

## 3. Activate the workflow in your Agent

Ask the Agent to load the installed Alipay wallet and payment skills. For a paid HTTP resource, provide the resource URL and the original request context. The official workflow should:

1. preserve the original method, URL, Body and required Headers;
2. recognize the `402` and `Payment-Needed` response;
3. show the user a comprehensible payment intent;
4. obtain the required Alipay authorization;
5. pay and query an unknown result instead of paying twice;
6. submit `Payment-Proof` and resume the original resource request internally;
7. return the resource or a structured non-success result.

Do not add a fixed `check-wallet` call before every payment. The official payment command owns wallet readiness during the actual payment workflow.

## 4. What counts as success

Local preflight success proves only that the host can run the official installer/CLI. Buyer integration success requires:

- the official Skill/CLI, not a copied Mock;
- an actual Alipay authorization path;
- a real cashier or 402 test payment;
- distinct pending, success, failure and authorization-required handling;
- sanitized evidence without binding codes, passwords or complete proofs.

Continue with the [end-to-end 402 Quickstart](../end-to-end-402/README.md) to test against a paid resource.

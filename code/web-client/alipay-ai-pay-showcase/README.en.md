# ACT × Alipay AI Pay Guided Showcase

[简体中文](README.md) | English

This demo explains how an agent purchases professional data during research. It presents business execution, participants, ACT 2.1 components, and Alipay product mappings side by side.

> **Scope: Guided Demo / Non-normative / No real payment**
> The demo does not connect to an Alipay sandbox, wallet, payment API, or proof-verification API. It receives no real events and performs no payment.

## What the demo covers

| Scenario | Core distinction | Alipay implementation boundary |
|---|---|---|
| L1 / `PSD-PAY-INS` | The user authenticates and confirms every payment | Shows an explanatory Alipay binding QR-code placeholder and payment confirmation card; the QR code cannot be scanned |
| L2 / `PSD-PAY-DEL` | The user pre-authorizes a specific item, merchant, amount, and number of payments; matching payments proceed automatically | Demonstrates ACT 2.1 semantics only; this repository makes no claim about an Alipay L2 implementation |
| L3 / `PSD-PAY-AUP` | The user sets task and budget boundaries; the agent selects and pays autonomously within them | Demonstrates ACT 2.1 semantics only; this repository makes no claim about an Alipay L3 implementation |

Each scenario shows `CID-PCA-NEG`, commercial confirmation, the resource request, HTTP 402, `Payment-Needed`, payment handling, retrying the original request with `Payment-Proof`, proof verification, resource delivery, and fulfillment confirmation. Failure modes cover an unknown payment result, proof mismatch, unavailable proof verification, and idempotent retry.

## Requirements

- Node.js 18 or later.
- No `npm install` is required.
- Run the commands below from the repository root.

## Start

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

After startup, the terminal prints:

```text
ACT showcase: http://127.0.0.1:4173/
```

The server does not open a browser automatically. Visit `http://127.0.0.1:4173/`, then:

1. Select L1, L2, or L3 to compare the three authorization levels.
2. Use step-by-step playback to inspect the business action, participants, and protocol component at each stage.
3. Use autoplay to watch the complete flow.
4. Switch failure modes to inspect an unknown payment result, proof mismatch, unavailable verification, and idempotent retry.

The server runs in the foreground. Press `Ctrl+C` to stop it.

## Change the port

The default port is `4173`. If it is already in use, set `PORT` to another value.

macOS or Linux:

```bash
PORT=4174 npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

Windows PowerShell:

```powershell
$env:PORT=4174; npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

Open the new address printed by the terminal. If startup reports `EADDRINUSE`, the selected port is also occupied; choose another port and retry.

## Boundaries

- Orders, amounts, transaction references, QR codes, and results shown in the page are explanatory demo data.
- The demo does not verify a real `Payment-Proof`, provide payment-success evidence, or constitute conformance certification.
- ACT semantics come from the finalized specification under [`docs/specification/`](../../../docs/specification/README.md).
- Use the [AIPay website](https://aipay.alipay.com/callpay) and its official integration documentation for Alipay product integration. This repository provides reference integration material only under [`integrations/alipay/`](../../../integrations/alipay/README.md).
- The official sandbox is provided and operated by Alipay. This demo does not copy, proxy, or offer a “connect sandbox” feature.

## Checks

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build
```

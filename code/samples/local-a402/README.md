# Local A402 Sample

This dependency-free sample demonstrates the minimum safe HTTP exchange around a protected resource:

1. request a paid resource;
2. receive `402 Payment Required` and `Payment-Needed`;
3. decode and inspect the requirement;
4. retry with a fake `Payment-Proof`;
5. confirm that no paid resource is delivered.

It never connects to a PSP, validates a real proof, performs payment, or simulates payment success.

## Run

Requires Node.js 18 or later.

```bash
npm --prefix code/samples/local-a402 run local
```

To keep the local server running:

```bash
npm --prefix code/samples/local-a402 run sample
```

Then inspect the response:

```bash
node code/samples/local-a402/inspect-402.mjs http://127.0.0.1:18080/paid-resource
```

The payload shape is checked against the non-normative artifacts under [`code/schemas/a402/`](../../schemas/a402/README.md). For a real product integration, see [`integrations/alipay/`](../../../integrations/alipay/README.md).

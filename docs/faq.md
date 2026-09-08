# FAQ

## Is ACT tied to Alipay?

No. ACT defines cross-product commerce and payment semantics. The Alipay directory is one product-specific reference integration.

## Does the local A402 sample perform a payment?

No. It only demonstrates a 402 challenge, local decoding, and rejection of a fake proof.

## Is the Web Showcase a reference implementation?

No. It is an explanatory user interface for protocol flows.

## Where are the machine-readable schemas?

Under [`code/schemas/`](../code/schemas/README.md). It currently contains A402 artifacts and the optional TSD-CRD `reference-v1` implementation profile. They are implementation aids and do not add requirements absent from the ACT 2.1 text.

## Is the TSD-CRD Sandbox a production credit service?

No. The [TSD-CRD Reference Implementation guide](../integrations/tsd-crd/README.md) documents a non-production implementation under [`code/samples/tsd-crd-reference/`](../code/samples/tsd-crd-reference/README.md) using Mock identity/credit providers, in-memory state, and temporary test keys. TSD-CRD remains a normative ACT 2.1 subprotocol, but this particular implementation's tests and basic conformance runner do not prove full ACT 2.1 conformance or production readiness.

## Where do I configure an Alipay sandbox?

Follow the [AIPay website](https://aipay.alipay.com/callpay) and official integration documentation. This repository intentionally does not reproduce the sandbox.

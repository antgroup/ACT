# TSD-CRD machine-readable artifacts

> **Status: Implementation Artifact / Non-normative**

This directory contains machine-readable implementation aids for the ACT 2.1
TSD-CRD (Credit Association) subprotocol. The normative requirements remain in
[`docs/specification/trust-services.md`](../../../docs/specification/trust-services.md).

- [`reference-v1/`](reference-v1/README.md): JSON Schema 2020-12, an OpenAPI
  3.1 local Sandbox binding, example messages, and fixed test vectors.

`reference-v1` is an implementation profile version, not an ACT protocol
version and not an official unified TSD wire contract. Implementations only
claim this profile when they deliberately adopt its field names, Ed25519
algorithm suite, signature projections, and HTTP binding.

The artifacts were integrated from the standalone TSD-CRD source at commit
`fdf7006d97ae06645dce82400fac2dff964691f2`. Wire field casing and fixed signed
vectors were preserved during integration.

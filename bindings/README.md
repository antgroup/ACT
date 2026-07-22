# ACT Bindings

Bindings define how ACT semantics are carried or packaged by a concrete developer surface. They do not redefine payment authorization, Alipay product fields, or merchant onboarding.

| Binding | Conference baseline | Responsibility |
|---|---|---|
| [HTTP A402](http-a402/README.md) | Seller-side baseline | Carry `Payment-Needed` and `Payment-Proof` while preserving the original resource request |
| [Skill/CLI](skill-cli/README.md) | Buyer-side baseline | Let the official Alipay workflow package payment, status query, proof submission, and request resumption |

Candidate `PSD-PAY-A402` is the access-protocol layer. INS, DEL, and AUP remain payment-scenario components. A Binding may package several protocol steps, but must state what it hides and what evidence it returns.

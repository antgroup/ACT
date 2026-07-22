# Quickstarts

Quickstarts are the shortest paths to an official product or sandbox. They are different from the simulated code under `impl/python/`.

| Goal | Start here | Real external dependency |
|---|---|---|
| Give a buyer Agent Alipay payment capability | [Agent Payment](alipay/agent-payment/README.md) | Official `@alipay/agent-payment` installer and user authorization |
| Make a REST resource accept Agent payment | [Metered REST provider](alipay/metered-rest-provider/README.md) | Alipay Sandbox application, service registration and APIs |
| Validate the two sides together | [End-to-end 402](alipay/end-to-end-402/README.md) | Both paths above and one authorized sandbox payment |

Passing local unit tests proves only local protocol handling. A real integration claim additionally requires the official Skill/CLI, Alipay Sandbox verification, fulfillment confirmation and sanitized evidence.

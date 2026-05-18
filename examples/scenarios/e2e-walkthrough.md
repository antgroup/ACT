# 端到端流程走查

本文档以"用户委托智能体每月自动续费手机套餐"为例，走查 ACT 协议四个域的完整交互流程。

## 参与方

- 委托人 Alice（`did:act:example.com/user-alice`）
- 买方智能体（`did:act:example.com/agent-alice-001`）
- 商户中国移动
- 支付服务方 PSP

## 阶段一：委托授权（ADD 域）

1. Alice 向智能体表达意图："帮我每个月自动续费我的中国移动手机号，套餐费用约 129 元"
2. 智能体解析意图，生成 ISR：
   - `delegation_mode: SPECIFIED`
   - `max_total_amount: 450.00`（3 个月 × 150 元含容差）
   - `ext.commerce.allowed_merchants: ["urn:act:merchant:example-merchant"]`
   - `ext.agent_behavior.price_deviation_tolerance: 10.0`
3. 智能体向 Alice 展示结构化摘要，Alice 确认
4. Alice 核身（指纹），智能体签发 IAC（VC-JWT 格式，ES256 签名）
5. 智能体异步上报 `act:delegation:intent-created` 与 `act:delegation:delegation-issued` 存证事件

## 阶段二：商业交互（CID 域）

6. 到期触发时，智能体通过意图上下文传递（`CID-INT-RUT`）向中国移动发送请求
7. 中国移动返回候选套餐列表
8. 智能体执行规则自检（`CID-CART-CFM`）：
   - 资金限额：129 元 < 单笔上限 150 元 ✓
   - 品类范围：手机套餐在允许品类内 ✓
   - 商户范围：中国移动在白名单内 ✓
   - 价格变动：当前价格 129 元在容差范围内 ✓
9. 智能体提交购物车确认，获取商户侧订单号
10. 智能体计算购物车快照摘要
11. 智能体异步上报 `act:commerce:cart-confirmed` 存证事件

## 阶段三：支付执行（PSD 域）

12. 智能体基于已绑定的支付标记构造委托支付请求（`PSD-PAY-DEL`）
13. PSP 执行核验：
    - IAC 签名有效 ✓
    - IAC 未过期、未吊销 ✓
    - 智能体身份匹配 ✓
    - 单笔金额 129 元 ≤ 150 元 ✓
    - 累计金额未超 450 元 ✓
    - 支付方式匹配 ✓
14. PSP 完成扣款，返回交易流水号
15. PSP 异步上报 `act:payment:transaction-completed` 存证事件

## 阶段四：信任存证（TSD 域）

16. 存证服务方接收并验证各域上报的存证事件
17. 生成存证记录，定期聚合为存证锚写入 ACT Trust Chain
18. 如后续发生争议，争议中心可基于完整存证链路进行裁决
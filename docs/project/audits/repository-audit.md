# 仓库可信度审计

> 状态：Active / Non-normative  
> 首次审计：2026-07-18  
> 范围：文档导航、成熟度声明、Demo、JSON/Python 基础语法、CI 与许可证

## 1. 审计结论

协议正文正在修订，但仓库还存在一层更基础的问题：部分目录和命令不存在，Demo 被描述为完整实现，成熟度声明缺少验证依据，且没有自动化检查阻止这些问题重新出现。

本轮治理不修改协议语义、组件编号和 Schema，只校正可以客观验证的工程事实。

## 2. 首次检查结果

| 检查项 | 初始结果 | 影响 |
|---|---|---|
| Markdown 本地链接 | 42 个失效引用 | 开发者无法按导航阅读或接入 |
| JSON 语法与编码 | JSON 语法可解析；发现 1 个 GB18030 文件 | 非 UTF-8 示例影响跨平台工具消费 |
| Python 语法 | 当前 Python 文件可在内存中编译 | 不证明依赖、运行时或业务流程可用 |
| CI | 不存在 workflow | 断链和语法问题可以重复进入仓库 |
| LICENSE | 根声明引用两个不存在的许可证正文 | 开源授权范围无法仅从仓库完整确认 |
| Demo 定位 | README 使用“完整、开箱即用、完全准备好”等描述 | 容易被误认为真实协议或支付产品接入 |
| 支付实现 | 大量账户、JWT、签名、扣款和支付结果使用 Mock | 不能作为支付宝接入或一致性证据 |
| Schema 一致性 | 没有自动化 example-to-schema 测试 | 示例与 Schema 漂移不可见 |

## 3. 本轮已处理

| ID | 问题 | 处理方式 | 状态 |
|---|---|---|---|
| AUD-001 | 根 README 导航和目录不真实 | 按开发者任务重写首页，只链接存在的文件 | Done |
| AUD-002 | 根 README 声称规范稳定、实现完整 | 改为修订中和实际成熟度说明 | Done |
| AUD-003 | Python 项目被描述为参考实现 | 明确标记为本地模拟 Demo | Done |
| AUD-004 | Demo 文档可能暗示真实支付 | 增加 Mock 和非生产警告 | Done |
| AUD-005 | 42 个本地断链 | 修复导航或移除不存在目标的链接 | Done，待自动检查确认 |
| AUD-006 | 缺少基础质量门禁 | 增加无第三方依赖的仓库检查和 CI | Done |
| AUD-007 | 贡献文档声称已有完整 Schema CI | 调整为当前实际检查范围 | Done |
| AUD-008 | `conversation-history-example.json` 不是 UTF-8 | 保留原内容并转换为 UTF-8 | Done |

## 4. 尚未解决

| ID | 问题 | 原因/依赖 | 建议阶段 | 状态 |
|---|---|---|---|---|
| AUD-101 | 缺少 `LICENSE-CC-BY-4.0` 和 `LICENSE-Apache-2.0` | 需要维护者确认版权主体、文件分类和双许可证边界 | July Preview | Blocked by maintainer/legal review |
| AUD-102 | 示例没有自动匹配并验证对应 Schema | 文件命名和 Schema 版本关系尚未统一 | Phase 1/3 | Open |
| AUD-103 | Python 依赖未锁定 | Demo 定位和支持版本需要确认 | Phase 1 | Open |
| AUD-104 | Demo 测试命名为 `test_*`，但部分是手工流程脚本 | 需区分自动测试和体验脚本 | Phase 1 | Open |
| AUD-105 | 协议组件名称在 README、规范、场景和 Demo 中存在差异 | 依赖协议修订，不能机械批量改名 | Phase 3 | Blocked by revision |
| AUD-106 | 缺少真实支付宝沙箱验证资产 | 依赖 Alipay Profile 候选和官方沙箱验证 | Phase 5 | Open |
| AUD-107 | CLA 要求存在，但公开签署机制和链接不完整 | 需要治理与维护者决定 | July Preview | Blocked by governance decision |
| AUD-108 | 安全披露渠道和支持版本需要维护者复核 | 对外承诺必须可执行 | July Preview | Open |

## 5. 自动检查范围

执行：

```bash
python3 scripts/check_repository.py
```

当前检查：

- Markdown 本地文件和目录链接存在。
- JSON 和 Markdown 文件是有效 UTF-8。
- JSON 具有合法语法。
- 旧 Python 2.0 Mock Demo 完成语法审计后已退出公开主线，历史代码保留在 Git。

当前不检查：

- 外部 URL 可用性。
- JSON 示例符合对应 Schema。
- Python 第三方依赖安装和 Streamlit 运行。
- 支付宝产品或沙箱的端到端行为。
- ACT 协议语义一致性。

未覆盖能力必须在 README 和 CI 中明确，不能将基础语法检查描述为协议一致性认证。

## 6. 下一轮

下一轮工程治理建议按以下顺序进行：

1. 建立 example-to-schema 显式映射并记录现有不一致。
2. 区分自动测试、流程演示脚本和 UI Demo。
3. 确认许可证、CLA 与安全披露的公开治理流程。
4. 在 Core 候选稳定后统一组件和状态名称。
5. 使用官方沙箱建立 Alipay Profile 验证，而不是扩展 Mock 支付代码。

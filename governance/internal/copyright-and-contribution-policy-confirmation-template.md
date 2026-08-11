# ACT Protocol 版权主体与贡献政策确认记录（历史，已取代）

> 状态：Superseded / Historical / Non-normative  
> 决定日期：2026-08-07  
> 取代日期：2026-08-11。当前政策不启用额外贡献协议或 DCO sign-off；本文件仅保留历史评审证据，不得用于阻塞外部贡献。现行公开政策见 [`governance/decisions/legal-and-contribution-policy.md`](../decisions/legal-and-contribution-policy.md)。

已记录的项目决定：

- 版权行：`Copyright (c) 2026 Ant Group Co., Ltd.`；
- 文档：`CC-BY-4.0`；
- 代码、JSON Schema、可执行示例、测试和自动化：`Apache-2.0`；
- 入站贡献：使用蚂蚁集团统一的个人贡献者许可协议和公司贡献者许可协议，不采用 DCO。

CLA 决策依据为蚂蚁开源知识库[《7.【合规】开源CLA》](https://yuque.antfin.com/open-source/how/oss-cla)，本次读取的正文更新时间为 `2023-09-01 18:10:25+08:00`。该指引要求项目使用以下统一文本：

- [蚂蚁集团个人贡献者许可协议（中英文，2023-08）](https://yuque.antfin.com/attachments/lark/0/2023/docx/22856539/1693563004989-5a7511e5-756a-48d6-874c-4c4cb6d86e92.docx)；
- [蚂蚁集团公司贡献者许可协议（中英文，2023-08）](https://yuque.antfin.com/attachments/lark/0/2023/docx/22856539/1693563018784-ad7ca60f-c955-4b73-805a-9a2c35798a00.docx)。

以上附件是本项目采用的蚂蚁集团统一 CLA 正式文本来源。内网链接不直接作为外部签署入口；公开仓库建立后仍需配置签署入口和状态校验方式，在此之前不得合并外部 PR。该运营配置不阻塞仓库首次公开。

## 1. 需要确认的项目事实

| 项目 | 待填写 |
|---|---|
| 项目名称 | ACT Protocol |
| 仓库 | `act-protocol`；公开 GitHub URL 待确认 |
| 首次公开版本 | ACT 2.1 Candidate Working Draft / Non-normative |
| 计划公开日期 | `YYYY-MM-DD` |
| 代码形成期间 | `YYYY-MM-DD` 至 `YYYY-MM-DD` |
| 主要来源 | 内部仓库、语雀协议正文、当前维护者提交；请附完整来源清单 |
| 版权主体 | `Ant Group Co., Ltd.`；中文法定全称和批准记录待补 |
| 员工职务作品归属依据 | 合同、公司制度或专项协议名称与版本；由法务填写 |
| 外部个人/供应商贡献 | 姓名或主体、内容范围、权利文件；没有也需明确填“无” |
| 第三方代码/文档/素材 | 依赖和素材清单、原许可证、NOTICE 要求 |

## 2. 版权主体模式参考

以下是开源项目常见做法。ACT 项目已选择模式 A。

### 模式 A：单一公司主体持有

适用于代码和文档均由同一公司依法持有，且外部贡献者通过适用的个人或公司 CLA 向项目主体授予贡献所需著作权、专利等许可的情况。

```text
Copyright (c) 2026 Ant Group Co., Ltd.
```

需确认：

- 中文主体全称、英文法定名称和注册地；
- 是否由集团主体、具体子公司或其他权利主体持有；
- 员工、跨主体协作人员和供应商成果是否都已进入同一权利链；
- 个人/公司 CLA 的签署入口、身份关联和 PR 校验方式是否可执行。

不得使用“蚂蚁集团”“支付宝”“ACT Team”等品牌或团队简称代替法定主体，除非法务明确批准该写法。

### 模式 B：各贡献者保留版权

适用于每位贡献者保留其贡献版权，项目依据入站许可统一分发的情况。常见表达可以是：

```text
Copyright (c) 2026 ACT Protocol contributors
```

或不设置单一总括版权行，通过 Git 历史、`AUTHORS` / `NOTICE` 和贡献条款保留各权利人信息。

需确认：

- “ACT Protocol contributors/authors” 只是集合称谓，不是法律主体，是否符合公司政策；
- 历史内部贡献是否允许按个人贡献者模式表示；
- 若未来采用贡献者保留版权模式，统一 CLA 是否仍提供项目继续分发所需的充分许可；
- `AUTHORS` / `NOTICE` 的收录规则和隐私要求。

### 模式 C：基金会或中立组织持有

只有在版权已实际转让、捐赠或由该组织直接形成时才可使用：

```text
Copyright (c) 2026 [基金会或中立组织完整法律名称]
```

未来计划捐赠不等于当前已转让。ACT 在完成正式权利文件前不得提前使用基金会名义。

## 3. 请求法务/开源办公室作出的决定

请对每项给出 `Approved`、`Rejected` 或 `Needs changes`，并附负责人和日期。

| 决定项 | 建议确认结果 |
|---|---|
| 版权主体模式 | 模式 A：单一公司主体持有；已确认 |
| 版权主体中文全称 | 蚂蚁集团；公开法律文件所需的中文法定全称待审批记录补充 |
| 版权主体英文法定名称 | `Ant Group Co., Ltd.` |
| 首年年份写法 | `2026` |
| 文档许可证 | `CC-BY-4.0` |
| 代码与 JSON Schema 许可证 | `Apache-2.0` |
| 混合目录判定 | 按文件类型和根 `LICENSE` 分配；是否追加逐文件 SPDX 待正式审批 |
| 入站贡献政策 | 蚂蚁集团统一个人/公司 CLA；不采用 DCO |
| CLA 类型 | 个人 CLA + 公司 CLA，使用蚂蚁开源办公室提供的 2023-08 中英文统一文本 |
| CLA 签署与校验 | 待公开仓库创建时配置；就绪前不得合并外部 PR，但不阻塞首次公开 |
| 第三方 NOTICE | 根 `NOTICE` 已声明第三方依赖、链接和资料保持各自条款；源码发布不捆绑第三方构建产物 |
| 商标与 Logo | 当前仓库未附带单独 Logo 或授予商标许可；第三方名称与商标不因开源许可证获得授权 |
| 历史版本与 Git 历史 | 删除 2.0 内容后是否需要历史清理；执行时点和责任人 |

## 4. 目录与许可证确认矩阵

当前仓库建议按下表确认；法务可逐项修改。

| 范围 | 当前建议 | 需确认的例外 |
|---|---|---|
| 根 Markdown、`specs/**/*.md`、`docs/**/*.md`、`integrations/profiles/**/*.md`、`integrations/bindings/**/*.md` | `CC-BY-4.0` | 语雀迁移内容、第三方图表和引用材料 |
| `specs/**/schemas/**/*.json` | `Apache-2.0` | 是否需要逐文件 SPDX |
| `scripts/`、`code/examples/`、`code/web-client/`、测试和自动化 | `Apache-2.0` | 生成代码、SDK 片段、第三方素材 |
| 外部链接和依赖 | 保持各自许可证 | 不纳入 ACT 再许可范围 |

## 5. 批准后可落库的文案模板

以下占位符在批准前不得替换为猜测值。

### `LICENSE` 或 `NOTICE`

```text
Copyright (c) 2026 Ant Group Co., Ltd.

Documentation is licensed under Creative Commons Attribution 4.0
International (CC-BY-4.0). Source code, JSON Schema, executable examples,
tests, and automation are licensed under Apache License 2.0, except where a
file or third-party notice states otherwise.
```

### 代码或 Schema 文件头（若审批要求逐文件标注）

```text
SPDX-FileCopyrightText: [YEAR] [EXACT LEGAL COPYRIGHT HOLDER]
SPDX-License-Identifier: Apache-2.0
```

### 文档文件头（若审批要求逐文件标注）

```text
SPDX-FileCopyrightText: [YEAR] [EXACT LEGAL COPYRIGHT HOLDER]
SPDX-License-Identifier: CC-BY-4.0
```

### `CONTRIBUTING.md` 入站条款

CLA 条款：

```text
Before an external contribution can be merged, the contributor must complete
the applicable Ant Group Individual or Corporate Contributor License
Agreement through the published signing path, and the maintainers must verify
the recorded CLA status. Accepted contributions remain licensed under the
outbound license applicable to the contributed files.
```

在公开文本、签署入口和校验方式就绪前，公开贡献指南必须明确“不合并外部 PR”，不能只写一个外部用户无法访问的内网地址，也不能把 DCO 同时描述为已采用。

## 6. 审批记录

| 角色 | 姓名/主体 | 结论 | 日期 | 证据链接或工单 |
|---|---|---|---|---|
| 项目负责人 | 待登记 | Approved project decision | 2026-08-07 | 本次项目维护确认；待补审批工单链接 |
| 法务/IP |  |  |  |  |
| 开源办公室 |  |  |  |  |
| 安全/合规（如需） |  |  |  |  |

最终落库前还应核对：主体名称拼写、许可证全文、第三方 NOTICE、贡献入口、所有 SPDX 标识和公开申请文档是否完全一致。

## 7. 官方参考

- [Apache Software Foundation：Applying the Apache License, Version 2.0](https://www.apache.org/legal/apply-license.html)
- [Apache License 2.0 正文与应用模板](https://www.apache.org/licenses/LICENSE-2.0.html)
- [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- [SPDX Specifications](https://spdx.dev/use/specifications/)

这些资料说明许可证、NOTICE、CLA 和 SPDX 的通用机制，不能替代对 ACT 权利链、员工职务作品和精确法律主体的个案确认。

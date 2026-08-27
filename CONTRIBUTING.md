# 贡献指南

[English](CONTRIBUTING.en.md) | 简体中文

感谢你参与 ACT Protocol。开始前请阅读[行为准则](CODE_OF_CONDUCT.md)并查看现有 Issue。

## 提交变更

1. 涉及协议语义、新行为或破坏性变更时，请先创建 Issue。安全漏洞必须通过 [SECURITY.md](SECURITY.md) 指定的私密渠道提交。
2. 每个 Pull Request 应聚焦单一主题，并说明变更属于协议、机器产物、产品接入还是文档。
3. 根据变更补充相应测试，并运行 `./tools/verify.sh`。
4. 在 Pull Request 中说明兼容性和安全影响。

ACT 2.1 已定稿。文字勘误和不改变含义的澄清可以更新；新增规范性行为必须面向未来协议版本。JSON Schema、产品接入和示例不得增加协议正文中不存在的要求。

产品接入必须引用当前有效的官方产品来源，不得向仓库提交凭证，也不得把本地测试表述为真实沙箱证据。

贡献者应确认有权提交相关内容。被接受的贡献适用 [LICENSE](LICENSE) 对相应文件或目录规定的许可证。目前不要求额外签署 CLA 或进行 DCO sign-off。

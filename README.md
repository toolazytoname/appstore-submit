# appstore-submit

把 iOS App 提交到 App Store 审核的端到端 Agent Skill：xcodebuild 归档上传、App Store Connect 网页自动化（元数据 / 截图 / 隐私 / 定价 / 分级 / 提交）、官网与隐私政策页部署、TestFlight。

来自 2026-09 一次真实上架（个人开发者账户，全程 headless + 浏览器自动化）的复盘，20 条坑全部实踩验证。

## 结构

- `SKILL.md` — 主流程与纪律（Agent 加载入口）
- `references/metadata-checklist.md` — ASC 全字段清单与填写顺序
- `references/browser-automation.md` — ASC React 表单自动化纪律
- `references/xcode-build-upload.md` — 归档/导出/上传命令与签名坑
- `references/website-privacy-page.md` — 官网三页 + Vercel 自定义域名
- `references/pitfalls.md` — 完整踩坑清单
- `scripts/exportOptions-appstore.plist` — App Store 导出配置模板
- `scripts/vercel-add-domain.sh` — Vercel 项目域名登记（绕过 alias 坑）

## 使用

把本目录作为 skill 挂载到支持 SKILL.md 的 agent（Kimi Work / Claude Code / Cursor 等），
触发语如「上架苹果商店」「提交 App Store 审核」「TestFlight 发布」。

## 许可

MIT

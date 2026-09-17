# appstore-submit

把 iOS App 提交到 App Store 审核的端到端 Agent Skill。两条路线：**主线 fastlane + App Store Connect API Key 脚本化**（省 token、可进 CI；有 Android 产品线时同一工具链走 `supply` 上 Google Play，iOS-only 项目可用更轻的 asc），网页独有操作（隐私问卷发布、年龄分级等）用浏览器自动化补齐。另含官网与隐私政策页部署、TestFlight。

来自 2026-09 一次真实上架（个人开发者账户，全程 headless）的复盘，20 条坑全部实踩验证。

## 结构

- `SKILL.md` — 主流程与纪律（Agent 加载入口）
- `references/toolchain.md` — asc / fastlane / API Key 路线对比与命令模板
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

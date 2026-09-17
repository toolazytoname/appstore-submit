---
name: appstore-submit
description: 端到端把 iOS App 提交到 App Store 审核的实战流程：两条路线——优先 fastlane（有 Android 产品线时双端统一主线；Android 侧 supply 走 Google Play）或 asc（iOS-only 轻量主线）+ App Store Connect API Key 脚本化（省 token、可进 CI），网页独有操作（隐私问卷发布、年龄分级等）用浏览器自动化补齐；xcodebuild 归档上传、元数据/截图/隐私/定价/分级、提交审核与 TestFlight。当用户要「上架苹果商店」「提交 App Store 审核」「TestFlight 发布」或需要复用 ASC 自动化经验时使用。覆盖真实踩坑（隐私答复草稿≠发布、-allowProvisioningUpdates、电话国家码等）。
---

# App Store 提交（appstore-submit）

把一个已可构建的 iOS App 从本地归档一路提交到 App Store 审核。本 skill 来自一次真实上架（2026-09，个人开发者账户，全程 headless + 浏览器自动化）的复盘，所有坑都实际踩过并验证了解法。

## 适用范围与前置条件

- macOS + Xcode（`xcodebuild` 可用），App 已能用 Release 配置编译。
- Apple Developer Program 付费账户；明确用**哪个团队**（个人账户 vs 公司团队，勿混）。
- 用户已明确授权：创建 App ID、建 App 记录、上传构建、提交审核。提交审核是对外动作，**必须拿到用户明确指令才执行**。

## 两条执行路线（先选路线再走流程）

**路线 A：API 工具脚本化（首选，省 token、可复现、可进 CI）**

用 **App Store Connect API Key**（`.p8` + Key ID + Issuer ID，ASC「用户和访问 → 密钥/集成」页生成，需管理职能）驱动：

- `fastlane`（Ruby 全家桶：`gym` 打包、`match` 签名、`pilot` TestFlight、`deliver` 元数据/截图/提审）——**有 Android 产品线时用它做双端统一主线**（Android 侧 `supply` 走 Google Play）。
- `asc`（App Store Connect CLI，Go 单二进制，`brew install asc`，TTY 感知 JSON 输出）——iOS ASC 轻量快查/排障备用；仅 iOS 单项目时可作主线。
- 二者底层都是 Apple 官方 App Store Connect API。API Key 无 2FA、不会话过期，CI 友好。

**路线 B：浏览器自动化（补齐 API 覆盖不到的部分）**

以下操作历史上只能网页做（或 API 覆盖不全），需要浏览器自动化能力：

- **App 隐私问卷的「发布」动作**、年龄分级分步问卷（本 skill 踩坑重灾区）
- App 记录创建、bundle id 换绑等一次性操作
- 纪律见 `references/browser-automation.md`

**推荐组合**：API 工具做元数据/上传/提审主线，浏览器只补隐私发布与分级问卷。工具对比、API Key 生成步骤和命令模板见 `references/toolchain.md`。

## 总流程（顺序执行，每步验证后再进下一步）

1. **身份与标识**：确认团队 → 定 bundle id（反向域名，建议和官网域名对应，如域名 `grove.example.studio` → bundle id `studio.example.grove`）→ 开发者门户注册 App ID（explicit）→ ASC 建 App 记录。
2. **官网三页**：首页 / 隐私政策 / 支持页，挂自定义域名。见 `references/website-privacy-page.md`（含 Vercel 自定义域名的大坑）。
3. **构建上传**：`xcodebuild archive` + `-exportArchive`。见 `references/xcode-build-upload.md`。**新 bundle id 首次导出必须带 `-allowProvisioningUpdates`**。
4. **ASC 元数据**：版本页（描述/关键词/技术支持 URL/营销 URL/版权/发布方式/审核备注/联系信息）、截图（iPhone 6.9" 槽 + iPad 13" 槽，6.5" 自动继承 6.9"）。完整清单见 `references/metadata-checklist.md`。
5. **App 信息**：副标题、主要/次要类别、年龄分级（分步问卷）。
6. **App 隐私**：政策 URL + 数据收集问卷。**填完必须点页面顶部的「发布」——「保存」只是草稿，不发布 = 提交时必报错**（见下）。
7. **定价与供应**：价格等级（免费选 $0.00 价格表）、分发方式「公开」、供应国家或地区。
8. **审核信息**：联系信息（**电话必须带 `+` 国家码**，如 `+8615901020559`）、审核备注；App 无账号体系则取消「需要登录」勾选。
9. **提交**：版本页「添加以供审核」→ 创建草稿提交 → 「提交以供审核」→ 状态变「正在等待审核」。官方口径审核最多约 48 小时，结果邮件通知。
10. **发布后动作**（可选）：TestFlight 内部群组 + 测试员 + 真机装启；手动发布模式下过审后需再点一次「发布」才真正上架。

## 关键纪律

- **每一步保存后重载复核**：ASC 表单偶发静默丢失，重载确认持久化再往下走。
- **隐私答复必须「发布」**：提交校验报「具有管理职能的用户必须在 App 隐私部分提供相关信息」时，先去 App 隐私页看顶部有没有「发布」按钮——答案早填好了但没发布是最常见根因。
- **截图槽位**：6.9" iPhone 槽是折叠手风琴，先展开；iPad 通过页面顶部设备下拉切换；只需填满 6.9" 和 13" 两槽，其余尺寸自动继承。
- **年龄分级保存时机**：分步问卷最后一步别点页面级「保存」，用问卷自己的「下一步」走到结果页（系统算出的分级，如 4+）再保存。
- **bundle id 不可换绑**：ASC 记录的 bundle id 建好后锁死。定错域名/bundle id 只能新建 App 记录（旧记录改名标注「旧版」弃用），所有元数据重做——第 1 步务必和用户确认清楚。
- **构建号单调递增**：同一版本重传必须 bump `CURRENT_PROJECT_VERSION`；归档文件保留在 /tmp 可复用，但 bundle id 变了必须重新归档。
- **多团队账户**：每次操作前核对 ASC 右上角团队名，公司团队和个人团队全流程勿混。
- **TestFlight 服务端故障**：若建内部群组反复报「发生错误，请稍后重试」、构建详情页间歇报「似乎出现一些问题」，是 ASC 服务端故障（可换时间重试或请用户在其浏览器手动建组），不要当成自己的数据问题反复改参数。
- 完整坑位清单见 `references/pitfalls.md`。

## 验证标准

- 版本状态从「准备提交」变为「正在等待审核」= 提交成功。
- 记录证据：App 记录 Apple ID、bundle id、构建版本号、提交时间、各页面最终状态截图或文本。
- 提交后更新项目检查点/交接文档，写明：发布方式（手动/自动）、待办（过审后点发布、TestFlight 装启）。

## 参考文件

- `references/toolchain.md` — 工具链路线：asc / fastlane / App Store Connect API Key 对比与命令模板
- `references/metadata-checklist.md` — ASC 全字段清单与填写顺序
- `references/browser-automation.md` — ASC 网页自动化纪律（React 表单、弹窗、路由）
- `references/xcode-build-upload.md` — 归档/导出/上传命令与签名坑
- `references/website-privacy-page.md` — 官网三页 + Vercel 自定义域名
- `references/pitfalls.md` — 完整踩坑清单
- `scripts/exportOptions-appstore.plist` — App Store 导出配置模板
- `scripts/vercel-add-domain.sh` — Vercel 项目级域名登记（绕过 alias 坑）

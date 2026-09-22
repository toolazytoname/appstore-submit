---
name: appstore-submit
description: 端到端把 iOS App 提交到 App Store 审核的实战流程：两条路线——优先 fastlane（有 Android 产品线时双端统一主线；Android 侧 supply 走 Google Play）或 asc（iOS-only 轻量主线）+ App Store Connect API Key 脚本化（省 token、可进 CI；定价/供应范围/年龄分级/截图均可裸 API 直写，提审建单必须网页），网页独有操作（隐私问卷发布、类别/内容版权等）用浏览器自动化补齐；xcodebuild 归档上传、元数据/截图/隐私/定价/分级、提交审核与 TestFlight；收款链路（银行账户、W-8BEN 税表、中国 810 号令合规）；Guideline 2.1 拒审回复全流程（换构建、Notes、真机演示录屏的 iPhone Mirroring 唯一可靠路线、无 UITest 工程的 CGEvent 手动驱动与环境加固、点击光圈叠加、隐私自查、附件上传）。当用户要「上架苹果商店」「提交 App Store 审核」「TestFlight 发布」「配置收款/税表」「被拒后回复 App Review」或需要复用 ASC 自动化经验时使用；也覆盖**国内安卓市场上架**——华为 AGC 实名/建应用/Publishing API、小米个人通道关闭检测、阿里云 APP 备案全流程（一自然人一省管局、证件冲突排查、备案接口对自动化卡死）、软著 2026-03 AI 承诺新规、market 双变体渠道包工程（编译期 UI 切换）、Bitwarden 托管签名钥匙（jks base64 可还原）、Vercel 官网 APK 分发与微信安装坎。覆盖真实踩坑（隐私答复草稿≠发布、提审硬前置：内容版权+价格、类别下拉保存锁定、appPriceSchedules 内联 id 字面 ${new-price} 格式、-allowProvisioningUpdates、电话国家码、homebrew rsync 遮蔽导致 Copy failed、displaysleep 20s 录黑屏、SIGINT 丢录像 等 80+ 条，含 CN 安卓 20+ 条）。
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
4. **ASC 元数据**：版本页（描述/关键词/技术支持 URL/营销 URL/版权/发布方式/审核备注/联系信息）、截图（iPhone 6.9" 槽 + iPad 13" 槽，6.5" 自动继承 6.9"）。完整清单见 `references/metadata-checklist.md`。**提交前先跑 `scripts/metadata-precheck.py` 扫元数据**（Apple 商标词=FAIL/占位词等=WARN；规则与权威来源见 `references/metadata-precheck.md`）——一次 5.2.5 拒审（副标题含 iPhone/iPad）本可这样拦下。
5. **App 信息**：副标题、主要/次要类别、年龄分级（分步问卷，或 `PATCH /v1/ageRatingDeclarations` API 直写）、**内容版权声明**。
6. **App 隐私**：政策 URL + 数据收集问卷。**填完必须点页面顶部的「发布」——「保存」只是草稿，不发布 = 提交时必报错**（见下）。
7. **定价与供应**：价格等级（免费选 $0.00 价格表；API 可一条龙：`POST /v1/appPriceSchedules` + `POST /v2/appAvailabilities`）、分发方式「公开」、供应国家或地区。**缺价格等级会被提审校验拦截**。
8. **审核信息**：联系信息（**电话必须带 `+` 国家码**，如 `+8615901020559`）、审核备注；App 无账号体系则取消「需要登录」勾选。
9. **提交**：版本页「添加以供审核」→ 创建草稿提交 → 「提交以供审核」→ 状态变「正在等待审核」。官方口径审核最多约 48 小时，结果邮件通知。**此两步必须网页**：`appStoreVersionSubmissions` 对 API Key 只有 DELETE 权限（Admin 也不行）。提审校验的已知硬前置：隐私已「发布」、内容版权已声明、价格等级已选——缺哪个校验信息会点名哪个。
10. **发布后动作**（可选）：TestFlight 内部群组 + 测试员 + 真机装启；手动发布模式下过审后需再点一次「发布」才真正上架。
11. **收款链路**（卖 IAP / 付费 App 必做）：签 Paid Apps 协议后依次配 银行账户（CNAPS 五行向导）→ Add user info → 证件核验 → 税表两张（W-8BEN + Certificate）→ 810 号令，全部 Active 后协议才 Active、收入才能结算。完整顺序与税务口径见 `references/banking-tax-compliance.md`。
12. **被拒回复**（Guideline 2.1 Information Needed 等）：先修问题传新构建（被拒版本可换构建）→ 真机演示录屏（iPhone Mirroring 窗口 + `screencapture -v -l`，见参考）→ 提审详情页 Reply to App Review（六项说明 + 附件）+ Notes 同步精简版 → 仅回复未换构建时审核自动恢复；换过构建必须 Update Review + Resubmit 才回 Waiting for Review。完整流程见 `references/rejection-reply.md`。

## 国内安卓市场（延伸能力）

同一套「商店提交 + 浏览器自动化 + 合规材料」经验覆盖国内安卓市场：华为 AGC（个人实名、建应用拿 AppID、提审材料）、阿里云 APP 备案（商店硬前置，关键路径 2–4 周）、market 双变体渠道包、官网 APK 分发。触发词如「上架华为」「小米市场」「APP 备案」「国内安卓商店」。全部规则、坑与时间线见 `references/cn-android-markets.md`（2026-09 实战复盘）。


## 提交门禁（每次提审/重提必须执行，缺一不可）

1. **precheck 证据**：`python3 scripts/metadata-precheck.py <元数据>` 必须退出码 0（WARN 需逐条人工确认）；**输出贴进工作记录**作为证据，贴不出 = 没跑 = 不许提。
2. **权威源回查触发器**：出现新拒审时，按拒审号回查权威原文（[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) / [商标指南](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html)），确认解法后有新坑回写本 skill——这是词表与规则的更新回路。
3. 常规提交**不需要**重读权威源全文：自动扫描（脚本）+ 本 skill 已提炼的规则（源自权威源）+ 被拒回查，三层足够。

## 关键纪律

- **每一步保存后重载复核**：ASC 表单偶发静默丢失，重载确认持久化再往下走。
- **CLI 账号会话不可靠**：`No Accounts with App Store Connect Access` 与 Xcode GUI 登录状态无关（2026-09 实测登录正常仍报），别反复重登，直接切 `references/headless-signing.md` 的 API Key 管线。
- **导出用净 PATH**：Homebrew rsync 会让 `exportArchive` 报裸 `Copy failed`（真实报错藏在 `.xcdistributionlogs` 分发包里），用 `env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin` 跑。
- **ASC 表单要真实鼠标事件**：程序化 click/fill 常不进 React 状态；「焦点+真实键盘」能过一部分，顽固表单用同源 iris API 直写（Cookie 会话）。价格下拉要点 menuitem 里的内层 button——或干脆走 API 建价格计划绕开。a11y 场景 AX `type` 后保存按钮仍灰时，对该字段 `select_text` 全选一次即触发 onChange。
- **类别下拉保存锁定**：主要类别改动未保存时，次要类别下拉对一切输入无响应；先「保存」（按钮变「已保存」）再开次要下拉。
- **提审校验三硬前置**：隐私已「发布」+ 内容版权已声明（弹层「完成」后还要页面级「保存」）+ 价格等级已选；缺哪个「添加以供审核」就点名哪个。
- **隐私答复必须「发布」**：提交校验报「具有管理职能的用户必须在 App 隐私部分提供相关信息」时，先去 App 隐私页看顶部有没有「发布」按钮——答案早填好了但没发布是最常见根因。
- **截图槽位**：6.9" iPhone 槽是折叠手风琴，先展开；iPad 通过页面顶部设备下拉切换；只需填满 6.9" 和 13" 两槽，其余尺寸自动继承。
- **年龄分级保存时机**：分步问卷最后一步别点页面级「保存」，用问卷自己的「下一步」走到结果页（系统算出的分级，如 4+）再保存。
- **bundle id 不可换绑**：ASC 记录的 bundle id 建好后锁死。定错域名/bundle id 只能新建 App 记录（旧记录改名标注「旧版」弃用），所有元数据重做——第 1 步务必和用户确认清楚。
- **构建号单调递增**：同一版本重传必须 bump `CURRENT_PROJECT_VERSION`；归档文件保留在 /tmp 可复用，但 bundle id 变了必须重新归档。
- **多团队账户**：每次操作前核对 ASC 右上角团队名，公司团队和个人团队全流程勿混。
- **TestFlight 服务端故障**：若建内部群组反复报「发生错误，请稍后重试」、构建详情页间歇报「似乎出现一些问题」，是 ASC 服务端故障（可换时间重试或请用户在其浏览器手动建组），不要当成自己的数据问题反复改参数。
- **收款链路三件套缺一不可**：银行 Active + 税表两张 Active + 810 提交，Paid Apps 协议才 Active；Business 页状态会闪烁，只认「带按钮的行动横幅」。税表/合规的状态探测走 `/ppm/v1/` API（Cookie 会话），iris 端点猜路径全 404。
- **Release 商店构建跑 UI 测试 = 写生产存储**：测试钩子若在 `#if DEBUG` 里，Release 无隔离；演示/回归后卸载重装，勿在含真实数据的设备上跑。
- **演示视频发出前做本地隐私自查**（通知横幅扫描 + 壁纸饱和度检查），设备帧不出本机。
- **录屏环境三件套**（2026-09 三轮实测）：caffeinate 防息屏且**验证断言**（displaysleep 可能只有 20s、合成事件不重置 idle）；`screencapture -v` 用 `-V` 定长**自然超时**收尾（SIGINT 丢文件）；`-l<窗口>` 录出全黑就改**全屏录 + ffmpeg crop**。
- **合成输入走 CGEvent 直注**：全屏 notificationcenterui 窗口会吃掉后台命中判定的点击；滚轮要 continuous+pixel 才滚得动 SwiftUI sheet；坐标每步动态取**面积最大**镜像窗口换算；注入期间用户鼠标勿动。
- **演示视频无音轨可接受**（实测过审提交）；CLI 拿不到麦克风（TCC 静默拒绝恒 -91dB），要音轨走 BlackHole 回环或 iOS 原生录屏。沙盒拉不到商品先查 Paid Apps 协议状态（未生效时 Product.products 返回空，症状与传播延迟相同），修完银行自然出价。
- **财务组件按钮静默失灵先查网络**（2026-09 四轮）：monkey-patch `window.fetch` 记录再点——ATB 业务组件约 2.5h 后 `/ppm/v1/2fa/*` 静默 401，UI 不报错只装死；残影银行（API 空返回+UI 行无状态+Add 按钮无响应）= 向导差最后 Certification，点银行行补完，2FA 码用户输。DSA 重报要传地址证明（对账单），联系表单要改值才放行 Next。详见 `references/banking-tax-compliance.md` 末节。
- **表单输入的 IME 雷**：真键盘打字母会被中文输入法混入候选词（实测污染地址栏）；字母文本走原生 setter，真键盘只用于数字；全屏 Spinner backdrop 期间一切点击无效，先等它消失。
- 完整坑位清单见 `references/pitfalls.md`。

## 验证标准

- 版本状态从「准备提交」变为「正在等待审核」= 提交成功。
- 记录证据：App 记录 Apple ID、bundle id、构建版本号、提交时间、各页面最终状态截图或文本。
- 提交后更新项目检查点/交接文档，写明：发布方式（手动/自动）、待办（过审后点发布、TestFlight 装启）。

## 参考文件

- `references/toolchain.md` — 工具链路线：asc / fastlane / App Store Connect API Key 对比与命令模板
- `references/metadata-checklist.md` — ASC 全字段清单与填写顺序
- `references/browser-automation.md` — ASC 网页自动化纪律（React 表单、弹窗、路由）
- `references/xcode-build-upload.md` — 归档/导出/上传命令与签名坑（含 rsync 遮蔽排障）
- `references/headless-signing.md` — 无头签名上传管线：API Key 建证书/描述文件 + 免口令临时钥匙串 + 手动签名导出 + altool 上传（2026-09 二次实战，CLI 账号会话无解时的主路线）
- `references/banking-tax-compliance.md` — 收款链路：银行账户（CNAPS）+ 证件核验 + W-8BEN/税表 + 中国 810 号令；状态依赖图与 ppm API 探测（2026-09 三次实战）
- `references/rejection-reply.md` — 2.1 拒审回复全流程：换构建、Notes、真机演示录屏（iPhone Mirroring 唯一可靠路线 + 无 UITest 工程的手动驱动/环境加固）、点击光圈叠加、隐私自查、附件上传（2026-09 四次实战）
- `references/metadata-precheck.md` — 送审前元数据自查：Apple 商标规则（5.2.5）+ fastlane precheck 分类借鉴 + 权威资源清单
- `scripts/metadata-precheck.py` — 送审前元数据扫描（Apple 产品词=FAIL，占位/未来功能/其他平台=WARN）
- `references/website-privacy-page.md` — 官网三页 + Vercel 自定义域名
- `references/cn-android-markets.md` — 国内安卓市场上架全流程：主体资格（小米个人关闭检测）、阿里云 APP 备案（规则/流程/证件外省主体冲突三板斧）、软著 AI 承诺新规、market flavor 渠道包工程、签名钥匙 Bitwarden 托管、官网 APK 分发（微信/纯血鸿蒙/国产 ROM 安装坎）、华为 AGC 控制台自动化坑、时间线（2026-09 实战）
- `references/pitfalls.md` — 完整踩坑清单
- `scripts/exportOptions-appstore.plist` — App Store 导出配置模板
- `scripts/vercel-add-domain.sh` — Vercel 项目级域名登记（绕过 alias 坑）

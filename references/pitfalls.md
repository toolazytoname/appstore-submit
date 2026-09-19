# 完整踩坑清单

按踩坑顺序记录，每条都实际发生并验证过解法（2026-09，个人账户上架 iOS App）。

## 提交阻塞类（不修就提交不了）

1. **隐私答复「保存」≠「发布」** ⭐最隐蔽
   - 症状：「添加以供审核」报「具有"管理"职能的用户必须在"App 隐私"部分提供相关信息」，但隐私页明明显示已填完（URL + 未收集数据）。
   - 根因：新版 ASC 隐私页顶部有独立「发布」按钮；问卷只保存为草稿。点「发布」→ 确认弹层 → 页面显示「由 X 发布」后，提交校验立即通过。
2. **电话格式**：审核联系信息电话必须带 `+` 国家码（`+8615901020559`），否则保存报错。
3. **「需要登录」默认勾选**：App 无账号体系时取消勾选；勾了又不给凭据，审核会被卡。
4. **价格时间表未保存**：选了 $0.00 但没持久化，校验会提示定价缺失；保存后重载复核。

## 构建上传类

5. **`No profiles found`**：新 bundle id 首次 `-exportArchive` 必带 `-allowProvisioningUpdates`。
6. **headless 下 xcodebuild/xcodegen 异常**：显式 `USER=$(whoami) LOGNAME=$(whoami)` 前缀。
7. **bundle id 变了旧归档作废**：必须重新 archive，不能用旧 .xcarchive 导出。

## ASC 表单类

8. **fill/native setter 不进 React 状态**：click 聚焦 + key_type 输入；保存后重载复核。
9. **「未保存的更改」弹窗**：一律选「保存」，选「舍弃」静默丢数据。
10. **直接 navigate 深层路由 ERR_ABORTED**：从侧栏链接点击进入。
11. **年龄分级保存时机**：分步问卷走到系统计算结果页（第 7 步显示 4+）再用问卷内按钮保存；提前点页面级「保存」丢进度。
12. **6.9" 截图槽是折叠手风琴**：不展开找不到上传入口；iPad 通过顶部设备下拉切换。
13. **「请选择你希望以何种方式向用户分发 App」** 是常驻说明文字，不是校验错误，别被误导。

## 命名与记录类

14. **App 名重名**：「Grove」被占，加后缀「Grove Git」。ASC 名称唯一性按全商店校验。
15. **bundle id 锁定不可换绑**：域名从 `.site` 改 `.studio` 时旧记录（含全部元数据/截图/构建）只能弃用，新建记录重做。改记录名为「XX 旧版」防混淆。
16. **域名/bundle id/记录三者第一步定死**，返工成本=全部元数据重填。

## 外部服务类

17. **Vercel alias ≠ custom domain**：`vercel alias set` 的域名被 `ssoProtection=all_except_custom_domains` 拦到登录页；必须 POST `/v10/projects/{id}/domains` 登记项目域名（`verified:true` + 证书签发后才算数）。
18. **TestFlight 服务端故障**：「新建内部群组」反复「发生错误，请稍后重试」+ 构建详情页间歇报错 = ASC 服务端问题。换参数重试 8+ 次无效后停止，等恢复或请用户在其浏览器手动建组。不阻塞 App Store 提交。
19. **审核时长**：官方口径最多约 48 小时，结果邮件通知；手动发布模式下过审还要再点一次「发布」。

## 界面文案注意

20. 「此 App 版本已添加以供审核」≠ 已提交——只是建了草稿提交，还要点草稿区的「提交以供审核」，状态变「正在等待审核」才算数。

## 无头构建上传类（2026-09 第二次实战）

21. **`No Accounts with App Store Connect Access` 无解于 CLI**：Xcode GUI 账号登录正常、沙箱内外、前后台都试过仍报。结论：别修账号，直接换 API Key 无头管线（见 `references/headless-signing.md`）。
22. **Homebrew rsync 弄挂导出**：`xcodebuild -exportArchive` 尾声报裸 `Copy failed`，分发包日志（`/var/folders/.../BunnyMetronome_*.xcdistributionlogs/IDEDistributionPipeline.log`）里是 `rsync: --extended-attributes: unknown option [server=3.4.1]`——Homebrew 的 rsync 3.4.1 抢了 PATH，系统 openrsync 才认 `-E`。**解法：`env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=$HOME xcodebuild ...` 净 PATH 跑**。stdout 只有 5 行日志，细节必须翻分发包。
23. **CLI 归档 Team 为空 → GUI Distribute 报 `No Team Found in Archive`**：`DEVELOPMENT_TEAM=` 当参数传不落盘。解法二选一：`plutil -replace Team -string <TEAMID>` + `plutil -replace ApplicationProperties.Team -string <TEAMID>` 直改归档 Info.plist；或归档时让签名落进归档。**个人账户有两个团队 ID（免费个人 + 付费会员），别用错**——付费那个才在分发证书上。
24. **创建分发证书的 CSR 必须 RSA 2048**：EC P-256 会被 `CSR algorithm/size incorrect. Expected: RSA(2048)` 拒（`openssl genrsa -out key.pem 2048`）。
25. **开发 profile 必须带 devices 关系**：`IOS_APP_DEVELOPMENT` 类型 POST 缺 `devices` 报 `The relationship 'devices' is required`；设备列表 `GET /v1/devices`。
26. **curl 打 ASC API 带 `filter[xxx]` 会报 `bad range in URL`**：方括号被当 glob，加 `-g/--globoff`。
27. **altool API Key 自动发现**：`.p8` 放 `~/.appstoreconnect/private_keys/AuthKey_<KEYID>.p8`，`xcrun altool --upload-app -f app.ipa -t ios --apiKey <KEYID> --apiIssuer <ISSUER>` 即可，无需 app-specific password。

## ASC 表单与流程类（2026-09 第二次实战）

28. **ASC React 表单只认真实鼠标事件**：程序化 `el.click()`/`fill()` 大概率不进状态（页面显示有值、保存时丢、按钮不激活）；先试「焦点 + 真实键盘」，顽固表单直接同源 iris API 直写（`fetch('/iris/v1/...')` 带 Cookie）。价格下拉要点 menuitem 里的**内层 button**，点外层 menuitem 无效。
29. **首个 IAP 随版本送审（2026 新流程）**：IAP 页「Add for Review」创建提交单（IAP 进单）→ 版本页「Add for Review」把版本加进同一单 → 对话框「Submit for Review」。版本加不进时先查：协议是不是 Verifying、DSA 是否已申报。
30. **IAP 卡 `MISSING_METADATA` 查 availability**：UI 的 Set Up Availability 会静默失败（点完 Done 什么都没存）。对 `GET /iris/v2/inAppPurchases/<id>/inAppPurchaseAvailability`，404 = 没建成。解法：`GET /v1/territories?limit=200` 拿全量 → `POST /v1/inAppPurchaseAvailabilities`（关系：inAppPurchase + availableTerritories 全量 + `availableInNewTerritories:true`）。
31. **IAP 本地化创建的关系键是 `inAppPurchaseV2`**（不是 `inAppPurchase`），报 `ENTITY_ERROR.RELATIONSHIP.UNKNOWN` 时换键重试；偶发 500 重试一次就过。
32. **签付费协议触发 KYC 链**：同意 Paid Apps Agreement 后要求「英文法定名称」证件（护照/身份证照片 + 出生国/城市 + 持股 100%），提交后**免费+付费协议都变 Verifying，版本 Add for Review 被闸**，等邮件（几小时～2 天）。DSA trader 申报类似：联系信息 + 邮箱验证码（可能验证两轮，中途退出不保存）。
33. **无 filechooser 的浏览器传截图**：读取本地 PNG → base64 分块（~400KB/块）传进页面 → `atob` + `DataTransfer` + `new File` 赋给 `input.files` → 派发 change。上传后看槽位计数（如「4 of 10」）确认。
34. **隐私答复问卷**：两个数据类型（Product Interaction + Device ID）都要走「用途=Analytics、不关联身份、不跟踪」三连；设置完必点顶部「发布」——草稿状态一切正常但提交校验必卡。

## 收款链路类（2026-09 第三次实战：银行/税表/810）

35. **银行向导静默重置 &「已经添加过了」**：五行向导会话断了会悄悄退回第一步；保存是否成功不能看外层列表（默认折叠），展开「See More」或查 `/ppm/v1/.../banks` API。状态生命周期 Pending User Info → Verifying → Active。
36. **「Add user info」不止一步**：加完银行还有「账户持有人 + 纳税人识别号」向导，之后还有 Compliance Screening（证件照 + 出生国/城市 + 上市否 + 持股%）。**缺任何一步银行都卡 Pending User Info，Paid Apps 协议翻不了 Active**。
37. **税表问卷先裂成两张表**：预判题（非美居民 No + 无美国商业活动 No）保存后生成 Certificate of Foreign Status 和 W-8BEN 两张**独立表**，要分别打开各自 Submit。
38. **W-8BEN 表单字段名有诈**：inline 输入 name 是 `articleReference` 和 `taxRate`（paragraph 无独立字段，别把段落号填进 taxRate）；FTIN 不填 Submit 也亮（标 Optional），但协定税率（中美 Article 12 / 10%）需要 FTIN（中国个人=身份证号）或出生日期，**不填可能按 30% 兜底扣**。
39. **单选框 value 语义反转**：`useIncomeTypeOther` 组里「Income from the sale of applications」的 value 是 `"NO"`。一律按 label 文本定位，别信 value。
40. **810 号令是三段式**：Compliance 表「Add Info」（无雇员/场所 + 纳税人识别号）→ 之后单独弹「Confirm Information」（Resident ID Card Number 再填一次）→ 状态 Verified/Active（生效日可能显示未来日期，如 Nov 30，属正常）。
41. **Business 页状态闪烁**：后端最终一致性导致横幅/协议状态在 reload 间跳变（一次 Active 一次 Pending）。判据：**带按钮的行动横幅** = 真缺信息；无按钮 = 服务端处理中，别追转态。
42. **状态探测用 ppm API 别猜 iris**：`/ppm/v1/accounts/{account}/banks|pendingBankAccounts|legalEntities|vendors/{id}/taxRequirements`（Cookie 会话直接 fetch）；iris 的组织/协议端点全是 404，真实 URL 从 `performance.getEntriesByType("resource")` 收割。
43. **浏览器面板关闭 = Cookie 清空**：ASC 整个重登（2FA 只有用户能做）。提示用户勾「Keep me signed in」、流程中途别关面板。
44. **证件照上传**（无 filechooser）：`node:fs` 读文件 → base64 ~400KB 分块 evaluate 推进 window 数组 → `join + atob` → `new File` + `DataTransfer` 赋 `input.files` → 派发 input/change；成功标志是 UI 出现文件名 + Delete 按钮（上限 7MB）。
## 拒审回复与真机演示类（2026-09 二轮：2.1 Information Needed 回复实战）

   - 症状：`-exportArchive` 走到 IDEDistributionCreateIPAStep 报 `Copy failed`，分发日志里 `/usr/bin/rsync exited with 1`、`rsync: on remote machine: --extended-attributes: unknown option [server=3.4.1]`。
   - 根因：打包 IPA 用系统 openrsync（`-E` = `--extended-attributes` 是 macOS 专有 flag），但 rsync 本地服务端按 PATH 解析到了 homebrew 的 rsync 3.4.1。
   - 解法：`env PATH="/usr/bin:/bin:/usr/sbin:/sbin" xcodebuild -exportArchive ...` 受控 PATH 重试（一次即成）。
45. **Release 商店构建没有 UI 测试钩子**：若 `--ui-test-storage-id` 之类的测试启动参数包在 `#if DEBUG` 里，Release 配置跑 UI 测试**直接写生产存储、无隔离**。演示/回归用完即卸载重装；绝不在有真实用户数据的设备上跑 Release 配置测试。
46. **中国区新容器首启「允许无线数据」弹窗**：全新安装的 App 首次键盘输入触发系统弹窗（SpringBoard Alert），拦截合成事件导致 typeText 静默丢失。测试里加 SpringBoard 弹窗处理器（启动后 + 首次输入前各查一次；模拟器无弹窗时 no-op）。
47. **真机演示录屏的唯一可靠路线 = iPhone Mirroring 窗口 + `screencapture -v -l<id>`**。QuickTime/AVFoundation 的 iPhone「外部设备」源是 Continuity Camera 摄像头不是屏幕；XCTest 真机录屏只保留失败轮；devicectl 无截屏。详见 `references/rejection-reply.md`。
48. **iPhone Mirroring LIVE 验证的假阴性**：对当前已在前台的 App 重复 devicectl launch = 画面无变化 = diff 0，会被误判成镜像死了。必须切一个「当前不在前台」的 App 再 diff。隔夜断连要手机锁屏一次才重连，连接期间别碰手机。
49. **ASC 登录会话隔夜过期**：内嵌浏览器跳 `login?...authResult=FAILED`。让用户自己在浏览器面板重新登录（凭据永远用户自输），自动化只做后续操作。
50. **2.1 回复后 Resubmit 保持禁用是正常的**：回复消息本身就是恢复审核的机制，不要去找「重新提交」按钮。
51. **被拒版本换构建**：版本页 Build 表删除按钮 hover 才可见（Playwright 直接 click 会超时，用 `evaluate(el => el.click())`）→ Add Build 弹层单选新构建 → 提审详情条目自动显示新构建号。

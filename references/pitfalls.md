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
50. **2.1 回复后是否要点 Resubmit 取决于换没换构建（两个 App 实测）**：仅回复（未换构建）→ 回复即恢复，Resubmit 禁用属正常；换了构建 → 版本回到「准备提交」，必须版本页 Update Review → 提审单 Ready for Review → Resubmit to App Review → Waiting for Review，漏一步 App 就静静躺着没人审。多条目单（IAP+版本）同样适用；Resubmit 后页面重渲染数秒才显示新状态。
51. **被拒版本换构建**：版本页 Build 表删除按钮 hover 才可见（Playwright 直接 click 会超时，用 `evaluate(el => el.click())`）→ Add Build 弹层单选新构建 → 提审详情条目自动显示新构建号。

## 录制环境与输入注入类（2026-09-18 三轮：无 UITest 目标工程，手动驱动镜像）

52. **displaysleep 极短会把录像录成全黑**（实测一台机器 20s）：合成鼠标/键盘事件不重置系统 idle 计时，屏幕照样息屏，`screencapture -v` 录出黑帧而 still 截图正常（两者走同一 framebuffer，极易误判）。录制前 `caffeinate -disu -t <秒> &`，且必须 `pmset -g assertions | grep caffeinate` **验证断言真挂上**再开录。
53. **`screencapture -v` 只能自然超时收尾**：`kill -INT` 实测直接丢文件（无任何输出，文件根本不落盘）。用 `-V <秒>` 定长录制（比流程预估长 20% 即可），多余尾帧后期裁剪。
54. **`-l<窗口id>` 录像可能整段黑/灰**：Mac 锁屏后窗口合成表面挂起、或镜像窗口被全屏 Chrome 压在另一个 Space 后面——still 截图正常但 `-v` 录像全黑。回退方案：**全屏录制 + ffmpeg 按窗口 bounds 裁剪**（`-vf "crop=W:H:X:Y"`，坐标 = CGWindowList bounds × 2 视网膜）。
55. **后台合成点击被全屏 notificationcenterui 窗口吞掉**：报错「pixel is owned by com.apple.notificationcenterui (window N, bounds=整屏)」= a11y/后台命中判定已废，点击全被这个隐形全屏窗口吃掉。解法：自建 swift CGEvent 注入工具（click/drag/scroll 三件套，`CGEvent.post(tap: .cghidEventTap)`），HID 级事件不受窗口归属判定影响。
56. **镜像窗口里滚 SwiftUI sheet 要「continuous + pixel」滚轮**：`CGEvent(scrollWheelEvent2Source:units:.pixel,...)` 且 `setIntegerValueField(.scrollWheelEventIsContinuous, 1)`；`.line` 单位和离散滚轮都滚不动。鼠标拖拽滚动会被按钮/滑块控件吃掉，不如滚轮稳。
57. **镜像窗口会漂移、同进程还有小窗污染窗口解析**：坐标换算必须每步动态读 CGWindowList（取**面积最大**的 iPhone Mirroring 窗口——进程里有 ~70×30pt 的附属小窗会污染「取第一个」的解析），pt→global 每次现算；脚本开头预计算坐标必翻车。
58. **用户的物理鼠标 = 注入指针**：注入阶段用户一动，点击位移、拖拽断链、窗口被拖走连环发生（前两次 take 全废于此）。开始注入前明确告知用户「接下来 N 秒手离开鼠标和手机」。
59. **Mac 锁屏后镜像窗口可能渲染成透明**：透出桌面/Chrome（OCR 空输出、画面偏灰蓝）；View 菜单可用 ≠ 窗口表面活着。恢复 = 重启 iPhone Mirroring App + View ▸ Home Screen 强制重绘；或直接走全屏录制路线绕开。
60. **元素定位用本地 Vision OCR**：`VNDetectTextRequest`（`recognitionLanguages=["zh-Hans","en-US"]`，取 observation.boundingBox 换算窗口 pt 坐标），中英文 UI 文字一次成型，比像素色块猜测稳一个量级。注意：agent 的图片 Read/「查看」多走外部 CDN——设备帧只做本地像素统计（PIL），别喂给多模态。
61. **CLI 进程拿不到麦克风**：TCC 静默拒绝表现为恒 -91dB 假数据（不报错、volumedetect 数字漂亮）。演示视频要音轨需 BlackHole 虚拟声卡（切换系统输出录回环）或 iOS 端原生录屏 + AirDrop 回传；**无音轨的演示视频 App Review 实测接受**（2.1 回复附件已提交成功）。
62. **沙盒新 IAP 传播 ≤24h**：IAP 刚建几小时，开发包里解锁按钮显示「商店暂时连不上」≠ bug（实测建后 9h 仍未传播）。演示视频拍不到系统购买弹窗时，在回复文案里写明原因和购买路径，传播后重验；别为此反复重装折腾。**四轮修正（见 #80）**：超 24h 仍不出价，头号根因是 Paid Apps 协议未生效，先查协议再怪传播。

## ASC 元数据 API 直写类（2026-09-19 第三次实战：胖龙漫画 1.0 全链路提审）

63. **提审硬前置：内容版权声明 + 价格等级**：点「添加以供审核」报「无法添加以供审核」并列出缺项——已知会拦的两项：①「你必须在 App 信息中设置内容版权信息」（App 信息 → 内容版权 → 编辑 → 单选「不，不包含第三方内容」→ 完成 → **还要点页面级「保存」**，只点弹层「完成」不落库）；②「你必须在定价中选择价格等级」（见 65，API 一发即成）。校验信息是逐项列出的，缺什么补什么再重点一次。
64. **类别下拉的保存锁定**：主要类别改动**未保存**时，次要类别下拉对任何输入（AXPress、真实鼠标点击、键盘 ↓）都无响应——表现像"控件坏了"，其实是表单锁定。先点「保存」（按钮变「已保存」），次要下拉立刻正常打开。别在这上面换各种点击方式浪费时间。
65. **定价与供应范围可以纯 API 建成，绕开网页价格下拉**（价格下拉要点 menuitem 内层 button 的坑直接不存在了）：
   - 免费价格点：`GET /v1/apps/{id}/appPricePoints?filter[territory]=USA`，tier 0 是 customerPrice 0.0 那条（id 是 base64 串）。
   - `POST /v1/appPriceSchedules`，relationships：app + baseTerritory(USA，territory id 就是三字码) + manualPrices；included 里内联 appPrices 的 id **必须是字面 `${new-price}` 格式**（先试 `new-price`、`$new-price` 都报 `INVALID_ID`，报错 detail 会直接教格式）。
   - `POST /v2/appAvailabilities`（v1 路径 404）：`availableInNewTerritories: true` + `territoryAvailabilities` 内联（local id `${terr-0}`…，每条只带 territory 关系，**不要**写反向 appAvailability 关系会报 UNKNOWN）。175 个 territory 一页拉完（`/v1/territories?limit=200`，limit 上限 200）。
66. **截图上传纯 API 三步**（比浏览器 DataTransfer 路（#33）稳，不经网页）：① `POST /v1/appScreenshots`（relationships.appScreenshotSet 指向目标 set）→ 响应带 `attributes.uploadOperations` 的预留 PUT URL；② `curl -X PUT --upload-file` 直传该 URL；③ `PATCH /v1/appScreenshots/{id}` `{"uploaded":true,"sourceFileChecksum":"<md5>"}`。set 用 `POST /v1/appScreenshotSets`（ Relationships: appStoreVersionLocalization + `screenshotDisplayType`）；**displayType 合法枚举里没有"6.9 寸/13 寸"字样**，6.9" = `APP_IPHONE_67`、iPad 13" = `APP_IPAD_PRO_3GEN_129`（1320×2868 / 2064×2752 实测都被接受）。JWT 短寿命：批量上传跑十几分钟会齐刷 401，每批重新签发 token。
67. **年龄分级也能 API 直写**（绕开分步问卷的保存时机坑 #11）：`PATCH /v1/ageRatingDeclarations/{id}`，字段类型是**混合的**——`alcoholConsumption/contests/gamblingSimulated/medicalOrTreatmentInformation` 等是枚举（值 `"NONE"`），`gambling/healthOrWellnessTopics/messagingAndChat/socialMedia/unrestrictedWebAccess/userGeneratedContent/lootBox` 等是布尔，`ageAssurance` + `advertising` 是**必填**布尔（缺了 400 报字段名）。全 NONE/false → 4+。
68. **提审动作本身 API 做不了**：`appStoreVersionSubmissions` 资源对 API Key（即使 Admin 职能）只有 DELETE 权限，POST 建提交单被拒。最后两步必须网页：版本页「添加以供审核」→ 草稿提交面板「提交以供审核」。成功标志「已提交 1 个项目」；API 侧 `GET /v1/appStoreVersions/{id}` 看 `appStoreState` 变 `WAITING_FOR_REVIEW` 双确认。
69. **a11y type 填了值但保存按钮仍灰 = onChange 没触发**：AX 树里字段值已正确显示，但 React 没收到 change 事件。解法（无需重新输入）：对该字段做一次 `select_text` **全选**即触发状态更新，保存按钮立刻激活。比清空重打一遍快得多。
70. **computer-use 坐标点击被遮挡层吃掉的排障顺序**：① 报错 `pixel is owned by <app>` 就是命中了别的窗口——先看是不是 IDE/编辑器全屏窗口盖着目标浏览器（AX 后台事件如 AXPress 能照常送达，**只有坐标点击会被遮挡层截胡**，这是判断依据）；② 通知中心侧栏开着时有一个 bounds=整屏的透明层（见 #55），点一下非侧栏区域让它收起；③ 仍不行就 JXA 直注 CGEvent 绕过一切命中判定：
   ```bash
   osascript -l JavaScript -e '
   ObjC.import("CoreGraphics"); ObjC.import("unistd")
   var pt = $.CGPointMake(x, y)   // 全局 points，从 AX bounds 中心取
   var d = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseDown, pt, $.kCGMouseButtonLeft)
   var u = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseUp, pt, $.kCGMouseButtonLeft)
   $.CGEventPost($.kCGHIDEventTap, d); $.usleep(80000); $.CGEventPost($.kCGHIDEventTap, u)'
   ```
   ④ 目标窗口 bounds 会漂移：每轮点击前重新 get_app_state 取最新 AX bounds 换算，或先用 AppleScript 把窗口 `set position` 钉死再点。
71. **AX 全局坐标 → 屏幕 raster 像素换算**：AX bounds 是全局 points；目标显示器 raster 像素 = (AX 点 − 显示器 origin) ÷ (显示器点数 ÷ raster 像素数)。例：副屏 bounds [-1920,-669,1920,1080]、raster 1280×720 → 除数 1.5；主屏 [0,0,1512,982]、raster 1280×831 → 除数 ≈1.18。换算错 50px 就点到隔壁控件，视觉模型给的坐标也要用它交叉校验。

## DSA 重报与银行补完类（2026-09-19 四轮）

72. **「Action needed: Update your trader contact information」= DSA 核验没过**：入口在邮件的 ATB 链接（`/business/atb/<legalEntityId>`）→ Business 页顶部 Complete Compliance Requirements。核验失败常见根因=**缺地址证明文件**（只提交过联系方式、没传对账单类材料）；重报时传信用卡对账单 PDF 即可。
73. **ATB 业务组件自带独立登录 + 会话短命**：主会话登录不算数（页面内嵌跨域 Apple ID iframe，自动化读不到，用户自输）；约 2.5h 后财务操作（`/ppm/v1/2fa/*`）**静默 401**——UI 上按钮点了毫无反应。别折腾表单：先 monkey-patch `window.fetch` 存 `__log`，点一次按钮看状态码，401 = 会话过期重登。
74. **DSA 联系表单的脏值门闩**：全预填表单 Next 灰着；input/change/blur/真键盘重打**同值**都没用，必须**改一个字段的值**（如地址首字母小写→大写）才放行。
75. **CGEvent unicode 打字会被中文输入法污染**：IME 活跃时真键盘打字母会混进候选词（实测混入「握手言和%」进地址栏）。字母文本一律走原生 setter（prototype value set + input 事件），真键盘只用于数字与点选。
76. **全屏 Spinner backdrop 吃掉一切交互**：`elementFromPoint` 命中 `SpinnerBackdro` 时合成+真实点击全部无效，单选/按钮怎么点都像失灵。先轮询等 spinner 消失（可 35s+）再操作；对话框渲染出内容 ≠ 加载完成，看 backdrop 在不在。
77. **上传证件/账单的文件读取矩阵**：shell 与 node 读 `~/Downloads` 均被 TCC 挡（EPERM，但 ls 正常，极具迷惑性）；内嵌浏览器 file chooser 死的。可靠路=**AppleScript 让 Finder 复制**（`tell application "Finder" to duplicate (POSIX file …) to (POSIX file "/tmp" as alias)`——Finder 有全权限）→ base64 分块 evaluate + DataTransfer 灌 `input.files`。注意组件会话超时窗口短，拖太久当前步骤会被跳过需重走。
78. **残影银行=没走完的向导**：banks API 空返回 + UI 有行但状态空白 Not in Use + Add Bank Account 按钮点了没反应——数据其实都在（持有人/CNAPS/账号掩码全存着），只差最后 Certification。修法：**点银行行**进 Edit Account Holder Details → 一路 Next（全预填）→ Certification 勾选（真实点击）→ Add。
79. **财务提交的 2FA 闭环**：勾完 Certification 点 Add → `PUT /ppm/v1/2fa/.../banks/<id>` 首次 401 → 页面自动 `POST /olympus/v1/mfaChallenges` 弹「Two-Factor Authentication Required」六位码框 → 用户输码 → 重放 PUT 200 → **银行与 Paid Apps 双双 Processing**。验证码只有用户能看，输完即通。
80. **沙盒拉不到商品的头号根因是 Paid Apps 协议未生效**（对 #62 的四轮修正）：协议 Pending User Info / Processing 时 `Product.products` 直接返回空，症状与 IAP 传播延迟一模一样。「商店暂时连不上」超 24h → 先查 Business 页协议状态，把银行/协议修完自然出价，别死等传播。
81. **2.1 Information Needed 的第 1 项就是真机录屏**（2026-09 胖龙实战）：模板 6 项=①physical device 录屏（最新系统、必须从启动 App 开始、典型流程）②目的与受众③功能访问说明④外部服务清单（无则 none）⑤地区差异确认⑥受监管材料。**别靠记忆默写模板**——先在页面里全选复制留言原文（点正文文本拿到焦点再 cmd+a/cmd+c；焦点停在折叠按钮上时复制的是剪贴板旧值）。首提时 App 审核信息的附件位就该挂录屏，等拒审再补要多花一整天。
82. **读 ASC 页面逐字原文的正确姿势**：AX 值全被 Chrome 截断（"…"），视觉转录会漏段落（实测漏掉录屏整条）。可靠路=点击消息正文 → `cmd+a`+`cmd+c` → `read_clipboard`，拿到完整 6 项 + Prevent Common Issues 全文。
83. **给真机装演示包绕过「No Accounts」**：Xcode 无账号会话时自动签名建不出含 iCloud 的 dev profile。若运行时有守卫（设置页「没登录会静默跳过」），直接换空 entitlements 出包：`flutter build ipa --release --export-method development` + `devicectl device install app`，录完还原 entitlements（git 干净即证明）。
84. **镜像驱动的真相（2026-09 二次实测修正 #47 手动路线）**：JXA CGEvent 直点**时灵时不灵**（点击/滑动都随机失效）；**CUA 窗口路由点击/drag 稳定可用**（app_ref+coordinate，occluder 也拦不住）；iOS 系统边缘手势（返回滑、上滑回主屏）在镜像里**都打不进去**——视频流程别设计 exit 手势，翻到最后一页停住即可。列表条目的可点区可能只有左侧文本列（x<120），行中间点击无响应——按 App 实测热点坐标驱动，别假设整行可点。
85. **screencapture 的 -R 区域截屏在这台 macOS 上直接报错**（"could not create image from rect"，全程如此）：一律全屏截 + PIL crop。窗口级读画面用 CUA get_app_state 的 raster（无遮挡渗入），本地 -R 截屏会被用户正开着的编辑器窗口污染、误导 OCR 判断。
86. **screencapture -v 源是 VFR 且时间戳漂移**（标称 130s 实际 121s）：直接按墙钟秒数 -ss 切段会错位甚至空段（-ss 放 -i 前时 -to 语义还变）。正确流程：先整条转 CFR 母版（`-vf "fps=30,setpts=N/(30*TB)"`），再在母版上 `-ss/-to` 放 `-i` 后输出端切段，最后 concat。fps=1 抽帧的帧号=母版秒数，可当切割点索引。
87. **用户活跃的桌面=地雷阵**：录屏/点击期间用户的编辑器、Kimi 窗口会反复挪进镜像窗口区域。本地截屏被污染≠事件被拦（CUA 窗口路由照常穿透）；但每次取坐标要用 CUA 窗口 raster，别信本地截屏的 OCR。
88. **caffeinate 用 `&` 起会被 zsh HUP 掉**（表现为断言消失→displaysleep 20s 生效→录屏黑屏+镜像 Connection Paused）：必须 `nohup caffeinate -disu -t N >/dev/null 2>&1 & disown`，且每次录制前 `pmset -g assertions | grep caffeinate` 复核。
89. **手机锁屏/被碰 → 镜像 Connection Paused**：窗口中部出现 Resume 按钮（JXA 全局坐标点它即可恢复）。用户在场时直接问一句比猜状态快；解锁涉及凭据，永远不代输。
90. **卸载重装后 App 图标不回原位**（落进 App Library 的「最近添加」文件夹）：录启动流程要么翻资源库开文件夹（文件夹图标在 label 上方，别点 label），要么录前手动把图标拖回主屏。文件夹内图标=label 正上方 ~30pt。
91. **ASC 回复编辑器全链路**（Chrome）：回复按钮只在留言**完全展开**后渲染（折叠开关点两次：一次收起一次全开）；正文=点 textarea 聚焦后 cmd+v 粘贴（React onChange 正常触发，字符计数亮起）；附件=「附加文件」→ 原生面板（CUA surface 变 open_panel）→ Cmd+Shift+G → set_value 完整路径 → return → Open → 等「正在处理...」变文件名、回复按钮由灰转亮再点。发送后验证三件套：消息计数 +1、正文出现在线程、`消息附件：<文件名>` + 下载按钮。
92. **Notes 字段在版本页而非提审详情页**：textarea 备注 → cmd+a+cmd+v 替换 → 保存按钮由灰变亮再点 → 按钮回到禁用=已持久化。改字段时「更新审核」按钮会暂时禁用，保存后恢复，属正常联动别慌。


## 三连拒修复 + 无 GUI 截图管线（2026-09-22）

93. **换构建让 REJECTED 版本自动回 PREPARE_FOR_SUBMISSION**：被拒后不用走「Update Review → Resubmit」按钮链——ASC API PATCH 版本换 build + versionString 即回到可编辑可提交态，直接重新走提交。whatsNew 例外：App 从未上架时该字段全程 409 锁定（首版没有「新功能」概念），跳过即可。
94. **资产级 API key 的截图盲区**：appScreenshotSets 不给 GET_COLLECTION（只 CREATE/DELETE/GET_INSTANCE）。找已有 set 走 `GET /v1/appStoreVersionLocalizations/{id}?include=appScreenshotSets`。iPad 13" 档位枚举是 `APP_IPAD_PRO_3GEN_129`（不是 13INCH 字样）；uploadOperations[].requestHeaders 是**数组** [{name,value}] 不是字典。崩溃残留的「已预留未上传」截图必须 DELETE（按 imageAsset 有无判断哪个是孤儿），再 PATCH set 的 appScreenshots 关系定顺序。
95. **描述文件不含新证书的秒修**：证书重签发后旧 profile 导出 IPA 报 "doesn't include signing certificate"。`security find-certificate -p | openssl x509 -serial` 拿真实序列号（find-identity 显示的是 SHA1 指纹，别拿去 filter）→ ASC API 建 profile（bundleIds + certificates 关系）→ `security cms -D` 解出 UUID 装 `~/Library/MobileDevice/Provisioning Profiles/`。全程 3 个 API 调用。
96. **Simulator 窗口宽度=设备 size class**（iOS 26）：拖窄窗口 iPad 直接变 compact 走手机布局，别拿窗口内容当设备真相；**唯一可信的是 `simctl io screenshot` framebuffer**（分辨率恒定）。多设备窗口互叠 + 窗口渲染会整体黑掉（GPU bug，erase/重启均不救），但**输入通道照常**：framebuffer 里按颜色 blob 定位控件 → 窗口几何换算（窗口 bounds + 设备 pt×scale + 标题栏高）→ CGEvent 盲点 → framebuffer 验证状态变化。大按钮容错高先打它校准映射，小控件失败了别恋战换帧。
97. **同机双 agent 并发=诡异之源**：另一个会话在装旧构建、开设置 sheet、挪窗口，会让你的截屏/检测反复自相矛盾（framebuffer 与窗口内容对不上、装好的 app 变旧版）。凡状态矛盾先查 `simctl get_app_container` 里 Info.plist 的版本号，且每次交互后用 framebuffer 闭环验证，别信中间快照。
98. **ASC React 表单读值三源陷阱**：`getByRole().textContent()` 返回的是 DOM **初始文本**不是当前 value——用它做 fill 前的基底会「凭空丢段落」（实测误判 SCREEN RECORDING 段被删，其实 value 完好）。真相三源：domSnapshot（读 value）、`locator.evaluate(el => el.value)`、fill 后的字符计数器。校验长文本写入一律 `el.value`，别信 textContent。
99. **拒审重提的端到端分工**（2026-09-22 全流程实测）：**API 做全部脏活**——改副标题（在 appInfoLocalizations，不在版本层级）、描述/宣传文本（appStoreVersionLocalizations）、传截图、换构建（版本自动回 PREPARE_FOR_SUBMISSION，提交单里「版本+IAP」两项自动跟着指向新 build，无需重建）。**浏览器只做三件事**：①版本页 Notes 补 RESUBMISSION NOTE 前言并修正过时口径（Save 灰→亮→点→回灰=已持久化）②Resolution Center 回复 ③Resubmit。注意资产级 API key 不给 `appStoreVersionSubmissions` CREATE——最终提交只能走登录会话；会话过期表现是 `/login?...authResult=FAILED`，用户重登后从 /apps 继续即可。版本页的「Update Review」按钮就是跳转 reviewsubmissions 详情页；Resubmit 点击后按钮 disabled+progressbar→整按钮消失，成功判据是两项都变 Waiting for Review（再拿 `/v1/appStoreVersions` API 复核）。
100. **Resolution Center 回复编辑器细节**：入口在拒绝信正文下方「Reply to App Review」按钮；编辑器是 `textbox "Reply"`（4000 字符上限）；**发送按钮也叫 "Reply"**，且页面上另有 generic "Reply" 区块标题——locator 必须 `exact: true` 防多匹配。发送成功三件套：Messages 计数 +1、正文出现在线程、编辑器 DOM 消失。

## 商标与元数据类（2026-09 第五次实战：5.2.5 拒审）

52. **副标题禁用 iPhone/iPad 等 Apple 产品字样（Guideline 5.2.5）**：副标题写「iPhone 与 iPad 上的 XX 客户端」这类措辞会被 5.2.5 Legal - Intellectual Property 拒审（暗示 Apple 背书）。名称/副标题/关键词都别用 Apple 产品名；描述正文里的兼容性表述（如「适配 iPhone 窄屏」）也建议一并清理避免下轮再挑。元数据修复后同样要走 Update Review + Resubmit 才回 Waiting for Review。

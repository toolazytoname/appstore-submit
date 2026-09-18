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

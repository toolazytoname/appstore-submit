# 构建、归档与上传

## 归档（archive）

```sh
# headless 环境必须显式给 USER/LOGNAME，否则 xcodebuild/xcodegen 可能异常
USER=$(whoami) LOGNAME=$(whoami) xcodebuild \
  -project YourApp.xcodeproj \
  -scheme YourApp \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath /tmp/yourapp-v1.0.0.xcarchive \
  archive
```

- 工程配置若由 XcodeGen 管理，改 `project.yml` 后先 `xcodegen` 再归档（同样带 USER/LOGNAME）。
- bundle id / 版本号改在配置源（project.yml 或 target 设置），不要手改 pbxproj 后不重新生成。
- **bundle id 变了必须重新归档**，旧归档作废。
- 归档文件保留在 /tmp，重传可复用（同 bundle id 同版本时）。

## 导出并上传（exportArchive）

```sh
USER=$(whoami) LOGNAME=$(whoami) xcodebuild -exportArchive \
  -archivePath /tmp/yourapp-v1.0.0.xcarchive \
  -exportPath /tmp/yourapp-export \
  -exportOptionsPlist scripts/exportOptions-appstore.plist \
  -allowProvisioningUpdates
```

- **新 bundle id 首次导出必须带 `-allowProvisioningUpdates`**：本地没有对应分发 profile，不带会报
  `No profiles for 'com.example.app' were found`。Xcode 会用已登录账户自动创建。
- 前提：Xcode 已登录开发者账户（Xcode → Settings → Accounts），且该账户对目标团队有权限。
- `exportOptions-appstore.plist` 模板见 `scripts/`，关键键：`method: app-store-connect`、`destination: upload`、
  `teamID`、`signingStyle: automatic`。
- 成功标志：输出 `EXPORT SUCCEEDED` 与 `UPLOAD SUCCEEDED`（destination 为 upload 时直接传到 ASC）。
- 上传后构建要在 ASC 处理几分钟~半小时才可选；TestFlight/版本页出现「处理中」属正常。

## 构建号纪律

- 同一版本重传必须 bump `CURRENT_PROJECT_VERSION`（build number 单调递增）。
- MARKETING_VERSION（如 1.0.0）与 ASC 版本页版本号（如 1.0）对应即可，不要求字面相同。
- 上传前核对：bundle id、版本号、签名团队三者都是目标团队/目标记录，别把公司团队证书签的包传到个人记录。

## 常用排障

| 报错 | 原因 | 解法 |
| --- | --- | --- |
| `No profiles found` | 新 bundle id 无分发 profile | 加 `-allowProvisioningUpdates` |
| 签名身份 ambiguous | 钥匙串里多个团队证书 | 明确 teamID；核对登录账户 |
| 上传成功但 ASC 看不到 | 构建还在处理 / 传错团队 | 等处理；核对 ASC 团队切换 |
| exportOptions 键不被识别 | Xcode 版本差异 | `xcodebuild -help` 查当前版本可用键 |
| `exportArchive` 报 `Copy failed` | homebrew rsync 遮蔽系统 rsync（openrsync 的 `--extended-attributes` flag，rsync 3.4.1 不认） | `env PATH="/usr/bin:/bin:/usr/sbin:/sbin" xcodebuild -exportArchive ...`；分发日志（xcdistributionlogs）里 grep `rsync` 确认 |

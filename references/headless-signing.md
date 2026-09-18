# 无头签名上传（API Key 全自动管线）

Xcode CLI 的账号会话不可靠（`No Accounts with App Store Connect Access` 可能无解），GUI 又需要人点。2026-09 实测一条**全程无 GUI、无账号会话**的路径：API Key 建签名资产 → 手动签名导出 IPA → altool 上传。

## 前提

- ASC API Key 三要素：`.p8` + Key ID + Issuer ID（Integrations 页生成；个人账户先点一次「Request Access」开通，即时批准）
- JWT：ES256 签名，`kid`=Key ID、`iss`=Issuer ID、`aud=appstoreconnect-v1`、exp ≤ 20 分钟。Node `crypto` 签出来是 DER，**要转 P1363 raw（r||s 各 32 字节）**，Apple 拒 DER
- API 基址 `https://api.appstoreconnect.apple.com/v1`（不是网页的 iris）

## 步骤

### 1) 建分发证书（CSR 必须 RSA 2048）

```sh
openssl genrsa -out key.pem 2048
openssl req -new -key key.pem -out csr.pem -subj "/CN=xxx/O=yyy/C=CN"
curl -sg -X POST .../v1/certificates -H "Authorization: Bearer $TOKEN" \
  -d '{"data":{"type":"certificates","attributes":{"certificateType":"DISTRIBUTION","csrContent":"<PEM 全文>"}}}'
# 响应 attributes.certificateContent 是 base64 的 .cer，解码保存
```

### 2) 装 keychain（免口令临时钥匙串，CI 友好）

```sh
security create-keychain -p "" /tmp/sign.keychain-db
security unlock-keychain -p "" /tmp/sign.keychain-db
security set-keychain-settings -lut 21600 /tmp/sign.keychain-db
security import key.pem -k /tmp/sign.keychain-db -P "" -A -T /usr/bin/codesign -T /usr/bin/xcodebuild
security import dist.cer -k /tmp/sign.keychain-db
security list-keychains -d user -s ~/Library/Keychains/login.keychain-db /tmp/sign.keychain-db
```

直接 import 到登录钥匙串会 `errSecInternalComponent`（codesign 拿不到密钥授权）。

### 3) 建 App Store 描述文件

```sh
# bundleId: GET /v1/bundleIds?filter[identifier]=<id>（curl 记得 -g）
curl -sg -X POST .../v1/profiles -d '{"data":{"type":"profiles","attributes":{"name":"xxx appstore","profileType":"IOS_APP_STORE"},"relationships":{"bundleId":{"data":{"type":"bundleIds","id":"<ID>"}},"certificates":{"data":[{"type":"certificates","id":"<CERTID>"}]}}}}'
# profileContent base64 → .mobileprovision；security cms -D 取 UUID，放 ~/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision
```

开发 profile（`IOS_APP_DEVELOPMENT`）另需 `devices` 关系（`GET /v1/devices` 拿 UDID 列表）。

### 4) 手动签名导出（⚠️ 净 PATH，绕开 Homebrew rsync）

exportOptions：

```xml
<dict>
  <key>method</key><string>app-store-connect</string>
  <key>destination</key><string>export</string>
  <key>teamID</key><string>TEAMID</string>
  <key>signingStyle</key><string>manual</string>
  <key>signingCertificate</key><string>Apple Distribution</string>
  <key>provisioningProfiles</key><dict><key>BUNDLE_ID</key><string>PROFILE_NAME</string></dict>
</dict>
```

```sh
env -i HOME="$HOME" USER=$(whoami) LOGNAME=$(whoami) \
  PATH=/usr/bin:/bin:/usr/sbin:/sbin \
  xcodebuild -exportArchive -archivePath app.xcarchive \
  -exportPath out -exportOptionsPlist export.plist
```

不带 `-allowProvisioningUpdates`（资产全在本地，不需要账号）。归档若是 CLI 产的，先确认 `Info.plist` 的 `Team` 与 `ApplicationProperties.Team` 非空，否则 GUI/导出报 `No Team Found in Archive`（`plutil -replace` 可直写）。

### 5) 上传

```sh
mkdir -p ~/.appstoreconnect/private_keys
cp AuthKey_<KEYID>.p8 ~/.appstoreconnect/private_keys/
xcrun altool --upload-app -f out/App.ipa -t ios --apiKey <KEYID> --apiIssuer <ISSUER>
# UPLOAD SUCCEEDED 后，ASC 处理几分钟～半小时
# 轮询：GET /v1/builds?filter[app]=<APPLE_ID>（processingState=VALID）
# 挂构建：PATCH /v1/appStoreVersions/<VER_ID>/relationships/build {"data":{"type":"builds","id":"<BUILD_ID>"}}
```

## 提交单（首个 IAP 随版本）

- IAP 页「Add for Review」→ 创建提交单（IAP 在单内）
- 版本页「Add for Review」→ 版本加入同一单（**需要 Free Apps 协议 Active**；签付费协议触发的 KYC 核验期会变 Verifying 并闸住此步）
- 提交单对话框「Submit for Review」→ 状态「正在等待审核」

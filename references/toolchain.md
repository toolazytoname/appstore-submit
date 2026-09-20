# 工具链路线：asc / fastlane / App Store Connect API

浏览器自动化是兜底路线；能走 API 就走 API——确定性高、可复现、省 token、可进 CI。

## 选型结论（按团队实际情况调整过）

**有 Android 产品线 → 主线 fastlane，一套工具链通吃双端；asc 作为 iOS ASC 的轻量查询/排障备用。**

- fastlane 双端一体：iOS 用 `gym/pilot/deliver`，Android 用 `gradle/supply`（Google Play），同一个 Fastfile 风格、同一套 API-key 模型、同一条 CI 流水线。Google Play 侧有官方 Android Publisher API 支撑（对应 ASC API）。
- 单一 iOS 项目、agent 驱动场景下 `asc` 仍更轻（Go 单二进制、JSON 输出）；但既然 Android 在路线图内，统一 fastlane 避免维护两套工具链和两套凭证流程。
- 二者底层都是官方 API（ASC API / Google Play Android Publisher API），混用不冲突：asc 适合随手 `asc builds list` 查状态，fastlane 跑正式流水线。

| 维度 | asc | fastlane |
| --- | --- | --- |
| 技术栈 | Go 单二进制，`brew install asc` | Ruby + gem 依赖链，偏重 |
| Agent 适配 | TTY 感知 JSON 输出，agent 直接解析 | 面向人类终端，日志冗长 |
| 覆盖 | 仅 iOS ASC 操作 | iOS + Android（supply）+ 签名（match）+ 截图裱框（frameit） |
| 签名 | 不管签名，交给 Xcode 自动签名 | match 统一团队证书，多人团队受益 |
| 适用 | iOS-only 快查快改 | 双端正式流水线、团队签名管理 |

## 第一步：生成 App Store Connect API Key

1. ASC →「用户和访问」→「密钥」（Integrations）→ 生成 **Team Key**（不要 Individual key——部分端点不支持）。
2. 职能选「管理」（Admin）或至少「App 管理」；提交审核/发布需要足够权限。
3. 立即下载 `.p8`（只给一次），记录 Key ID 和 Issuer ID。
4. `.p8` 放本地安全路径（如 `~/.appstoreconnect/AuthKey_XXXX.p8`），**不进 git、不进日志、不进文档**；agent 只引用路径，不读内容。

## asc 常用命令（v1.x，以 `asc --help` 为准）

```sh
asc apps list                          # 列 App 记录，确认 Apple ID
asc builds list --app <APPLE_ID>       # 列构建，确认处理完成
asc release run --dry-run              # 预演完整发布流水线
asc submit create --confirm            # 提交审核（对外动作，需用户明确授权）
```

- 非交互环境自动输出 JSON；加 `--output json` 显式固定。
- 安装：`brew install asc`。仓库 rudrankriyam/App-Store-Connect-CLI（MIT）。

## fastlane 速查（主线）

```ruby
# Fastfile（iOS）
lane :release do
  app_store_connect_api_key(
    key_id: ENV["ASC_KEY_ID"],
    issuer_id: ENV["ASC_ISSUER_ID"],
    key_filepath: "./AuthKey.p8"
  )
  gym(scheme: "YourApp", export_method: "app-store")   # 打包
  upload_to_testflight                                  # pilot：传 TestFlight
  deliver(app_version: "1.1")                           # 元数据/截图/提审
end

# Fastfile（Android，同仓库可并存）
lane :release_android do
  gradle(task: "bundleRelease")                         # 打 AAB
  upload_to_play_store(track: "internal")               # supply：传 Google Play
end
```

- `deliver` 只能写「可编辑状态」的版本（准备提交/被拒），审核中或已上架改不了；在上传构建之后、点提审之前跑。
- `deliver` 的 metadata 目录「有什么传什么」：残留旧 description.txt 会覆盖线上描述。把 metadata 目录当纯派生产物，每次由脚本重新生成。
- locale 代码不统一带地区后缀：日语 `ja`、韩语 `ko`，但英语 `en-US`、德语 `de-DE`。
- API Key 支持度官方对照表：docs.fastlane.tools/app-store-connect-api（pilot/deliver/sigh/cert/match 全支持，produce 部分支持，pem 仅 Apple ID）。

### Android 侧（supply / Google Play）

- 认证：Google Play Console → API 访问 → 创建 **service account JSON key**（对应 ASC 的 .p8），同样只下发一次、不进 git。
- `supply` 管元数据/截图/上架，track 支持 internal/alpha/beta/production 分级推送。
- Google Play 的「数据安全」表单、内容分级问卷与 ASC 的隐私问卷/年龄分级一样，**历史上是控制台网页独有**，自动化前查证当前 API 覆盖。
- iOS 的坑位经验大部分可平移：草稿≠发布、联系人格式、版本状态机「可编辑才写得进」。

## 两条路线的分工（当前 Apple 能力边界）

| 操作 | API 工具 | 浏览器自动化 |
| --- | --- | --- |
| 归档上传 | ✅ xcodebuild/asc | 不需要 |
| 元数据/截图/关键词 | ✅ deliver / asc / 裸 ASC API（截图三步直传见 pitfalls #66） | 兜底 |
| TestFlight 群组与测试员 | ✅ pilot / asc | 兜底 |
| 年龄分级 | ✅ `PATCH /v1/ageRatingDeclarations`（2026-09 实测，字段类型坑见 pitfalls #67） | 兜底 |
| 定价与供应情况 | ✅ `POST /v1/appPriceSchedules` + `POST /v2/appAvailabilities`（2026-09 实测一条龙，见 pitfalls #65） | 兜底 |
| **提交审核（建提交单）** | ❌ `appStoreVersionSubmissions` 对 API Key 只有 DELETE 权限，POST 被拒（2026-09 实测，Admin 职能也不行） | ✅ 唯一路线：版本页「添加以供审核」→「提交以供审核」 |
| 版本发布（过审后手动模式） | ✅ PATCH appStoreVersion 的 releaseRequest / asc | 兜底 |
| **App 隐私问卷「发布」** | ⚠️ 历史上网页独有，用前查证 | ✅ 主路线 |
| **类别 / 内容版权声明** | ❌ primaryCategory 关系 API 只读（FORBIDDEN） | ✅ 唯一路线（内容版权是提审硬前置，见 pitfalls #63） |
| App 记录创建 / bundle id 换绑 | ⚠️ 一次性操作 | ✅ 主路线 |

⚠️ 标记的边界随 ASC API 版本演进，用前查 Apple 官方文档确认；网页独有操作的纪律见 `references/browser-automation.md`。

## CI 化提示

- API Key 三要素（Key ID / Issuer ID / .p8 内容）存 CI secrets；`.p8` 内容注意保留换行。
- `skip_waiting_for_build_processing: true` 会造成「假成功」——包可能被 Apple 静默拒绝。排障时设回 `false` 让工具等到 Apple 处理结果。
- 打包/签名必须在 macOS runner；纯 ASC 操作（元数据/提审）可在 Linux runner 用 asc 完成。

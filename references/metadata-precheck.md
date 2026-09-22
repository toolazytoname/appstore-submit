# 送审前元数据自查（precheck）

来源：2026-09 一次 5.2.5 拒审（副标题用了 iPhone/iPad 字样）后的复盘。目的：**在提交前本地扫一遍元数据，把最常见的元数据类拒审在提交前拦下**。可借鉴的现成体系见文末。

## 一、Apple 商标规则（5.2.5 / 2.3.7 高危）

权威来源：[Guidelines for Using Apple Trademarks and Copyrights](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html)。

硬规则（名称 / 副标题 / 关键词，出现即高危）：

- 产品名：`iPhone`、`iPad`、`Mac`、`Watch`、`Vision Pro`、`AirPods`、`Pencil` 等——尤其「iPhone 与 iPad 上的 XX」「XX for iPhone」这类式样（暗示 Apple 背书，5.2.5 直接拒）。
- `Apple`、`App Store`、`iOS`、`iPadOS`、`macOS`、`Safari` 等服务/系统名做宣传性使用。
- 「for iPhone / for iPad / 适配 iPhone」式兼容表述：描述正文里也建议清理（本轮 Apple 只点了副标题，但描述同类措辞一并清了，防下轮）。

正确姿势：说「面向开发者的原生 XX 客户端」「适配窄屏与宽屏设备」，兼容性交给平台字段与截图表达。

## 二、其他高频元数据拒审点（借鉴 fastlane precheck 分类）

fastlane 曾有 `precheck` 专门做这件事（现已弃维护，但分类仍有效，词表见 [fastlane 源码 rules](https://github.com/fastlane/fastlane/tree/master/precheck/lib/precheck/rules)）：

| 类别 | 触发词示例 | 对应指南 |
| --- | --- | --- |
| 占位/假文案 | lorem ipsum、placeholder、text here | 2.1 |
| 未来功能 | coming soon、即将推出、in the next release | 2.1（宣称未实现功能） |
| 其他平台 | android、google、windows（白名单：兼容性说明里的 google analytics/drive） | 2.3.7 |
| IAP 免费 | free（有 IAP 时宣称 free） | 3.1.2 |
| 脏话 | fastlane 用哈希表存（`curse_word_hashes/en_us.txt`） | 1.1 |
| 版权年份 | © 年份过期/缺年份 | 5.2.5 |

## 三、本地一键扫描

`scripts/metadata-precheck.py`：

```sh
# 从 JSON/键值文件读（键=name/subtitle/keywords/description/promo_text）
python3 scripts/metadata-precheck.py metadata.json
# 或直接传字段
python3 scripts/metadata-precheck.py --name "Grove Git" --subtitle "..." --keywords "..." --description "..."
```

- 名称/副标题/关键词命中 Apple 产品词 = **FAIL**；描述命中 = WARN；占位词/未来功能/其他平台词 = WARN。
- 退出码非 0 = 存在 FAIL，送审前必须处理。

## 四、权威/可借鉴资源清单

- [App Review Guidelines（官方，唯一裁决标准）](https://developer.apple.com/app-store/review/guidelines/)
- [Guidelines for Using Apple Trademarks and Copyrights](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html)（5.2.5 的判定依据）
- [App Store 审核提交前检查单（Apple 官方 checklist）](https://developer.apple.com/help/app-store-connect/reference/app-review-checklist)
- [fastlane precheck 源码规则目录](https://github.com/fastlane/fastlane/tree/master/precheck/lib/precheck/rules)（弃维护但分类与词表可抄）
- 经验教训：fastlane precheck 也没覆盖「副标题用 Apple 产品名」——**官方商标指南才是 5.2.5 的唯一可靠依据**，本地扫描词表只是下限。

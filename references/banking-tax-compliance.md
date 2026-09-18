# 收款链路：银行账户 + 税表 + 合规申报

卖 IAP / 付费 App 必走。来自 2026-09 第三次实战（中国个人开发者，个人账户 + 付费协议）。

## 触发点与依赖图

签 Paid Apps Agreement 后触发 KYC 链。**收款的充要条件**（全部满足 Paid Apps 协议才 Active）：

```
银行账户 Active ──┐
税表两张 Active ──┼──→ Paid Apps Agreement Active → IAP 收入可结算
810 合规提交    ──┘
（DSA trader 申报独立走，只影响版本提交闸门）
```

银行状态生命周期：`Pending User Info`（还缺资料）→ `Verifying`（Apple 核验中，几分钟～几天）→ `Active`。

## 顺序（实测最短路径）

1. **银行账户**（Business 页「Add Bank Account」五行向导）：国家 → 账户持有人（同法实体 / Individual）→ CNAPS 行号 + 账号 + 昵称 → 确认。中国银行走 CNAPS 12 位联行号（招商银行北京海淀科技金融支行 = `308100005297`）。
2. **Add user info 向导**（加完银行横幅出现）：账户持有人信息 + 纳税人识别号（中国个人 = 身份证号）→ 一路 Next 到 Done。
3. **Compliance Screening**（可能滞后出现）：传**证件照**（护照/身份证，≤7MB）+ 出生国家/城市 + 是否上市（个人选 No）+ 持股比例（个人 100%）→ Submit。**这步提交后银行才从 Pending User Info 转 Verifying**。
4. **税表**（Tax Forms「Add Tax Info」）：预判题两问（非美税务居民？No；有美国商业活动？No）→ Save → 表格裂成**两张独立表**，分别打开各自 Submit：
   - Certificate of Foreign Status：预填好，勾声明 + 签名区 Title（填 Owner 即可）→ Submit
   - W-8BEN：勾第 9 条协定声明 → 填 Article 12 / 税率 10% → 收入类型选「Income from the sale of applications」→ 勾 Part III 两个认证框 → 6.a 填外国税号（中国个人 = 18 位身份证号）
5. **810 号令**（Compliance 表「Add Info」）：有无中国境内雇员/场所（个人开发者 No）→ 纳税人识别号（身份证号）→ Submit。之后可能再弹一个「Confirm Information」（Resident ID Card Number），再填一次身份证号。
6. 全绿后 DSA 仍 In Review 属正常（Apple 处理中，无需动作）。

## 中国个人开发者的税务口径（用户会问）

- App Store 收入在美国税法下按**特许权使用费（royalties）**处理；中美协定 Article 12 预扣 **10%**，这是该收入类型可得的最低美国预扣税率，**免不掉**。
- 10% **只扣美国区商店销售**；中国区及其他地区销售不扣美国税。
- W-8BEN 不填 FTIN/出生日期 Apple 也让提交（标 Optional），但协定税率可能不认、按 30% 兜底扣——**一定填 FTIN**。

## 状态探测（Cookie 会话直接 fetch，别猜 iris 路径）

`/ppm/v1/accounts/{accountId}/` 下的资源是 Business 页的真实数据源：

- `banks?legalEntityId={id}` / `pendingBankAccounts?legalEntityId={id}` — 银行状态
- `legalEntities` — 法实体（地址、vendorId、OFAC 状态）
- `legalEntities/{id}/complianceInfo` — 810/DSA
- `vendors/{vendorId}/taxRequirements` / `vendorScopes/{id}/taxForms` — 税表

iris 的组织/协议端点（`/iris/v1/organizations` 等）**不存在**（404）。拿真实 URL 的办法：页面加载后 `performance.getEntriesByType("resource")` 过滤 `ppm|tax|agreement|banking`。

## 排坑

- **Business 页状态闪烁**：后端最终一致性导致横幅/协议状态在 reload 之间跳变（一次 Active 一次 Pending）。判断标准：**有没有带按钮的行动横幅**——有按钮 = 真缺信息，没按钮 = 服务端处理中，别追着转态跑。
- **银行加没加上**不能看外层列表（默认折叠），展开「See More」或查 `banks` API；向导保存后提示「已经添加过了」= 其实存上了。
- **单选框 value 语义反转**：如 `useIncomeTypeOther` 组里「Income from the sale of applications」的 value 是 `"NO"`（= 不用 Other）。**一律按 label 文本定位，别信 value**。
- **W-8BEN 的 inline 输入** name 是 `articleReference` 和 `taxRate`（没有单独的 paragraph 字段）；别把段落号填进 taxRate。
- **证件照上传**（无 filechooser 的浏览器）：`node:fs` 读文件 → base64 按 ~400KB 分块多次 evaluate 推进 `window` 数组 → `join + atob` → `new File` + `DataTransfer` 赋 `input.files` → 派发 input/change。上传成功的标志是 UI 出现文件名 + Delete 按钮。
- **会话脆弱**：浏览器面板关闭/重启会清 Cookie → ASC 整个重登（2FA 只有用户能做）。提示用户登录页勾「Keep me signed in」，流程中途别关面板。

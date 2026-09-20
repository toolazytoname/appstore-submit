# ASC 网页自动化纪律

App Store Connect 是 React SPA，自动化填表最容易「看着填了其实没进状态」。以下纪律全部来自实战失败。

## 表单输入

- **`fill` / native setter 经常不进 React 状态**（页面显示有值，保存时丢或校验说没填）。
  可靠做法：先 `click` 聚焦输入框，再用 `key_type`（insertText）逐字输入。
- **a11y/AX 工具场景**：AX `type` 把值写进字段但保存按钮仍灰 = onChange 没触发；对该字段做一次 `select_text` **全选**即可触发状态更新（无需清空重输，2026-09 实测）。
- `<select>`：用 value 赋值 + 派发 `change` 事件（`select_option` 或 evaluate）。ASC 自定义下拉（类别）例外：**主要类别改动未保存时次要下拉被锁定**，先保存再操作（pitfalls #64）。
- radio / checkbox：**点 label** 比点 input 更稳。AX 的 `AXPress` 对 radio/普通按钮通常有效；`AXPick` 在 Chrome 自定义菜单上会失焦菜单，用 `AXPress`。
- 保存后**重载页面复核**持久化，不要信保存按钮的 toast。按钮文案变化（「保存」→「已保存」）是持久化成功的最快信号。

## 弹窗与对话框

- 「未保存的更改」导航拦截弹窗：一律先选「保存」，不要「舍弃」——否则刚填的静默丢失。
- ASC 的确认弹层（如「是否发布你的 App 隐私答复？」）是页面内 dialog，不是原生 alert；正常 snapshot 能看到，直接点按钮。
- 原生 JS dialog 会冻结渲染，必须先 `dialog status/accept/dismiss` 处理再继续。

## 导航

- 直接 `navigate` 某些 ASC 深层路由会 `ERR_ABORTED`（SPA 路由守卫）。改为从侧栏/列表页的链接点过去。
- ASC URL 结构：`/apps/{appleId}/distribution/ios/version/inflight`（版本页）、`/apps/{appleId}/distribution/privacy`（隐私）、`/apps/{appleId}/testflight/...`。带 `/teams/{teamId}/` 前缀的 URL 也能用。
- 多团队账户：URL 里的 teamId 和右上角团队名核对，别在错误团队下操作。

## 排障

- 抓包：`network` action 抓 `filter:"iris"`（ASC 后端 API 域名含 iris），看真实请求/响应比猜前端状态快。
- 页面间歇报「很抱歉，似乎出现一些问题」：多半是 ASC 服务端故障，换路由重进或等几分钟；连续多次（5+）同一路由失败就判定服务端问题，停止改参数重试。
- 表单状态异常时，用 `evaluate` 读 `input.value` / `checked` 拿真值，snapshot 的 accessibility 树可能滞后。
- **computer-use / 屏幕坐标场景的拦截层排障**（2026-09 实测）：坐标点击报 `pixel is owned by <别的 app>` 时按序排查——① IDE/编辑器全屏窗口盖住目标浏览器（AX 后台事件如 AXPress 照常送达、只有坐标点击被截胡，这是判断依据；解法 = AppleScript `set position` 钉住窗口 + activate）；② 通知中心透明全屏层（点非侧栏区域收起）；③ JXA 直注 CGEvent 绕过命中判定（模板见 pitfalls #70）；④ 目标窗口 bounds 会漂移，每轮点击前重新取 AX bounds 换算 raster 像素（公式见 pitfalls #71）。

## 会话

- 复用用户已登录的浏览器会话；不要在自动化里处理登录/2FA，会话过期请用户重新登录。
- 每个动作带 `tabId` 定位标签页；多标签时先 `find_tab` 重解析。

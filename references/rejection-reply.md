# 拒审回复（Guideline 2.1 Information Needed）

来自 2026-09 一次真实「2.1 - Information Needed」拒审的完整回复实战（新开发者账号首提被要求补充材料），全部步骤在 ASC 网页 + 命令行验证过。

## 2.1 Information Needed 的机制

- 邮件只说「requires your attention」，真正的 6 项要求在 ASC → App Review → 提审详情页的 Apple 消息里。
- 典型 6 项：①真机录屏（最新系统、从启动开始、典型流程；含账号注册/删除、UGC 举报、付费内容才需额外展示）②App 目的与目标用户 ③主要功能设置与访问说明（无凭据要明说）④核心功能依赖的外部服务清单（无就写 none）⑤地区差异（确认全球一致）⑥受监管行业/第三方受保护材料授权（不适用要说明）。
- **回复后审核自动恢复，不需要也不应该点 Resubmit**（该按钮保持禁用是正常的）。
- Apple 明确要求：信息既要回复在消息里，也要**同步填进 App Review Information 的 Notes 字段**（供后续提交参考）。

## 回复前先做的两件事

1. **把修复传上去**：若拒审前后有真机 bug 修复（例如本次 fd-walk EPERM），bump build 号重传。被拒版本可以换构建：版本页 Build 表删旧行（按钮 hover 才显示，Playwright 用 `evaluate(el => el.click())` 绕过可见性判定）→ 点 Add Build → 弹层里单选新构建 → Done → Save。提审详情页的条目会跟着显示新构建号。
2. **录真机演示视频**（Apple 要的核心材料），见下节。

## 真机演示录屏：唯一可靠路线

**结论先行：用 Mac 端 iPhone Mirroring 窗口 + `screencapture -v -l<窗口id>` 只录该窗口；用 UI 测试驱动真机跑完整流程。**

走过的弯路（都不可行）：

- ❌ QuickTime「新建影片录制」选 iPhone：新版 macOS 里 iPhone 源是 **Continuity Camera（后置摄像头）**，录到的是房间/人脸，不是屏幕。macOS Ventura 起已移除 QuickTime 的 iPhone 屏幕镜像。
- ❌ AVFoundation `AVCaptureDevice(deviceType: .external)`：同样是摄像头，不是屏幕。
- ❌ XCTest 自动录屏：testmanagerd 真的会录（失败轮的 xcresult 里有 mp4），但**官方只保留失败轮**，没有「总是保留」配置（xctestplan 的录屏选项只在失败时附加）；模拟器才有 `simctl io recordVideo`。
- ❌ devicectl：无截屏/录屏子命令；也没有 `terminate` 子命令。

正确路线步骤：

1. 打开 iPhone Mirroring（`/System/Applications/iPhone Mirroring.app`），窗口 ID 用一个小 Swift 脚本查 `CGWindowListCopyWindowInfo`（过滤 owner=iPhone Mirroring）。
2. **验证镜像 LIVE 必须用「可见的 App 切换」**：截两张 still → 中间用 devicectl 启动一个**当前不在前台**的 App → diff。对已前台 App 重复 launch 是 diff=0 假阴性，坑过三次。
3. 隔夜断连后重连：窗口会显示「iPhone in Use — Lock your iPhone to connect」→ 需要手机**锁屏一次**自动重连（超时了会出现 Connect 按钮可点）；**连接期间不要碰手机**（devicectl 启动会把「使用中」状态打回去导致 Timed Out）。已建立的会话在解锁后保持。
4. 录制：`screencapture -v -l<id> -V 300 out.mov`（后台跑；**视频文件在停止时才落盘**，别用「文件没出现」判断失败）。窗口在副屏也没关系，`-l` 按窗口 ID 录。注意 `screencapture` 不带 `-C` 时不录光标——但鼠标停在镜像窗口上可能被镜像注入成手机上的指针，**录制前把鼠标移出窗口**。
5. 同时跑 UI 测试驱动流程（`xcodebuild test -configuration Release -only-testing:<你的全流程测试>`，先卸载 App 保证全新首启）。
6. 后期（可选但强烈推荐）：**点击光圈叠加**——从 xcresult 活动日志提取每次 Tap 的绝对时间戳（`xcresulttool get test-results activities`），坐标用一个临时探针测试打印各屏 `app.debugDescription` 解析元素中心（**新测试文件必须先 xcodegen 重生成，否则 0 测试空过**），`ffmpeg overlay` 链逐点叠 PNG 圆点，时间对齐 = Tap epoch − 测试起始 epoch −（录像里启动转场时刻 − 裁剪起点）。
7. 裁剪：主屏引导留 2~3 秒起，流程结束 +2 秒止（帧差法找转场和静息点）。

### 无 UITest 目标时的手动驱动路线（2026-09-18 三轮实测）

纯手写 pbxproj 工程（无 xcodegen / project.yml）加 UITest 目标要动 8 处 section，风险大于收益时，可以**手动驱动镜像窗口**录屏：CGEvent 注入点击/滚轮跑流程 + 全屏（或 -l 窗口）录制。但环境坑密集，先读 `references/pitfalls.md` 52-62：防息屏（caffeinate 且**验证断言**）、`-V` 自然超时收尾（**SIGINT 丢文件**）、`-l` 全黑时全屏录 + `crop=` 裁剪、CGEvent 注入绕过全屏通知中心窗口、滚轮 continuous+pixel、每步动态取**面积最大**镜像窗口换算坐标、用户鼠标勿动、锁屏后镜像透明化、Vision OCR 本地定位元素、CLI 无麦克风（无音轨实测可过审）、沙盒新 IAP ≤24h 传播期「商店连不上」。第三次实战（节拍器 2.1 回复）全流程一镜过并成功提交。

## 视频隐私自查（发出前必做，全本地）

- **通知横幅扫描**：抽帧（fps=2），「顶栏变化但全屏不变」= 横幅候选；真横幅前后无全屏变化，**启动转场会造成误报**（用 6fps 放大复核前后帧是否被全屏 diff 包裹）。
- **壁纸检查**：照片壁纸含家人照片等隐私——首帧 RGB 饱和度直方图（照片 median_sat > 0.25）；或直接从 App 界面首帧开始剪掉主屏。
- 用户 Mac 上的查看工具若会把截图上传外部 CDN，改用纯本地像素统计（PIL）做判定，不要把设备帧传出本机。

## ASC 网页回复操作

1. 提审详情页 → Apple 消息底部「Reply to App Review」→ 编辑器（4000 字符上限）。
2. 正文 = 6 项完整英文说明（开头声明附件录屏的设备/系统/覆盖流程）。
3. **附件**：点 Attach File 会弹**原生 Open 面板**（内嵌浏览器也能弹）——Cmd+Shift+G 输完整路径 → 选中 → Open → 等待 Processing 上传完成（Reply 按钮从禁用变回可用）。若浏览器自动化不支持文件选择器，用桌面自动化驱动原生面板。
4. 点 Reply 发送 → 验证：编辑器关闭、Messages 计数 +1、消息体里出现正文与「Message Attachments: <文件名>」。
5. Notes 字段：版本页 App Review Information → Notes 填英文精简版 → Save（按钮从可点变回禁用 = 已持久化）。

## 命令速查

```sh
# 窗口 ID（取面积最大的镜像窗口，进程里有小窗会污染解析）
swiftc -O -o /tmp/find_win /tmp/find_win.swift && /tmp/find_win   # CGWindowListCopyWindowInfo 过滤 iPhone Mirroring
# 防息屏（先验证断言真的挂上）
caffeinate -disu -t 300 & pmset -g assertions | grep caffeinate
# 录制（定长自然超时收尾；kill -INT 会丢文件）
screencapture -v -l<WINID> -V 300 /tmp/demo.mov
# -l 录出全黑时的回退：全屏录 + 按窗口 bounds 裁剪（×2 视网膜）
screencapture -v -V 300 /tmp/raw.mov
ffmpeg -i /tmp/raw.mov -vf "crop=668:1470:708:66" -c:v libx264 -crf 23 /tmp/demo.mp4
# 测试驱动（全新安装起）
xcodebuild test -project X.xcodeproj -scheme X -configuration Release \
  -destination 'id=<UDID>' -allowProvisioningUpdates \
  -only-testing:UITests/YourFlowTest -resultBundlePath /tmp/r.xcresult \
  CODE_SIGN_STYLE=Automatic CODE_SIGNING_REQUIRED=YES CODE_SIGNING_ALLOWED=YES DEVELOPMENT_TEAM=<TEAM>
# Tap 时间戳
xcrun xcresulttool get test-results activities --test-id "<bundle/test()>" --path /tmp/r.xcresult
```

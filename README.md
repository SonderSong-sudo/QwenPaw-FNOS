# QwenPaw For FNOS

> 本仓库为 QwenPaw 的 FNOS 打包版本，适用于 FNOS 平台一键部署。
>
> **双入口版**：桌面提供两个程序 ——「QwenPaw」为完整 Web 界面，「QwenPaw 控制台」为侧边栏服务管理控制台（参考 [com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) 控制台模块，仅保留运行状态与运行日志，删除外网访问 / QQ群交流 / 关于模块）。
>
> **飞牛统一网关**：控制台侧边栏底部新增「飞牛统一网关」入口 —— 单端口 HTTP/HTTPS 自适应反向代理、外部自定义访问地址、访问密码鉴权（参考 [yuexps/deepseek.harness.fnos](https://github.com/yuexps/deepseek.harness.fnos) 的 harnessAdmin 设计）。
>
> **皮肤模式与应用设置**：控制台支持浅色 / 深色 / 跟随系统三态皮肤（应用设置 → 外观卡片可精确选择，localStorage 持久化）；「应用设置」入口 —— 外观、网络代理、重置访问密码、重置运行环境/修复服务（参考 [yuexps/deepseek.harness.fnos](https://github.com/yuexps/deepseek.harness.fnos) 应用设置模块）；「检查更新/升级」位于控制台首页「快速操作」模块。
>
> **外网访问**：「打开 QwenPaw」在飞牛网关模式下经 fnOS 统一网关子路径（`/app/qwenpaw_yuexps/qwenpaw/`，nginx 经 web.sock 转发），配合 DDNS / FN Connect / 路由器端口映射即可在外网访问；控制台「飞牛统一网关 → 访问地址」卡片会展示统一网关与反代端口两种入口。

<p align="center">
  <img src="https://gw.alicdn.com/imgextra/i1/O1CN01sens5C1TuwioeGexL_!!6000000002443-55-tps-771-132.svg" alt="QwenPaw Logo" width="120">
</p>

<p align="center"><b>懂你所需，伴你左右。</b></p>

</div>

你的 AI 个人助理；安装极简、本地与云上均可部署；支持多端接入、能力轻松扩展。

## 控制台功能

桌面安装后出现两个入口：

- **QwenPaw** — 完整 Web 界面（直连服务端口）
- **QwenPaw 控制台** — 带侧边栏的服务管理控制台：
  - **服务状态** — 实时显示运行/停止状态、PID、运行时长、版本、端口、认证状态
  - **服务控制** — 一键启动 / 停止 / 重启 QwenPaw 服务，支持打开完整 Web 界面
  - **快速操作** — 检查更新 / 打开 QwenPaw 完整界面 / 跳转运行日志（检查更新为双层版本检查：QwenPaw 内核查 PyPI、应用框架查 GitHub Releases，支持经网络代理检查；内核检测到新版本时**自动开始升级**，无需再点任何按钮——按钮短暂变蓝色「更新」即转入「升级中」），升级采用「**先 pip 升级 → 成功后才停服重启**」顺序（26.8.57 起：升级期间服务不断线，pip 失败则保持原服务继续运行），顶部横幅提示关键状态（检查结果 / 正在更新 / 启动成功，20s 自动消失），升级完成自动重启服务、恢复「检查」按钮并刷新页面，升级过程实时日志可查、滚动位置保持；无新版本提示「当前版本 vX 是最新版」。「打开 QwenPaw」按钮随服务状态切换：运行中为「打开」，未运行为「启动」。服务停止后状态卡「停止」按钮置灰不可点。升级流程为「**先 pip 升级 → 成功后才彻底停止服务（等内核进程真正退出且端口释放）→ 再启动**」，启动命令以 exec 自替换 bash、pid 文件即内核 pid，停止/升级语义确定。前端每 5s 轮询服务状态自愈按钮态（升级中断/请求异常导致的禁用态最多 5s 自动恢复），API 请求统一 40s 超时防挂起。应用框架新版 `.fpk` 仍经 fnOS 应用中心安装，数据与配置保留。网关反代 JS 的 basename 补丁采用全泛化正则，上游任意构建版本均可命中，参考 [com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) 控制台升级模块）
  - **运行日志** — 自动刷新、内容筛选、分页查看（最近 500 条）、一键清空
  - **飞牛统一网关**（侧边栏底部）— 单端口 HTTP/HTTPS 自适应反向代理：
    - **反向代理端口** — 默认 `2280`，同一端口自动识别 HTTP（局域网明文）与 HTTPS（自签名证书，首次访问需手动信任）请求并转发到 QwenPaw 内部服务
    - **访问密码鉴权** — 设置后所有经网关的访问需输入密码，SHA256 会话令牌 + 30 天 Cookie，连续 3 次输错锁定 1 小时
    - **三种打开方式** — 飞牛统一网关（经 fnOS 统一网关 `/app/qwenpaw_yuexps/qwenpaw/` 子路径，外网需先登录飞牛）/ 反代端口（直连代理端口）/ 自定义地址（填外部反向代理域名后跳转）
    - **自定义外部地址** — 支持 `http(s)://` 前缀，方便接入已有反代域名
    - 注：原「访问地址」卡片已移除（按 hostname 猜内网/外网天然不可靠：外网场景下页面无法获知 FN Connect/DDNS 公网域名、5666/5667 公网不可达、origin+/app/ 必先经 fnOS 登录墙；统一通过概览页快速操作与运行态状态卡上的「打开 QwenPaw」按钮访问，按配置的打开方式正确跳转）
  - **应用设置**（侧边栏底部）— 参考 DHS 应用设置模块：
    - **外观** — 皮肤模式三态：浅色 / 深色 / 跟随系统（localStorage 持久化，应用设置 → 外观卡片可精确选择）
    - **网络代理** — HTTP / HTTPS / SOCKS5 三种类型，支持认证；保存后注入 QwenPaw 出站环境变量（`HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`，`NO_PROXY` 排除本机回环），重启服务生效
    - **重置访问密码** — 已设密码时需校验当前密码（防外网恶意改密），重置后旧会话 Cookie 全部失效
    - **重置与修复** — 重置运行环境（停止 → 清日志 → 启动）、重启服务、修复服务

> 说明：若安装时修改了 Web 端口，「QwenPaw」桌面入口仍指向默认端口 2277，此时请从控制台的「打开 QwenPaw」按钮访问完整界面。

> **核心能力：**
>
> **由你掌控** — 记忆与个性化完全由你掌控，支持本地或云端部署。无第三方托管，无数据上传。
>
> **Skills 扩展** — 内置定时任务、PDF/Office 处理、新闻摘要等；自定义技能自动加载，无绑定。通过 Skills 决定 QwenPaw 能做什么。
>
> **多智能体协作** — 创建多个独立智能体，各司其职；启用协作技能，智能体间互相通信共同完成复杂任务。
>
> **多层安全防护** — 工具防护、文件访问控制、技能安全扫描，保障运行安全。
>
> **全域触达** — 钉钉、飞书、微信、Discord、Telegram 等频道，一个 QwenPaw 按需连接。
>
> **记忆进化与主动交互** — 智能体从交互中学习、反思经验、主动服务，越用越聪明。
>
> <details>
> <summary><b>你可以用 QwenPaw 做什么</b></summary>
>
> <br>
>
> - **社交媒体**：每日热帖摘要（小红书、知乎、Reddit），B 站/YouTube 新视频摘要。
> - **生产力**：邮件与 Newsletter 精华推送到钉钉/飞书/QQ，邮件与日历整理联系人。
> - **创意与构建**：睡前说明目标、自动执行，次日获得雏形；从选题到成片全流程。
> - **研究与学习**：追踪科技与 AI 资讯，个人知识库检索复用。
> - **桌面与文件**：整理与搜索本地文件、阅读与摘要文档，在会话中索要文件。
> - **探索更多**：用 Skills 与定时任务组合成你自己的 agentic app。
>
> </details>

---

## AGENTS.md 建议添加
```
## 依赖安装规范
- Python 仅使用虚拟环境，如`/var/apps/qwenpaw_yuexps/var/venv/bin/python3 与 pip`，QwenPaw本体已在此虚拟环境内。
- Node.js 严禁 -g/--global，只允许项目本地安装，所有命令严格遵循环境隔离。

---

## Dependency Installation Specifications
- Python: Use only virtual environments, e.g. `/var/apps/qwenpaw_yuexps/var/venv/bin/python3` and pip. QwenPaw runs inside this venv.
- Node.js: No `-g`/`--global` installs. Only local project dependencies, all commands with strict environment isolation.
```

## 更新日志

> 只记大变动，完整细节见各版本 commit。

### 1.1.4

- **内置内核升级至 QwenPaw 2.3.0**：与官方 wheel 逐字节一致（1136 个 py 文件 AST 全过）。依赖对齐 2.3.0 新结构：频道 SDK 27 项迁入 `[channels]` extra（框架 pip 安装行同步加 `-e …[channels]`）、`reme-ai==0.4.2.0`、新增 `PyJWT[crypto]`/`filelock`/`markdown-it-py` 等。
- **修复 2.3.0 启动失败（DEPENDENCY_STATE_ROOT_UNAVAILABLE）**：2.3.0 起 `import qwenpaw` 即要求 `<home>/.qwenpaw/dependency-environments` 可写，而 fnOS 应用账号 home 不存在 → 在 `cmd/common`（框架启停真实路径）与 `fngateway.build_service_command`（网关 API 重启路径）两处显式注入 `QWENPAW_DEPENDENCY_STATE_DIR`。
- **修复控制台主内容白屏**：2.3.0 前端把 basename 推断改成字面量 `"/console".replace(...)` 形态，网关 JS 补丁新增第四种注入形态（`window.__QWENPAW_BASENAME__`），未命中上游旧形态时兜底。
- **「QwenPaw」主入口统一走应用网关**：`app/ui/config` 改 `gatewaySocket: web.sock` + 网关深路径，不再直连 2277 拿未打补丁的前端（直连入口此前必白屏，外部 DDNS/IPv6 访问同样命中此问题）。
- **安全加固**（10-26 审计 #2/#3）：启动命令环境变量全部 `shlex.quote`；升级日志对代理凭据脱敏、脚本权限 600。
- **图标转标准 8bit RGBA**（尺寸画面不变）。注：商店详情页图标占位图的根因是 fnOS 安装器把 `/vol1/appcenter-downloads/<appid>-<ver>-tpk/` 解包目录建成无执行位目录，与包内容无关，`chmod -R 755` 该目录即可恢复。
- 收录「使用文档.md」。

### 1.1.3

- **修复「检查更新」对 post 版本的误判**（10-22）：PyPI 正式版判定原把版本串里含字母的一律当预发布挡掉——上游发 `2.2.2.post1` 后，检查更新永远停在 `2.2.2`、误报「已是最新版」。现按 PEP 440 只挡预发布/开发版（`a`/`b`/`rc`/`alpha`/`beta`/`pre`/`preview`/`dev`），放行 `post`/`rev`/`r` 修订（属正式发布，pip 不带 `--pre` 即可安装）；`2.2.1b2`/`rc1`/`dev1` 这类仍挡，防「说有新版、点升级装不上」。
- **内置内核升级至 QwenPaw 2.2.2.post1**（10-23）：与官方 wheel 逐字节一致；依赖新增钉住 `certifi>=2026.10.19`（post1 的实质变更）。

### 1.1.2

- **默认开启认证，启用控制台「终端」**（10-21）：`cmd/common` 的 `QWENPAW_AUTH_ENABLED` 由 `false` 改 `true`；QW-022 启动清理收窄为只清 `COPAW_AUTH_ENABLED`。凭据不入包——由使用者经控制台「环境变量」提供，启动时 `auto_register_from_env()` 建号。代价：直连端口会弹登录页（开认证的正常表现）。

- **关闭应用框架层（fpk）更新检查**（10-20 重发，版本号仍为 1.1.1）：点「检查更新」不再问外部 release 线——本包由本仓库自行构建，别人的版本号不代表你装了什么。`UPDATE_CHECK_URL` 改指本仓库 `SonderSong-sudo/QwenPaw-FNOS` 备用。**内核层 PyPI 检查与自动升级不受影响。**

- **版本号方案重置**：弃用 `26.8.x` 日期式编号，改用常规三段式。与历史版本无对应关系，不代表功能回退。
- **修复「应用权限」新增可访问文件夹导致应用停服约 2 分钟**：`cmd/common` 的配置回调此前无条件 `stop_process`，而飞牛对任何应用设置变更都会触发它。现改为仅当 **WebUI 端口真的变化**时才重启（端口需要进程重新监听），其余变更即时生效。依据：文件夹授权由文件系统记名 ACL 在 `open()` 时执法，内核并不读取 `TRIM_DATA_ACCESSIBLE_PATHS`（全包零命中），重启对它没有任何收益。
- **统一网关两项**：内容寻址资产（`/assets/` 带哈希）补 `Cache-Control: public, max-age=31536000, immutable`；不再无条件写 `Connection: close`，改由 HTTP/1.1 + 准确 `Content-Length` 维持 keep-alive。

---

## 致谢与版权

本仓库是 **QwenPaw 的 FNOS 打包分发版**，非 QwenPaw 本体。

- **原作者 / 上游项目**：[agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw)（QwenPaw 本体的全部知识产权归原作者所有）
- **打包分发**：`yuexps` —— [yuexps/QwenPaw-FNOS](https://github.com/yuexps/QwenPaw-FNOS)
- **本仓库维护**：[SonderSong-sudo](https://github.com/SonderSong-sudo)（基于上述分发版做控制台与网关增强）

参考与借鉴：

| 项目 | 借鉴内容 |
|---|---|
| [yuexps/deepseek.harness.fnos](https://github.com/yuexps/deepseek.harness.fnos) | 统一网关设计、应用设置模块、皮肤三态方案、反代子路径适配 |
| [dustink66/com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) | 控制台模块（服务状态 / 启停 / 运行日志） |

> 应用内标识（`manifest`）：`maintainer = agentscope-ai`、`distributor = yuexps`，保留原作者与分发方署名。

## Resources
QwenPaw: https://github.com/agentscope-ai/QwenPaw

FNOS: https://developer.fnnas.com/docs/guide

## License
本项沿用 Apache License 2.0 协议。

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
  - **快速操作** — 检查更新 / 打开 QwenPaw 完整界面 / 跳转运行日志 / 应用更新（检查更新为双层版本检查：QwenPaw 内核查 PyPI、应用框架查 GitHub Releases，支持经网络代理检查；内核检测到新版本后**自动开始升级**，无需再点「应用更新」，升级完成自动重启服务并实时展示升级日志；「应用更新」按钮保留为手动触发入口；应用框架新版 `.fpk` 仍经 fnOS 应用中心安装，数据与配置保留，参考 [com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) 控制台升级模块）
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

### 26.8.33（2026-09-01）

- **皮肤模式**：控制台支持浅色 / 深色 / 跟随系统三态切换（应用设置 → 外观卡片精确选择，localStorage 持久化）
  - 参考 [yuexps/deepseek.harness.fnos](https://github.com/yuexps/deepseek.harness.fnos) 的 `data-theme` 方案
- **UI 收敛**：移除侧边栏底部的「皮肤」快捷按钮，统一入口收敛到应用设置 → 外观卡片（修复原快捷按钮误触发导航监听导致主内容区空白的根因，单一交互入口更稳定）
- **运行态状态卡片**：在「重启服务」按钮旁新增「打开 QwenPaw」按钮，行为与快速操作入口完全一致（`port` 模式走 `http://host:proxyPort/`、`custom` 模式走 `customUrl`、默认走 `origin/app/qwenpaw_yuexps/qwenpaw/`，`_blank` 打开）
- **移除「飞牛统一网关 → 访问地址」卡片**：按 hostname 猜内网/外网天然不可靠（外网场景下页面无法获知 FN Connect/DDNS 公网域名、5666/5667 端口公网不可达、`origin + /app/` 必先经 fnOS 登录墙），改为通过概览页快速操作 + 运行态状态卡上的「打开 QwenPaw」按钮唯一可控跳转
- **修复外网访问地址**：「飞牛网关」模块的「访问地址」按访问来源动态渲染 —— 外网（FN Connect / DDNS / 域名）访问时只展示「当前 origin + `/app/qwenpaw_yuexps/qwenpaw/`」这一个可用地址（点击后先登录飞牛，登录成功自动进入 QwenPaw），不再展示公网不可达的 `:5666` / `:5667` 端口地址和反代端口直连地址；局域网访问仍完整展示 5666/5667 与反代端口地址。根因：外网链路中 5666/5667 端口不开放（FN Connect 为隧道转发），此前展示的端口地址外网打不开
- **修复**：外网访问 QwenPaw 时登录页图标不显示 —— 网关桥接脚本原先只拦截 `fetch` / `XHR` / `EventSource` / `WebSocket`，未覆盖 React 运行时通过 `img.src = "/xxx"` 设置的资源；已扩展 DOM 属性 setter 拦截（`src` / `href` / `poster` / `action` + `setAttribute` 兜底 + `style.backgroundImage` 的 `url()`），自动补 `/qwenpaw/` 子路径前缀
- **修复**：安装回调创建 venv 时未固定 umask，权限随执行环境漂移（可能建成 700 导致服务不可读）；已在 `install_callback()` 中设置 `umask 022`，稳定为 755/644
- **调整**：「检查更新 / 升级」从应用设置移至控制台首页「快速操作」模块

### 26.8.31（2026-08-31）

- **飞牛统一网关**：控制台侧边栏底部新增入口 —— 单端口 HTTP/HTTPS 自适应反向代理、外部自定义访问地址、访问密码鉴权（参考 DHS harnessAdmin 设计）
- **应用设置**：新增外观、网络代理（HTTP/HTTPS/SOCKS5）、重置访问密码、重置运行环境 / 修复服务
- **修复外网访问**：「打开 QwenPaw」改走 fnOS 统一网关子路径 `/app/qwenpaw_yuexps/qwenpaw/`（nginx 经 web.sock 转发），配合 DDNS / FN Connect / 端口映射即可外网访问
- **5667 HTTPS 场景对齐 DHS**：`randomUUID` polyfill（HTTP 非安全上下文不可用）、CSP 响应头剥离（防内联桥接脚本被拦截）、WebSocket 显式同源绝对地址、`Location` 响应头子路径改写

### 更早

- **控制台版改造**：桌面拆分为「QwenPaw」（完整界面）+「QwenPaw 控制台」（服务启停 / 状态 / 运行日志），参考 [com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) 控制台模块
- QwenPaw 升级至 v2.1.0

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

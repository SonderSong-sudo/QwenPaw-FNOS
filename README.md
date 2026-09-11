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
  - **快速操作** — 检查更新 / 打开 QwenPaw 完整界面 / 跳转运行日志（检查更新为双层版本检查：QwenPaw 内核查 PyPI、应用框架查 GitHub Releases，支持经网络代理检查；内核检测到新版本时**自动开始升级**，无需再点任何按钮——按钮短暂变蓝色「更新」即转入「升级中」，升级采用「先停服务 → pip 升级 → 再启动」顺序（避免 pip 替换运行中文件导致内核进程崩溃），顶部横幅提示关键状态（检查结果 / 正在更新 / 启动成功，20s 自动消失），升级完成自动重启服务、恢复「检查」按钮并刷新页面，升级过程实时日志可查、滚动位置保持；无新版本提示「当前版本 vX 是最新版」。「打开 QwenPaw」按钮随服务状态切换：运行中为「打开」，未运行为「启动」。服务停止后状态卡「停止」按钮置灰不可点。升级流程为「先彻底停止服务（等内核进程真正退出且端口释放）→ pip 升级 → 再启动」，启动命令以 exec 自替换 bash、pid 文件即内核 pid，停止/升级语义确定。前端每 5s 轮询服务状态自愈按钮态（升级中断/请求异常导致的禁用态最多 5s 自动恢复），API 请求统一 40s 超时防挂起。应用框架新版 `.fpk` 仍经 fnOS 应用中心安装，数据与配置保留。网关反代 JS 的 basename 补丁采用全泛化正则，上游任意构建版本均可命中，参考 [com.dustinky.qwenpaw](https://github.com/dustink66/com.dustinky.qwenpaw) 控制台升级模块）
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

### 26.8.71

- 修复内核升级被残留元数据误判为「版本未变化」（升级实际成功却不重启）；控制台版本显示抗残留（与内核一致）
- 运行日志按操作打中文分段横幅（服务启动/停止/重启、内核升级开始/完成/失败）
- 「修改配置」向导移除账号密码字段
- 修复 PyPI 官方源仍被 pip.conf 镜像副源压制

### 26.8.70

- 安装向导移除账号密码创建（装后默认免密）
- 应用设置新增「PyPI 安装源」选择（官方 / 清华 / 阿里云 / 中科大）

### 26.8.69

- 修复 PyPI 官方源选项不生效

### 26.8.68

- 修复控制台「更新」假成功（镜像滞后误判，升级前校验内核版本变化）
- 「历史日志」弹窗限高修复（关闭按钮始终可点）

### 26.8.67

- 修复外网访问被要求登录 QwenPaw（转发时剥离代理头，防内核按公网 IP 误判鉴权）

### 26.8.64-66

- 新增「登录认证」模块（网关访问密码开关、重置账号密码）
- 顶部横幅堆叠去重；开关状态获取修复

### 26.8.63

- 经飞牛统一网关访问免 QwenPaw 登录（网关信任模式）

### 26.8.62

- 修复 fnOS 系统更新后 WebUI 全页白屏（统一网关拦截 Authorization，改发带外自定义头）
- 治理配置升级自愈（fpk 升级不再打回安全配置）

### 26.8.61

- ReMe 状态面板 500 打包级自愈补丁；网关访问密码改掩码语义

### 26.8.60

- 修复「清空日志」后运行日志一直空白（跨天锚点与 fd 分裂）

### 26.8.58

- 修复远程网关访问时 DELETE/PUT/PATCH 操作报 501

### 26.8.57

- 升级流程改为 pip 成功才停服重启（升级期间服务不断线）

### 26.8.56

- 内核升级至 QwenPaw 2.2.0（上游正式版）

### 26.8.55

- 运行日志按天归档 + 历史日志浏览（保留 180 天）

### 26.8.54

- 运行日志改版为沉浸式终端

### 26.8.53

- 修复升级后内核闪退（启动确认 + 失败回传内核日志）

### 26.8.52

- 修复提示弹窗重叠

### 更早（26.8.31-39）

- 适配飞牛统一网关子路径挂载（WebUI 网关模式免密直出）与桌面图标
- 飞牛统一网关、应用设置、皮肤三态、控制台版改造（详见上文「控制台功能」）

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

#!/usr/bin/env python3
"""
QwenPaw 飞牛控制台网关
========================
参考 com.dustinky.qwenpaw 控制台模块实现：
在 fnOS 桌面打开应用时，不再进入 QwenPaw 完整聊天界面，
而是展示一个「控制台 + 运行日志」页面。

职责：
1. 通过 Unix Domain Socket 提供控制台静态页面（app/www，侧边栏控制台）
2. 提供服务管理 REST API：
   - GET  /api/status      -> 运行状态（running/pid/startAt/version/authEnabled）
   - GET  /api/config      -> 服务配置（port/working_dir/auth_enabled/access_mode/...）
   - GET  /api/logs        -> 运行日志（默认最近 500 行，剥除 ANSI）
   - POST /api/start       -> 启动 QwenPaw 服务
   - POST /api/stop        -> 停止 QwenPaw 服务
   - POST /api/restart     -> 重启 QwenPaw 服务
   - POST /api/clear_logs  -> 清空运行日志
   - GET  /api/check_update    -> 双层版本检查（内核 PyPI / 应用框架 GitHub Releases）
   - POST /api/action {upgrade}-> 后台 pip 升级内核并自动重启服务
   - GET  /api/upgrade_status  -> 升级进行中状态（结束后返回 exit code）
   - GET  /api/upgrade_logs    -> 升级过程日志
3. 飞牛统一网关（参考 deepseek.harness.fnos 的 proxy.go 设计）：
   - 单端口 HTTP/HTTPS 自适应反代（peek 首字节嗅探 TLS 分流）
   - 反向代理 QwenPaw WebUI 到外部反代端口
   - 访问密码鉴权（SHA256 token Cookie，3 次失败锁定 1 小时）
   - GET/POST /api/gateway -> 读写网关配置（proxy_port/access_password/access_mode/reverse_proxy_url）
"""

import os
import re
import sys
import ssl
import json
import time
import hashlib
import signal
import socket
import logging
import argparse
import subprocess
import socketserver
import importlib.util
from http.server import BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("fngateway")

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
STATUS_CACHE_TTL = 60

# 应用安装包版本（与 manifest 的 version 保持同步；升级时同步更新）
APP_VERSION = "26.8.41"
# 内核更新检查（PyPI 上游 qwenpaw 包；控制台「应用更新」直升内核的数据源）
PYPI_CHECK_URL = "https://pypi.org/pypi/qwenpaw/json"
# 应用框架更新检查（GitHub Releases，QwenPaw-FNOS 分发仓库）
UPDATE_CHECK_URL = "https://api.github.com/repos/yuexps/QwenPaw-FNOS/releases/latest"
UPDATE_CHECK_TTL = 600  # 检查结果缓存 10 分钟

if hasattr(socketserver, "UnixStreamServer"):
    BaseUnixServer = socketserver.UnixStreamServer
else:
    class BaseUnixServer(socketserver.TCPServer):
        address_family = getattr(socket, "AF_UNIX", socket.AF_INET)

        def server_bind(self):
            self.socket.bind(self.server_address)
            self.server_address = self.socket.getsockname()


class ThreadingUnixHTTPServer(socketserver.ThreadingMixIn, BaseUnixServer):
    """Unix Domain Socket HTTP 服务"""

    daemon_threads = True

    def __init__(self, socket_path: str, prefix: str, www_dir: str, cfg: dict):
        self.socket_path = socket_path
        self.prefix = prefix.rstrip("/")
        self.www_dir = www_dir
        self.cfg = cfg
        self._status_cache = None
        self._status_cache_ts = 0.0

        # 飞牛统一网关配置（data_dir/gateway.json）
        self.gateway_cfg = GatewayConfig(cfg.get("data_dir", ""))
        self._proxy_server = None
        self._proxy_thread = None
        self._update_cache = None
        self._update_cache_ts = 0.0

        if os.path.exists(socket_path):
            try:
                os.unlink(socket_path)
            except Exception:
                pass

        super().__init__(socket_path, FnGatewayHandler)

        try:
            os.chmod(socket_path, 0o666)
        except Exception:
            pass

    # ---------------- 服务状态 ----------------

    def read_pid(self) -> str:
        pid_file = self.cfg.get("pid_file", "")
        try:
            with open(pid_file, encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""

    def process_alive(self, pid: str) -> bool:
        if not pid or not pid.isdigit():
            return False
        try:
            os.kill(int(pid), 0)
            return True
        except (OSError, ProcessLookupError, PermissionError):
            return False

    def get_version(self) -> str:
        """从 venv 中读取 qwenpaw 版本（带 60s 缓存）"""
        now = time.time()
        if self._status_cache is not None and (now - self._status_cache_ts) < STATUS_CACHE_TTL:
            return self._status_cache

        version = "未知"
        venv_python = os.path.join(self.cfg.get("venv", ""), "bin", "python3")
        if os.path.exists(venv_python):
            try:
                code = (
                    "import importlib.metadata as m;"
                    "v='';"
                    "exec('try:\\n v=m.version(\\'qwenpaw\\')\\nexcept Exception: pass');"
                    "print(v)"
                )
                result = subprocess.run(
                    [venv_python, "-c", code],
                    capture_output=True, text=True, timeout=15,
                )
                version = result.stdout.strip() or "未知"
            except Exception as e:
                logger.warning(f"读取版本失败: {e}")

        self._status_cache = version
        self._status_cache_ts = now
        return version

    def auth_enabled(self) -> bool:
        """认证是否启用（与 cmd/common 的 QWENPAW_AUTH_ENABLED 保持一致）"""
        raw = os.environ.get("QWENPAW_AUTH_ENABLED", "true")
        return raw.strip().lower() in ("true", "1", "yes", "on")

    def working_dir(self) -> str:
        """QwenPaw 工作目录（与 cmd/common 保持一致）"""
        data_dir = self.cfg.get("data_dir", "")
        return os.environ.get("QWENPAW_WORKING_DIR", os.path.join(data_dir, ".qwenpaw"))

    def status(self) -> dict:
        running = False
        pid = ""
        start_at = None

        pid = self.read_pid()
        if self.process_alive(pid):
            running = True
            try:
                start_at = int(os.path.getmtime(self.cfg.get("pid_file", "")))
            except Exception:
                start_at = None
        else:
            pid = ""

        return {
            "success": True,
            "running": running,
            "pid": pid,
            "startAt": start_at,
            "version": self.get_version(),
            "authEnabled": self.auth_enabled(),
        }

    def config(self) -> dict:
        """控制台概览页所需的服务配置信息"""
        return {
            "success": True,
            "port": self.cfg.get("port", "2277"),
            "working_dir": self.working_dir(),
            "data_dir": self.cfg.get("data_dir", ""),
            "auth_enabled": self.auth_enabled(),
            # 飞牛统一网关（供「打开 QwenPaw」按钮按 access_mode 联动）
            "access_mode": self.gateway_cfg.get("access_mode"),
            "reverse_proxy_url": self.gateway_cfg.get("reverse_proxy_url"),
            "proxy_port": self.gateway_cfg.get("proxy_port"),
        }

    # ---------------- 飞牛统一网关（反代端口 + 密码鉴权） ----------------

    def gateway_config(self) -> dict:
        """GET /api/gateway：返回网关配置（密码不回传明文，仅返回是否已设置）"""
        gw = self.gateway_cfg
        np = gw.get("network_proxy") or {}
        return {
            "success": True,
            "proxy_port": gw.get("proxy_port"),
            "password_set": gw.password_set(),
            "access_mode": gw.get("access_mode"),
            "reverse_proxy_url": gw.get("reverse_proxy_url"),
            "proxy_running": self.proxy_running(),
            "internal_port": self.cfg.get("port", "2277"),
            "manifest_version": self.manifest_version(),
            "runtime_version": self.get_version(),
            "network_proxy": {
                "enabled": bool(np.get("enabled")),
                "type": np.get("type", "http"),
                "host": np.get("host", ""),
                "port": np.get("port", 0),
                "username": np.get("username", ""),
                "password_set": bool(np.get("password")),
            },
        }

    def save_gateway_config(self, data: dict) -> dict:
        """POST /api/gateway：校验并保存网关配置；端口变化时动态重启反代监听"""
        try:
            port = int(data.get("proxy_port", 0))
        except (TypeError, ValueError):
            return {"success": False, "message": "反代端口无效"}
        if not (1 <= port <= 65535):
            return {"success": False, "message": "反代端口必须在 1-65535 之间"}

        mode = str(data.get("access_mode", "fngateway")).strip()
        if mode not in ("fngateway", "port", "custom"):
            return {"success": False, "message": "打开方式无效"}

        url = str(data.get("reverse_proxy_url", "")).strip()
        if mode == "custom" and not url:
            return {"success": False, "message": "选择自定义地址时必须填写外部访问地址"}
        if url and not (url.startswith("http://") or url.startswith("https://")):
            return {"success": False, "message": "外部访问地址需以 http:// 或 https:// 开头"}

        # 网络代理（参考 DHS 应用设置的 network_proxy 模块）
        np_data = data.get("network_proxy")
        if isinstance(np_data, dict):
            try:
                np_port = int(np_data.get("port", 0) or 0)
            except (TypeError, ValueError):
                np_port = 0
            np_type = str(np_data.get("type", "http")).strip().lower()
            if np_type not in ("http", "https", "socks5"):
                np_type = "http"
            np_cur = dict(self.gateway_cfg.get("network_proxy") or {})
            new_np = {
                "enabled": bool(np_data.get("enabled")),
                "type": np_type,
                "host": str(np_data.get("host", "")).strip(),
                "port": np_port,
                "username": str(np_data.get("username", "")).strip(),
                "password": np_cur.get("password", ""),  # 默认保留旧密码
            }
            if "password" in np_data:
                pwd_field = str(np_data.get("password", ""))
                new_np["password"] = pwd_field  # 显式传空则清除
            if new_np["enabled"] and (not new_np["host"] or not (1 <= new_np["port"] <= 65535)):
                return {"success": False, "message": "启用网络代理时必须填写主机和有效端口"}
            self.gateway_cfg.set("network_proxy", new_np)

        old_port = self.gateway_cfg.get("proxy_port")
        self.gateway_cfg.set("proxy_port", port)
        # 密码仅在显式携带字段时更新（应用设置页保存代理时省略该字段，避免误清已设密码）
        if "access_password" in data:
            self.gateway_cfg.set("access_password", str(data.get("access_password", "")))
        self.gateway_cfg.set("access_mode", mode)
        self.gateway_cfg.set("reverse_proxy_url", url)
        self.gateway_cfg.save()

        if int(port) != int(old_port):
            self.start_proxy()

        return {
            "success": True,
            "message": "网关设置已保存",
            "proxy_running": self.proxy_running(),
        }

    def proxy_running(self) -> bool:
        t = getattr(self, "_proxy_thread", None)
        return t is not None and t.is_alive()

    def start_proxy(self):
        """启动单端口 HTTP/HTTPS 自适应反代监听"""
        self.stop_proxy()
        gw = self.gateway_cfg
        try:
            port = int(gw.get("proxy_port") or 0)
        except (TypeError, ValueError):
            port = 0
        if not (1 <= port <= 65535):
            logger.warning("飞牛统一网关: 反代端口无效(%r)，跳过启动", gw.get("proxy_port"))
            return

        try:
            internal_port = int(self.cfg.get("port", "2277"))
        except (TypeError, ValueError):
            internal_port = 2277

        srv = DualProtocolProxyServer(
            ("0.0.0.0", port),
            ProxyRequestHandler,
            gw,
            internal_port,
            self.cfg.get("data_dir", ""),
        )
        srv._active = True
        t = threading.Thread(target=self._proxy_loop, args=(srv,), daemon=True)
        t.start()
        self._proxy_server = srv
        self._proxy_thread = t
        logger.info("飞牛统一网关已启动: 反代端口=%d (HTTP/HTTPS 自适应, 目标 127.0.0.1:%d)", port, internal_port)

    def _proxy_loop(self, srv):
        try:
            while getattr(srv, "_active", False):
                try:
                    srv.handle_request()
                except OSError:
                    break
                except Exception as e:
                    logger.debug("代理请求处理异常: %s", e)
        finally:
            try:
                srv.server_close()
            except Exception:
                pass

    def stop_proxy(self):
        s = getattr(self, "_proxy_server", None)
        if s is not None:
            s._active = False
            try:
                s.socket.close()
            except Exception:
                pass
            t = getattr(self, "_proxy_thread", None)
            if t is not None and t.is_alive():
                t.join(timeout=3)
        self._proxy_server = None
        self._proxy_thread = None

    # ---------------- 日志 ----------------

    def _tail_lines(self, path: str, lines: int) -> list:
        """读取文件末尾 N 行，剥除 ANSI 颜色码"""
        result = []
        if not path or not os.path.exists(path):
            return result
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
                tailed = all_lines[-lines:] if len(all_lines) > lines else all_lines
            for line in tailed:
                stripped = ANSI_ESCAPE.sub("", line.rstrip("\n"))
                if stripped.strip():
                    result.append({"level": "info", "time": "", "message": stripped})
        except Exception as e:
            logger.error(f"读取日志失败: {e}")
        return result

    def read_log_tail(self, lines: int = 500) -> list:
        """读取运行日志末尾 N 行，剥除 ANSI 颜色码"""
        return self._tail_lines(self.cfg.get("log_file", ""), lines)

    # ---------------- 服务控制 ----------------

    def build_service_command(self) -> str:
        """构造 QwenPaw 启动命令（与 cmd/common 保持一致）"""
        venv_python = os.path.join(self.cfg.get("venv", ""), "bin", "python3")
        port = self.cfg.get("port", "2277")
        data_dir = self.cfg.get("data_dir", "")

        env_home = os.environ.get("HOME", data_dir)
        working_dir = os.environ.get("QWENPAW_WORKING_DIR", os.path.join(data_dir, ".qwenpaw"))
        auth_enabled = os.environ.get("QWENPAW_AUTH_ENABLED", "true")
        auth_user = os.environ.get("QWENPAW_AUTH_USERNAME", "admin")
        auth_pass = os.environ.get("QWENPAW_AUTH_PASSWORD", "admin")
        node_path = os.environ.get("PATH", "")

        cmd = (
            f"export HOME={env_home} && "
            f"export QWENPAW_WORKING_DIR={working_dir} && "
            f"export QWENPAW_AUTH_ENABLED={auth_enabled} && "
            f"export QWENPAW_AUTH_USERNAME={auth_user} && "
            f"export QWENPAW_AUTH_PASSWORD={auth_pass} && "
            f"export PATH={node_path} && "
            f"{venv_python} -m qwenpaw app --host 0.0.0.0 --port {port}"
        )
        proxy_env = self.proxy_env()
        if proxy_env:
            cmd = proxy_env + " && " + cmd
        return cmd

    def start_service(self) -> dict:
        if self.process_alive(self.read_pid()):
            return {"success": True, "message": "QwenPaw 已在运行"}

        log_file = self.cfg.get("log_file", "")
        pid_file = self.cfg.get("pid_file", "")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        cmd = self.build_service_command()
        try:
            with open(log_file, "ab") as log_f:
                proc = subprocess.Popen(
                    ["bash", "-c", cmd],
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )
            with open(pid_file, "w", encoding="utf-8") as f:
                f.write(str(proc.pid))

            time.sleep(2)
            if self.process_alive(str(proc.pid)):
                return {"success": True, "message": "QwenPaw 启动成功"}
            return {"success": False, "message": "QwenPaw 启动失败，请查看日志"}
        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            return {"success": False, "message": f"启动失败: {e}"}

    def stop_service(self) -> dict:
        pid = self.read_pid()
        pid_file = self.cfg.get("pid_file", "")

        if self.process_alive(pid):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass

            count = 0
            while self.process_alive(pid) and count < 10:
                time.sleep(1)
                count += 1

            if self.process_alive(pid):
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except Exception:
                    pass
                time.sleep(1)

            try:
                os.remove(pid_file)
            except Exception:
                pass
            return {"success": True, "message": "QwenPaw 已停止"}

        try:
            os.remove(pid_file)
        except Exception:
            pass
        return {"success": True, "message": "QwenPaw 未在运行"}

    def restart_service(self) -> dict:
        self.stop_service()
        return self.start_service()

    def clear_logs(self) -> dict:
        for key in ("log_file", "gateway_log"):
            path = self.cfg.get(key, "")
            if path:
                try:
                    open(path, "w").close()
                except Exception:
                    pass
        return {"success": True, "message": "日志已清空"}

    # ---------------- 版本升级 ----------------

    def manifest_version(self) -> str:
        """当前安装包版本（与 manifest 同步的常量）"""
        return APP_VERSION

    def _build_update_opener(self):
        """按网关 network_proxy 配置构造 urllib opener（GitHub 访问常需代理）"""
        import urllib.request
        proxy = self.gateway_cfg.get("network_proxy") or {}
        if proxy.get("enabled") and proxy.get("host") and proxy.get("port"):
            userinfo = ""
            if proxy.get("username"):
                userinfo = urllib.parse.quote(str(proxy["username"]), safe="")
                if proxy.get("password"):
                    userinfo += ":" + urllib.parse.quote(str(proxy["password"]), safe="")
                userinfo += "@"
            url = "%s://%s%s:%s" % (proxy.get("type", "http"), userinfo, proxy["host"], proxy["port"])
            handler = urllib.request.ProxyHandler({"http": url, "https": url})
        else:
            handler = urllib.request.ProxyHandler({})
        return urllib.request.build_opener(handler)

    def _pypi_latest(self):
        """查询 PyPI 上 qwenpaw 内核最新版本（失败返回 None，不抛异常）"""
        try:
            import urllib.request
            req = urllib.request.Request(
                PYPI_CHECK_URL,
                headers={"User-Agent": "QwenPaw-FNOS/" + APP_VERSION},
            )
            with self._build_update_opener().open(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            version = str((data.get("info") or {}).get("version") or "").strip()
            return version or None
        except Exception as e:
            logger.warning("查询 PyPI 内核最新版本失败: %s" % e)
            return None

    def check_update(self, force: bool = False) -> dict:
        """GET /api/check_update：双层版本检查（带缓存与失败降级）

        - 内核层（venv 里的 qwenpaw 包 vs PyPI 最新）：「应用更新」按钮可直接升级；
        - 应用框架层（fpk 安装包 APP_VERSION vs GitHub Releases）：
          只能经 fnOS 应用中心安装新版 .fpk，此处仅提示，失败也不影响内核层结果。
        """
        now = time.time()
        if not force and self._update_cache is not None and (now - self._update_cache_ts) < UPDATE_CHECK_TTL:
            return dict(self._update_cache)

        runtime_version = self.get_version()
        runtime_latest = self._pypi_latest()
        runtime_update = bool(
            runtime_latest
            and runtime_version != "未知"
            and self._version_gt(runtime_latest, runtime_version)
        )

        result = {
            "success": True,
            "current_version": self.manifest_version(),
            "runtime_version": runtime_version,
            "runtime_latest_version": runtime_latest,
            "runtime_update_available": runtime_update,
            "runtime_url": "https://pypi.org/project/qwenpaw/",
            "latest_version": None,
            "release_url": "",
            "release_name": "",
            "shell_update_available": False,
            # 兼容旧字段：任一层有更新即视为有更新
            "update_available": runtime_update,
            "message": "",
            "error": None,
        }

        # 应用框架（fpk）检查：GitHub Releases；失败仅降级为提示
        shell_error = None
        try:
            import urllib.request
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={
                    "User-Agent": "QwenPaw-FNOS/" + APP_VERSION,
                    "Accept": "application/vnd.github+json",
                },
            )
            with self._build_update_opener().open(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            tag = str(data.get("tag_name") or "").lstrip("v")
            latest = tag or None
            result["latest_version"] = latest
            result["release_url"] = data.get("html_url") or ""
            result["release_name"] = data.get("name") or tag
            cur = self.manifest_version()
            if latest and self._version_gt(latest, cur):
                result["shell_update_available"] = True
        except Exception as e:
            shell_error = str(e)

        # 组装提示文案
        parts = []
        if runtime_update:
            parts.append(
                "发现 QwenPaw 内核新版本 v%s（当前 v%s），点击「更新」直接升级"
                % (runtime_latest, runtime_version)
            )
        elif runtime_latest is None:
            parts.append(
                "QwenPaw 内核版本检查失败（当前 v%s），请确认 NAS 可访问 PyPI，或在「应用设置」中配置网络代理"
                % runtime_version
            )
        else:
            parts.append("QwenPaw 内核已是最新版本（v%s）" % runtime_version)
        if result["shell_update_available"]:
            parts.append(
                "应用框架有新版 v%s（当前 v%s），可在 fnOS 应用中心安装新版 .fpk（数据与配置保留）"
                % (result["latest_version"], result["current_version"])
            )
        elif shell_error:
            parts.append("应用框架版本检查失败（GitHub 访问异常）")
        result["message"] = "；".join(parts)

        self._update_cache = result
        self._update_cache_ts = now
        return result

    @staticmethod
    def _version_gt(a: str, b: str) -> bool:
        """'26.8.31' > '26.8.28'（忽略非数字段）"""
        def parts(v):
            return [int(seg) if seg.isdigit() else 0 for seg in re.split(r"[._-]", v)]
        return parts(a) > parts(b)

    # ---------------- 内核直接升级（参考 com.dustinky.qwenpaw 控制台升级模块） ----------------

    def _upgrade_paths(self) -> tuple:
        """升级相关文件路径（与 PID 文件同目录，即 TRIM_PKGVAR）"""
        var_dir = os.path.dirname(self.cfg.get("pid_file", "")) or "/tmp"
        return (
            os.path.join(var_dir, "upgrade.log"),     # 升级过程日志
            os.path.join(var_dir, "upgrade.pid"),     # 升级后台进程 PID
            os.path.join(var_dir, "upgrade.lock"),    # 并发锁目录
            os.path.join(var_dir, "upgrade.result"),  # 升级结果（exit code）
        )

    def upgrade_running(self) -> bool:
        """升级后台进程是否存活；顺便清理上次升级残留（PID 文件 / 锁目录）"""
        _log, up_pid, up_lock, _result = self._upgrade_paths()
        pid = ""
        try:
            with open(up_pid, encoding="utf-8") as f:
                pid = f.read().strip()
        except OSError:
            pid = ""
        if pid and self.process_alive(pid):
            return True
        if os.path.exists(up_pid) or os.path.exists(up_lock):
            try:
                os.remove(up_pid)
            except OSError:
                pass
            try:
                os.rmdir(up_lock)
            except OSError:
                pass
        return False

    def _build_upgrade_script(self, venv_python: str, pid_file: str, log_file: str,
                              up_log: str, up_pid: str, up_result: str, start_cmd: str) -> str:
        """构造后台升级脚本：pip 升级内核 -> 成功则重启服务（自包含，页面关闭也不中断）"""
        s = ""
        s += ': > "' + up_log + '"\n'
        s += 'echo "=== QwenPaw 内核升级开始 ===" >> "' + up_log + '"\n'
        s += 'echo "时间: $(date \'+%Y-%m-%d %H:%M:%S\')" >> "' + up_log + '"\n'
        s += 'echo "" >> "' + up_log + '"\n'
        s += 'echo "$ PYTHONUNBUFFERED=1 ' + venv_python + ' -m pip install --upgrade qwenpaw" >> "' + up_log + '"\n'
        s += ('PYTHONUNBUFFERED=1 "' + venv_python + '" -m pip install --upgrade --no-input qwenpaw'
              ' >> "' + up_log + '" 2>&1\n')
        s += 'rc=$?\n'
        s += 'echo "" >> "' + up_log + '"\n'
        s += 'if [ $rc -eq 0 ]; then\n'
        s += '  echo "=== 内核升级成功 ===" >> "' + up_log + '"\n'
        s += '  echo "正在重启 QwenPaw 服务..." >> "' + up_log + '"\n'
        s += '  if [ -f "' + pid_file + '" ]; then\n'
        s += '    old_pid=$(head -n 1 "' + pid_file + '" | tr -d \'[:space:]\')\n'
        s += '    if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then\n'
        s += '      kill -TERM "$old_pid" 2>/dev/null\n'
        s += '      count=0\n'
        s += '      while kill -0 "$old_pid" 2>/dev/null && [ $count -lt 20 ]; do\n'
        s += '        sleep 0.5\n'
        s += '        count=$((count + 1))\n'
        s += '      done\n'
        s += '      if kill -0 "$old_pid" 2>/dev/null; then\n'
        s += '        kill -KILL "$old_pid" 2>/dev/null\n'
        s += '      fi\n'
        s += '    fi\n'
        s += '    rm -f "' + pid_file + '"\n'
        s += '  fi\n'
        s += '  sleep 1\n'
        s += '  bash -c \'' + start_cmd + '\' >> "' + log_file + '" 2>&1 &\n'
        s += '  echo $! > "' + pid_file + '"\n'
        s += '  echo "QwenPaw 已重启" >> "' + up_log + '"\n'
        s += 'else\n'
        s += '  echo "=== 内核升级失败 (exit code: $rc) ===" >> "' + up_log + '"\n'
        s += 'fi\n'
        s += 'echo "$rc" > "' + up_result + '"\n'
        s += 'rm -f "' + up_pid + '"\n'
        return s

    def start_upgrade(self) -> dict:
        """POST /api/action {action:'upgrade'}：后台 pip 升级内核并自动重启服务"""
        if self.upgrade_running():
            return {"success": False, "message": "升级正在进行中，请稍候"}

        up_log, up_pid, up_lock, up_result = self._upgrade_paths()
        try:
            os.mkdir(up_lock)
        except OSError:
            return {"success": False, "message": "升级正在进行中，请稍候"}

        try:
            venv_python = os.path.join(self.cfg.get("venv", ""), "bin", "python3")
            if not os.path.exists(venv_python):
                return {"success": False, "message": "未找到 Python 虚拟环境，无法升级"}

            # 预检：PyPI 可达且内核已最新时直接拒绝，避免无谓的重启
            runtime_version = self.get_version()
            latest = self._pypi_latest()
            if (latest and runtime_version != "未知"
                    and not self._version_gt(latest, runtime_version)):
                return {
                    "success": False,
                    "message": "QwenPaw 内核已是最新版本（v%s），无需升级" % runtime_version,
                    "runtime_version": runtime_version,
                    "runtime_latest_version": latest,
                }

            log_file = self.cfg.get("log_file", "")
            pid_file = self.cfg.get("pid_file", "")
            start_cmd = self.build_service_command()
            script = self._build_upgrade_script(
                venv_python, pid_file, log_file, up_log, up_pid, up_result, start_cmd
            )

            # 清理上次结果文件
            try:
                os.remove(up_result)
            except OSError:
                pass

            proc = subprocess.Popen(
                ["bash", "-c", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            with open(up_pid, "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
            return {
                "success": True,
                "message": "内核升级已开始，升级期间请勿关闭页面",
                "pid": proc.pid,
            }
        except Exception as e:
            logger.error(f"启动内核升级失败: {e}")
            return {"success": False, "message": f"启动升级失败: {e}"}
        finally:
            # Popen 失败或预检拒绝时释放锁；成功时锁留给 upgrade_running 存活检测后清理
            if not os.path.exists(up_pid):
                try:
                    os.rmdir(up_lock)
                except OSError:
                    pass

    def upgrade_status(self) -> dict:
        """GET /api/upgrade_status：升级中返回 upgrading=true；结束后首次查询返回结果并消费"""
        if self.upgrade_running():
            return {"success": True, "upgrading": True}

        _log, _pid, _lock, up_result = self._upgrade_paths()
        exit_code = None
        if os.path.exists(up_result):
            try:
                with open(up_result, encoding="utf-8") as f:
                    exit_code = int(f.read().strip() or "-1")
            except Exception:
                exit_code = -1
            try:
                os.remove(up_result)
            except OSError:
                pass
            # 版本缓存失效，让状态页立即反映新版本
            self._status_cache = None

        if exit_code is None:
            return {"success": True, "upgrading": False, "finished": False}

        if exit_code == 0:
            new_version = self.get_version()
            return {
                "success": True,
                "upgrading": False,
                "finished": True,
                "exit_code": 0,
                "new_version": new_version,
                "message": "QwenPaw 内核升级完成（v%s），服务已重启" % new_version,
            }
        return {
            "success": True,
            "upgrading": False,
            "finished": True,
            "exit_code": exit_code,
            "new_version": None,
            "message": "QwenPaw 内核升级失败（exit %s），请查看升级日志" % exit_code,
        }

    def upgrade_logs(self) -> dict:
        """GET /api/upgrade_logs：返回升级日志末尾 500 行"""
        up_log, _pid, _lock, _result = self._upgrade_paths()
        return {"success": True, "logs": self._tail_lines(up_log, 500)}

    # ---------------- 重置密码 / 重置运行环境 ----------------

    def reset_password(self, data: dict) -> dict:
        """POST /api/gateway/reset_password：重置网关访问密码

        已设置密码时必须校验当前密码（防止外网控制台被恶意改密）；
        未设置密码时可直接设置新密码。密码变更后旧会话 Cookie 自动失效。
        """
        new_pwd = str(data.get("new_password", ""))
        confirm = str(data.get("confirm_password", ""))
        if not new_pwd:
            return {"success": False, "message": "请输入新密码"}
        if len(new_pwd) < 4:
            return {"success": False, "message": "密码长度至少 4 位"}
        if new_pwd != confirm:
            return {"success": False, "message": "两次输入的密码不一致"}

        cur = str(self.gateway_cfg.get("access_password") or "")
        if cur:
            old = str(data.get("current_password", ""))
            if not old:
                return {"success": False, "message": "已设置访问密码，请输入当前密码以确认重置"}
            if old != cur:
                return {"success": False, "message": "当前密码不正确"}

        self.gateway_cfg.set("access_password", new_pwd)
        self.gateway_cfg.save()
        return {"success": True, "message": "访问密码已重置，旧会话将全部失效"}

    def reset_runtime(self) -> dict:
        """POST /api/action {action:'reset'}：重置运行环境（停止 -> 清日志 -> 启动）"""
        self.stop_service()
        self.clear_logs()
        time.sleep(1)
        return self.start_service()

    # ---------------- 网络代理 ----------------

    def proxy_env(self) -> str:
        """按网关 network_proxy 配置生成环境变量导出语句（注入 QwenPaw 出站请求）"""
        proxy = self.gateway_cfg.get("network_proxy") or {}
        if not (proxy.get("enabled") and proxy.get("host") and proxy.get("port")):
            return ""
        host = str(proxy["host"])
        port = proxy["port"]
        userinfo = ""
        if proxy.get("username"):
            userinfo = urllib.parse.quote(str(proxy["username"]), safe="")
            if proxy.get("password"):
                userinfo += ":" + urllib.parse.quote(str(proxy["password"]), safe="")
            userinfo += "@"
        no_proxy = "export NO_PROXY=127.0.0.1,localhost,::1 && export no_proxy=127.0.0.1,localhost,::1"
        if str(proxy.get("type", "http")).lower() == "socks5":
            url = "socks5://%s%s:%s" % (userinfo, host, port)
            return "export ALL_PROXY=%s && export all_proxy=%s && %s" % (url, url, no_proxy)
        url = "http://%s%s:%s" % (userinfo, host, port)
        return (
            "export HTTP_PROXY=%s && export http_proxy=%s && "
            "export HTTPS_PROXY=%s && export https_proxy=%s && %s"
        ) % (url, url, url, url, no_proxy)


class FnGatewayHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        logger.info(f"{self.command} {self.path} - {format % args}")

    def do_GET(self): self.handle_request()

    def do_POST(self): self.handle_request()

    def do_HEAD(self): self.handle_request()

    def handle_request(self):
        prefix = self.server.prefix
        full = self.strip_prefix(self.path, prefix)  # 保留 query
        req_path = full.split("?", 1)[0]

        # 统一网关子路径：/qwenpaw/ -> 反代 QwenPaw WebUI（含 HTML 桥接改写）
        if req_path == "/qwenpaw":
            self.send_response(302)
            self.send_header("Location", prefix + "/qwenpaw/")
            self.end_headers()
            return
        if req_path.startswith("/qwenpaw/"):
            self.proxy_qwenpaw(full)
            return

        if req_path.startswith("/api/"):
            self.handle_api(req_path)
            return

        self.handle_static(req_path)

    @staticmethod
    def strip_prefix(path: str, prefix: str) -> str:
        if prefix and (path == prefix or path.startswith(prefix + "/")):
            path = path[len(prefix):]
            if not path.startswith("/"):
                path = "/" + path
        return path or "/"

    # ---------------- API ----------------

    def handle_api(self, path: str):
        server = self.server
        action = path[len("/api/"):].strip("/").replace("/", "_")
        method = self.command

        if action == "status":
            self.send_json(server.status())
            return

        if action == "config":
            self.send_json(server.config())
            return

        if action == "gateway":
            if method == "POST":
                body = self.read_body()
                try:
                    data = json.loads(body) if body else {}
                except Exception:
                    self.send_json({"success": False, "message": "请求体不是合法的 JSON"})
                    return
                self.send_json(server.save_gateway_config(data))
            else:
                self.send_json(server.gateway_config())
            return

        if action == "logs":
            lines = 500
            try:
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                for kv in query.split("&"):
                    if kv.startswith("lines="):
                        lines = int(kv.split("=", 1)[1])
            except Exception:
                pass
            logs = server.read_log_tail(max(50, min(lines, 2000)))
            self.send_json({"success": True, "logs": logs})
            return

        if action == "check_update":
            full_path = self.path or ""
            force = ("force=1" in full_path) or ("force=true" in full_path.lower())
            self.send_json(server.check_update(force=force))
            return

        if action == "upgrade_status":
            self.send_json(server.upgrade_status())
            return

        if action == "upgrade_logs":
            self.send_json(server.upgrade_logs())
            return

        if method != "POST":
            self.send_json({"success": False, "message": "仅支持 POST 请求"})
            return

        if action == "reset_password":
            body = self.read_body()
            try:
                data = json.loads(body) if body else {}
            except Exception:
                self.send_json({"success": False, "message": "请求体不是合法的 JSON"})
                return
            self.send_json(server.reset_password(data))
            return

        if action == "action":
            body = self.read_body()
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
            act = str(data.get("action", "")).strip()
            if act == "upgrade":
                self.send_json(server.start_upgrade())
            elif act == "reset":
                self.send_json(server.reset_runtime())
            elif act in ("restart", "repair"):
                self.send_json(server.restart_service())
            else:
                self.send_json({"success": False, "message": "未知操作: %s" % act})
            return

        if action == "start":
            self.send_json(server.start_service())
        elif action == "stop":
            self.send_json(server.stop_service())
        elif action == "restart":
            self.send_json(server.restart_service())
        elif action == "clear_logs":
            self.send_json(server.clear_logs())
        else:
            self.send_json({"success": False, "message": "无效的操作"})

    def send_json(self, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> bytes:
        """读取请求体（按 Content-Length）"""
        try:
            clen = int(self.headers.get("Content-Length", "0") or "0")
        except (TypeError, ValueError):
            clen = 0
        if clen <= 0:
            return b""
        return self.rfile.read(clen)

    # ---------------- 静态文件 ----------------

    def handle_static(self, path: str):
        www_dir = self.server.www_dir
        if path == "/" or path == "":
            path = "/index.html"

        rel = path.lstrip("/")
        if not rel or ".." in rel:
            self.send_error(400, "Bad Request")
            return

        target = os.path.normpath(os.path.join(www_dir, rel))
        if not target.startswith(os.path.normpath(www_dir)):
            self.send_error(403, "Forbidden")
            return

        if not os.path.isfile(target):
            self.send_error(404, "Not Found")
            return

        ext = os.path.splitext(target)[1].lower()
        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".htm": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".txt": "text/plain; charset=utf-8",
            ".log": "text/plain; charset=utf-8",
        }
        content_type = mime_map.get(ext, "application/octet-stream")

        try:
            with open(target, "rb") as f:
                body = f.read()
        except Exception as e:
            logger.error(f"读取静态文件失败 {target}: {e}")
            self.send_error(500, "Internal Server Error")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    # ---------------- 统一网关子路径反代（/qwenpaw/） ----------------

    def proxy_qwenpaw(self, full_path: str):
        """把 /qwenpaw/* 子路径反代到 QwenPaw 内部端口。

        参考 deepseek.harness.fnos 的 fngateway.go 实现：
        - 请求头伪装同源（Host/Origin/Sec-Fetch-Site）
        - 响应 HTML 改写绝对资源路径 + 注入桥接脚本（fetch/XHR/WebSocket/EventSource）
        - Set-Cookie 作用域从根路径改写为子路径
        - SSE / 无长度响应 chunked 流式；WebSocket 升级后裸双向透传
        """
        server = self.server
        try:
            internal_port = int(server.cfg.get("port", "2277"))
        except (TypeError, ValueError):
            internal_port = 2277
        upstream = full_path[len("/qwenpaw"):] or "/"
        if not upstream.startswith("/"):
            upstream = "/" + upstream

        body = self.read_body()
        conn = http.client.HTTPConnection("127.0.0.1", internal_port, timeout=60)
        try:
            conn.putrequest(self.command, upstream, skip_host=True, skip_accept_encoding=True)
            conn.putheader("Host", "127.0.0.1:%d" % internal_port)
            for k, v in self.headers.items():
                kl = k.lower()
                if kl in HOP_BY_HOP or kl == "host":
                    continue
                if kl == "origin":
                    conn.putheader("Origin", "http://127.0.0.1:%d" % internal_port)
                    continue
                if kl == "sec-fetch-site":
                    conn.putheader("Sec-Fetch-Site", "same-origin")
                    continue
                if kl == "accept-encoding":
                    # 禁用压缩，便于对 HTML 做注入改写
                    conn.putheader("Accept-Encoding", "identity")
                    continue
                if kl == "content-length":
                    continue
                conn.putheader(k, v)
            if body:
                conn.putheader("Content-Length", str(len(body)))
            conn.endheaders(body if body else None)

            resp = conn.getresponse()
            status, reason = resp.status, resp.reason
            rh = resp.getheaders()
            rh_dict = {k.lower(): v for k, v in rh}

            out = ["HTTP/1.1 %d %s" % (status, reason)]
            for k, v in rh:
                kl = k.lower()
                if kl in HOP_BY_HOP or kl == "content-length":
                    continue
                if kl == "set-cookie":
                    # 把根路径 Cookie 作用域改写为子路径，避免污染其他应用
                    v = re.sub(r";\s*Path=/(?=[,;\s]|$)", "; Path=/qwenpaw/", v, flags=re.IGNORECASE)
                if kl == "content-security-policy" or kl == "content-security-policy-report-only":
                    # 移除 CSP：注入的内联桥接脚本需放行，参考 DHS 适配
                    continue
                if kl == "location" and v.startswith("/") and not v.startswith("/qwenpaw"):
                    # 内部绝对路径重定向 -> 补子路径前缀，防止跳回 NAS 根路径 404
                    v = "/qwenpaw" + v
                out.append("%s: %s" % (k, v))

            # WebSocket 升级 -> 双向裸转发
            if status == 101:
                out.append("Connection: Upgrade")
                self._write_head_raw(out)
                self._tunnel_raw(conn, resp)
                return

            ct = rh_dict.get("content-type", "")
            is_html = "text/html" in ct.lower()
            is_js = "javascript" in ct.lower()
            has_cl = "content-length" in rh_dict
            is_stream = (not has_cl) or ("text/event-stream" in ct)

            if is_stream and not is_html:
                # SSE / 无长度响应 -> chunked 流式转发
                out.append("Transfer-Encoding: chunked")
                out.append("Connection: close")
                self._write_head_raw(out)
                self.wfile.flush()
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(("%x\r\n" % len(chunk)).encode("ascii") + chunk + b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
            else:
                payload = resp.read()
                if is_html:
                    payload = self._adapt_qwenpaw_html(payload)
                elif is_js:
                    payload = self._patch_qwenpaw_js(payload)
                out.append("Content-Length: %d" % len(payload))
                out.append("Connection: close")
                self._write_head_raw(out)
                self.wfile.write(payload)
                self.wfile.flush()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _patch_qwenpaw_js(self, payload: bytes) -> bytes:
        """给上游 JS 的 basename 推断函数打补丁，使其识别 fnOS 网关子路径。

        上游 QwenPaw WebUI（react-router v7）用 n6(pathname) 推断 basename，正则只认
        /console 一种前缀。挂在 fnOS 统一网关子路径（/app/<appid>/qwenpaw/）下时无法
        识别，basename 退化为 "/"，导致路由 /、/sessions 等全部失配、主内容 <Outlet />
        渲染为空（侧边栏正常）。这里让 n6() 优先返回网关注入的
        window.__QWENPAW_BASENAME__（由桥接脚本注入），未注入时保持原逻辑。
        """
        global _QWENPAW_PATCH_WARNED
        try:
            js = payload.decode("utf-8", "replace")
        except Exception:
            return payload

        # 1) 精确 anchor 快速路径（当前构建命中）
        if QWENPAW_BASENAME_ANCHOR in js:
            return js.replace(QWENPAW_BASENAME_ANCHOR, QWENPAW_BASENAME_PATCH, 1).encode("utf-8", "replace")

        # 2) 兜底：上游换构建导致 minified 标识符变化时，用正则泛化匹配
        m = QWENPAW_BASENAME_RE.search(js)
        if m:
            fn, const = m.group(1), m.group(2)
            patched = (
                'function %s(i){var b=window.__QWENPAW_BASENAME__;'
                'if(b&&i.indexOf(b)===0)return b;'
                'return/^\\/console(?:\\/|$)/.test(i)?%s:void 0}' % (fn, const)
            )
            logger.info("QwenPaw basename 补丁：精确 anchor 未命中，改用正则兜底 (函数 %s, 常量 %s)", fn, const)
            # 必须 encode 回 bytes：调用方按字节流处理（Content-Length / wfile.write）
            return (js[:m.start()] + patched + js[m.end():]).encode("utf-8", "replace")

        # 3) 都没命中：可能是上游改了实现。静默跳过会导致主内容空白且极难排查，故告警。
        if not _QWENPAW_PATCH_WARNED:
            _QWENPAW_PATCH_WARNED = True
            logger.warning(
                "QwenPaw basename 补丁未命中（%d 字节 JS）：未找到 n6 形式的 basename 推断函数。"
                "上游可能已改动实现，WebUI 挂在网关子路径下可能出现主内容空白，请重新核对上游产物。",
                len(payload),
            )
        return payload

    def _adapt_qwenpaw_html(self, payload: bytes) -> bytes:
        """改写 QwenPaw 前端 HTML：绝对资源路径 -> 相对路径 + 注入 <base href> + 网关桥接脚本"""
        try:
            html = payload.decode("utf-8", "replace")
        except Exception:
            return payload
        # 网关子路径基准（注入到桥接脚本，替代运行时依赖 location.pathname 推算）：
        # 外部访问形如 <NAS>:5666/app/qwenpaw_yuexps/qwenpaw/，SPA 路由 pushState 一旦脱前缀，
        # location.pathname 就不再可靠，必须由网关侧把正确基准钉死。
        gw_base = (self.server.prefix or "") + "/qwenpaw"
        # 静态资源属性（src/href/poster/action）的 "/xxx" -> "./xxx"（相对 <base href> 解析）
        html = re.sub(r'(\b(?:src|href|poster|action)\s*=\s*["\'])/', r"\1./", html)
        bridge = QWENPAW_BRIDGE_SCRIPT.replace("__GW_BASE__", gw_base)
        m = re.search(r"<head[^>]*>", html, re.IGNORECASE)
        if m:
            head_end = m.end()
            # <base href> 必须在 head 内其它 URL 引用元素之前（规范要求），故插在 head 最前
            base_tag = '<base href="%s/" />' % gw_base
            html = html[:head_end] + base_tag + bridge + html[head_end:]
        else:
            html = '<base href="%s/" />' % gw_base + bridge + html
        return html.encode("utf-8", "replace")

    def _write_head_raw(self, lines):
        head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
        self.wfile.write(head)
        self.wfile.flush()

    def _tunnel_raw(self, conn, resp):
        """WebSocket 升级后双向透传（client <-> 后端 TCP 裸转发）"""
        backend = conn.sock

        def pump(src, dst):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        t1 = threading.Thread(target=pump, args=(self.connection, backend), daemon=True)
        t2 = threading.Thread(target=pump, args=(backend, self.connection), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()


def parse_listen_address(addr: str):
    """兼容旧参数（已不再使用反向代理，仅解析保留）"""
    clean_addr = addr.replace("http://", "").replace("https://", "").strip().rstrip("/")
    if ":" in clean_addr:
        parts = clean_addr.split(":")
        host = parts[0] if parts[0] else "127.0.0.1"
        port = int(parts[1])
        return host, port
    return "127.0.0.1", int(clean_addr)


# =====================================================================
# 飞牛统一网关
# 单端口 HTTP/HTTPS 自适应反代 + 外部自定义地址 + 访问密码鉴权
# 参考 deepseek.harness.fnos (dhs) 的 proxy.go / fngateway.go 设计，
# 用 Python 标准库实现（Go 的 cmux 连接嗅探 -> socket.MSG_PEEK 首字节判断）
# =====================================================================

import threading  # noqa: E402
import urllib.parse  # noqa: E402
import http.client  # noqa: E402

GATEWAY_CFG_FILE = "gateway.json"
AUTH_COOKIE = "qwenpaw_gateway_session"
AUTH_LOGIN_PATH = "/_qwenpaw_auth"
AUTH_MAX_ATTEMPTS = 3
AUTH_LOCKOUT_SEC = 3600  # 3 次失败锁定 1 小时
AUTH_SALT = "qwenpaw_gateway_salt:"

HOP_BY_HOP = frozenset({
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
})

# 上游 QwenPaw WebUI 的 basename 推断函数（react-router v7）：
#   function n6(i){return/^\/console(?:\/|$)/.test(i)?c8e:void 0}   // c8e === "/console"
# 它只认 /console 一种子路径前缀，挂在 fnOS 统一网关子路径下时返回 undefined，
# 导致 basename 退化为 "/"、路由全部失配、主内容 <Outlet /> 空白（侧边栏正常）。
# 实测：Bse("/app/<appid>/qwenpaw/sessions") 修复前原样返回带前缀路径（失配），
# 修复后返回 "/sessions"（命中）。网关注入 window.__QWENPAW_BASENAME__ 后，
# 由下面的补丁让 n6() 优先返回它。
QWENPAW_BASENAME_ANCHOR = r'function n6(i){return/^\/console(?:\/|$)/.test(i)?c8e:void 0}'
QWENPAW_BASENAME_PATCH = (
    r'function n6(i){var b=window.__QWENPAW_BASENAME__;'
    r'if(b&&i.indexOf(b)===0)return b;'
    r'return/^\/console(?:\/|$)/.test(i)?c8e:void 0}'
)
# 兜底正则：上游重新构建后函数名(n6)/常量名(c8e)这类 minified 标识符会变，
# 精确 anchor 会失配。这里泛化两个标识符，保证换 hash/换构建仍能命中。
# 注意：被匹配的目标是一段 JS 源码文本，里面的 (?: \/ | $ ) 都是**字面字符**，
# 必须逐个转义（\| 和 \$）；若把 "|" 留作 alternation 运算符，整条正则会被切成
# 两个分支，常量名捕获组将落到分支外而永远为 None。
QWENPAW_BASENAME_RE = re.compile(
    r'function\s+(\w+)\(i\)\{return/\^\\/console\(\?:\\/\|\$\)/\.test\(i\)\?(\w+):void\s*0\}'
)
# 同一进程内只告警一次，避免每个 JS 请求都刷日志
_QWENPAW_PATCH_WARNED = False

# 统一网关子路径反代时注入前端页面的桥接脚本（参考 DHS fnGatewayBridgeScript）：
# 把 SPA 发出的同源绝对路径请求（/api/... 等）自动补全网关子路径前缀，
# 并改写 WebSocket/EventSource 的同源路径。静态资源由 HTML 改写为相对路径。
QWENPAW_BRIDGE_SCRIPT = """<script>
(function(){
  // 网关侧注入的子路径基准（如 /app/qwenpaw_yuexps/qwenpaw）。
  // 优先用注入值：SPA 路由脱前缀后 location.pathname 不可靠，必须由网关钉死。
  var B = "__GW_BASE__" || location.pathname.replace(/\\/+$/,'');
  // 网关注入：应用子路径 basename（如 /app/qwenpaw_yuexps/qwenpaw）。
  // 上游 QwenPaw WebUI（react-router v7）用 n6(pathname) 推断 basename，但其正则只认
  // /console 一种前缀；fnOS 网关路径 /app/<appid>/qwenpaw/ 无法被识别 -> basename 退化为
  // "/" -> 路由 /、/sessions 等全部失配 -> <Outlet /> 渲染空（侧边栏在、主内容空白）。
  // 注意：不能依赖 location.pathname 现算 —— SPA 路由脱前缀后它已不可靠，必须由网关钉死。
  try { window.__QWENPAW_BASENAME__ = B; } catch(_) {}
  // randomUUID polyfill：HTTP 局域网（非安全上下文）下 crypto.randomUUID 不可用，
  // 参考 DHS 适配文档（randomUUID is not a function），纯 JS 实现 RFC4122 v4 兜底
  try {
    if (window.crypto && !window.crypto.randomUUID) {
      window.crypto.randomUUID = function () {
        var b = new Uint8Array(16);
        var g = window.crypto.getRandomValues || window.crypto.webkitGetRandomValues;
        g.call(window.crypto, b);
        b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
        var h = [];
        for (var i = 0; i < 16; i++) h.push((b[i] < 16 ? '0' : '') + b[i].toString(16));
        return h[0]+h[1]+h[2]+h[3]+'-'+h[4]+h[5]+'-'+h[6]+h[7]+'-'+h[8]+h[9]+'-'+h[10]+h[11]+h[12]+h[13]+h[14]+h[15];
      };
    }
  } catch(_) {}
  // 站内 http(s) 绝对 URL -> 补子路径前缀（仅同源，跨域原样放行）
  function fix(u){
    if (typeof u !== 'string' || !u) return u;
    if (u.charAt(0) === '/') {
      if (u.indexOf(B) === 0) return u;  // 已带前缀（如 location.pathname 拼接），幂等
      return B + u;
    }
    if (!/^https?:/i.test(u)) return u;
    try {
      var x = new URL(u);
      if (x.origin !== location.origin) return u;
      if (x.pathname.indexOf(B) === 0) return u;
      return x.origin + B + x.pathname + x.search + x.hash;
    } catch(e) { return u; }
  }
  if (window.fetch) {
    var of = window.fetch.bind(window);
    window.fetch = function(input, init){
      if (typeof input === 'string') { input = fix(input); }
      else if (input && typeof input === 'object' && typeof input.url === 'string') {
        try { input = new Request(fix(input.url), input); } catch(e){}
      }
      return of(input, init);
    };
  }
  // SPA 路由（React Router v7 等）通过 history.pushState/replaceState 跳转。
  // basename 正确后上游自身会写出带前缀的 URL（basename + to），此处补前缀仅作兜底：
  // 保证 URL 不脱出 fnOS 统一网关（否则 favicon、刷新、子路由 fallback 全部 404）。
  // 幂等：已带前缀的 URL 不重复补。
  try {
    var _push = history.pushState, _replace = history.replaceState;
    history.pushState = function(st, t, u){
      if (typeof u === 'string' && u.charAt(0) === '/' && u.indexOf(B) !== 0) u = B + u;
      return _push.call(this, st, t, u);
    };
    history.replaceState = function(st, t, u){
      if (typeof u === 'string' && u.charAt(0) === '/' && u.indexOf(B) !== 0) u = B + u;
      return _replace.call(this, st, t, u);
    };
  } catch(_) {}
  if (window.XMLHttpRequest) {
    var ox = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(m, u){
      var a = arguments; a[1] = fix(u);
      return ox.apply(this, a);
    };
  }
  if (window.EventSource) {
    var OE = window.EventSource;
    window.EventSource = function(u, c){ return new OE(fix(u), c); };
    window.EventSource.prototype = OE.prototype;
    window.EventSource.CONNECTING = OE.CONNECTING;
    window.EventSource.OPEN = OE.OPEN;
    window.EventSource.CLOSED = OE.CLOSED;
  }
  if (window.WebSocket) {
    var OW = window.WebSocket;
    window.WebSocket = function(u, p){
      if (typeof u === 'string') {
        if (u.charAt(0) === '/') {
          // 站内相对路径：https 页面走 wss，http 页面走 ws
          u = (location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host + fix(u);
        } else {
          // 显式同源绝对地址（如 ws://<NAS>:5667/xxx）：补前缀；跨域/外部 OneBot 原样放行
          try {
            var wu = new URL(u, location.href);
            var pg = new URL(location.href);
            var pagePort = pg.port || (pg.protocol === 'https:' ? '443' : '80');
            var wsPort = wu.port || (wu.protocol === 'wss:' ? '443' : '80');
            if ((wu.protocol === 'ws:' || wu.protocol === 'wss:') &&
                wu.hostname === pg.hostname && wsPort === pagePort &&
                wu.pathname.indexOf(B) !== 0) {
              wu.pathname = B + wu.pathname;
              u = wu.toString();
            }
          } catch(_) {}
        }
      }
      return (p === undefined) ? new OW(u) : new OW(u, p);
    };
    window.WebSocket.prototype = OW.prototype;
    window.WebSocket.CONNECTING = OW.CONNECTING;
    window.WebSocket.OPEN = OW.OPEN;
    window.WebSocket.CLOSING = OW.CLOSING;
    window.WebSocket.CLOSED = OW.CLOSED;
  }
  // DOM 属性 setter 拦截：JS 直接设置的 /xxx 资源路径（如 img.src = "/creator-logo.png"）。
  // 浏览器对属性赋值走 origin root，不受 HTML 属性正则改写覆盖，必须在 setter 层补前缀。
  // 覆盖：<img>/<script>/<link>/<a>/<source>/<video>/<audio> 的 src/href/poster/action，
  // 以及 element.setAttribute('src'|'href'|...) 兜底（部分代码绕过 property setter）。
  try {
    (function(){
        var P = ['src','href','poster','action'];
        function patch(proto){
          if (!proto) return;
          P.forEach(function(p){
            var d = Object.getOwnPropertyDescriptor(proto, p);
            if (!d || !d.set || !d.configurable) return;
            Object.defineProperty(proto, p, {
              get: d.get, set: function(v){
                if (typeof v === 'string' && v.charAt(0) === '/' && v.indexOf(B) !== 0) v = B + v;
                d.set.call(this, v);
              }, configurable: true, enumerable: d.enumerable
            });
          });
        }
        patch(window.HTMLImageElement && HTMLImageElement.prototype);
        patch(window.HTMLScriptElement && HTMLScriptElement.prototype);
        patch(window.HTMLLinkElement && HTMLLinkElement.prototype);
        patch(window.HTMLAnchorElement && HTMLAnchorElement.prototype);
        patch(window.HTMLSourceElement && HTMLSourceElement.prototype);
        patch(window.HTMLMediaElement && HTMLMediaElement.prototype);
        // 拦截 setAttribute('src'|'href'|..., '/foo')：部分代码绕过 property setter
        if (window.Element && !Element.prototype.__qwenpaw_patched) {
          var osa = Element.prototype.setAttribute;
          Element.prototype.setAttribute = function(n, v){
            if (typeof v === 'string' && P.indexOf(n) !== -1 &&
                v.charAt(0) === '/' && v.indexOf(B) !== 0) v = B + v;
            return osa.call(this, n, v);
          };
          Element.prototype.__qwenpaw_patched = true;
        }
        // 拦截 element.style.backgroundImage = "url('/foo')" 的内联样式绝对路径
        try {
          var ob = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, 'backgroundImage');
          if (ob && ob.set && ob.configurable) {
            Object.defineProperty(CSSStyleDeclaration.prototype, 'backgroundImage', {
              get: ob.get, set: function(v){
                if (typeof v === 'string' && v.indexOf('url(') !== -1) {
                  // 捕获包含前导 / 的整段路径，避免 B 与 / 直接拼接缺分隔符
                  v = v.replace(/url\(\s*(['"]?)(\/[^'"\s)]+)\1\s*\)/g,
                    function(_, q, pth){
                      if (pth.indexOf(B) === 0) return 'url(' + q + pth + q + ')';
                      return 'url(' + q + B + pth + q + ')';
                    });
                }
                ob.set.call(this, v);
              }, configurable: true, enumerable: ob.enumerable
            });
          }
        } catch(_) {}
      })();
  } catch(_) {}
})();
</script>"""

# 内置兜底自签名证书（openssl 不可用 / 生成失败时回退；有效期 10 年）
FALLBACK_CERT = """-----BEGIN CERTIFICATE-----
MIIDHTCCAgWgAwIBAgIUCknZzBOJL2CSh8IvmwYZbdmfOJswDQYJKoZIhvcNAQEL
BQAwHjEcMBoGA1UEAwwTUXdlblBhdy1OQVMtR2F0ZXdheTAeFw0yNjA4MzEwNzA2
MzVaFw0zNjA4MjgwNzA2MzVaMB4xHDAaBgNVBAMME1F3ZW5QYXctTkFTLUdhdGV3
YXkwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC6a8fX6tXYNGZdtTFc
QhRDlPnJ4b1FbFvuf90FXuTk0jgyzqu70fLTC827LEqt+UCfdOcVKQNnR3UygBFj
Vud/WYU377tQg86d9S85cN63Vvd1VmjEuB0A7fjSiBJr+fouFBXgf4kYvlI1wKiI
RJl5fIpc9VkUK1+wTpcKBJbrx1LQvmxcy1VLOzAYATQIRItZT+Akpoh2fmQ/Qt/M
nC5ch53ysQ1vhbfPvkdjHNSGPgFMUajvRvqudjQYIhNTw0sAsEX02Z9yvuowLBxF
bm8HBCqTMQ4W82OoP79CSgjLoB9jLkGXzpRvE/GM6wo1d5CjWKa+PbSbnWW+yLc8
7g0bAgMBAAGjUzBRMB0GA1UdDgQWBBSqmi5KOaWMC73Xuy7C98qotxN4ejAfBgNV
HSMEGDAWgBSqmi5KOaWMC73Xuy7C98qotxN4ejAPBgNVHRMBAf8EBTADAQH/MA0G
CSqGSIb3DQEBCwUAA4IBAQAk+6V9aJoG0UjMZnu0xtgNfc9i7ips33wUMFJbyYt8
Zo1QQDxJ/oTfPTWGamRstvkPF+zGM1+Rlbbc8cvaUTNwbA/wvCiJxWA8wkYTC5va
FTLuK4mvDFshnvF8C41A6iX8HqgpUsYYoIx18G7JQZZLLjD4ZAjp/4qAJGkn+oJ1
b8rcpIqSnGWEwi3FCSx/18XizJTFTdNHJ30dSwtakuV2HD/awKT1Iepo3FQNXgMl
JQ9wBhi+GZYcYFJl5ZMbdbkdbpqoSIirWLXpuz8FJe0LGEoYRMcr21LDc9XYEkuG
37td7yob4qCv8YECM7GmjIqeXzbtfOoSRzqFI7E7ySdk
-----END CERTIFICATE-----
"""
FALLBACK_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC6a8fX6tXYNGZd
tTFcQhRDlPnJ4b1FbFvuf90FXuTk0jgyzqu70fLTC827LEqt+UCfdOcVKQNnR3Uy
gBFjVud/WYU377tQg86d9S85cN63Vvd1VmjEuB0A7fjSiBJr+fouFBXgf4kYvlI1
wKiIRJl5fIpc9VkUK1+wTpcKBJbrx1LQvmxcy1VLOzAYATQIRItZT+Akpoh2fmQ/
Qt/MnC5ch53ysQ1vhbfPvkdjHNSGPgFMUajvRvqudjQYIhNTw0sAsEX02Z9yvuow
LBxFbm8HBCqTMQ4W82OoP79CSgjLoB9jLkGXzpRvE/GM6wo1d5CjWKa+PbSbnWW+
yLc87g0bAgMBAAECggEAVU9TcczGtZ0tJz7u6sBWk6LOOIO0YNu4qkkbNQT7DHfj
PeT0FAx86fWh3UDkn/7Lgu01fqp5Iz9BM64FxwcTA2VNII71kl/vIrv8M3YihZYn
wiub4EI9C5rbXkTk4ULRKVsJs+XJMGiQKIcU2N9DuKO0kdu5OxCqRn2AgxYclqKl
mTGfpC5uWwDhONjrn81CqyDzwFf0EciZJsdaDQveoFjObN1K9mV1lh+di5Aega/w
CKUB3R2I7fPjH14aJTu3zAZohgTagnpUlwN9EL5ML2sD+YitAQrFA3bzv0wzfzRx
LPq+yi+S7yIrRRbtRA1a12QvTHAATZ5WAJ8OKmeBYQKBgQDetYbuoFtYnnhOYdJe
GBylJKYI2HchsbpJTRDkOm0t74b0Wj0nnCUylrH5mWU8tg3vDF6ytgljCzYQMGxI
4O43k/jo6+iVA3z93GehvzW7hg6COMa/dtKwFgw4gsst7LwVOK6w+xg2qNykbyDR
rAtFjplCLe511ecqfom4M9i+6wKBgQDWSZuB9FjQ5inDTPOEB7C3kiBNnHExTVFM
TCI35jqLhC6wocSODcJKagIbNhVMqjUx+QYjO3k9o70YuI5RA5otjiQdU/F4uVvl
tX6I6fF4Qi9XAF1T9nzAhs5fy+7Js5a1tVF26UJYbL3tCL0dfspgdzNN69QveH/N
ITe1WYc+kQKBgQC0vpZXrAT2kwYIdxOIEgGNdYTawPNOgTMysjz3PQPGuBLK1UG0
l+EIgYzHiVrEPuxoCZ4BZAOSQlMKKIJ5UzOCH7FvN6Z26XHThcEFYG13V4EG5pVG
ZmTvS7V3V48WIn8yqeH8+IvaMImBWj9Ea2BqfySatTRGpecKcc/LkyhhKQKBgQCK
YLQkQndMRyV28e1bOGAc2yczFzBdZxF11MBQGsN5rt07wOsd1LK/vR8pFU7B2DRL
1gTpoZFUhbUqDpwQouPgQSb/LWME06YNe5t/rJr7TrolU53xB35eEW+ZmybTZ76O
Ds3RnSXz1hz7waXmMydbDf66dezqzsSw4Z+I44ybkQKBgHRy+pJvljv1mmzIrM6r
1jxBBGpcboR0991h+E4VymYhh5QWcW0ZLbltafRJCSvNEu8hJldSucmwJWIMDnB5
nBnJTRRFwGz+pJN+h8P03ORCR+o98Iq7CWk6B+0ubhu3x56vZt66TNJ5PG86nFH/
YBctkKs1Ap4OVzrPWvIuNtt1
-----END PRIVATE KEY-----
"""


def auth_token(pwd: str) -> str:
    """访问密码 -> 会话 token（SHA256）"""
    return hashlib.sha256((AUTH_SALT + pwd).encode("utf-8")).hexdigest()


class AuthTracker:
    """按客户端 IP 记录密码失败次数与锁定时间"""

    def __init__(self):
        self._locks = {}
        self._mu = threading.Lock()

    def _purge(self, ip):
        rec = self._locks.get(ip)
        if rec and rec["lock_until"] and time.time() >= rec["lock_until"]:
            self._locks.pop(ip, None)
            return None
        return rec

    def check(self, ip):
        """返回 (locked, remain_seconds, attempts_left)"""
        with self._mu:
            rec = self._purge(ip)
            if rec and rec["failed"] >= AUTH_MAX_ATTEMPTS:
                return True, max(0, rec["lock_until"] - time.time()), 0
            return False, 0, AUTH_MAX_ATTEMPTS - (rec["failed"] if rec else 0)

    def fail(self, ip):
        """记录一次失败；返回 (locked_now, remain_seconds, attempts_left)"""
        with self._mu:
            rec = self._purge(ip)
            if not rec:
                rec = {"failed": 0, "lock_until": 0}
                self._locks[ip] = rec
            rec["failed"] += 1
            if rec["failed"] >= AUTH_MAX_ATTEMPTS:
                rec["lock_until"] = time.time() + AUTH_LOCKOUT_SEC
                return True, AUTH_LOCKOUT_SEC, 0
            return False, 0, AUTH_MAX_ATTEMPTS - rec["failed"]

    def success(self, ip):
        with self._mu:
            self._locks.pop(ip, None)


class GatewayConfig:
    """飞牛统一网关配置，持久化于 {data_dir}/gateway.json"""

    DEFAULTS = {
        "proxy_port": 2280,
        "access_password": "",
        "access_mode": "fngateway",      # fngateway | port | custom
        "reverse_proxy_url": "",
        "network_proxy": {"enabled": False, "type": "http", "host": "", "port": 0, "username": "", "password": ""},
    }

    def __init__(self, data_dir: str):
        self.path = os.path.join(data_dir, GATEWAY_CFG_FILE) if data_dir else ""
        self._data = dict(self.DEFAULTS)
        self.load()

    def load(self):
        if not self.path or not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k in self.DEFAULTS:
                    if k in data:
                        self._data[k] = data[k]
        except Exception as e:
            logger.warning("读取网关配置失败: %s", e)

    def save(self):
        if not self.path:
            return
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            logger.error("保存网关配置失败: %s", e)

    def get(self, key, default=None):
        return self._data.get(key, self.DEFAULTS.get(key, default))

    def set(self, key, value):
        self._data[key] = value

    def password_set(self) -> bool:
        return bool(self.get("access_password"))


def ensure_cert(data_dir: str):
    """确保 HTTPS 证书存在：优先 openssl 现生成，失败回退内置证书"""
    if not data_dir:
        return None, None
    cert_dir = os.path.join(data_dir, "certs")
    cert_file = os.path.join(cert_dir, "server.pem")
    key_file = os.path.join(cert_dir, "server-key.pem")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    try:
        os.makedirs(cert_dir, exist_ok=True)
        subprocess.run(
            ["openssl", "req", "-x509", "-newkey", "rsa:2048",
             "-keyout", key_file, "-out", cert_file, "-days", "3650", "-nodes",
             "-subj", "/CN=QwenPaw-NAS-Gateway"],
            check=True, capture_output=True, timeout=30,
        )
        logger.info("已生成 HTTPS 自签名证书: %s", cert_file)
        return cert_file, key_file
    except Exception as e:
        logger.warning("openssl 生成证书失败，回退内置证书: %s", e)
        try:
            with open(cert_file, "w", encoding="utf-8") as f:
                f.write(FALLBACK_CERT)
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(FALLBACK_KEY)
            return cert_file, key_file
        except Exception as e2:
            logger.error("写入内置证书失败: %s", e2)
            return None, None


class DualProtocolProxyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """单端口 HTTP/HTTPS 自适应反代监听。

    通过 peek 连接首字节区分 TLS ClientHello(0x16) 与明文 HTTP，
    等价于 Go 版用 cmux 做的连接嗅探分流。
    """

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, addr, handler, gateway: GatewayConfig, internal_port: int, data_dir: str):
        self.gateway = gateway
        self.internal_port = internal_port
        self.auth_tracker = AuthTracker()
        self._ssl_ctx = self._build_ssl_ctx(data_dir)
        super().__init__(addr, handler)

    @staticmethod
    def _build_ssl_ctx(data_dir: str):
        cert_file, key_file = ensure_cert(data_dir)
        if not cert_file:
            return None
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert_file, key_file)
            return ctx
        except Exception as e:
            logger.warning("加载 HTTPS 证书失败，反代端口仅支持 HTTP: %s", e)
            return None

    def get_request(self):
        sock, addr = self.socket.accept()
        try:
            sock.settimeout(10)
            first = sock.recv(1, socket.MSG_PEEK)
            if first == b"\x16" and self._ssl_ctx is not None:
                try:
                    ssl_sock = self._ssl_ctx.wrap_socket(sock, server_side=True)
                    ssl_sock.settimeout(None)
                    return ssl_sock, addr
                except Exception as e:
                    logger.debug("TLS 握手失败: %s", e)
                    try:
                        sock.close()
                    except Exception:
                        pass
                    raise ConnectionError("tls handshake failed")
            sock.settimeout(None)
            return sock, addr
        except Exception:
            try:
                sock.close()
            except Exception:
                pass
            raise


LOGIN_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QwenPaw · 访问验证</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f4f6fb;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
color:#1e293b;padding:16px}
.card{background:#fff;border-radius:16px;padding:32px 28px;width:100%;max-width:350px;
border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,.03)}
.logo{width:48px;height:48px;background:#f0f5ff;border-radius:14px;border:1px solid #e0eaff;
display:flex;align-items:center;justify-content:center;margin:0 auto 14px;
font-size:22px;font-weight:800;color:#1669ff}
h1{text-align:center;font-size:17px;font-weight:600;color:#0f172a;margin-bottom:4px}
.sub{text-align:center;font-size:12px;color:#64748b;margin-bottom:20px}
input{width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;
outline:none;background:#f8fafc;color:#0f172a}
input:focus{border-color:#1669ff;background:#fff}
button{width:100%;margin-top:12px;padding:9px 12px;background:#1669ff;color:#fff;border:none;
border-radius:8px;font-size:13px;font-weight:500;cursor:pointer}
button:hover:not(:disabled){background:#3b82f6}
button:disabled{background:#94a3b8;cursor:not-allowed}
.err{margin-top:12px;font-size:12px;color:#ef4444;background:#fef2f2;border:1px solid #fee2e2;
padding:8px 10px;border-radius:8px;display:none;line-height:1.4}
.foot{text-align:center;font-size:11px;color:#94a3b8;margin-top:18px}
</style>
</head>
<body>
<div class="card">
  <div class="logo">Q</div>
  <h1>QwenPaw 访问验证</h1>
  <p class="sub">该入口已启用访问密码保护</p>
  <input id="pwd" type="password" placeholder="请输入访问密码" autocomplete="current-password">
  <div id="err" class="err"></div>
  <button id="btn" type="button">验证并进入</button>
  <p class="foot">QwenPaw 飞牛统一网关</p>
</div>
<script>
(function(){
  var pwd=document.getElementById('pwd'),err=document.getElementById('err'),btn=document.getElementById('btn');
  function submit(){
    if(btn.disabled)return;
    btn.disabled=true;btn.textContent='验证中...';
    fetch('/_qwenpaw_auth',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({password:pwd.value})})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d&&d.code===0){location.href='/';return;}
      err.style.display='block';err.textContent=(d&&d.message)||'密码错误';
      btn.disabled=false;btn.textContent='验证并进入';pwd.select();
    }).catch(function(){
      err.style.display='block';err.textContent='网络错误，请重试';
      btn.disabled=false;btn.textContent='验证并进入';
    });
  }
  btn.addEventListener('click',submit);
  pwd.addEventListener('keydown',function(e){if(e.key==='Enter')submit();});
  pwd.focus();
})();
</script>
</body>
</html>
"""


class ProxyRequestHandler(socketserver.BaseRequestHandler):
    """反代请求处理器：读取请求头 -> 密码鉴权 -> 反代到内部端口"""

    max_line = 65536

    def setup(self):
        self.rfile = self.request.makefile("rb")
        self.wfile = self.request.makefile("wb")
        self._tunneled = False

    def finish(self):
        try:
            if not self._tunneled:
                self.wfile.flush()
            self.rfile.close()
            self.wfile.close()
        except Exception:
            pass
        try:
            self.request.close()
        except Exception:
            pass

    def handle(self):
        try:
            request_line = self.rfile.readline(self.max_line)
            if not request_line:
                return
            parts = request_line.decode("latin-1", "replace").strip().split()
            if len(parts) < 2:
                return
            method, raw_path = parts[0], parts[1]
            headers = {}
            while True:
                line = self.rfile.readline(self.max_line)
                if not line or line in (b"\r\n", b"\n"):
                    break
                k, _, v = line.decode("latin-1", "replace").partition(":")
                headers[k.strip().lower()] = v.strip()

            body = b""
            try:
                clen = int(headers.get("content-length", "0") or "0")
            except (TypeError, ValueError):
                clen = 0
            if clen > 0:
                body = self.rfile.read(clen)

            if not self.handle_auth(method, raw_path, headers, body):
                return
            self.proxy(method, raw_path, headers, body)
        except Exception as e:
            logger.debug("反代请求处理异常: %s", e)

    # ---------------- 密码鉴权 ----------------

    def handle_auth(self, method, path, headers, body) -> bool:
        pwd = self.server.gateway.get("access_password")
        if not pwd:
            return True
        if path == AUTH_LOGIN_PATH or path.startswith(AUTH_LOGIN_PATH + "/"):
            self.serve_login(method, headers, body)
            return False
        if self._is_authed(headers, pwd):
            return True
        accept = headers.get("accept", "")
        if "application/json" in accept:
            self._send_json(401, {"code": 401, "message": "未授权，请先通过访问验证"})
        else:
            self._send_redirect(AUTH_LOGIN_PATH)
        return False

    def _is_authed(self, headers, pwd) -> bool:
        token = auth_token(pwd)
        for part in headers.get("cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == AUTH_COOKIE and (v == token or v == pwd):
                return True
        return False

    def serve_login(self, method, headers, body):
        ip = self.client_address[0]
        tracker = self.server.auth_tracker
        locked, remain, attempts = tracker.check(ip)

        if method == "POST":
            if locked:
                self._send_login_deny("密码错误次数过多，已锁定约 %d 分钟，请稍后再试" % (int(remain // 60) + 1), 429)
                return
            ctype = headers.get("content-type", "")
            input_pwd = ""
            if "json" in ctype:
                try:
                    input_pwd = json.loads(body or b"{}").get("password", "")
                except Exception:
                    input_pwd = ""
            else:
                try:
                    params = urllib.parse.parse_qs((body or b"").decode("utf-8", "replace"))
                    input_pwd = (params.get("password") or [""])[0]
                except Exception:
                    input_pwd = ""
            if input_pwd == self.server.gateway.get("access_password"):
                tracker.success(ip)
                token = auth_token(self.server.gateway.get("access_password"))
                self._send_login_ok(token, headers)
            else:
                locked_now, _, left = tracker.fail(ip)
                if locked_now:
                    self._send_login_deny("密码错误次数过多，已锁定 1 小时，请稍后再试", 429)
                else:
                    self._send_login_deny("密码错误，还可尝试 %d 次" % left, 400)
            return

        self._send_login_page()

    def _send_login_ok(self, token, headers):
        set_cookie = _make_cookie(token)
        accept = headers.get("accept", "")
        if "application/json" in accept:
            # JSON 登录同样下发 Set-Cookie，前端 fetch 后跳转 / 即可自动携带
            self._send_json(
                200,
                {"code": 0, "message": "success", "token": token, "redirect": "/"},
                extra_headers=[("Set-Cookie", set_cookie)],
            )
            return
        body = ("<html><body><script>location.href='/';</script></body></html>").encode("utf-8")
        self._write_raw(
            302,
            [("Location", "/"), ("Set-Cookie", set_cookie), ("Content-Length", str(len(body)))],
            body,
        )

    def _send_login_deny(self, message, status):
        self._send_json(status, {"code": status, "message": message})

    def _send_login_page(self):
        body = LOGIN_PAGE_HTML.encode("utf-8")
        self._write_raw(
            200,
            [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body))), ("Cache-Control", "no-store")],
            body,
        )

    # ---------------- 反代转发 ----------------

    def proxy(self, method, path, headers, body):
        internal_port = self.server.internal_port
        conn = http.client.HTTPConnection("127.0.0.1", internal_port, timeout=60)
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            conn.putheader("Host", "127.0.0.1:%d" % internal_port)
            for k, v in headers.items():
                kl = k.lower()
                if kl in HOP_BY_HOP or kl == "host":
                    continue
                if kl == "origin":
                    conn.putheader("Origin", "http://127.0.0.1:%d" % internal_port)
                    continue
                if kl == "sec-fetch-site":
                    conn.putheader("Sec-Fetch-Site", "same-origin")
                    continue
                if kl == "content-length":
                    continue
                conn.putheader(k, v)
            if body:
                conn.putheader("Content-Length", str(len(body)))
            conn.endheaders(body if body else None)

            resp = conn.getresponse()
            status, reason = resp.status, resp.reason
            rh = resp.getheaders()
            rh_dict = {k.lower(): v for k, v in rh}

            out = ["HTTP/1.1 %d %s" % (status, reason)]
            for k, v in rh:
                kl = k.lower()
                if kl in HOP_BY_HOP or kl == "content-length":
                    continue
                out.append("%s: %s" % (k, v))

            # WebSocket 升级 -> 双向裸转发
            if status == 101:
                out.append("Connection: Upgrade")
                self.wfile.write(("\r\n".join(out) + "\r\n\r\n").encode("latin-1"))
                self.wfile.flush()
                self._tunnel(conn, resp)
                return

            has_cl = "content-length" in rh_dict
            ct = rh_dict.get("content-type", "")
            is_stream = (not has_cl) or ("text/event-stream" in ct)

            if is_stream:
                # SSE / 无长度响应 -> chunked 流式转发
                out.append("Transfer-Encoding: chunked")
                out.append("Connection: close")
                self.wfile.write(("\r\n".join(out) + "\r\n\r\n").encode("latin-1"))
                self.wfile.flush()
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(("%x\r\n" % len(chunk)).encode("ascii") + chunk + b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
            else:
                payload = resp.read()
                out.append("Content-Length: %d" % len(payload))
                out.append("Connection: close")
                self.wfile.write(("\r\n".join(out) + "\r\n\r\n").encode("latin-1") + payload)
                self.wfile.flush()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _tunnel(self, conn, resp):
        """WebSocket 升级后双向透传"""
        self._tunneled = True
        backend = conn.sock

        def pump(src, dst):
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        t1 = threading.Thread(target=pump, args=(self.request, backend), daemon=True)
        t2 = threading.Thread(target=pump, args=(backend, self.request), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    # ---------------- 基础写响应 ----------------

    def _write_raw(self, status, headers, body: bytes):
        lines = ["HTTP/1.1 %d %s" % (status, _HTTP_REASONS.get(status, ""))]
        for k, v in headers:
            lines.append("%s: %s" % (k, v))
        head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
        try:
            self.wfile.write(head + body)
            self.wfile.flush()
        except Exception:
            pass

    def _send_redirect(self, location):
        body = ("<html><body><a href='%s'>继续</a></body></html>" % location).encode("utf-8")
        self._write_raw(
            302,
            [("Location", location), ("Content-Length", str(len(body)))],
            body,
        )

    def _send_json(self, status, data, extra_headers=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ]
        if extra_headers:
            headers.extend(extra_headers)
        self._write_raw(status, headers, body)


_HTTP_REASONS = {
    200: "OK", 302: "Found", 400: "Bad Request", 401: "Unauthorized",
    403: "Forbidden", 404: "Not Found", 429: "Too Many Requests", 500: "Internal Server Error",
}


def _make_cookie(token: str) -> str:
    import datetime as _dt
    exp = _dt.datetime.utcnow() + _dt.timedelta(days=30)
    return (
        "%s=%s; Path=/; Max-Age=2592000; Expires=%s; HttpOnly; SameSite=Lax"
        % (AUTH_COOKIE, token, exp.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    )


def main():
    parser = argparse.ArgumentParser(description="QwenPaw 飞牛控制台网关")
    parser.add_argument("--socket", type=str, required=True, help="Unix Domain Socket 监听路径")
    parser.add_argument("--prefix", type=str, required=True, help="飞牛网关路由前缀")
    parser.add_argument("--www-dir", type=str, default="", help="控制台静态文件目录（默认脚本同级的 www）")
    parser.add_argument("--port", type=str, default="2277", help="QwenPaw WebUI 端口")
    parser.add_argument("--log-file", type=str, default="", help="QwenPaw 运行日志路径")
    parser.add_argument("--gateway-log", type=str, default="", help="网关自身日志路径")
    parser.add_argument("--pid-file", type=str, default="", help="PID 文件路径")
    parser.add_argument("--venv", type=str, default="", help="Python 虚拟环境目录")
    parser.add_argument("--data-dir", type=str, default="", help="HOME 数据目录")
    parser.add_argument("--listen", type=str, default="", help="(兼容旧参数，已弃用)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    www_dir = args.www_dir or os.path.join(script_dir, "www")

    cfg = {
        "port": args.port,
        "log_file": args.log_file,
        "gateway_log": args.gateway_log,
        "pid_file": args.pid_file,
        "venv": args.venv,
        "data_dir": args.data_dir,
    }

    def cleanup():
        if os.path.exists(args.socket):
            try:
                os.unlink(args.socket)
            except Exception:
                pass

    def sig_handler(*_):
        sys.exit(0)

    import atexit
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    server = ThreadingUnixHTTPServer(args.socket, args.prefix, www_dir, cfg)
    server.start_proxy()
    logger.info(f"控制台网关已启动: [{args.socket}] 前缀={args.prefix} 静态目录={www_dir}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop_proxy()
        cleanup()
        logger.info("控制台网关已停止并清理套接字")


if __name__ == "__main__":
    main()

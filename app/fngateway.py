#!/usr/bin/env python3
"""
飞牛网关反向代理中间件
监听 Unix Domain Socket 并代理至目标 TCP 端口，实现子路径路由剥除、请求/响应头重写及前端运行时环境适配。
"""

import os
import re
import sys
import gzip
import socket
import select
import atexit
import signal
import logging
import argparse
import http.client
import socketserver
from http.server import BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("fngateway")

HTML_ATTR_RE = re.compile(r'(?i)\b(src|href|action)\s*=\s*(["\'])(/[^"\']*)')
MAX_HTML_INJECT_SIZE = 10 * 1024 * 1024


def generate_bridge_script(prefix: str) -> str:
    """生成前端运行时拦截与环境适配补丁脚本"""
    return f"""<script>
(function (prefix) {{
  if (typeof window === "undefined" || !window.location) return;
  if (window.location.pathname.indexOf(prefix) !== 0 && window.location.pathname !== prefix) return;

  var isAlreadyPrefixed = function (pathname) {{
    return prefix !== "" && (pathname === prefix || pathname.indexOf(prefix + "/") === 0);
  }};

  var toGatewayUrl = function (value) {{
    if (!value) return null;
    var str = String(value).trim();
    if (str.indexOf("blob:") === 0 || str.indexOf("data:") === 0 || str.indexOf("javascript:") === 0 || str.indexOf("about:") === 0) return null;
    var url;
    try {{ url = new URL(str, window.location.href); }}
    catch (_) {{ return null; }}
    if (url.protocol !== "http:" && url.protocol !== "https:" && url.protocol !== "ws:" && url.protocol !== "wss:") return null;
    if (url.origin !== window.location.origin) return null;
    if (isAlreadyPrefixed(url.pathname)) return null;
    var rawPath = url.pathname.indexOf('/') === 0 ? url.pathname : '/' + url.pathname;
    url.pathname = prefix + rawPath;
    return url;
  }};

  var toGatewaySrcset = function (srcsetStr) {{
    if (!srcsetStr || typeof srcsetStr !== "string") return srcsetStr;
    return srcsetStr.split(",").map(function (part) {{
      var item = part.trim();
      if (!item) return item;
      var segs = item.split(/\\s+/);
      var mapped = toGatewayUrl(segs[0]);
      if (mapped !== null) segs[0] = mapped.toString();
      return segs.join(" ");
    }}).join(", ");
  }};

  var rewriteHtmlString = function (html) {{
    if (typeof html !== "string" || html.indexOf("/") === -1) return html;
    var htmlAttrRe = new RegExp("\\\\b(src|href|action)=([\\"'])(/[^\\"']*)\\\\2", "gi");
    return html.replace(htmlAttrRe, function (match, attr, quote, path) {{
      if (isAlreadyPrefixed(path) || path.indexOf("//") === 0) return match;
      return attr + "=" + quote + prefix + path + quote;
    }});
  }};

  var installBridge = function (targetWindow) {{
    if (!targetWindow || targetWindow.__fnGatewayBridgeReady) return;
    targetWindow.__fnGatewayBridgeReady = true;

    // 拦截 Fetch
    if (targetWindow.fetch) {{
      var nativeFetch = targetWindow.fetch.bind(targetWindow);
      targetWindow.fetch = function (input, init) {{
        if (typeof Request !== "undefined" && input instanceof Request) {{
          var mapped = toGatewayUrl(input.url);
          if (mapped !== null) {{
            try {{ input = new Request(mapped.toString(), input); }} catch (_) {{}}
          }}
        }} else {{
          var mapped = toGatewayUrl(input);
          if (mapped !== null) input = mapped.toString();
        }}
        return nativeFetch(input, init);
      }};
    }}

    // 拦截 XHR
    if (targetWindow.XMLHttpRequest) {{
      var nativeXHROpen = targetWindow.XMLHttpRequest.prototype.open;
      targetWindow.XMLHttpRequest.prototype.open = function (method, url) {{
        var mapped = toGatewayUrl(url);
        if (mapped !== null) arguments[1] = mapped.toString();
        return nativeXHROpen.apply(this, arguments);
      }};
    }}

    // 拦截 DOM 属性
    var hookProperty = function (proto, prop, isSrcset) {{
      if (!proto) return;
      var desc = Object.getOwnPropertyDescriptor(proto, prop);
      if (!desc || !desc.set) return;
      var nativeSet = desc.set;
      Object.defineProperty(proto, prop, {{
        set: function (val) {{
          if (isSrcset) return nativeSet.call(this, toGatewaySrcset(val));
          var mapped = toGatewayUrl(val);
          return nativeSet.call(this, mapped !== null ? mapped.toString() : val);
        }},
        get: desc.get,
        configurable: true,
        enumerable: true
      }});
    }};

    if (targetWindow.HTMLImageElement) {{
      hookProperty(targetWindow.HTMLImageElement.prototype, "src", false);
      hookProperty(targetWindow.HTMLImageElement.prototype, "srcset", true);
    }}
    if (targetWindow.HTMLLinkElement) hookProperty(targetWindow.HTMLLinkElement.prototype, "href", false);
    if (targetWindow.HTMLAnchorElement) hookProperty(targetWindow.HTMLAnchorElement.prototype, "href", false);
    if (targetWindow.HTMLIFrameElement) hookProperty(targetWindow.HTMLIFrameElement.prototype, "src", false);
    if (targetWindow.HTMLScriptElement) hookProperty(targetWindow.HTMLScriptElement.prototype, "src", false);
    if (targetWindow.HTMLFormElement) hookProperty(targetWindow.HTMLFormElement.prototype, "action", false);
    if (targetWindow.HTMLMediaElement) hookProperty(targetWindow.HTMLMediaElement.prototype, "src", false);
    if (targetWindow.HTMLSourceElement) {{
      hookProperty(targetWindow.HTMLSourceElement.prototype, "src", false);
      hookProperty(targetWindow.HTMLSourceElement.prototype, "srcset", true);
    }}

    // 拦截 setAttribute 与 innerHTML
    if (targetWindow.Element) {{
      var nativeSetAttr = targetWindow.Element.prototype.setAttribute;
      targetWindow.Element.prototype.setAttribute = function (name, value) {{
        var n = String(name).toLowerCase();
        if (n === "src" || n === "href" || n === "action") {{
          var mapped = toGatewayUrl(value);
          if (mapped !== null) value = mapped.toString();
        }} else if (n === "srcset") {{
          value = toGatewaySrcset(value);
        }}
        return nativeSetAttr.call(this, name, value);
      }};

      var innerDesc = Object.getOwnPropertyDescriptor(targetWindow.Element.prototype, "innerHTML");
      if (innerDesc && innerDesc.set) {{
        var nativeInnerSet = innerDesc.set;
        Object.defineProperty(targetWindow.Element.prototype, "innerHTML", {{
          set: function (val) {{ return nativeInnerSet.call(this, rewriteHtmlString(val)); }},
          get: innerDesc.get,
          configurable: true,
          enumerable: true
        }});
      }}
    }}

    // 拦截 <a> 点击
    targetWindow.addEventListener("click", function (e) {{
      var target = e.target;
      while (target && target.tagName !== "A") target = target.parentElement;
      if (target && target.tagName === "A") {{
        var href = target.getAttribute("href") || target.href;
        var mapped = toGatewayUrl(href);
        if (mapped !== null) {{
          target.setAttribute("href", mapped.toString());
          if (target.href) target.href = mapped.toString();
        }}
      }}
    }}, true);

    // 拦截 History
    if (targetWindow.history) {{
      var wrapHistory = function (orig) {{
        if (!orig) return orig;
        return function (state, unused, url) {{
          if (url) {{
            var mapped = toGatewayUrl(url);
            if (mapped !== null) url = mapped.toString();
          }}
          return orig.call(this, state, unused, url);
        }};
      }};
      targetWindow.history.pushState = wrapHistory(targetWindow.history.pushState);
      targetWindow.history.replaceState = wrapHistory(targetWindow.history.replaceState);
    }}

    // 拦截 EventSource
    if (targetWindow.EventSource) {{
      var nativeEventSource = targetWindow.EventSource;
      targetWindow.EventSource = new Proxy(nativeEventSource, {{
        construct: function (target, args, newTarget) {{
          var mapped = toGatewayUrl(args[0]);
          if (mapped !== null) args = [mapped.toString()].concat(args.slice(1));
          return Reflect.construct(target, args, newTarget);
        }}
      }});
    }}

    // 拦截 WebSocket
    if (targetWindow.WebSocket) {{
      var nativeWebSocket = targetWindow.WebSocket;
      var page = new URL(targetWindow.location.href);
      var pagePort = page.port || (page.protocol === "https:" ? "443" : "80");
      targetWindow.WebSocket = new Proxy(nativeWebSocket, {{
        construct: function (target, args, newTarget) {{
          var url;
          try {{ url = new URL(String(args[0]), targetWindow.location.href); }}
          catch (_) {{ return Reflect.construct(target, args, newTarget); }}
          var socketPort = url.port || (url.protocol === "wss:" ? "443" : "80");
          if ((url.protocol === "ws:" || url.protocol === "wss:") &&
              url.hostname === page.hostname && socketPort === pagePort &&
              !isAlreadyPrefixed(url.pathname)) {{
            var rawPath = url.pathname.indexOf('/') === 0 ? url.pathname : '/' + url.pathname;
            url.pathname = prefix + rawPath;
            args = [url.toString()].concat(args.slice(1));
          }}
          return Reflect.construct(target, args, newTarget);
        }}
      }});
    }}

    // 拦截 window.open 与 sendBeacon
    if (typeof targetWindow.open === "function") {{
      var nativeOpen = targetWindow.open.bind(targetWindow);
      targetWindow.open = function (url, target, features) {{
        var mapped = toGatewayUrl(url);
        return nativeOpen(mapped !== null ? mapped.toString() : url, target, features);
      }};
    }}
    if (targetWindow.navigator && typeof targetWindow.navigator.sendBeacon === "function") {{
      var nativeBeacon = targetWindow.navigator.sendBeacon.bind(targetWindow.navigator);
      targetWindow.navigator.sendBeacon = function (url, data) {{
        var mapped = toGatewayUrl(url);
        return nativeBeacon(mapped !== null ? mapped.toString() : url, data);
      }};
    }}

    // 拦截 Worker
    if (targetWindow.Worker) {{
      var nativeWorker = targetWindow.Worker;
      targetWindow.Worker = new Proxy(nativeWorker, {{
        construct: function (target, args, newTarget) {{
          var mapped = toGatewayUrl(args[0]);
          if (mapped !== null) args = [mapped.toString()].concat(args.slice(1));
          return Reflect.construct(target, args, newTarget);
        }}
      }});
    }}
    if (targetWindow.SharedWorker) {{
      var nativeSharedWorker = targetWindow.SharedWorker;
      targetWindow.SharedWorker = new Proxy(nativeSharedWorker, {{
        construct: function (target, args, newTarget) {{
          var mapped = toGatewayUrl(args[0]);
          if (mapped !== null) args = [mapped.toString()].concat(args.slice(1));
          return Reflect.construct(target, args, newTarget);
        }}
      }});
    }}

    // 注入同源 iframe
    var injectIframe = function (el) {{
      try {{
        if (!el || el.__fnHooked) return;
        el.__fnHooked = true;
        var hookWin = function () {{
          try {{
            var win = el.contentWindow;
            if (win && win !== targetWindow) installBridge(win);
          }} catch (_) {{}}
        }};
        el.addEventListener("load", hookWin);
        hookWin();
      }} catch (_) {{}}
    }};

    if (targetWindow.MutationObserver) {{
      var observer = new MutationObserver(function (mutations) {{
        for (var i = 0; i < mutations.length; i++) {{
          var nodes = mutations[i].addedNodes;
          for (var j = 0; j < nodes.length; j++) {{
            if (nodes[j].tagName === "IFRAME") injectIframe(nodes[j]);
          }}
        }}
      }});
      if (targetWindow.document && targetWindow.document.documentElement) {{
        observer.observe(targetWindow.document.documentElement, {{ childList: true, subtree: true }});
      }}
    }}
  }};

  installBridge(window);
}})("{prefix}");
</script>"""


def strip_prefix(path: str, prefix: str) -> str:
    """剥除网关前缀"""
    if prefix and (path == prefix or path.startswith(prefix + "/")):
        path = path[len(prefix):]
        if not path.startswith("/"):
            path = "/" + path
    return path or "/"


class FnGatewayHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    STATIC_EXTS = (".js", ".css", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".webp", ".map")

    def log_message(self, format, *args):
        """输出访问日志"""
        code = str(args[0]) if args else ""
        if code.startswith(("2", "3")) and self.path.endswith(self.STATIC_EXTS):
            return
        logger.info(f"{self.command} {self.path} - {format % args}")

    def do_HEAD(self): self.handle_proxy()
    def do_GET(self): self.handle_proxy()
    def do_POST(self): self.handle_proxy()
    def do_PUT(self): self.handle_proxy()
    def do_DELETE(self): self.handle_proxy()
    def do_PATCH(self): self.handle_proxy()
    def do_OPTIONS(self): self.handle_proxy()

    def _send_direct(self, status: int, reason: str, headers: list[tuple[str, str]], body: bytes = b""):
        """构建并发送响应数据"""
        resp_lines = [f"HTTP/1.1 {status} {reason}"]
        for k, v in headers:
            resp_lines.append(f"{k}: {v}")
        if body is not None:
            resp_lines.append(f"Content-Length: {len(body)}")
        resp_lines.append("Connection: close")
        resp_lines.append("\r\n")

        head_data = "\r\n".join(resp_lines).encode("latin1")
        try:
            self.connection.sendall(head_data + (body or b""))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_proxy(self):
        """HTTP 反向代理处理"""
        prefix = self.server.prefix
        target_host = self.server.target_host
        target_port = self.server.target_port

        if self.headers.get("Upgrade", "").lower() == "websocket":
            self.handle_websocket_tunnel()
            return

        req_path = strip_prefix(self.path, prefix)

        # 读取请求体
        content_len = int(self.headers.get("Content-Length", 0))
        is_chunked_req = self.headers.get("Transfer-Encoding", "").lower() == "chunked"
        body = self.rfile.read(content_len) if content_len > 0 else (self.rfile if is_chunked_req else None)

        # 构建转发请求头
        headers = {}
        for k, v in self.headers.items():
            if k.lower() not in ("host", "origin", "sec-fetch-site", "connection"):
                headers[k] = v

        headers["Host"] = f"{target_host}:{target_port}"
        headers["Origin"] = f"http://{target_host}:{target_port}"
        headers["Sec-Fetch-Site"] = "same-origin"
        headers["Connection"] = "close"

        try:
            conn = http.client.HTTPConnection(target_host, target_port, timeout=30)
            conn.connect()
            if conn.sock:
                conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            conn.request(self.command, req_path, body=body, headers=headers)
            resp = conn.getresponse()

            content_type = ""
            content_encoding = ""
            content_length = -1
            out_headers = []

            for k, v in resp.getheaders():
                k_lower = k.lower()
                if k_lower == "content-type":
                    content_type = v.lower()
                elif k_lower == "content-encoding":
                    content_encoding = v.lower()
                elif k_lower == "content-length":
                    try:
                        content_length = int(v)
                    except ValueError:
                        pass
                elif k_lower == "location":
                    if v.startswith("/") and not v.startswith("//") and not (prefix and (v == prefix or v.startswith(prefix + "/"))):
                        v = prefix + v
                elif k_lower == "set-cookie":
                    if "path=/;" in v.lower() or v.lower().endswith("path=/"):
                        v = re.sub(r'(?i)path=/;', f'Path={prefix}/;', v)
                        if v.lower().endswith("path=/"):
                            v = v[:-7] + f"Path={prefix}/"

                if k_lower not in ("content-length", "transfer-encoding", "connection"):
                    out_headers.append((k, v))

            # 1. SSE 流式直通
            if "text/event-stream" in content_type:
                self.send_response_only(resp.status, resp.reason)
                for k, v in out_headers:
                    self.send_header(k, v)
                self.send_header("Cache-Control", "no-cache, no-transform")
                self.send_header("X-Accel-Buffering", "no")
                self.send_header("Connection", "close")
                self.end_headers()
                while True:
                    chunk = resp.read(1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
                self.close_connection = True
                conn.close()
                return

            # 2. HTML 注入改写
            is_html = "text/html" in content_type and (0 <= content_length <= MAX_HTML_INJECT_SIZE or content_length == -1)
            if is_html:
                resp_body = resp.read()
                if "gzip" in content_encoding:
                    try:
                        resp_body = gzip.decompress(resp_body)
                    except Exception:
                        pass

                html_text = resp_body.decode("utf-8", errors="ignore")

                def replace_attr(m):
                    attr, quote, p = m.group(1), m.group(2), m.group(3)
                    return m.group(0) if (p.startswith("//") or (prefix and p.startswith(prefix))) else f"{attr}={quote}{prefix}{p}"

                modified_html = HTML_ATTR_RE.sub(replace_attr, html_text)
                bridge_code = self.server.bridge_code

                head_match = re.search(r"(?i)<head[^>]*>", modified_html)
                if head_match:
                    idx = head_match.end()
                    modified_html = modified_html[:idx] + bridge_code + modified_html[idx:]
                else:
                    modified_html = bridge_code + modified_html

                final_bytes = modified_html.encode("utf-8")
                filtered_headers = [(k, v) for k, v in out_headers if k.lower() not in ("content-encoding", "content-security-policy", "content-security-policy-report-only")]
                self._send_direct(resp.status, resp.reason, filtered_headers, final_bytes)
                self.close_connection = True
                conn.close()
                return

            # 3. 大文件分块转发
            if content_length > 10 * 1024 * 1024:
                resp_lines = [f"HTTP/1.1 {resp.status} {resp.reason}"]
                for k, v in out_headers:
                    resp_lines.append(f"{k}: {v}")
                if content_length >= 0:
                    resp_lines.append(f"Content-Length: {content_length}")
                resp_lines.append("Connection: close\r\n\r\n")

                try:
                    self.connection.sendall("\r\n".join(resp_lines).encode("latin1"))
                    while True:
                        chunk = resp.read(262144)
                        if not chunk:
                            break
                        self.connection.sendall(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                self.close_connection = True
                conn.close()
                return

            # 4. 静态与通用响应转发
            resp_body = resp.read()
            is_gzip_js = "gzip" in content_encoding and req_path.endswith(".js")
            if is_gzip_js:
                try:
                    resp_body = gzip.decompress(resp_body)
                    content_encoding = ""
                except Exception:
                    pass

            if self.server.patch_func and req_path.endswith(".js"):
                if self.server.target_func in resp_body:
                    resp_body = resp_body.replace(self.server.target_func, self.server.patch_func)

            filtered_headers = [(k, v) for k, v in out_headers if not (is_gzip_js and k.lower() == "content-encoding")]
            self._send_direct(resp.status, resp.reason, filtered_headers, resp_body)

            self.close_connection = True
            conn.close()

        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        except Exception as e:
            logger.error(f"代理请求失败 [{self.command} {self.path}]: {e}")
            try:
                self.send_error(http.client.BAD_GATEWAY, f"Bad Gateway: {str(e)}")
            except Exception:
                pass
            self.close_connection = True

    def handle_websocket_tunnel(self):
        """WebSocket 全双工隧道"""
        prefix = self.server.prefix
        target_host = self.server.target_host
        target_port = self.server.target_port

        req_path = strip_prefix(self.path, prefix)

        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_sock.connect((target_host, target_port))

        handshake = [f"{self.command} {req_path} HTTP/1.1"]
        for k, v in self.headers.items():
            k_lower = k.lower()
            if k_lower == "host":
                handshake.append(f"Host: {target_host}:{target_port}")
            elif k_lower == "origin":
                handshake.append(f"Origin: http://{target_host}:{target_port}")
            else:
                handshake.append(f"{k}: {v}")
        handshake.append("\r\n")
        target_sock.sendall("\r\n".join(handshake).encode("utf-8"))

        client_sock = self.connection
        sockets = [client_sock, target_sock]
        logger.info(f"WebSocket 隧道建立: {req_path}")
        try:
            while True:
                r_list, _, x_list = select.select(sockets, [], sockets, 60)
                if x_list:
                    break
                for s in r_list:
                    data = s.recv(65536)
                    if not data:
                        return
                    if s is client_sock:
                        target_sock.sendall(data)
                    else:
                        client_sock.sendall(data)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.close_connection = True
            target_sock.close()
            logger.info(f"WebSocket 隧道关闭: {req_path}")


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
    def __init__(self, socket_path: str, target_host: str, target_port: int, prefix: str):
        self.socket_path = socket_path
        self.target_host = target_host
        self.target_port = target_port
        self.prefix = prefix.rstrip("/")
        self.bridge_code = generate_bridge_script(self.prefix)
        self.target_func = b"function n6(i){return/^\\/console(?:\\/|$)/.test(i)?c8e:void 0}"
        self.patch_func = f'function n6(i){{const p="{self.prefix}";const s=i.startsWith(p)?i.slice(p.length)||"/":i;return/^\\/console(?:\\/|$)/.test(s)?(i.startsWith(p)?p+c8e:c8e):(i.startsWith(p)?p:void 0)}}'.encode("utf-8") if self.prefix else None

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


def parse_listen_address(addr: str) -> tuple[str, int]:
    """解析监听地址为 host 与 port"""
    clean_addr = addr.replace("http://", "").replace("https://", "").strip().rstrip("/")
    if ":" in clean_addr:
        parts = clean_addr.split(":")
        host = parts[0] if parts[0] else "127.0.0.1"
        port = int(parts[1])
        return host, port
    return "127.0.0.1", int(clean_addr)


def main():
    parser = argparse.ArgumentParser(description="飞牛网关反向代理中间件")
    parser.add_argument("--listen", type=str, required=True, help="目标后端地址 (格式: 127.0.0.1:2298 或 2298)")
    parser.add_argument("--socket", type=str, required=True, help="Unix Domain Socket 监听路径")
    parser.add_argument("--prefix", type=str, required=True, help="飞牛网关反向代理路由前缀")
    args = parser.parse_args()

    target_host, target_port = parse_listen_address(args.listen)

    def cleanup():
        if os.path.exists(args.socket):
            try:
                os.unlink(args.socket)
            except Exception:
                pass

    def sig_handler(*_):
        sys.exit(0)

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    server = ThreadingUnixHTTPServer(args.socket, target_host, target_port, args.prefix)
    logger.info(f"服务已启动: Unix套接字 [{args.socket}] -> 目标后端 [{target_host}:{target_port}] (路由前缀: {args.prefix})")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        logger.info("服务已停止并清理套接字")


if __name__ == "__main__":
    main()

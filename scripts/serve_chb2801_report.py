#!/usr/bin/env python3
"""本機下載伺服器：提供 2801 彰銀五年報告 PDF。

🎯 在本機開一個只讀 HTTP 埠，讓瀏覽器按按鈕下載 PDF（零外部 API）。
守 #5（只服務指定檔）· #18。

執行指令矩陣：
  python3 scripts/serve_chb2801_report.py                 # 先建 PDF，再聽 127.0.0.1:8765
  python3 scripts/serve_chb2801_report.py --port 8765     # 指定埠
  python3 scripts/serve_chb2801_report.py --bind 0.0.0.0  # 對容器／雲端開放
  python3 scripts/serve_chb2801_report.py --build-only    # 只產檔、不開伺服器
  python3 scripts/serve_chb2801_report.py --selftest      # 產檔＋用 http.server 單次 GET 驗下載頭
"""
from __future__ import annotations

import argparse
import http.server
import sys
import threading
from pathlib import Path
from urllib.parse import unquote

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from build_chb2801_report_pdf import (  # noqa: E402
    DEFAULT_OUT,
    HTML_NAME,
    PDF_NAME,
    write_html,
    write_pdf,
)

MIME_PDF = "application/pdf"
MIME_HTML = "text/html; charset=utf-8"


class Handler(http.server.BaseHTTPRequestHandler):
    out_dir: Path

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = unquote(self.path.split("?", 1)[0])
        if path in ("/", "/index.html", "/download"):
            html = (self.out_dir / HTML_NAME).read_bytes()
            return self._send(200, html, MIME_HTML)
        if path in (f"/{PDF_NAME}", "/report.pdf", "/download.pdf"):
            data = (self.out_dir / PDF_NAME).read_bytes()
            return self._send(
                200,
                data,
                MIME_PDF,
                extra={
                    "Content-Disposition": f'attachment; filename="{PDF_NAME}"',
                },
            )
        return self._send(404, b"not found\n", "text/plain; charset=utf-8")

    def do_HEAD(self):  # noqa: N802
        path = unquote(self.path.split("?", 1)[0])
        if path in ("/", "/index.html", "/download"):
            n = (self.out_dir / HTML_NAME).stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", MIME_HTML)
            self.send_header("Content-Length", str(n))
            self.end_headers()
            return
        if path in (f"/{PDF_NAME}", "/report.pdf", "/download.pdf"):
            n = (self.out_dir / PDF_NAME).stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", MIME_PDF)
            self.send_header("Content-Length", str(n))
            self.send_header("Content-Disposition", f'attachment; filename="{PDF_NAME}"')
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()


def ensure_built(out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    pdf = write_pdf(out / PDF_NAME)
    write_html(out / HTML_NAME, PDF_NAME)
    return pdf


def selftest() -> int:
    import tempfile
    from http.client import HTTPConnection

    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        ensure_built(out)
        Handler.out_dir = out
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("GET", "/report.pdf")
            resp = conn.getresponse()
            body = resp.read()
            assert resp.status == 200, resp.status
            assert resp.getheader("Content-Type") == MIME_PDF
            disp = resp.getheader("Content-Disposition") or ""
            assert "attachment" in disp and PDF_NAME in disp, disp
            assert body.startswith(b"%PDF-"), body[:16]
            conn.request("HEAD", "/report.pdf")
            head = conn.getresponse()
            head.read()
            assert head.status == 200
            assert head.getheader("Content-Type") == MIME_PDF
            conn.request("GET", "/")
            resp2 = conn.getresponse()
            html = resp2.read().decode("utf-8")
            assert resp2.status == 200 and "下載 PDF" in html
            conn.request("GET", "/no-such")
            resp3 = conn.getresponse()
            resp3.read()
            assert resp3.status == 404
        finally:
            httpd.shutdown()
            httpd.server_close()
    print("selftest PASS  GET /report.pdf → 200 attachment PDF")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="2801 報告本機下載伺服器")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--build-only", action="store_true")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    out = Path(args.out)
    pdf = ensure_built(out)
    print(f"PDF 已寫入 {pdf}  ({pdf.stat().st_size} bytes)")
    print(f"HTML {out / HTML_NAME}")
    if args.build_only:
        return 0
    Handler.out_dir = out
    httpd = http.server.ThreadingHTTPServer((args.bind, args.port), Handler)
    print(f"下載頁  http://{args.bind}:{args.port}/")
    print(f"PDF     http://{args.bind}:{args.port}/report.pdf  （Content-Disposition: attachment）")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

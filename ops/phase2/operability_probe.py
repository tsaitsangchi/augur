#!/usr/bin/env python3
"""Phase 2 可運作探測（Operability Probe）—— 純 stdlib、唯讀、探測而非自陳。

性質：[I] 資訊性證據工具，不創設義務。對照 LAYER-SEALING-SCHEDULE.md 第二階段
「可運作探測」工項：PG / ollama(11434) / qdrant(6333) / GPU-VRAM / augur 應用碼在否。

紀律（承本專案「不採信自陳、對抗審查方為關卡」）：
  * 每項皆實地連線/查詢取證，不讀設定檔的宣稱值。
  * 失敗即據實記 ABSENT/PARTIAL，不美化、不靜默。
  * 唯讀：不寫入任何服務、不改任何檔（只讀 /proc、只對服務發唯讀請求）。

用法：
  python3 ops/phase2/operability_probe.py
  AUGUR_CODE=/path/to/augur-code python3 ops/phase2/operability_probe.py   # 指定應用碼位置

輸出：人可讀證據表；退出碼恆 0（探測工具不因「服務不在」而視為自身失敗）。
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import urllib.error
import urllib.request

HOST = "127.0.0.1"


def _http_json(url: str, timeout: float = 3.0):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode(errors="replace"))


def probe_ollama() -> tuple[str, str]:
    try:
        tags = _http_json(f"http://{HOST}:11434/api/tags")
    except (urllib.error.URLError, OSError, ValueError) as e:
        return "ABSENT", f"11434 無回應：{e}"
    models = [m.get("name", "?") for m in (tags.get("models") or [])]
    loaded = ""
    try:
        ps = _http_json(f"http://{HOST}:11434/api/ps")
        loaded = ", ".join(m.get("name", "?") for m in (ps.get("models") or [])) or "（無常駐載入）"
    except Exception:
        loaded = "（/api/ps 無法取得）"
    return "UP", f"模型 {len(models)} 個：{', '.join(models) or '無'}｜已載入：{loaded}"


def probe_qdrant() -> tuple[str, str]:
    try:
        root = _http_json(f"http://{HOST}:6333/")
    except (urllib.error.URLError, OSError, ValueError) as e:
        return "ABSENT", f"6333 無回應：{e}"
    ver = root.get("version", "?") if isinstance(root, dict) else "?"
    ncol = "?"
    try:
        cols = _http_json(f"http://{HOST}:6333/collections")
        result = cols.get("result", {}) if isinstance(cols, dict) else {}
        ncol = len(result.get("collections", []))
    except Exception:
        pass
    return "UP", f"qdrant version={ver}｜collections={ncol}"


def probe_pg(port: int) -> tuple[str, str]:
    """以 PG 前導協定（SSLRequest）證實對端確為 PostgreSQL，非僅埠開。"""
    try:
        s = socket.create_connection((HOST, port), timeout=2)
    except OSError as e:
        return "ABSENT", f"{port} 連線失敗：{e}"
    try:
        s.sendall(struct.pack("!ii", 8, 80877103))  # len=8, SSLRequest code
        resp = s.recv(1)
    except OSError as e:
        s.close()
        return "PARTIAL", f"{port} 埠開但握手失敗：{e}"
    s.close()
    if resp in (b"S", b"N"):
        return "UP", f"{port} 確為 PostgreSQL（SSLRequest 回 {resp.decode()!r}）"
    return "PARTIAL", f"{port} 埠開但非 PG 協定（回 {resp!r}）"


def probe_gpu() -> tuple[str, str]:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return "ABSENT", "PATH 無 nvidia-smi"
    try:
        out = subprocess.run(
            [exe, "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return "PARTIAL", f"nvidia-smi 執行失敗：{e}"
    line = (out.stdout or "").strip().splitlines()
    if not line:
        return "PARTIAL", f"nvidia-smi 無輸出（stderr：{(out.stderr or '').strip()[:120]}）"
    return "UP", "；".join(line)


def probe_mem_disk() -> tuple[str, str]:
    total_kb = None
    try:
        with open("/proc/meminfo") as f:
            for ln in f:
                if ln.startswith("MemTotal:"):
                    total_kb = int(ln.split()[1])
                    break
    except OSError:
        pass
    mem = f"{total_kb/1024/1024:.0f} GiB" if total_kb else "?"
    try:
        du = shutil.disk_usage("/")
        disk = f"/ 總 {du.total/1e9:.0f} GB、可用 {du.free/1e9:.0f} GB"
    except OSError:
        disk = "?"
    return "INFO", f"MemTotal={mem}｜{disk}"


def probe_augur_code() -> tuple[str, str]:
    candidates = []
    envp = os.getenv("AUGUR_CODE")
    if envp:
        candidates.append(envp)
    candidates += [
        "/home/giga/augur-code-work",
        "/home/giga/augur-archive/augur-code-latest",
        "/home/giga/augur/augur-code",
        os.path.expanduser("~/project/augur"),
        "/home/hugo/project/augur",
    ]
    _MARKERS = ("src", "scripts", "core", "advisor", "venv", ".env",
                "requirements.txt", "pyproject.toml", ".git")
    found = []
    for p in candidates:
        if p and os.path.isdir(p):
            markers = [m for m in _MARKERS if os.path.exists(os.path.join(p, m))]
            found.append(f"{p}（標記：{', '.join(markers) or '目錄存在但無常見標記'}）")
    if not found:
        return "ABSENT", "候選路徑皆不存在：" + ", ".join(c for c in candidates if c)
    return "FOUND", " ｜ ".join(found)


def main() -> int:
    print("=" * 72)
    print("Augur Phase 2 可運作探測 [I]（探測而非自陳；唯讀）")
    print(f"hostname={socket.gethostname()}｜python={sys.version.split()[0]}")
    print("=" * 72)

    checks = [
        ("ollama (11434)", probe_ollama),
        ("qdrant (6333)", probe_qdrant),
        ("PostgreSQL (5432 標準)", lambda: probe_pg(5432)),
        ("PostgreSQL (55432 userspace)", lambda: probe_pg(55432)),
        ("GPU / VRAM", probe_gpu),
        ("記憶體 / 磁碟", probe_mem_disk),
        ("augur 應用碼", probe_augur_code),
    ]

    rows = []
    for name, fn in checks:
        try:
            status, detail = fn()
        except Exception as e:  # 探測工具本身不得因單項異常而崩
            status, detail = "ERROR", f"探測例外：{e!r}"
        rows.append((name, status, detail))
        print(f"[{status:^7}] {name}\n          {detail}")

    print("-" * 72)
    up = sum(1 for _, s, _ in rows if s in ("UP", "FOUND"))
    print(f"小結：{up}/{len(rows)} 項就緒。ABSENT/PARTIAL 即為 Phase 2 待補之縫。")
    print("注意：entity_registry(3,491)/advisor/審議引擎一輪 等『應用層』探測，"
          "須有 augur 應用碼＋DB 驅動方能實跑；本腳本先確立服務/硬體/碼在否之現實。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

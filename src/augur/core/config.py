"""augur 設定中樞 — 路徑、DB 連線參數、API 密鑰的單一來源。

🎯 這支在做什麼（白話）：
- 從專案根目錄的 `.env` 讀進所有設定（DB 連線、FinMind/FRED 密鑰、運維選項）。
- `.env` 是 machine-local、被 gitignore、**永不進 git**；密鑰只活在這裡，其他模組一律
  `from augur.core import config` 取用，不各自去讀 `.env`。
- `PROJECT_ROOT` 由本檔實體位置推得（不做舊專案那種 anchor 自癒/比對）。
- 用 python-dotenv 載入，能正確忽略行尾 `# 註解`。

守 #12（單一引用源/SSOT：設定·密鑰集中於此，他模組不各自讀 .env）；密鑰只從 `.env`、不入 git（§一.5）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.core.config              # 印用途+公開入口（唯讀）
  python -m augur.core.config --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 本檔：<root>/src/augur/core/config.py → parents[3] = <root>
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

# ---- 路徑（machine-local 產出，不進 git）----
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOG_DIR = DATA_DIR / "logs"


def ensure_dirs() -> None:
    """建立本機產出目錄（data / models / reports / logs），存在則略過。"""
    for d in (DATA_DIR, MODELS_DIR, REPORTS_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ---- DB 連線參數：psycopg2.connect(**DB_PARAMS) ----
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "augur"),
    "user": os.getenv("DB_USER", "augur"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# ---- API 密鑰 ----
FINMIND_TOKEN = os.getenv("FINMIND_TOKEN", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# ---- 運維選項 ----
ENV = os.getenv("ENV", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TZ = os.getenv("TZ", "Asia/Taipei")


def _selftest():
    """自測（零 IO：只驗路徑派生不變式 + DB_PARAMS 結構 + 型別；不觸 fs/DB/API #29a）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("PROJECT_ROOT 為 Path", isinstance(PROJECT_ROOT, Path))
    # 路徑派生不變式：data/models/reports 皆掛 root、logs 掛 data（screaming 巢狀，純 Path 運算零 fs）
    chk("DATA/MODELS/REPORTS 皆 PROJECT_ROOT 直屬",
        DATA_DIR.parent == PROJECT_ROOT and MODELS_DIR.parent == PROJECT_ROOT
        and REPORTS_DIR.parent == PROJECT_ROOT)
    chk("LOG_DIR = DATA_DIR/logs", LOG_DIR == DATA_DIR / "logs" and LOG_DIR.parent == DATA_DIR)
    # DB_PARAMS：psycopg2.connect(**DB_PARAMS) 之必備鍵齊全、port 解析為 int
    chk("DB_PARAMS 五鍵齊全",
        set(DB_PARAMS) == {"host", "port", "dbname", "user", "password"})
    chk("DB_PARAMS.port 為 int", isinstance(DB_PARAMS["port"], int))
    chk("密鑰/運維選項為 str", all(isinstance(x, str)
        for x in (FINMIND_TOKEN, FRED_API_KEY, ENV, LOG_LEVEL, TZ)))
    chk("ensure_dirs 為可呼叫", callable(ensure_dirs))   # 結構斷言：不實呼叫（會 mkdir=IO）
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.core.config --selftest;免 DB 免 API)")

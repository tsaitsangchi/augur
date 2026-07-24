"""augur DB 存取層 — PostgreSQL 連線與交易邊界的單一入口。

🎯 這支在做什麼（白話）：
- 用 `config.DB_PARAMS`（app）或 `config.DB_PARAMS_PREDICT`（受限 predict role）連上 PostgreSQL。
- 提供乾淨的 context manager，讓其他模組不必各自管 commit/rollback/關連線：
  - `connect(params=None)`：預設 app `DB_PARAMS`；可傳入自訂 params；離開區塊自動關。
  - `connect_predict()`：顯式走 `augur_predict`（G-ISO-2 runtime 接線）；advisor／migrate 勿用。
  - `transaction(conn)`：在該連線上開一段交易——區塊正常結束就 `commit`、丟例外就 `rollback`
    （交易邊界乾淨 → 任一批失敗只回滾該批，重跑安全，扣 #6）。
  - `ping()`／`ping_predict()`：連得上且 `SELECT 1` 成功 → True（健康檢查；predict 缺密碼／role 未建 → False）。
- 典型用法：`with connect() as conn:`；預測寫入：`with connect_predict() as conn:`。

邊界：只管連線/交易；**不建表**（infra 表由 schema.py、API 原始表由 generic_schema 各自負責）、
**不抓 API、不算特徵、不選股**。

守 #6（冪等+斷點：交易 commit-or-rollback，重跑安全）· #8（predict role 動態隔離閘）· 核心橫切基礎（DB 連線/交易單一入口）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.core.db              # 印用途+公開入口（唯讀）
  python -m augur.core.db --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Mapping, Optional

import psycopg2

from augur.core import config


@contextmanager
def connect(params: Optional[Mapping[str, Any]] = None):
    """開一個 DB 連線；params 缺省＝`config.DB_PARAMS`（app）。離開區塊自動關閉（不自動 commit）。"""
    conn = psycopg2.connect(connect_timeout=10, **dict(params or config.DB_PARAMS))
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def connect_predict():
    """顯式以 `augur_predict` 連線（`config.DB_PARAMS_PREDICT`）。預測寫入路徑用；advisor／knowledge 勿用。"""
    with connect(config.DB_PARAMS_PREDICT) as conn:
        yield conn


@contextmanager
def transaction(conn):
    """在 conn 上開一段交易：正常結束 commit、例外 rollback（不關連線，連線由呼叫端持有）。"""
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def ping() -> bool:
    """連線健康檢查（app role）：連得上且 SELECT 1 → True；任何錯誤 → False。"""
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
    except Exception:
        return False


def ping_predict() -> bool:
    """predict role 健康檢查：連得上且 SELECT 1 → True；缺密碼／role 未建／拒連 → False。"""
    try:
        with connect_predict() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
    except Exception:
        return False


def _selftest():
    # 本檔全 IO-bound（connect/transaction/ping 皆需 DB 連線）→ 只做 import-smoke + 結構斷言，零 IO。
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    import inspect
    chk("connect 可呼叫", callable(connect))
    chk("connect_predict 可呼叫", callable(connect_predict))
    chk("transaction 可呼叫", callable(transaction))
    chk("ping 可呼叫", callable(ping))
    chk("ping_predict 可呼叫", callable(ping_predict))
    # connect/transaction 皆 @contextmanager → wrap 後仍是 function、原函式為 generator
    chk("connect 是 contextmanager 工廠", inspect.isgeneratorfunction(connect.__wrapped__))
    chk("connect_predict 是 contextmanager 工廠",
        inspect.isgeneratorfunction(connect_predict.__wrapped__))
    chk("transaction 是 contextmanager 工廠", inspect.isgeneratorfunction(transaction.__wrapped__))
    chk("transaction 收 conn 參數", list(inspect.signature(transaction.__wrapped__).parameters) == ["conn"])
    chk("connect 可選 params", "params" in inspect.signature(connect.__wrapped__).parameters)
    chk("ping 標註回傳 bool", inspect.signature(ping).return_annotation in (bool, "bool"))  # future annotations→str
    chk("ping_predict 標註回傳 bool",
        inspect.signature(ping_predict).return_annotation in (bool, "bool"))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.core.db --selftest;免 DB 免 API)")

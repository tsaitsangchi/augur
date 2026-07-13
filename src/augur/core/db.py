"""augur DB 存取層 — PostgreSQL 連線與交易邊界的單一入口。

🎯 這支在做什麼（白話）：
- 用 `config.DB_PARAMS` 連上 augur 的 PostgreSQL。
- 提供乾淨的 context manager，讓其他模組不必各自管 commit/rollback/關連線：
  - `connect()`：拿一個連線，離開區塊自動關。
  - `transaction(conn)`：在該連線上開一段交易——區塊正常結束就 `commit`、丟例外就 `rollback`
    （交易邊界乾淨 → 任一批失敗只回滾該批，重跑安全，扣 #6）。
  - `ping()`：連得上且 `SELECT 1` 成功 → True（PHASE 0 環境/連線健康檢查）。
- 典型用法：`with connect() as conn:`，再對每個 (dataset/批次) `with transaction(conn) as cur:` 寫入。

邊界：只管連線/交易；**不建表**（infra 表由 schema.py、API 原始表由 generic_schema 各自負責）、
**不抓 API、不算特徵、不選股**。

守 #6（冪等+斷點：交易 commit-or-rollback，重跑安全）· 核心橫切基礎（DB 連線/交易單一入口）。
"""
from __future__ import annotations

from contextlib import contextmanager

import psycopg2

from augur.core import config


@contextmanager
def connect():
    """開一個 augur DB 連線；離開區塊自動關閉（不自動 commit——交易由 transaction() 管）。"""
    conn = psycopg2.connect(connect_timeout=10, **config.DB_PARAMS)
    try:
        yield conn
    finally:
        conn.close()


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
    """連線健康檢查：連得上且 SELECT 1 → True；任何錯誤 → False。"""
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
    except Exception:
        return False

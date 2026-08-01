#!/usr/bin/env python3
"""🎯 從 mc_simulation_run 史料反推各模擬法之 param_schema 草案——解 impl plan U-2（20 法規格空懸）。

守原則 #9/#10（x-observed／x-provenance 全由 DB aggregate 現查、可溯源）、#15（summary 鍵只列
x-unclassified 不代判語意——輸出欄之分類屬人審，腳本禁自動入 properties）、#29a/d。

推導規則（H2 呈案 §3.1 拍板；SSOT＝reports/w2_20260801/H2_sim_first_method.md）：
- **參數欄白名單**＝horizon_td／n_paths／seed／block_len_td（run_id=PK、target_id/asof_date=資料座標、
  method=法名、summary=輸出、is_simulation=誠實旗標、git_sha/created_at=provenance——皆非參數）。
- 全列非 NULL 之欄入 required；全列 NULL 之欄不入 properties、列 x-excluded；部分 NULL＝入
  properties 不入 required。`additionalProperties: false`。
- summary 鍵形逐法全列（鍵集合＋列數）入 x-unclassified，一鍵不漏、一鍵不分類。
- 產出＝**草案**（title 明標「未經人審不生效」）；x-scope-warning 明標：入冊僅解 B-1 物理死鎖，
  sim 軸合法評估仍待 D-2 另案（prereg gate axis='sim'），不得據此宣稱 sim 可開跑。
- 確定性：同 HEAD 同資料連跑兩次 byte-identical（x-provenance 時點＝資料側 max(created_at)，
  非 wall-clock；查詢 wall-clock 只印 stderr）。

執行指令矩陣
------------
    python scripts/derive_sim_param_schema.py                      # 無參數：現況摘要（20 法×列數×鍵形數，唯讀）
    python scripts/derive_sim_param_schema.py --method iid_bootstrap   # 單法 param_schema 草案 JSON → stdout
    python scripts/derive_sim_param_schema.py --all                # 全法草案（JSON object，method 為鍵）
    python scripts/derive_sim_param_schema.py --all --out <dir>    # 寫檔 <dir>/<method>.param_schema.draft.json（僅明示路徑才寫）
    python scripts/derive_sim_param_schema.py --selftest           # 零 DB 紅綠自測（三絆線）
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import _bootstrap  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]

# 呈案 §3.1 白名單（語意分類=拍板判準，屬邏輯非策展資料；#29b 豁免理由記於 docstring）
PARAM_COLS = ("horizon_td", "n_paths", "seed", "block_len_td")

_JSON_TYPE = {
    "integer": "integer", "bigint": "integer", "smallint": "integer",
    "double precision": "number", "numeric": "number", "real": "number",
    "boolean": "boolean",
}

SCOPE_WARNING = ("入冊僅解 B-1 物理死鎖；sim 軸合法評估仍待 D-2 另案"
                 "（evolution_prereg_gate axis='sim'）——不得據此宣稱 sim 可開跑")


def observed_param_profile(cur, method: str, git_sha: str) -> dict:
    """DB aggregate 現查單法之參數欄觀測值（#9/#10；唯讀）。"""
    cur.execute("SELECT count(*) FROM mc_simulation_run WHERE method=%s", (method,))
    n_rows = cur.fetchone()[0]
    if n_rows == 0:
        raise SystemExit(f"✗ method={method!r} 於 mc_simulation_run 零列——無素材可推（#9 不補造）")
    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='mc_simulation_run' AND column_name = ANY(%s)", (list(PARAM_COLS),))
    db_types = dict(cur.fetchall())
    params = {}
    for col in PARAM_COLS:
        cur.execute(
            f"SELECT count({col}), min({col}), max({col}) FROM mc_simulation_run WHERE method=%s",
            (method,))
        n_nonnull, mn, mx = cur.fetchone()
        cur.execute(
            f"SELECT DISTINCT {col} FROM mc_simulation_run WHERE method=%s AND {col} IS NOT NULL ORDER BY 1",
            (method,))
        params[col] = {"db_type": db_types.get(col, "unknown"),
                       "values": [r[0] for r in cur.fetchall()],
                       "min": mn, "max": mx, "n_nonnull": n_nonnull}
    cur.execute("SELECT max(created_at) FROM mc_simulation_run WHERE method=%s", (method,))
    asof = cur.fetchone()[0]
    return {"method": method, "n_rows": n_rows, "params": params,
            "asof_data_max_created_at": asof.isoformat(), "git_sha": git_sha}


def summary_key_shapes(cur, method: str) -> list[dict]:
    """逐法列出 summary 之每一種鍵形（鍵集合＋該形列數）；一鍵不漏（唯讀）。"""
    cur.execute(
        """SELECT keys, count(*) FROM (
             SELECT r.run_id,
                    COALESCE(array_agg(k.k ORDER BY k.k) FILTER (WHERE k.k IS NOT NULL),
                             ARRAY[]::text[]) AS keys
             FROM mc_simulation_run r
             LEFT JOIN LATERAL jsonb_object_keys(r.summary) AS k(k) ON true
             WHERE r.method=%s GROUP BY r.run_id) s
           GROUP BY keys ORDER BY count(*) DESC, keys""", (method,))
    return [{"keys": list(keys), "n_rows": n} for keys, n in cur.fetchall()]


def draft_schema(profile: dict, shapes: list[dict]) -> dict:
    """**純函式**（selftest 標的）：觀測 profile＋鍵形 → param_schema 草案。
    絆線機制：properties 唯一來源＝PARAM_COLS 白名單之觀測欄；shapes 只落 x-unclassified。"""
    method, n_rows = profile["method"], profile["n_rows"]
    props: dict = {}
    required: list[str] = []
    excluded: dict = {}
    for col in PARAM_COLS:  # 固定順序＝確定性
        p = profile["params"].get(col)
        if p is None:
            continue
        if p["n_nonnull"] == 0:
            excluded[col] = f"史料全 NULL（{method} 無此參數）"
            continue
        props[col] = {"type": _JSON_TYPE.get(p["db_type"], "string"),
                      "x-observed": {"values": p["values"], "min": p["min"], "max": p["max"],
                                     "n_nonnull": p["n_nonnull"], "n_rows": n_rows}}
        if p["n_nonnull"] == n_rows:
            required.append(col)
    assert set(props) <= set(PARAM_COLS), "properties 只許來自參數欄白名單"
    return {
        "title": f"{method} param_schema（derive 草案；未經人審不生效）",
        "type": "object",
        "properties": props,
        "required": required,
        "additionalProperties": False,
        "x-excluded": excluded,
        "x-unclassified": {
            "summary_key_shapes": [{"keys": s["keys"], "n_rows": s["n_rows"]} for s in shapes],
            "note": "summary 鍵＝輸出非參數；不自動入 properties，逐鍵分類屬人審"},
        "x-scope-warning": SCOPE_WARNING,
        "x-provenance": {
            "source": "mc_simulation_run", "filter": f"method='{method}'", "n_rows": n_rows,
            "asof_data_max_created_at": profile["asof_data_max_created_at"],
            "git_sha": profile["git_sha"],
            "sql": "observed_param_profile／summary_key_shapes 之 DB aggregate（本檔原文）"},
    }


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _overview(cur) -> int:
    cur.execute("SELECT method, count(*) FROM mc_simulation_run GROUP BY 1 ORDER BY 2 DESC, 1")
    rows = cur.fetchall()
    print(f"── mc_simulation_run 現況（{sum(n for _, n in rows)} 列／{len(rows)} 法；唯讀）──")
    for method, n in rows:
        nshapes = len(summary_key_shapes(cur, method))
        print(f"  {method:<28} {n:>4} 列  summary 鍵形 {nshapes}")
    print("（單法草案：--method <名>；全法：--all；寫檔須 --out）")
    return 0


def _run(method: str | None, do_all: bool, out: str | None) -> int:
    print(f"# queried at {datetime.now().isoformat()}（wall-clock 只入 stderr，保 byte-identical）",
          file=sys.stderr)
    sha = _git_sha()
    from augur.core import db
    import psycopg2
    try:  # graceful（#29a）：連線失敗不裸 traceback（connect 為 contextmanager，例外在 __enter__ 才炸）
        with db.connect() as conn, db.transaction(conn) as cur:
            if not (method or do_all):
                return _overview(cur)
            if do_all:
                cur.execute("SELECT DISTINCT method FROM mc_simulation_run ORDER BY 1")
                methods = [r[0] for r in cur.fetchall()]
            else:
                methods = [method]
            drafts = {m: draft_schema(observed_param_profile(cur, m, sha),
                                      summary_key_shapes(cur, m)) for m in methods}
    except psycopg2.OperationalError as e:
        print(f"✗ DB 連線失敗：{str(e).strip()}（需 .env 環境；set -a && . ./.env && set +a）")
        return 1
    if out:
        outdir = Path(out)
        outdir.mkdir(parents=True, exist_ok=True)
        for m, d in drafts.items():
            p = outdir / f"{m}.param_schema.draft.json"
            p.write_text(_dumps(d), encoding="utf-8")
            print(f"✓ 寫出 {p}", file=sys.stderr)
        return 0
    sys.stdout.write(_dumps(drafts[methods[0]] if not do_all else drafts))
    return 0


def _fixture_profile(method: str, blk_nonnull: int, n_rows: int = 261) -> dict:
    p = {"horizon_td": {"db_type": "integer", "values": [21, 30, 42, 60, 63, 126],
                        "min": 21, "max": 126, "n_nonnull": n_rows},
         "n_paths": {"db_type": "integer", "values": [10000], "min": 10000, "max": 10000,
                     "n_nonnull": n_rows},
         "seed": {"db_type": "integer", "values": [42], "min": 42, "max": 42, "n_nonnull": n_rows},
         "block_len_td": {"db_type": "integer",
                          "values": [21] if blk_nonnull else [],
                          "min": 21 if blk_nonnull else None,
                          "max": 21 if blk_nonnull else None, "n_nonnull": blk_nonnull}}
    return {"method": method, "n_rows": n_rows, "params": p,
            "asof_data_max_created_at": "2026-07-27T16:44:15+08:00", "git_sha": "fixedsha"}


_FIXTURE_SHAPES = [  # 真鍵形（2026-08-01 親驗 iid 之 260+1）＋毒鍵測絆線②
    {"keys": ["cone", "disclaimer", "horizon_td", "last_close", "note_p_up",
              "sim_stat_p_terminal_up", "terminal"], "n_rows": 260},
    {"keys": ["cell", "disclaimer", "kind", "maxdd", "terminal"], "n_rows": 1},
]


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    iid = draft_schema(_fixture_profile("iid_bootstrap", 0), _FIXTURE_SHAPES)
    blk = draft_schema(_fixture_profile("block_bootstrap", 261), _FIXTURE_SHAPES)
    part = draft_schema(_fixture_profile("partial_case", 100), _FIXTURE_SHAPES)
    # 絆線①：全 NULL 欄不入 properties/required、入 x-excluded；非 NULL 欄必入
    chk("絆線①a iid 全 NULL 之 block_len_td 不入 properties",
        "block_len_td" not in iid["properties"])
    chk("絆線①b iid 之 block_len_td 不入 required", "block_len_td" not in iid["required"])
    chk("絆線①c iid 之 block_len_td 入 x-excluded 並註史料全 NULL",
        "史料全 NULL" in iid["x-excluded"].get("block_len_td", ""))
    chk("絆線①d block 之 block_len_td 入 properties＋required",
        "block_len_td" in blk["properties"] and "block_len_td" in blk["required"])
    chk("絆線①e 部分 NULL＝入 properties 不入 required",
        "block_len_td" in part["properties"] and "block_len_td" not in part["required"])
    # 絆線②：summary 鍵禁入 properties（毒鍵 cone/cell 在 fixture shapes 內）
    chk("絆線②a summary 鍵（cone/cell/last_close）皆不入 properties",
        not ({"cone", "cell", "last_close", "terminal"} & set(iid["properties"]))),
    chk("絆線②b properties ⊆ 參數欄白名單", set(iid["properties"]) <= set(PARAM_COLS))
    chk("絆線②c 鍵形一鍵不漏落 x-unclassified",
        iid["x-unclassified"]["summary_key_shapes"] == [
            {"keys": s["keys"], "n_rows": s["n_rows"]} for s in _FIXTURE_SHAPES])
    # 絆線③：確定性（同輸入兩次 byte-identical＋fixture 輸出凍結黃金鎖——
    # 鎖行為輸出非原始碼字面；秒級 wall-clock 混入等慢變非確定性唯黃金鎖抓得到，突變驗紅實證）
    again = draft_schema(_fixture_profile("iid_bootstrap", 0), _FIXTURE_SHAPES)
    chk("絆線③a 同輸入兩次呼叫 byte-identical", _dumps(iid) == _dumps(again))
    import hashlib
    chk("絆線③b fixture 輸出 sha256 合黃金鎖",
        hashlib.sha256(_dumps(iid).encode()).hexdigest()
        == "4dbc67ff3e3e6143675111c0613905a3bb2a3eb5455233552d61d7f76120f83a")
    # 草案性質與警語（裁決要求：明標未經人審＋D-2 邊界）
    chk("required ⊆ properties", set(iid["required"]) <= set(iid["properties"]))
    chk("title 明標「未經人審不生效」", "未經人審不生效" in iid["title"])
    chk("x-scope-warning 明標 D-2 邊界（不得宣稱 sim 可開跑）",
        "D-2" in iid["x-scope-warning"] and "不得據此宣稱 sim 可開跑" in iid["x-scope-warning"])
    chk("additionalProperties=false", iid["additionalProperties"] is False)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="mc_simulation_run → param_schema 草案（唯讀；H2）")
    ap.add_argument("--method")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="輸出目錄（僅明示才寫檔）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.method and a.all:
        print("✗ --method 與 --all 互斥")
        return 2
    return _run(a.method, a.all, a.out)


if __name__ == "__main__":
    sys.exit(main())

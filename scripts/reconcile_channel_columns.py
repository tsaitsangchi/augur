#!/usr/bin/env python
"""M-W2 欄位級唱讀對帳 — `world_channel_binding` × `column_catalog` × 實體表，逐欄對不對得上。

🎯 這支在做什麼（白話）：
WM.36 欄 3 要求通道映射「**粒度至欄位級**」，但 98 條通道之 `source_column` 現為 **0/98**。
要把它填起來（M-W5 S3），得先知道「**欄位級真值對不對得上**」——本支就是那把尺：
對每條通道，把三份欄位清單擺在一起**唱讀**——
  · **實體表**（`information_schema.columns` ＋ `pg_constraint` 之真 PK）＝真值
  · **`column_catalog`**（登錄簿；欄名／型別／PK／中文名／anti-leakage 旗標）
  · **通道列**（`world_channel_binding.source_column`；現全 NULL）
逐欄判「對得上／對不上」，對不上者分六型（見 `ISSUES`），並算每條通道之**展開難度桶**
（值欄數＝live 欄 − 真 PK 欄；單值欄＝機械唯一可自動配對，多值欄＝須人裁哪些欄屬該概念）。
產出即 M-W5 S3 之**單位成本與規模**依據——把「來不來得及」從感覺變機械。

**本支不填欄、不寫入**：純 SELECT，零 DDL、零 INSERT/UPDATE、零外部 API（FinMind／FRED 凍結中）。
`source_column` 之實際填值屬 M-W5，且粒度須待 M-W3／M-W4 裁定後方可展開。

守原則 #9/#10（每個數字出自 DB query、可 trace）· #15（對不上就列，不四捨五入成「大致對上」）·
#28（純 SQL 零 Claude token）· #29(a)(c)(d)（個別可執行／參數化通用／指令矩陣）· #35（回歸鎖三規則）。

條文錨：`specs/WORLD-MODEL-SPECIFICATION.md` WM.36:344-358（登錄七欄；欄 3「粒度至欄位級、一對多」；
「登錄項七欄俱全且各欄可解析者為登錄完成」）· WM.35:336-340（unmapped＝顯式合法過渡態）。
SSOT＝`reports/augur_optimization_master_plan_20260803.md` 第 25 步（M-W2）。

執行指令矩陣：
  python scripts/reconcile_channel_columns.py                 # 母體唱讀對帳總表（唯讀；無參數安全預設）
  python scripts/reconcile_channel_columns.py --survey        # 同上，明示
  python scripts/reconcile_channel_columns.py --issues        # 逐列印「對不上」之欄（唯讀）
  python scripts/reconcile_channel_columns.py --sample 10     # 分層抽樣 N 條通道＋逐條機械展開與計時
  python scripts/reconcile_channel_columns.py --binding 75    # 單一通道之逐欄唱讀明細
  python scripts/reconcile_channel_columns.py --selftest      # 純紅綠自測（免 DB 免 API、零 usage）
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

# ── 對不上之型態閉集（單一住所；統計與逐列共用同一組碼，避免兩處漂移）──
ISSUES = {
    "catalog_missing": "實體表有此欄、column_catalog 未登錄（新欄漏登／命名漂移）",
    "live_missing":    "column_catalog 有此欄、實體表無（欄已改名／已刪／catalog 過期）",
    "type_unregistered": "catalog 之 inferred_type 為 NULL（型別未登錄，無從比對）",
    "type_mismatch":   "catalog 之 inferred_type 與實體型別不符",
    "pk_mismatch":     "catalog 之 is_pk 與實體 PK 不符",
    "table_absent":    "通道之 source_table 在庫內無實體表（僅 catalog 有登錄，無真值可對）",
}

# catalog 之 inferred_type → 實體 data_type（`information_schema.columns.data_type` 字面）
TYPE_MAP = {
    "VARCHAR": "character varying",
    "NUMERIC": "numeric",
    "DATE": "date",
    "TEXT": "text",
}

# 展開難度桶：值欄數決定「能否機械唯一配對」。值欄＝live 欄 − 真 PK 欄。
BUCKETS = (
    ("B0_無實體表", "catalog 有登錄但表不存在 ⇒ 欄位級展開無真值可驗"),
    ("B1_零值欄", "全部欄皆為 PK ⇒ 事實載體是「列存在」本身，無值欄可指"),
    ("B2_單值欄", "恰一個非 PK 欄 ⇒ **機械唯一**，可自動配對"),
    ("B3_2-4值欄", "少量值欄 ⇒ 須人裁哪些欄屬該概念"),
    ("B4_5-9值欄", "中量值欄 ⇒ 須人裁"),
    ("B5_10值欄以上", "大量值欄 ⇒ 須人裁，且多為多值表（尚須列鍵，見 M-W4）"),
)


# ── 純函式核心（#35(1)：餵真列形即可紅綠雙向；無 DB、無字面比對）──
def reconcile_column(cat: dict | None, live: dict | None) -> tuple:
    """單欄唱讀：回**問題碼 tuple**（空 tuple＝對得上）。純函式。

    `cat`＝column_catalog 列（`column_name`／`inferred_type`／`is_pk`），`live`＝實體欄
    （`column_name`／`data_type`／`is_pk`）。任一為 None＝該側無此欄。
    回 tuple 而非單一 verdict，是因為同一欄可同時型別未登錄且 PK 不符（`data_audit_log.id` 即此）
    ——壓成單一 verdict 會靜默吃掉第二個問題。
    """
    if live is None and cat is None:
        raise ValueError("兩側皆無此欄——不該進入唱讀")
    if cat is None:
        return ("catalog_missing",)
    if live is None:
        return ("live_missing",)
    out = []
    it = cat.get("inferred_type")
    if it is None:
        out.append("type_unregistered")
    elif TYPE_MAP.get(it, it) != live.get("data_type"):
        out.append("type_mismatch")
    if bool(cat.get("is_pk")) != bool(live.get("is_pk")):
        out.append("pk_mismatch")
    return tuple(out)


def expansion_bucket(n_live: int, n_value: int) -> str:
    """展開難度桶（純函式）。`n_live`＝實體欄數（0＝無實體表）；`n_value`＝非 PK 欄數。"""
    if n_live == 0:
        return "B0_無實體表"
    if n_value == 0:
        return "B1_零值欄"
    if n_value == 1:
        return "B2_單值欄"
    if n_value <= 4:
        return "B3_2-4值欄"
    if n_value <= 9:
        return "B4_5-9值欄"
    return "B5_10值欄以上"


def auto_pairable(bucket: str, issues: tuple) -> bool:
    """該通道之 `source_column` 能否**機械唯一**決定（純函式）。

    唯 B2（恰一值欄）且該表逐欄唱讀零問題者為真——有問題即代表 catalog 這把尺本身對不上
    實體表，據以自動配對會把錯的欄名寫進 Registry。保守：不確定即 False。
    """
    return bucket == "B2_單值欄" and not issues


def allocate_strata(counts: dict, n: int) -> dict:
    """依層大小比例配置抽樣數（最大餘數法；純函式、決定性）。

    回 {層: 抽幾條}，總和恰為 min(n, 母體)。每個非空層至少配 0（不強塞），比例相同者依鍵序穩定。
    """
    total = sum(counts.values())
    n = min(n, total)
    if total == 0 or n == 0:
        return {k: 0 for k in counts}
    quota = {k: v * n / total for k, v in counts.items()}
    base = {k: int(q) for k, q in quota.items()}
    rest = n - sum(base.values())
    order = sorted(counts, key=lambda k: (-(quota[k] - base[k]), k))
    for k in order[:rest]:
        base[k] += 1
    return base


def sample_order(binding_ids, seed: str) -> list:
    """決定性抽樣順序（純函式）：以 md5(seed:binding_id) 排序。同 seed 必得同樣本，可復現。"""
    return sorted(binding_ids,
                  key=lambda b: hashlib.md5(f"{seed}:{b}".encode()).hexdigest())


def stratified_sample(rows, n: int, seed: str) -> list:
    """分層抽樣（純函式）：rows＝[{binding_id, bucket, ...}]，回抽中之 binding_id 列表。"""
    by = {}
    for r in rows:
        by.setdefault(r["bucket"], []).append(r["binding_id"])
    alloc = allocate_strata({k: len(v) for k, v in by.items()}, n)
    out = []
    for bucket in sorted(by):
        out.extend(sample_order(by[bucket], seed)[:alloc[bucket]])
    return sorted(out)


# ── DB 面（全部 SELECT；#30 不觸 DDL、M-T5 不搶 heavy slot）──
LIVE_COLS_SQL = """
SELECT c.table_name, c.column_name, c.data_type, c.ordinal_position,
       (pk.col IS NOT NULL) AS is_pk
  FROM information_schema.columns c
  LEFT JOIN (
       SELECT rel.relname AS t, att.attname AS col
         FROM pg_constraint con
         JOIN pg_class rel ON rel.oid = con.conrelid
         JOIN pg_namespace ns ON ns.oid = rel.relnamespace AND ns.nspname = 'public'
         JOIN unnest(con.conkey) k(attnum) ON true
         JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = k.attnum
        WHERE con.contype = 'p') pk
    ON pk.t = c.table_name AND pk.col = c.column_name
 WHERE c.table_schema = 'public'
   AND c.table_name IN (SELECT DISTINCT source_table FROM world_channel_binding
                         WHERE superseded_at IS NULL)
"""

CAT_COLS_SQL = """
SELECT dataset, column_name, inferred_type, is_pk, ordinal,
       column_name_zh, anti_leakage_flag, last_verified
  FROM column_catalog
 WHERE dataset IN (SELECT DISTINCT source_table FROM world_channel_binding
                    WHERE superseded_at IS NULL)
"""

BINDING_SQL = """
SELECT binding_id, concept_key, source_table, source_column, channel_role, mapping_status
  FROM world_channel_binding
 WHERE superseded_at IS NULL
 ORDER BY binding_id
"""


def _fetch(conn) -> list:
    """讀三份清單並組成逐通道之唱讀結果（唯讀）。回 [{binding..., cols:[...], issues:(...)}]。"""
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = '60s'")
        cur.execute(LIVE_COLS_SQL)
        live = {}
        for t, col, dt, ordi, is_pk in cur.fetchall():
            live.setdefault(t, {})[col] = {
                "column_name": col, "data_type": dt, "ordinal": ordi, "is_pk": is_pk}
        cur.execute(CAT_COLS_SQL)
        cat = {}
        for ds, col, it, is_pk, ordi, zh, alf, lv in cur.fetchall():
            cat.setdefault(ds, {})[col] = {
                "column_name": col, "inferred_type": it, "is_pk": is_pk, "ordinal": ordi,
                "column_name_zh": zh, "anti_leakage_flag": alf, "last_verified": lv}
        cur.execute(BINDING_SQL)
        bindings = [dict(zip(("binding_id", "concept_key", "source_table", "source_column",
                              "channel_role", "mapping_status"), r)) for r in cur.fetchall()]
    return [_reconcile_binding(b, live.get(b["source_table"], {}),
                               cat.get(b["source_table"], {})) for b in bindings]


def _reconcile_binding(b: dict, live: dict, cat: dict) -> dict:
    """組單一通道之唱讀結果（純函式；live／cat 為欄名→列形之 dict）。"""
    cols = []
    for name in sorted(set(live) | set(cat)):
        iss = reconcile_column(cat.get(name), live.get(name))
        cols.append({"column_name": name, "issues": iss,
                     "live": live.get(name), "cat": cat.get(name)})
    n_live = len(live)
    n_value = sum(1 for c in live.values() if not c["is_pk"])
    issues = tuple(sorted({i for c in cols for i in c["issues"]}))
    if n_live == 0:
        issues = tuple(sorted(set(issues) | {"table_absent"}))
    bucket = expansion_bucket(n_live, n_value)
    return {**b, "cols": cols, "n_live": n_live, "n_value": n_value, "n_cat": len(cat),
            "bucket": bucket, "issues": issues,
            "auto_pairable": auto_pairable(bucket, issues),
            "value_cols": sorted(c for c, v in live.items() if not v["is_pk"])}


# ── 輸出面 ──
def _survey(rows) -> int:
    n = len(rows)
    tot_cols = sum(len(r["cols"]) for r in rows)
    bad_cols = sum(1 for r in rows for c in r["cols"] if c["issues"])
    filled = sum(1 for r in rows if (r["source_column"] or "").strip())
    print(f"── 通道欄位級唱讀對帳（唯讀；母體＝{n} 條現行通道）──")
    print(f"  source_column 已填：{filled}/{n}"
          f"　｜　mapping_status=mapped：{sum(1 for r in rows if r['mapping_status']=='mapped')}/{n}")
    print(f"\n【欄級】唱讀 {tot_cols} 欄（catalog ∪ 實體表之聯集）："
          f"對得上 {tot_cols-bad_cols}（{(tot_cols-bad_cols)/tot_cols:.1%}）／"
          f"對不上 {bad_cols}（{bad_cols/tot_cols:.1%}）")
    per = {}
    for r in rows:
        for c in r["cols"]:
            for i in c["issues"]:
                per[i] = per.get(i, 0) + 1
    for code in ISSUES:
        if code in per:
            print(f"    · {code:<18}{per[code]:>4} 欄　{ISSUES[code]}")
    print(f"\n【通道級】展開難度桶（值欄＝實體欄 − 真 PK 欄）：")
    bk = {}
    for r in rows:
        bk.setdefault(r["bucket"], []).append(r)
    for name, why in BUCKETS:
        g = bk.get(name, [])
        if not g:
            continue
        print(f"    · {name:<14}{len(g):>3} 條　值欄合計 {sum(x['n_value'] for x in g):>3}　{why}")
    ap = [r for r in rows if r["auto_pairable"]]
    print(f"\n【自動配對率】機械唯一可決者 {len(ap)}/{n}（{len(ap)/n:.1%}）"
          f"；須人裁 {n-len(ap)}/{n}（{(n-len(ap))/n:.1%}）")
    print(f"  展開總面（全部值欄）＝{sum(r['n_value'] for r in rows)} 欄")
    dirty = [r for r in rows if r["issues"]]
    print(f"  逐通道至少一欄對不上者：{len(dirty)}/{n}（{len(dirty)/n:.1%}）")
    return 0


def _issues(rows) -> int:
    print("── 對不上之欄（逐列；唯讀）──")
    k = 0
    for r in rows:
        bad = [c for c in r["cols"] if c["issues"]]
        if not bad and "table_absent" not in r["issues"]:
            continue
        head = (f"binding {r['binding_id']:>3}  {r['source_table']}"
                f"  [{r['mapping_status']}]  bucket={r['bucket']}")
        print(f"\n{head}")
        if "table_absent" in r["issues"]:
            print(f"    ! table_absent    （catalog {r['n_cat']} 欄；實體表不存在，無真值可對）")
        for c in bad:
            cat, live = c["cat"], c["live"]
            det = (f"catalog={cat.get('inferred_type') if cat else '—'}"
                   f"/pk={cat.get('is_pk') if cat else '—'}"
                   f"  live={live.get('data_type') if live else '—'}"
                   f"/pk={live.get('is_pk') if live else '—'}")
            print(f"    - {c['column_name']:<28}{','.join(c['issues']):<32}{det}")
            k += 1
    print(f"\n合計對不上 {k} 欄。")
    return 0


def _detail(rows, bid: int) -> int:
    hit = [r for r in rows if r["binding_id"] == bid]
    if not hit:
        print(f"✗ 無 binding_id={bid} 之現行通道列")
        return 1
    r = hit[0]
    print(f"── binding {bid}：{r['source_table']}　[{r['mapping_status']}]"
          f"　concept_key={r['concept_key']}　source_column={r['source_column']}")
    print(f"   bucket={r['bucket']}　實體欄 {r['n_live']}／catalog 欄 {r['n_cat']}"
          f"　值欄 {r['n_value']}　自動配對={r['auto_pairable']}")
    print(f"   {'欄名':<30}{'實體型別':<26}{'PK':<6}{'catalog型別':<12}{'中文名':<18}唱讀")
    for c in r["cols"]:
        live, cat = c["live"], c["cat"]
        print(f"   {c['column_name']:<30}"
              f"{(live.get('data_type') if live else '—'):<26}"
              f"{('Y' if live and live['is_pk'] else '.'):<6}"
              f"{str(cat.get('inferred_type') if cat else '—'):<12}"
              f"{str(cat.get('column_name_zh') if cat else '—')[:16]:<18}"
              f"{','.join(c['issues']) if c['issues'] else 'ok'}")
    if r["value_cols"]:
        print(f"   值欄候選（source_column 之展開面）：{', '.join(r['value_cols'])}")
    return 0


def _sample(rows, n: int, seed: str) -> int:
    picked = stratified_sample(rows, n, seed)
    idx = {r["binding_id"]: r for r in rows}
    print(f"── 分層抽樣 {len(picked)}/{len(rows)} 條（seed={seed!r}；決定性，同 seed 可復現）──")
    alloc = allocate_strata(
        {b: sum(1 for r in rows if r["bucket"] == b) for b, _ in BUCKETS
         if any(r["bucket"] == b for r in rows)}, n)
    print(f"   配置：{alloc}")
    print(f"\n{'bid':>4} {'表':<44}{'桶':<15}{'值欄':>4} {'唱讀問題':<34}{'自動':<5}{'機械耗時':>9}")
    tot = 0.0
    for bid in picked:
        r = idx[bid]
        t0 = time.perf_counter()
        _ = [reconcile_column(c["cat"], c["live"]) for c in r["cols"]]
        _ = expansion_bucket(r["n_live"], r["n_value"])
        dt = time.perf_counter() - t0
        tot += dt
        print(f"{bid:>4} {r['source_table'][:43]:<44}{r['bucket']:<15}{r['n_value']:>4} "
              f"{(','.join(r['issues']) or 'ok')[:33]:<34}"
              f"{('Y' if r['auto_pairable'] else 'N'):<5}{dt*1000:>7.2f}ms")
    print(f"\n   機械對帳合計 {tot*1000:.1f} ms／{len(picked)} 條"
          f"（＝{tot/max(len(picked),1)*1000:.2f} ms/條）")
    print("   ⚠ 上列僅**機械**耗時。`source_column` 之實際展開另含人裁成本"
          "（哪些值欄屬該概念、多值表之列鍵），不在本計時內——見抽樣報告之逐條實測。")
    return 0


# ── 紅綠自測（#35：純函式餵真列形／輸入側突變驗紅／零字面斷言；免 DB 免 API）──
def _live(col, dt, pk=False):
    return {"column_name": col, "data_type": dt, "is_pk": pk}


def _cat(col, it, pk=False):
    return {"column_name": col, "inferred_type": it, "is_pk": pk}


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    # (1) 真實例：TaiwanStockPrice.close（2026-08-03 唯讀親驗之列形）→ 對得上
    chk("catalog 與實體逐項相同 → 空 tuple（對得上）",
        reconcile_column(_cat("close", "NUMERIC"), _live("close", "numeric")) == ())

    # (2) 真實例：TaiwanStockConvertibleBondDailyOverview.date（catalog=VARCHAR、實體=date）
    chk("型別不符（VARCHAR vs date）→ type_mismatch",
        reconcile_column(_cat("date", "VARCHAR"), _live("date", "date")) == ("type_mismatch",))

    # (3) 資料驅動之鎖：同一輸入改對型別，判決必須跟著變綠
    #     （若實作把表名／欄名寫死成白名單或恆回 mismatch，這條回舊值 ⇒ 紅）
    chk("同一欄把 catalog 型別改成相符 → 轉為對得上（證明真比對輸入、非內建對照）",
        reconcile_column(_cat("date", "DATE"), _live("date", "date")) == ()
        and reconcile_column(_cat("date", "VARCHAR"), _live("date", "date")) != ())

    # (4) 真實例：data_audit_log.id（catalog inferred_type NULL 且 is_pk=False，實體 bigint PK）
    #     兩個問題必須同時出現——壓成單一 verdict 會靜默吃掉第二個
    chk("型別未登錄＋PK 不符 → 兩碼並存（不得只回其一）",
        set(reconcile_column(_cat("id", None), _live("id", "bigint", pk=True)))
        == {"type_unregistered", "pk_mismatch"})

    # (5) 真實例：fred_series.realtime_start（實體有、catalog 無）
    chk("catalog 無此欄 → catalog_missing",
        reconcile_column(None, _live("realtime_start", "date")) == ("catalog_missing",))
    chk("實體表無此欄 → live_missing",
        reconcile_column(_cat("ghost", "NUMERIC"), None) == ("live_missing",))
    try:
        reconcile_column(None, None)
        chk("兩側皆無 → 拋（不得靜默回對得上）", False)
    except ValueError:
        chk("兩側皆無 → 拋（不得靜默回對得上）", True)

    # (6) 桶邊界：以真值欄數驗（TaiwanStockTradingDate=1 欄全 PK；TaiwanStockLoanCollateralBalance=35 值欄）
    chk("桶邊界逐點正確（0/1/2/4/5/9/10 值欄）",
        [expansion_bucket(nl, nv) for nl, nv in
         ((0, 0), (1, 0), (2, 1), (5, 4), (6, 5), (10, 9), (37, 35))]
        == ["B0_無實體表", "B1_零值欄", "B2_單值欄", "B3_2-4值欄",
            "B4_5-9值欄", "B4_5-9值欄", "B5_10值欄以上"])

    # (7) 自動配對：唯「單值欄且零問題」為真；有問題即不得自動配對
    chk("單值欄且零問題 → 可自動配對", auto_pairable("B2_單值欄", ()) is True)
    chk("單值欄但有唱讀問題 → 不得自動配對（catalog 這把尺本身對不上）",
        auto_pairable("B2_單值欄", ("type_mismatch",)) is False)
    chk("多值欄即使零問題 → 不得自動配對（哪些欄屬該概念須人裁）",
        auto_pairable("B3_2-4值欄", ()) is False)

    # (8) 分層配置：餵 2026-08-03 之真母體分佈，總數必須恰為 n 且隨母體變動
    real = {"B0_無實體表": 11, "B1_零值欄": 10, "B2_單值欄": 10,
            "B3_2-4值欄": 29, "B4_5-9值欄": 25, "B5_10值欄以上": 13}
    a10 = allocate_strata(real, 10)
    chk("真母體 98 條配 10 → 總和恰 10、且最大層配得不少於最小層",
        sum(a10.values()) == 10 and a10["B3_2-4值欄"] >= a10["B0_無實體表"])
    shifted = {**real, "B5_10值欄以上": 60}
    chk("母體分佈改變 → 配置隨之改變（證明真按比例、非寫死表）",
        allocate_strata(shifted, 10)["B5_10值欄以上"] > a10["B5_10值欄以上"])
    chk("n 大於母體 → 取母體全量（不虛報樣本數）",
        sum(allocate_strata(real, 9999).values()) == sum(real.values()))
    chk("n=0／空母體 → 全 0（不除零）",
        sum(allocate_strata(real, 0).values()) == 0 and allocate_strata({}, 5) == {})

    # (9) 抽樣決定性與可復現：同 seed 必同序、異 seed 必異序（否則 seed 是裝飾品）
    ids = list(range(1, 99))
    chk("同 seed → 同順序（可復現）", sample_order(ids, "w2") == sample_order(ids, "w2"))
    chk("異 seed → 不同順序（seed 真的參與雜湊）",
        sample_order(ids, "w2") != sample_order(ids, "other"))
    chk("抽樣為母體之子集且不重複",
        set(sample_order(ids, "w2")) == set(ids) and len(set(sample_order(ids, "w2"))) == len(ids))

    # (10) 端到端：餵真列形之通道，逐欄唱讀與桶／自動配對一致
    b = _reconcile_binding(
        {"binding_id": 88, "concept_key": None, "source_table": "data_audit_log",
         "source_column": None, "channel_role": "observation", "mapping_status": "unmapped"},
        {"id": _live("id", "bigint", pk=True), "dataset": _live("dataset", "character varying"),
         "rows": _live("rows", "bigint")},
        {"id": _cat("id", None), "dataset": _cat("dataset", None), "rows": _cat("rows", None)})
    chk("端到端：3 欄／2 值欄 → B3 桶、三欄皆有問題、不可自動配對",
        b["n_value"] == 2 and b["bucket"] == "B3_2-4值欄"
        and all(c["issues"] for c in b["cols"]) and b["auto_pairable"] is False)
    b_clean = _reconcile_binding(
        {"binding_id": 4, "concept_key": "tw.trading_calendar",
         "source_table": "TaiwanStockTradingDate", "source_column": None,
         "channel_role": "observation", "mapping_status": "mapped"},
        {"date": _live("date", "date", pk=True)}, {"date": _cat("date", "DATE", pk=True)})
    chk("端到端：全 PK 單欄 → B1 零值欄、零問題、仍不可自動配對（無值欄可指）",
        b_clean["bucket"] == "B1_零值欄" and b_clean["issues"] == ()
        and b_clean["auto_pairable"] is False)
    b_absent = _reconcile_binding(
        {"binding_id": 24, "concept_key": None, "source_table": "TaiwanStockKBar",
         "source_column": None, "channel_role": "observation", "mapping_status": "unmapped"},
        {}, {"close": _cat("close", "NUMERIC")})
    chk("端到端：無實體表 → table_absent＋live_missing，桶為 B0",
        b_absent["bucket"] == "B0_無實體表"
        and set(b_absent["issues"]) == {"table_absent", "live_missing"})

    # (11) 型態閉集不得漏碼：凡實作產生之碼皆須在 ISSUES 有說明（新增碼漏寫說明即紅）
    produced = set(b["issues"]) | set(b_absent["issues"]) | {
        i for c in (reconcile_column(_cat("date", "VARCHAR"), _live("date", "date")),
                    reconcile_column(None, _live("x", "date")))
        for i in c}
    chk("所有產生之問題碼皆在 ISSUES 閉集內有說明", produced <= set(ISSUES))

    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="M-W2 通道欄位級唱讀對帳（唯讀；零 DDL、零外部 API）")
    ap.add_argument("--survey", action="store_true", help="母體唱讀對帳總表（無參數之預設）")
    ap.add_argument("--issues", action="store_true", help="逐列印出對不上之欄")
    ap.add_argument("--sample", type=int, metavar="N", help="分層抽樣 N 條並逐條機械展開＋計時")
    ap.add_argument("--seed", default="w2", help="抽樣 seed（決定性；預設 w2）")
    ap.add_argument("--binding", type=int, metavar="ID", help="單一通道之逐欄唱讀明細")
    ap.add_argument("--selftest", action="store_true", help="純紅綠自測（免 DB 免 API）")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    try:
        from augur.core import db
        with db.connect() as conn:
            rows = _fetch(conn)
    except Exception as e:  # noqa: BLE001 — 無參數須 graceful（#29a），不裸 traceback
        print(f"（本支需 DB 唯讀連線；現不可達：{type(e).__name__}: {e}）")
        print("（--selftest 免 DB 可跑；連線設定見 .env）")
        return 0 if not (a.survey or a.issues or a.sample or a.binding) else 1
    if a.binding is not None:
        return _detail(rows, a.binding)
    if a.sample:
        return _sample(rows, a.sample, a.seed)
    if a.issues:
        return _issues(rows)
    return _survey(rows)


if __name__ == "__main__":
    sys.exit(main())

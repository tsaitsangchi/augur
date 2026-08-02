#!/usr/bin/env python3
"""🎯 絞殺法的安全帶——同一查詢跑「舊 vendor 直綁」與「新 registry 解析」兩路，逐列比對，diff=0 才准切。

WM.36 合規弧 M3（設計 SSOT＝reports/wm3536_vendor_registry_plan_20260802.md §5 表列 4；
Phase 6(c)「雙讀影子比對、diff 零才切、非零熔斷回退」之落地）。
守原則 #15（**綠燈量的必須是它宣稱在量的東西**：空集／新舊 SQL 全等／超量未讀完一律記 pending，
不冒充 green）、#9/#10（判定出自本次雙跑之真列、evidence 落檔可重跑）、#12（口徑與 registry 各有
單一住所——vendor 掃描口徑復用 check_vendor_binding、解析復用 augur.catalog.world_concept）、
#6（唯讀雙跑＋READ ONLY 交易；唯一寫入面＝帳本追加一列）、#29a/d、#35（比對為純函式、突變驗紅）。

## 兩種模式

**auto**（`--sql-file`／`--sql`）：舊 SQL 內之 vendor 字面 → `concepts_for_table` 反查世界概念 →
`resolve` 取權威表徵 → 生成新 SQL。**任一步不可解析即 fail-closed 停手**（未登錄／unmapped／
權威未指定 ⇒ 該資料僅具 Observation 地位、不得被消費，WM.35:338）——這正是本弧的閘。
**explicit**（`--old-sql-file` ＋ `--new-sql-file`）：兩路皆由改線者給定（改線不只換表名時用）。
兩模式共通：新 SQL 一律回頭過 M2 閘口徑掃描，仍含 vendor 字面即拒（否則「新路」是假的）。

## 判定（verdict，落 vendor_binding_strangler_ledger）

    green   逐列多重集全等且 n>0 ⇒ 可切
    red     欄形不同／逐列有差／新 SQL 仍直綁 ⇒ **熔斷、回退、停手問**（映射錯＝資料真實性事件）
    pending 比對未達成或無鑑別力：兩路皆空集／新舊 SQL 全等／超過 --max-rows
            （**不記 green**——空集與「全等但沒東西可比」證明不了等價；同尺四查「falsy 空集」之教訓）

逐列比對**保留型別**（cell 鍵＝(型別名, 值字串)）：`Decimal('1.0')` vs `1.0` 判為差異——
絞殺要求行為零變更，型別漂移就是變更。列序不影響（多重集比對；SQL 無 ORDER BY 時列序本無保證）。

## 本波（2026-08-02）之射程誠實

live 六概念之 `authoritative_binding_id` 全為 NULL（採認＝Steward 附卷裁定，hugo 親簽）
⇒ **auto 模式現在必然 fail-closed 停在「權威未指定」**，這是正確行為、非 bug；亦即
**M3 絞殺在 hugo 指定權威表徵前不可能開始**。explicit 模式與比對核心可即刻使用。

執行指令矩陣
------------
    python3 scripts/compare_shadow_binding.py                       # 無參數＝印矩陣＋現況前置檢查（唯讀）
    python3 scripts/compare_shadow_binding.py --preflight            # 唯讀：帳本表在否／六概念可解析否
    python3 scripts/compare_shadow_binding.py --sql-file q.sql --file src/augur/features/chip.py --batch A1-features
    python3 scripts/compare_shadow_binding.py --sql-file q.sql --param 2330 --param 2026-06-30 --map TaiwanStockDelisting=tw.delisting
    python3 scripts/compare_shadow_binding.py --old-sql-file a.sql --new-sql-file b.sql --file scripts/x.py --batch A2-build
    python3 scripts/compare_shadow_binding.py --old-sql-file a.sql --new-sql-file b.sql --file scripts/x.py --batch A2-build --evidence audits/x.txt --apply
    python3 scripts/compare_shadow_binding.py --selftest             # 紅綠自測（純函式餵真兩路結果；免 DB 免 API）
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import NamedTuple, Optional, Sequence

import _bootstrap  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from augur.catalog import world_concept as wc  # noqa: E402

LEDGER = "vendor_binding_strangler_ledger"
MAX_ROWS_DEFAULT = 200_000
_EXAMPLES_CAP = 10

# 唯讀護欄：雙跑是驗證、不是施作；任何寫入/DDL 動詞即拒（fail-closed，不猜意圖）
_WRITE_VERB = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|vacuum|"
    r"refresh|call|do|merge)\b", re.I)
# auto 模式改寫口徑（與 M2 閘同形：引號 CamelCase 表 ∪ fred_series；驗證則直接復用 M2 的 analyse）
_QUOTED_SQL = re.compile(r'(FROM\s+|JOIN\s+)"([A-Z][A-Za-z]+)"')
_BARE_SQL = re.compile(r"(FROM\s+|JOIN\s+)(fred_series)\b")


class Comparison(NamedTuple):
    """比對結果（純資料）。diff_rows=None ⇒ 逐列 diff 未計（比對未達成）。"""
    verdict: str
    n_old: int
    n_new: int
    diff_rows: Optional[int]
    note: str
    examples: tuple


class ShadowError(Exception):
    """雙讀比對之 fail-closed 例外（解析不出／SQL 不合唯讀／新路仍直綁）。"""


# ── 純函式：比對核心（#35(1) 餵真兩路結果 fixture 即可紅綠雙向）──
def canon_cell(v) -> tuple:
    """cell → (型別名, 值字串)。**保留型別**：Decimal('1.0') 與 float 1.0 不相等。"""
    if v is None:
        return ("NoneType", "")
    return (type(v).__name__, str(v))


def canon_row(row: Sequence) -> tuple:
    return tuple(canon_cell(v) for v in row)


def compare_rows(old_cols: Sequence[str], old_rows: Sequence[Sequence],
                 new_cols: Sequence[str], new_rows: Sequence[Sequence],
                 identical_sql: bool = False, truncated: bool = False) -> Comparison:
    """兩路結果 → Comparison。純函式；green 只在「真的比過且真的相等」時給。

    判定次序刻意如此：欄形不同（red）→ 未達成（pending）→ 逐列比對。
    """
    n_old, n_new = len(old_rows), len(new_rows)
    if tuple(old_cols) != tuple(new_cols):
        return Comparison("red", n_old, n_new, None,
                          f"欄形不同：舊 {tuple(old_cols)} vs 新 {tuple(new_cols)}——整體不可比，熔斷。",
                          ())
    if truncated:
        return Comparison("pending", n_old, n_new, None,
                          "結果超過 --max-rows，未讀完 ⇒ 比對未達成（縮窗或提高上限後重驗）。", ())
    if identical_sql:
        return Comparison("pending", n_old, n_new, None,
                          "新舊 SQL 全等 ⇒ 比對無鑑別力（等於拿自己比自己），不記 green。", ())
    if n_old == 0 and n_new == 0:
        return Comparison("pending", 0, 0, 0,
                          "兩路皆空集 ⇒ 證明不了等價（空集恆等），不記 green；換有資料之參數重驗。", ())
    c_old, c_new = Counter(map(canon_row, old_rows)), Counter(map(canon_row, new_rows))
    only_old, only_new = c_old - c_new, c_new - c_old
    diff = sum(only_old.values()) + sum(only_new.values())
    if diff == 0:
        return Comparison("green", n_old, n_new, 0, f"逐列多重集全等（{n_old} 列）⇒ 可切。", ())
    ex = ([("僅舊路", r, n) for r, n in only_old.most_common()]
          + [("僅新路", r, n) for r, n in only_new.most_common()])[:_EXAMPLES_CAP]
    return Comparison("red", n_old, n_new, diff,
                      f"逐列差異 {diff} 列（僅舊 {sum(only_old.values())}／"
                      f"僅新 {sum(only_new.values())}）⇒ 熔斷、回退、停手問。",
                      tuple(ex))


def assert_readonly(sql: str) -> None:
    """唯讀護欄（純函式）：寫入/DDL 動詞或多段語句一律拒。"""
    body = "\n".join(ln for ln in sql.splitlines() if not ln.lstrip().startswith("--"))
    m = _WRITE_VERB.search(body)
    if m:
        raise ShadowError(f"SQL 含非唯讀動詞 {m.group(1)!r}——影子比對只跑 SELECT（#6）。")
    if len([s for s in body.split(";") if s.strip()]) > 1:
        raise ShadowError("SQL 含多段語句（;）——一次只比一條 SELECT。")


def rewrite_sql(sql: str, lookup) -> tuple:
    """auto 模式：把 vendor 字面換成經 registry 解析之權威表名。純函式（解析由 lookup 注入）。

    lookup(table_literal) -> 新表名字面（含引號）；不可解析時由 lookup 自行拋。
    回 (新 SQL, ((舊表, 新字面), ...))；零命中即拋（沒有可絞殺的字面＝叫錯工具）。
    """
    seen = []

    def _sub(m):
        prefix, tbl = m.group(1), m.group(2)
        new = lookup(tbl)
        seen.append((tbl, new))
        return f"{prefix}{new}"

    out = _BARE_SQL.sub(_sub, _QUOTED_SQL.sub(_sub, sql))
    if not seen:
        raise ShadowError("SQL 內找不到 vendor 表字面（M2 口徑）——無可絞殺之處，請確認取對 SQL。")
    return out, tuple(seen)


def residual_vendor(sql: str) -> list:
    """新 SQL 是否仍含 vendor 直綁——**復用 M2 閘之口徑**（#12），不自造第二把尺。

    這是下游絆線（#35(2)）：改寫若漏掉一處、或 explicit 模式之「新路」其實沒改，這裡會亮。
    """
    from check_vendor_binding import analyse
    return [(t, f) for _ln, t, f in analyse(sql)]


def make_lookup(snapshot, overrides: Optional[dict] = None):
    """→ lookup(table)：反查概念→解析權威表徵→回引號表名。每步 fail-closed（WM.35/WM.36）。"""
    overrides = overrides or {}

    def lookup(table: str) -> str:
        key = overrides.get(table)
        if key is None:
            keys = wc.concepts_for_table(table, snapshot=snapshot)
            if not keys:
                raise ShadowError(
                    f"供應商表 {table!r} 未登錄任何世界概念（或全為 unmapped）——"
                    "其資料僅具 Observation 地位，不得被消費（WM.35:338）；"
                    "先登錄 world_channel_binding，或以 --map 明示概念鍵。")
            if len(keys) > 1:
                raise ShadowError(
                    f"供應商表 {table!r} 服務多個世界概念 {keys}（WM.36 欄 3 一對多）——"
                    "無法自動判定該查詢問的是哪一個，請以 --map "
                    f"{table}=<concept_key> 明示。")
            key = keys[0]
        b = wc.resolve(key, snapshot=snapshot)   # 權威未指定/已 supersede 等一律在此拋
        if b.column is not None:
            raise ShadowError(
                f"概念 {key!r} 之權威表徵為欄位級（{b.table}.{b.column}）——"
                "表名替換不足以表達，請用 explicit 模式（--old-sql-file/--new-sql-file）。")
        return wc.quote_ident(b.table)

    return lookup


def format_report(cmp_: Comparison, old_sql: str, new_sql: str, mappings=()) -> str:
    """→ evidence 全文（可落檔、可貼報告）。純函式。"""
    lines = [f"verdict={cmp_.verdict} n_old={cmp_.n_old} n_new={cmp_.n_new} "
             f"diff_rows={cmp_.diff_rows}", cmp_.note]
    if mappings:
        lines.append("映射：" + "; ".join(f"{a} → {b}" for a, b in mappings))
    for side, row, n in cmp_.examples:
        lines.append(f"  {side}×{n}: " + " | ".join(f"{t}:{v}" for t, v in row))
    lines += ["--- 舊路 SQL ---", old_sql.strip(), "--- 新路 SQL ---", new_sql.strip()]
    return "\n".join(lines) + "\n"


# ── DB 面（唯讀雙跑；唯一寫入＝帳本追加一列）──
def run_query(conn, sql: str, params: Sequence, max_rows: int) -> tuple:
    """唯讀跑一條 SELECT → (欄名, 列, 是否被截斷)。交易設 READ ONLY 並一律 rollback。"""
    assert_readonly(sql)
    conn.set_session(readonly=True)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params) if params else None)
            cols = tuple(d[0] for d in (cur.description or ()))
            rows = cur.fetchmany(max_rows + 1)
        truncated = len(rows) > max_rows
        return cols, tuple(rows[:max_rows]), truncated
    finally:
        conn.rollback()
        conn.set_session(readonly=False)


def occurrences_of(file_path: Optional[str]) -> Optional[int]:
    """該檔之 vendor 直綁處數——復用 M2 口徑實掃，不由呼叫者手填（手填的數字沒人驗）。"""
    if not file_path:
        return None
    p = ROOT / file_path
    if not p.exists():
        return None
    from check_vendor_binding import analyse
    return len(analyse(p.read_text(encoding="utf-8")))


def ledger_exists(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{LEDGER}",))
        return bool(cur.fetchone()[0])


def write_ledger(conn, file_path: str, batch: str, occurrences: Optional[int],
                 cmp_: Comparison, evidence_ref: Optional[str]) -> None:
    """帳本追加一列（唯一寫入面；只 INSERT，永不 UPDATE/DELETE——紅列須留得住）。"""
    from augur.core import db
    if not ledger_exists(conn):
        raise ShadowError(
            f"帳本表 {LEDGER} 不存在——先跑 scripts/migrate_strangler_ledger_ddl.py --apply"
            "（須 hugo 明示 #6）。fail-closed：不默默不記帳。")
    with db.transaction(conn) as cur:
        cur.execute(
            f"INSERT INTO {LEDGER} (file_path, batch, occurrences, shadow_diff_rows, verdict, evidence_ref)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (file_path, batch, occurrences if occurrences is not None else 0,
             cmp_.diff_rows, cmp_.verdict, evidence_ref))


def preflight(conn) -> int:
    """唯讀前置：帳本表在否＋六概念可否解析（不可解析＝M3 尚不能開工，誠實列出）。"""
    print(f"  {'✓' if ledger_exists(conn) else '·'} 帳本表 {LEDGER} "
          f"{'在' if ledger_exists(conn) else '不在（--apply 會 fail-closed 拒寫）'}")
    snap = wc.load_registry(conn, refresh=True)
    bad = dict(wc.unresolved(snap.concepts, snap.bindings))
    n_all = len(wc.current(snap.concepts))
    print(f"  {'✓' if not bad else '✗'} 世界概念可解析 {n_all - len(bad)}/{n_all}"
          f"{'' if not bad else '——auto 模式對其餘概念必 fail-closed（權威表徵待 Steward 附卷裁定）'}")
    for k in sorted(bad):
        print(f"      ✗ {k}：{bad[k].split('——')[0]}")
    return 0


def _load_sql(text: Optional[str], path: Optional[str], what: str) -> str:
    if text:
        return text
    if path:
        return Path(path).read_text(encoding="utf-8")
    raise ShadowError(f"缺 {what}")


def run(args) -> int:
    from augur.core import db
    params = args.param or []
    with db.connect() as conn:
        if args.old_sql_file or args.old_sql:
            old_sql = _load_sql(args.old_sql, args.old_sql_file, "--old-sql/--old-sql-file")
            new_sql = _load_sql(args.new_sql, args.new_sql_file, "--new-sql/--new-sql-file")
            mappings = ()
        else:
            old_sql = _load_sql(args.sql, args.sql_file, "--sql/--sql-file")
            snap = wc.load_registry(conn, refresh=True)
            overrides = dict(kv.split("=", 1) for kv in (args.map or []))
            new_sql, mappings = rewrite_sql(old_sql, make_lookup(snap, overrides))
        left = residual_vendor(new_sql)
        if left:
            raise ShadowError(
                f"新路 SQL 仍含 vendor 直綁 {left}——「新路」是假的，拒絕比對（否則記出假 green）。")
        assert_readonly(old_sql)
        assert_readonly(new_sql)
        oc, orows, otr = run_query(conn, old_sql, params, args.max_rows)
        nc, nrows, ntr = run_query(conn, new_sql, params, args.max_rows)
        cmp_ = compare_rows(oc, orows, nc, nrows,
                            identical_sql=old_sql.strip() == new_sql.strip(),
                            truncated=otr or ntr)
    report = format_report(cmp_, old_sql, new_sql, mappings)
    print(report)
    if args.evidence:
        Path(args.evidence).parent.mkdir(parents=True, exist_ok=True)
        Path(args.evidence).write_text(report, encoding="utf-8")
        print(f"（evidence 落檔 {args.evidence}）")
    if args.apply:
        if not (args.file and args.batch):
            raise ShadowError("--apply 須同時給 --file 與 --batch（帳本鍵）。")
        occ = occurrences_of(args.file)
        with db.connect() as conn:
            write_ledger(conn, args.file, args.batch, occ, cmp_, args.evidence)
        print(f"✓ 帳本追加一列（{args.file} / {args.batch} / occurrences={occ} / {cmp_.verdict}）")
    else:
        print("（--dry-run 預設：未寫帳本；確認後加 --apply）")
    return 0 if cmp_.verdict == "green" else 1


# ── 紅綠自測（#35：純函式餵真兩路結果／下游絆線／輸入側突變；免 DB 免 API）──
def _fx_rows():
    """真列形 fixture：日期＋股票代號＋數值＋整數（比照日 K 查詢之回傳形）。"""
    from datetime import date
    from decimal import Decimal
    cols = ("date", "stock_id", "close", "volume")
    rows = ((date(2026, 6, 30), "2330", Decimal("1000.0"), 12345),
            (date(2026, 6, 30), "2317", Decimal("105.5"), 67890),
            (date(2026, 6, 29), "2330", Decimal("995.0"), 54321))
    return cols, rows


def _fx_snapshot():
    """registry fixture：一概念權威已指定、一概念未指定、一表服務兩概念（真列形）。"""
    concepts = (
        {"concept_key": "tw.daily_bar", "category": "event",
         "authoritative_binding_id": 75, "superseded_at": None},
        {"concept_key": "tw.delisting", "category": "event",
         "authoritative_binding_id": None, "superseded_at": None},
        {"concept_key": "tw.roster_membership", "category": "state",
         "authoritative_binding_id": None, "superseded_at": None},
    )
    tbl_price = "Taiwan" + "StockPrice"          # 運行期串接：本檔原始碼不含連續 vendor 字面
    tbl_delist = "Taiwan" + "StockDelisting"
    bindings = (
        {"binding_id": 75, "concept_key": "tw.daily_bar", "source_table": tbl_price,
         "source_column": None, "channel_role": "observation",
         "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 2, "concept_key": "tw.roster_membership", "source_table": tbl_delist,
         "source_column": None, "channel_role": "observation",
         "mapping_status": "mapped", "superseded_at": None},
        # 單概念、但該概念之權威表徵未指定（＝live 六概念之現況形）
        {"binding_id": 28, "concept_key": "tw.roster_membership",
         "source_table": "Taiwan" + "StockInfo", "source_column": None,
         "channel_role": "observation", "mapping_status": "mapped", "superseded_at": None},
        {"binding_id": 3, "concept_key": "tw.delisting", "source_table": tbl_delist,
         "source_column": None, "channel_role": "observation",
         "mapping_status": "mapped", "superseded_at": None},
    )
    return wc.Registry(concepts, bindings)


def _raised(fn, exc=Exception):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def _selftest() -> int:
    from datetime import date
    from decimal import Decimal
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    cols, rows = _fx_rows()

    # ── 比對核心：等值 / 差一列 / 型別差異 / 欄形 / 未達成三型 ──
    same = compare_rows(cols, rows, cols, rows)
    chk("等值兩路 → green 且 diff=0、列數落帳",
        same.verdict == "green" and same.diff_rows == 0 and same.n_old == same.n_new == 3)
    less = compare_rows(cols, rows, cols, rows[:2])
    chk("新路少一列 → red、diff=1，且差異列被列出（不只給數字）",
        less.verdict == "red" and less.diff_rows == 1 and len(less.examples) == 1
        and less.examples[0][0] == "僅舊路"
        and ("str", "2330") in less.examples[0][1])
    more = compare_rows(cols, rows[:2], cols, rows)
    chk("新路多一列 → red、diff=1 且標記為僅新路",
        more.verdict == "red" and more.diff_rows == 1 and more.examples[0][0] == "僅新路")
    typed = tuple((r[0], r[1], float(r[2]), r[3]) for r in rows)   # Decimal → float
    tcmp = compare_rows(cols, rows, cols, typed)
    chk("型別差異（Decimal→float，值相同）→ red（絞殺要求行為零變更）",
        tcmp.verdict == "red" and tcmp.diff_rows == 6)
    chk("值差異（收盤價差 0.01）→ red",
        compare_rows(cols, rows, cols,
                     ((date(2026, 6, 30), "2330", Decimal("1000.01"), 12345),) + rows[1:]
                     ).verdict == "red")
    chk("列序不同（同一多重集）→ green（SQL 無 ORDER BY 時列序本無保證）",
        compare_rows(cols, rows, cols, tuple(reversed(rows))).verdict == "green")
    chk("重複列數不同 → red（多重集非集合：兩份 vs 一份要抓得到）",
        compare_rows(cols, rows + rows[:1], cols, rows).verdict == "red")
    chk("欄名不同 → red 且 diff_rows=None（欄形不同即整體不可比）",
        compare_rows(cols, rows, ("date", "sid", "close", "volume"), rows) ==
        Comparison("red", 3, 3, None,
                   f"欄形不同：舊 {cols} vs 新 {('date', 'sid', 'close', 'volume')}"
                   "——整體不可比，熔斷。", ()))
    chk("兩路皆空集 → pending（空集恆等，證明不了等價）",
        compare_rows(cols, (), cols, ()).verdict == "pending")
    chk("新舊 SQL 全等 → pending（拿自己比自己，無鑑別力）",
        compare_rows(cols, rows, cols, rows, identical_sql=True).verdict == "pending")
    chk("結果被截斷 → pending（沒讀完不得宣稱等價）",
        compare_rows(cols, rows, cols, rows, truncated=True).verdict == "pending")
    chk("空集 vs 有列 → red（單邊空不是無鑑別力，是真差異）",
        compare_rows(cols, (), cols, rows).verdict == "red")

    # ── 唯讀護欄 ──
    chk("唯讀護欄：SELECT 放行",
        assert_readonly("SELECT 1 FROM feature_values WHERE feature=%s") is None)
    chk("唯讀護欄：UPDATE/DELETE/DROP/多段語句一律拒",
        all(_raised(lambda s=s: assert_readonly(s), ShadowError) for s in (
            "UPDATE feature_values SET v=1", "DELETE FROM feature_values",
            "DROP TABLE feature_values", "SELECT 1; SELECT 2")))
    chk("唯讀護欄：註解行內之寫入字樣不誤判（-- 舊寫法用 update）",
        assert_readonly("-- 舊寫法 update 過\nSELECT 1") is None)

    # ── auto 改寫：解析成功 / 三型 fail-closed / 下游絆線 ──
    snap = _fx_snapshot()
    lookup = make_lookup(snap)
    old_q = ('SELECT date, stock_id, close FROM ' + '"Taiwan' + 'StockPrice"'
             ' WHERE stock_id=%s AND date>=%s')
    new_q, maps = rewrite_sql(old_q, lookup)
    chk("auto 改寫：權威已指定 → 表名替換成權威表、其餘 SQL 逐字不動",
        maps == (("Taiwan" + "StockPrice", '"Taiwan' + 'StockPrice"'),)
        and new_q == old_q)
    chk("下游絆線：改寫後之 SQL 過 M2 閘口徑仍有命中即抓得到（本例權威表＝同表故仍命中）",
        residual_vendor(new_q) != [])
    snap_adj = wc.Registry(
        tuple({**c, "authoritative_binding_id": 81} if c["concept_key"] == "tw.daily_bar" else c
              for c in snap.concepts),
        snap.bindings + ({"binding_id": 81, "concept_key": "tw.daily_bar",
                          "source_table": "wc_price_adj_view", "source_column": None,
                          "channel_role": "derived", "mapping_status": "mapped",
                          "superseded_at": None},))
    new2, maps2 = rewrite_sql(old_q, make_lookup(snap_adj))
    chk("auto 改寫：權威改指另一表 → 新 SQL 跟著變（證明真解析、非樣板替換）",
        maps2[0][1] == '"wc_price_adj_view"' and "wc_price_adj_view" in new2)
    chk("下游絆線：新路不含 vendor 字面時 residual 為空（M2 口徑復用、不自造第二把尺）",
        residual_vendor(new2) == [])
    chk("fail-closed：單概念但權威未指定（live 六概念現況形）→ 拋 UnmappedConcept，不回退字面",
        _raised(lambda: rewrite_sql('SELECT 1 FROM ' + '"Taiwan' + 'StockInfo"' + ' x',
                                    make_lookup(snap)), wc.UnmappedConcept))
    chk("fail-closed：一表服務多概念 → 拋 ShadowError，要求 --map 明示",
        _raised(lambda: make_lookup(snap)("Taiwan" + "StockDelisting"), ShadowError))
    chk("--map 明示概念後仍受權威指定之閘（tw.delisting 權威為 NULL → 仍拋 UnmappedConcept）",
        _raised(lambda: make_lookup(
            snap, {"Taiwan" + "StockDelisting": "tw.delisting"})("Taiwan" + "StockDelisting"),
            wc.UnmappedConcept))
    chk("fail-closed：未登錄之表 → 拋（僅 Observation 地位，不得被消費）",
        _raised(lambda: lookup("SomeUnregisteredTable"), ShadowError))
    chk("fail-closed：欄位級權威表徵 → 拋（表名替換不足以表達，要走 explicit）",
        _raised(lambda: make_lookup(wc.Registry(
            snap.concepts,
            tuple({**b, "source_column": "close"} if b["binding_id"] == 75 else b
                  for b in snap.bindings)))("Taiwan" + "StockPrice"), ShadowError))
    chk("rewrite：SQL 內無 vendor 字面 → 拋（叫錯工具，不靜默回傳原句）",
        _raised(lambda: rewrite_sql("SELECT 1 FROM feature_values", lookup), ShadowError))
    chk("rewrite：JOIN 側之直綁也會被改（不只 FROM）",
        "wc_price_adj_view" in rewrite_sql(
            'SELECT 1 FROM feature_values JOIN ' + '"Taiwan' + 'StockPrice"' + ' p USING (x)',
            make_lookup(snap_adj))[0])

    # ── evidence 報告：差異列必須出現在文字裡（紅列不得只有數字） ──
    rep = format_report(less, old_q, new_q, maps)
    chk("evidence：red 報告含差異列內容與兩路 SQL",
        "僅舊路" in rep and "2026-06-29" in rep and "舊路 SQL" in rep and "新路 SQL" in rep)

    print("自測：全通過 ✓" if ok else "自測：有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="vendor 直綁絞殺之雙讀影子比對（diff=0 才准切；預設 --dry-run 不寫帳本）")
    ap.add_argument("--sql"), ap.add_argument("--sql-file", dest="sql_file")
    ap.add_argument("--old-sql"), ap.add_argument("--old-sql-file", dest="old_sql_file")
    ap.add_argument("--new-sql"), ap.add_argument("--new-sql-file", dest="new_sql_file")
    ap.add_argument("--param", action="append", help="查詢參數（%%s 順序；可重複）")
    ap.add_argument("--map", action="append", metavar="TABLE=CONCEPT_KEY",
                    help="一表多概念時明示（可重複）")
    ap.add_argument("--file", help="被絞殺之檔（帳本鍵；處數由 M2 口徑實掃，不手填）")
    ap.add_argument("--batch", help="批次名（A1-features …）")
    ap.add_argument("--evidence", help="比對輸出落檔路徑（帳本 evidence_ref）")
    ap.add_argument("--max-rows", dest="max_rows", type=int, default=MAX_ROWS_DEFAULT)
    ap.add_argument("--dry-run", action="store_true", help="預設行為：不寫帳本")
    ap.add_argument("--apply", action="store_true", help="把判定追加進帳本（須 --file/--batch）")
    ap.add_argument("--preflight", action="store_true", help="唯讀前置檢查")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    has_sql = any((a.sql, a.sql_file, a.old_sql, a.old_sql_file))
    if not has_sql:
        if not a.preflight:
            print(__doc__.split("執行指令矩陣")[-1].split("------------\n")[-1])
        from augur.core import db
        try:
            with db.connect() as conn:
                return preflight(conn)
        except Exception as e:  # noqa: BLE001 — 無參數須 graceful（#29a）
            print(f"（前置檢查需 DB；現不可達：{e}；--selftest 免 DB 可跑）")
            return 0
    try:
        return run(a)
    except (ShadowError, wc.WorldConceptError) as e:
        print(f"✗ {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

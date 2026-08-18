"""as-of 就緒閘 — 歷史 D 能否收特徵／訓練／出單（anti fake-B3）。

🎯 這支在做什麼（白話）：判斷某個交易日 D 是「庫內當時世界夠不夠」：
  PriceAdj(TAIEX)≥D 且 feature_values 有 D → ready（可訓可出單）；
  有價無特徵 → need_collect（可 build_feature_panel，不是假今天）；
  價 < D → fake_b3（禁止把模型登記成還沒發生的 asof）。
  方向臂訓練鎖＝pick_lock／resolve_lock（未指定 → 價頂＝可更新最新日；≠ COMPLETENESS_ASOF）。
  截面族共用同一張 panel。零 live API。

執行指令矩陣（本檔=library #18；自測免 DB 免 API）:
  python -m augur.core.asof_ready
  python -m augur.core.asof_ready --selftest
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Optional
import json

from augur.core.closed_horizons import H_TRACK

STATUS_READY = "ready"
STATUS_NEED_COLLECT = "need_collect"
STATUS_FAKE_B3 = "fake_b3"
STATUS_NO_PRICE = "no_price"

A_FAMILIES = (
    "RankRidge",
    "RankGBDT",
    "RankXGB",
    "RankCat",
    "RankRF",
    "RankKNN",
    "RankMLP",
    "RankSVM",
)

# 方向臂（⊥ 邊界 A；RETRAIN-ALL 包）。數 model_id，不是 family。
DAILY_IDS = ("DailyLogit", "DailyGBDT", "DailyGBDT_cal")
MKT_IDS = ("MktLogit", "MktLogit_v2")
STACK_IDS = ("DirStackM",)
NEED_A_CELLS = len(A_FAMILIES) * len(H_TRACK)
NEED_DAILY = len(DAILY_IDS)
NEED_MKT = len(MKT_IDS)
NEED_STACK = len(STACK_IDS)

# 其他模型軌（≠ RETRAIN-ALL）。--track other --apply＝fail-loud 不開訓；
# --track other --dry-plan＝V0／族矩陣盤點（verify_asof_families，零寫庫）。
NF_PAUSE_0812 = (
    "ArimaUnivariate",
    "VarSmall",
    "KalmanLocalLevel",
    "CointPairEG",
    "GarchMeanDir",
    "GcnSmall",
)
V2_NAMED_GO = ("VECM", "TCN", "NB", "RL")
SEQ_EVAL_ONLY = ("SeqLSTM",)

RC_READY = 0
RC_NEED_COLLECT = 2
RC_FAKE_B3 = 3
RC_NO_PRICE = 4
RC_OTHER_LANE = 6

# 完整性定案錨（憲章歷史判準）。方向臂訓練鎖 ≠ 此常數，見 pick_lock／resolve_lock。
COMPLETENESS_ASOF = date(2026, 5, 31)

_STATUS_RC = {
    STATUS_READY: RC_READY,
    STATUS_NEED_COLLECT: RC_NEED_COLLECT,
    STATUS_FAKE_B3: RC_FAKE_B3,
    STATUS_NO_PRICE: RC_NO_PRICE,
}


def as_date(v: Any) -> Optional[date]:
    """CLI／DB 值 → date；空／非 ISO → None。純函式。"""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()[:10]
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def date_arg_error(v: Any) -> Optional[str]:
    """非 YYYY-MM-DD／佔位符 D → 錯誤字；合法或空 → None。"""
    if v is None or str(v).strip() == "":
        return None
    if as_date(v) is not None:
        return None
    raw = str(v).strip()
    if raw in ("D", "d", "<D>", "YYYY-MM-DD"):
        return (
            "✗ --date 須 YYYY-MM-DD（D 是佔位符，例如 "
            "2026-08-07；價頂：python scripts/check_asof_ready.py --latest-date）"
        )
    return f"✗ --date 須 YYYY-MM-DD（收到 {raw!r}）"


def classify_asof(d: Any, price_max: Any, fv_rows: int) -> str:
    """純函式：D × 價頂 × 該日特徵列數 → 狀態字。"""
    dd = as_date(d)
    pm = as_date(price_max)
    n = int(fv_rows or 0)
    if dd is None:
        return STATUS_NO_PRICE
    if pm is None:
        return STATUS_NO_PRICE
    if dd > pm:
        return STATUS_FAKE_B3
    if n <= 0:
        return STATUS_NEED_COLLECT
    return STATUS_READY


def rc_of(status: str) -> int:
    return _STATUS_RC.get(status, 1)


def pack_is_complete(
    *,
    a_cells: int,
    daily: int,
    mkt: int,
    stack: int,
    asof: Any,
    price_max: Any,
) -> bool:
    """截面 8×8 已齊才算包；方向臂只在 D＝價頂列入（單一 model_id，歷史 D 不得要求）。"""
    if int(a_cells or 0) < NEED_A_CELLS:
        return False
    dd, pm = as_date(asof), as_date(price_max)
    if dd is None or pm is None or dd != pm:
        return True
    return (
        int(daily or 0) >= NEED_DAILY
        and int(mkt or 0) >= NEED_MKT
        and int(stack or 0) >= NEED_STACK
    )


def other_lane_policy() -> dict:
    """其他模型怎麼走歷史 as-of（純函式；不開訓）。"""
    return {
        "shared_panel": list(A_FAMILIES),
        "direction_at_tip": list(DAILY_IDS + MKT_IDS + STACK_IDS),
        "nf_pause_0812": list(NF_PAUSE_0812),
        "named_go": list(V2_NAMED_GO),
        "eval_only": list(SEQ_EVAL_ONLY),
    }


def other_lane_oneline() -> str:
    """探針／殼一行：誰能共用 panel、誰禁、誰須點名。"""
    return (
        "截面8族共用 feature_values＠D（--track A|all 訓；other --dry-plan＝V0/V1 盤點）；"
        "Daily*/Mkt/DirStackM＝價頂鎖；"
        "0812 NF 六族禁同尺重掃；"
        "VECM/TCN/NB/RL 須點名 GO；"
        "SeqLSTM 評測不寫庫；"
        "--track other --apply＝rc=6 不開訓"
    )


def other_lane_refuse_msg() -> str:
    """--track other --apply 的 fail-loud 全文。"""
    p = other_lane_policy()
    return (
        "其他模型不走本殼開訓（--track other --apply＝說明＋退出，rc=6）。\n"
        "  盤點／已實現窗 rank IC：--dry-plan --track other 或 "
        "python scripts/verify_asof_families.py --date 2026-08-07 --ic --oos\n"
        f"  共用 panel＠D：{', '.join(p['shared_panel'])} → --track A 或 all 才訓\n"
        "  方向臂：只在價頂動；歷史 D 預設 --skip-daily --skip-mkt --skip-stack\n"
        f"  0812 NF 禁重掃：{', '.join(p['nf_pause_0812'])}\n"
        f"  殘格須點名 GO：{', '.join(p['named_go'])}（缺 adapter／額外張量，不是同一張 feature_values）\n"
        f"  評測不寫庫：{', '.join(p['eval_only'])}\n"
    )


def label_n_needed(h: int) -> int:
    """t+1 進場後要湊齊 label：日曆上 panel 之後至少 h+1 個交易日（exit=cal[h]）。"""
    return int(h) + 1


def label_is_realized(n_trading_days_after: int, h: int) -> bool:
    """純函式：panel 之後已有幾個交易日 × 窗 → 標籤是否已實現（#8 不外推）。"""
    return int(n_trading_days_after or 0) >= label_n_needed(h)


def realized_horizons(n_trading_days_after: int, horizons=H_TRACK) -> tuple[int, ...]:
    """已實現的 H 窗（升序）。"""
    n = int(n_trading_days_after or 0)
    return tuple(h for h in horizons if label_is_realized(n, h))


def n_trading_days_after(calendar, panel_date, until) -> int:
    """日曆上 panel 之後、until 以前（含）的交易日數。純函式。"""
    p, u = as_date(panel_date), as_date(until)
    if p is None or u is None:
        return 0
    return sum(1 for d in calendar if p < as_date(d) <= u)


def stamp_kind(model_asof: Any, panel_asof: Any) -> str:
    """模型 stamp vs 評測 panel：oos / same_day / future / unknown。"""
    ma, pa = as_date(model_asof), as_date(panel_asof)
    if ma is None or pa is None:
        return "unknown"
    if ma > pa:
        return "future"
    if ma == pa:
        return "same_day"
    return "oos"


def format_family_matrix(present: Mapping[tuple[str, int], Any], *, families=A_FAMILIES, horizons=H_TRACK) -> str:
    """8×8 有無格 → 固定寬表（純函式；值 truthy＝有）。"""
    hs = tuple(horizons)
    fams = tuple(families)
    head = f"{'family':<10}" + "".join(f"{'H' + str(h):<6}" for h in hs)
    lines = [head, "-" * len(head)]
    for fam in fams:
        bits = []
        for h in hs:
            mark = "✓" if present.get((fam, int(h))) else "."
            bits.append(f"{mark:<6}")
        lines.append(f"{fam:<10}" + "".join(bits))
    return "\n".join(lines)


def a_cell_gap(n_cells: int) -> int:
    """截面 8×8 還缺幾格（≥0）。"""
    g = NEED_A_CELLS - int(n_cells or 0)
    return g if g > 0 else 0


def format_incomplete_scan(rows: list) -> str:
    """未齊歷史日表（純函式）。row keys: asof, a_cells, has_core, realized_h（可省）。"""
    head = f"{'asof':<12}{'A格':<8}{'缺':<6}{'core':<8}realized_H"
    lines = [head, "-" * len(head)]
    for r in rows:
        hs = r.get("realized_h")
        hs_s = ",".join(str(x) for x in hs) if hs else "—"
        core = "Y" if r.get("has_core") else "N"
        n = int(r.get("a_cells") or 0)
        lines.append(
            f"{str(r.get('asof')):<12}{n:<8}{a_cell_gap(n):<6}{core:<8}{hs_s}"
        )
    if len(rows) == 0:
        lines.append("(無未齊日)")
    return "\n".join(lines)


def snapshot(cur, d: Any) -> dict:
    """唯讀 DB：D 的價／特徵／核心／邊界 A＋方向臂 registry。cur 須已開。"""
    dd = as_date(d)
    if dd is None:
        raise ValueError(date_arg_error(d) or "as-of 日空")
    price_max = taiex_price_max(cur)
    cur.execute(
        "SELECT count(distinct feature), count(*) FROM feature_values WHERE panel_date=%s",
        (dd,),
    )
    nfeat, nrows = cur.fetchone()
    cur.execute(
        "SELECT 1 FROM core_universe_asof WHERE as_of_date=%s LIMIT 1",
        (dd,),
    )
    has_core = bool(cur.fetchone())
    iso = dd.isoformat()
    cur.execute(
        """
        SELECT count(*) FROM model_registry
        WHERE asof_snapshot::text = %s
          AND family = ANY(%s)
        """,
        (iso, list(A_FAMILIES)),
    )
    registry_a = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT count(DISTINCT family || ':' || horizon::text)
          FROM model_registry
         WHERE family = ANY(%s)
           AND horizon = ANY(%s)
           AND asof_snapshot::text = %s
        """,
        (list(A_FAMILIES), list(H_TRACK), iso),
    )
    registry_a_cells = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(DAILY_IDS), iso),
    )
    registry_daily = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(MKT_IDS), iso),
    )
    registry_mkt = int(cur.fetchone()[0] or 0)
    cur.execute(
        """
        SELECT count(DISTINCT model_id) FROM model_registry
         WHERE model_id = ANY(%s) AND asof_snapshot::text = %s
        """,
        (list(STACK_IDS), iso),
    )
    registry_stack = int(cur.fetchone()[0] or 0)
    cur.execute("SELECT max(panel_date) FROM feature_values")
    fv_max = cur.fetchone()[0]
    st = classify_asof(dd, price_max, int(nrows or 0))
    price_max_s = None if price_max is None else str(price_max)[:10]
    at_tip = price_max_s == iso
    pack_complete = pack_is_complete(
        a_cells=registry_a_cells,
        daily=registry_daily,
        mkt=registry_mkt,
        stack=registry_stack,
        asof=dd,
        price_max=price_max,
    )
    return {
        "asof": iso,
        "status": st,
        "rc": rc_of(st),
        "price_max": price_max_s,
        "fv_max": None if fv_max is None else str(fv_max)[:10],
        "fv_nfeat": int(nfeat or 0),
        "fv_nrows": int(nrows or 0),
        "has_core": has_core,
        "registry_a": registry_a,
        "registry_a_cells": registry_a_cells,
        "registry_daily": registry_daily,
        "registry_mkt": registry_mkt,
        "registry_stack": registry_stack,
        "need_a_cells": NEED_A_CELLS,
        "at_tip": at_tip,
        "pack_complete": pack_complete,
    }


def family_cells(cur, d: Any) -> dict[tuple[str, int], dict]:
    """DB：asof_snapshot＝D 的截面 8×8（每格最新一列）。缺格不出現。"""
    dd = as_date(d)
    if dd is None:
        return {}
    iso = dd.isoformat()
    cur.execute(
        """
        SELECT DISTINCT ON (family, horizon)
               family, horizon, model_id, metrics
          FROM model_registry
         WHERE family = ANY(%s)
           AND horizon = ANY(%s)
           AND asof_snapshot::text = %s
         ORDER BY family, horizon, created_at DESC
        """,
        (list(A_FAMILIES), list(H_TRACK), iso),
    )
    out: dict[tuple[str, int], dict] = {}
    for fam, h, mid, metrics in cur.fetchall():
        met = metrics
        if isinstance(met, str):
            try:
                met = json.loads(met) or {}
            except Exception:
                met = {}
        if not isinstance(met, dict):
            met = {}
        out[(str(fam), int(h))] = {
            "model_id": mid,
            "n_train_rows": met.get("n_train_rows"),
        }
    return out


def other_lane_registry(cur) -> dict[str, dict]:
    """DB：NF／殘格／Seq 是否已登錄（任何 asof）。空＝尚未開訓，屬預期。"""
    names = list(NF_PAUSE_0812) + list(V2_NAMED_GO) + list(SEQ_EVAL_ONLY)
    cur.execute(
        """
        SELECT family, count(*), max(asof_snapshot::text)
          FROM model_registry
         WHERE family = ANY(%s)
         GROUP BY 1
        """,
        (names,),
    )
    found = {
        str(fam): {"n": int(n), "max_asof": mx}
        for fam, n, mx in cur.fetchall()
    }
    return {name: found.get(name, {"n": 0, "max_asof": None}) for name in names}


def scan_incomplete_asof(cur, *, since: Any = None, limit: int = 40) -> list[dict]:
    """DB：有 feature_values、截面 <8×8、且 D≤價頂 的歷史日（新→舊）。"""
    price_max = taiex_price_max(cur)
    if price_max is None:
        return []
    since_d = as_date(since) or date(2026, 5, 1)
    cur.execute(
        """
        WITH panels AS (
          SELECT DISTINCT panel_date AS d
            FROM feature_values
           WHERE panel_date >= %s AND panel_date <= %s
        ),
        cells AS (
          SELECT asof_snapshot::text AS asof,
                 count(DISTINCT family || ':' || horizon::text) AS n
            FROM model_registry
           WHERE family = ANY(%s) AND horizon = ANY(%s)
           GROUP BY 1
        )
        SELECT p.d::text,
               coalesce(c.n, 0),
               EXISTS (
                 SELECT 1 FROM core_universe_asof u WHERE u.as_of_date = p.d
               )
          FROM panels p
          LEFT JOIN cells c ON c.asof = p.d::text
         WHERE coalesce(c.n, 0) < %s
         ORDER BY p.d DESC
         LIMIT %s
        """,
        (
            since_d,
            price_max,
            list(A_FAMILIES),
            list(H_TRACK),
            NEED_A_CELLS,
            int(limit),
        ),
    )
    out = []
    for iso, n, has_core in cur.fetchall():
        out.append({
            "asof": iso,
            "a_cells": int(n or 0),
            "has_core": bool(has_core),
            "gap": a_cell_gap(int(n or 0)),
            "price_max": price_max.isoformat(),
        })
    return out


def scan_complete_asof(cur, *, limit: int = 12) -> list[dict]:
    """DB：截面已 64 格的 asof（新→舊）。"""
    cur.execute(
        """
        SELECT asof_snapshot::text,
               count(DISTINCT family || ':' || horizon::text)
          FROM model_registry
         WHERE family = ANY(%s) AND horizon = ANY(%s)
         GROUP BY 1
        HAVING count(DISTINCT family || ':' || horizon::text) >= %s
         ORDER BY 1 DESC
         LIMIT %s
        """,
        (list(A_FAMILIES), list(H_TRACK), NEED_A_CELLS, int(limit)),
    )
    return [{"asof": iso, "a_cells": int(n)} for iso, n in cur.fetchall()]


def scan_realized_panels(
    cur,
    calendar,
    *,
    need_h: int = 5,
    limit: int = 12,
) -> list[dict]:
    """DB：D≤價頂、有 panel、標籤窗 need_h 已實現的歷史日（新→舊）。不要求 8×8 已齊。"""
    tip = taiex_price_max(cur)
    if tip is None:
        return []
    cur.execute(
        """
        SELECT DISTINCT panel_date
          FROM feature_values
         WHERE panel_date <= %s
         ORDER BY 1 DESC
         LIMIT 80
        """,
        (tip,),
    )
    out: list[dict] = []
    for (d,) in cur.fetchall():
        n = n_trading_days_after(calendar, d, tip)
        hs = realized_horizons(n)
        if int(need_h) not in hs:
            continue
        iso = as_date(d).isoformat()
        out.append({
            "asof": iso,
            "n_after": n,
            "realized_h": hs,
            "price_max": tip.isoformat(),
        })
        if len(out) >= int(limit):
            break
    return out


def assert_not_fake_b3(price_max: Any, asof: Any) -> Optional[str]:
    """價 < asof → 錯誤字；否則 None。純函式。"""
    st = classify_asof(asof, price_max, 1)
    if st == STATUS_FAKE_B3:
        return (
            f"假 B3：PriceAdj TAIEX max({as_date(price_max)}) < asof({as_date(asof)})"
        )
    if st == STATUS_NO_PRICE:
        return "假 B3：TaiwanStockPriceAdj 無 TAIEX 價"
    return None


ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36；不直綁還原價表字面


def taiex_price_max(cur) -> Optional[date]:
    """DB：TAIEX 還原價頂（經 tw.daily_bar_adjusted）。"""
    from augur.catalog import world_concept
    adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=cur.connection)
    cur.execute(f"SELECT max(date) FROM {adj} WHERE stock_id=%s", ("TAIEX",))
    return as_date(cur.fetchone()[0])


def refuse_if_fake_b3(cur, asof: Any) -> Optional[str]:
    """讀價頂後走 assert_not_fake_b3。訓練／特徵 until 共用。"""
    return assert_not_fake_b3(taiex_price_max(cur), asof)


def pick_lock(asof: Any, price_max: Any) -> tuple[Optional[date], Optional[str]]:
    """方向臂訓練鎖（純函式）：未指定 → 價頂（可更新最新日）；指定則不得超過價頂。"""
    pm = as_date(price_max)
    if pm is None:
        return None, "假 B3：TaiwanStockPriceAdj 無 TAIEX 價"
    if asof is None or asof == "":
        return pm, None
    err = assert_not_fake_b3(pm, asof)
    if err:
        return None, err
    return as_date(asof), None


def latest_legal(cur) -> Optional[date]:
    """可更新最新日＝TAIEX PriceAdj 價頂。不是日曆今天。"""
    return taiex_price_max(cur)


def resolve_lock(cur, asof: Any = None) -> tuple[Optional[date], Optional[str]]:
    """DB：方向臂 as-of／until。未指定 → 價頂。"""
    return pick_lock(asof, taiex_price_max(cur))


def bind_iso(cur, asof: Any = None) -> tuple[Optional[str], Optional[str]]:
    """resolve_lock → (ISO 日, None) 或 (None, 錯字)。"""
    d, err = resolve_lock(cur, asof)
    if err:
        return None, err
    return d.isoformat(), None


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    d = date(2026, 8, 7)
    chk("as_date ISO", as_date("2026-08-07") == d)
    chk("as_date date", as_date(d) == d)
    chk("as_date 佔位符 D→None", as_date("D") is None)
    chk("date_arg_error 佔位符", "佔位符" in (date_arg_error("D") or ""))
    chk("date_arg_error 合法→None", date_arg_error("2026-08-07") is None)
    chk("ready", classify_asof(d, date(2026, 8, 12), 10) == STATUS_READY)
    chk(
        "need_collect",
        classify_asof(d, date(2026, 8, 12), 0) == STATUS_NEED_COLLECT,
    )
    chk(
        "fake_b3 今天無價",
        classify_asof(date(2026, 8, 13), date(2026, 8, 12), 99) == STATUS_FAKE_B3,
    )
    chk("no_price", classify_asof(d, None, 10) == STATUS_NO_PRICE)
    chk("rc fake=3", rc_of(STATUS_FAKE_B3) == 3)
    chk("rc collect=2", rc_of(STATUS_NEED_COLLECT) == 2)
    chk(
        "assert fake 有字",
        assert_not_fake_b3("2026-08-12", "2026-08-13") is not None,
    )
    chk(
        "assert 歷史 D 過",
        assert_not_fake_b3("2026-08-12", "2026-08-07") is None,
    )
    chk("A 包 8 族", len(A_FAMILIES) == 8)
    chk("H_TRACK 8 窗", len(H_TRACK) == 8 and NEED_A_CELLS == 64)
    chk("方向臂 id 數", NEED_DAILY == 3 and NEED_MKT == 2 and NEED_STACK == 1)
    chk(
        "hist D 不要求方向臂",
        pack_is_complete(
            a_cells=64, daily=0, mkt=0, stack=0,
            asof="2026-07-31", price_max="2026-08-14",
        ),
    )
    chk(
        "hist D 截面未齊",
        not pack_is_complete(
            a_cells=4, daily=3, mkt=2, stack=1,
            asof="2026-07-31", price_max="2026-08-14",
        ),
    )
    chk(
        "價頂缺方向臂未齊",
        not pack_is_complete(
            a_cells=64, daily=0, mkt=0, stack=0,
            asof="2026-08-14", price_max="2026-08-14",
        ),
    )
    chk(
        "價頂全包",
        pack_is_complete(
            a_cells=64, daily=3, mkt=2, stack=1,
            asof="2026-08-14", price_max="2026-08-14",
        ),
    )
    pol = other_lane_policy()
    chk("其他軌截面 8 族", len(pol["shared_panel"]) == 8)
    chk("0812 NF 六族", len(pol["nf_pause_0812"]) == 6)
    chk("殘格四點名", pol["named_go"] == ["VECM", "TCN", "NB", "RL"])
    chk("other rc=6", RC_OTHER_LANE == 6)
    chk("other 一行含禁重掃", "禁同尺重掃" in other_lane_oneline())
    chk("other refuse 含 VECM", "VECM" in other_lane_refuse_msg())
    chk("H5 需 6 個交易日", label_n_needed(5) == 6)
    chk("5 日不夠 H5", not label_is_realized(5, 5))
    chk("6 日夠 H5", label_is_realized(6, 5))
    chk("11 日實現 H5+H10", realized_horizons(11) == (5, 10))
    chk("0 日無實現窗", realized_horizons(0) == ())
    cal = [date(2026, 8, d) for d in (3, 4, 5, 6, 7, 10, 11, 12, 13, 14)]
    chk("n_after 08-07→08-14=5", n_trading_days_after(cal, "2026-08-07", "2026-08-14") == 5)
    chk("stamp oos", stamp_kind("2026-07-31", "2026-08-07") == "oos")
    chk("stamp same_day", stamp_kind("2026-08-07", "2026-08-07") == "same_day")
    chk("stamp future", stamp_kind("2026-08-14", "2026-08-07") == "future")
    mx = format_family_matrix({("RankRidge", 5): {"model_id": "x"}, ("RankGBDT", 5): True})
    chk("matrix 含族名", "RankRidge" in mx and "RankSVM" in mx)
    chk("matrix 缺格點", "." in mx)
    chk("matrix 有格勾", "✓" in mx)
    chk("缺 12 格→gap 52", a_cell_gap(12) == 52)
    chk("齊包 gap 0", a_cell_gap(64) == 0)
    sc = format_incomplete_scan([
        {"asof": "2026-08-07", "a_cells": 12, "has_core": True, "realized_h": (5,)},
    ])
    chk("scan 表含 08-07", "2026-08-07" in sc and "12" in sc)
    d, e = pick_lock(None, date(2026, 8, 12))
    chk("未指定鎖價頂", d == date(2026, 8, 12) and e is None)
    d, e = pick_lock("2026-08-07", "2026-08-12")
    chk("指定歷史 D", d == date(2026, 8, 7) and e is None)
    d, e = pick_lock("2026-08-13", "2026-08-12")
    chk("指定假 B3", d is None and e is not None)
    d, e = pick_lock(None, None)
    chk("無價拒鎖", d is None and e is not None)
    chk("完整性錨≠訓練鎖", COMPLETENESS_ASOF == date(2026, 5, 31))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測: python -m augur.core.asof_ready --selftest；免 DB 免 API)")

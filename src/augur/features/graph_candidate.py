"""圖旁路特徵候選（GRAPH-G3 path=A）— 邊聚合 → feature_candidate_values。

🎯 這支在做什麼（白話）：把 G2 `stock_graph_edge`（S-EQ）聚合成每股扁平候選，
寫進 staging 表，供日後提拔閘複核。**不**進生產 `feature_values`、**不**掛
RankRidge／B3 熱路徑、**不**開訓 GNN。

契約名（≤3）：
  graph_ind_deg_xsec       — industry_same 無向度 → panel 橫斷面 percentile
  graph_corr60_wdeg_xsec   — return_corr_60d 無向 |w| 合計 → percentile
  graph_corr60_meanw_xsec  — return_corr_60d 無向 |w| 均值 → percentile

S-EQ：panel_date 必須等於圖 as_of；缺圖 → 整 panel SKIP（不填舊圖）。
邊表為單向列 → 兩端皆計入（無向）。零鄰居＝可計算 → 寫 0 再做 xsec（#1 不發明假邊）。

守 #1 · #8（S-EQ／anti-leakage）· 母原則③（xsec 相對化）· NF-pause。

執行指令矩陣（library #18）：
  python -m augur.features.graph_candidate
  python -m augur.features.graph_candidate --selftest
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Iterable, Sequence

from psycopg2.extras import execute_values

from augur.audit import feature_candidate as cand
from augur.core import db
from augur.features.graph_consume import (
    DECLARED_EDGE_TYPES,
    GraphAsofMissing,
    GraphConsumeError,
    GraphEdgeBatch,
    load_edges,
    load_edges_seq,
)

NAMES = (
    "graph_ind_deg_xsec",
    "graph_corr60_wdeg_xsec",
    "graph_corr60_meanw_xsec",
)

_ET_IND = "industry_same"
_ET_C60 = "return_corr_60d"


def _as_date(d) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d)[:10])


def _xsec_pctile(raw: dict[str, float]) -> dict[str, float]:
    """同 panel 橫斷面 percentile ∈[0,1]；n<2 → 空（無法相對化）。"""
    if len(raw) < 2:
        return {}
    items = sorted(raw.items(), key=lambda kv: kv[1])
    n = len(items)
    out: dict[str, float] = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and items[j + 1][1] == items[i][1]:
            j += 1
        # average rank of tie group, scaled to [0,1]
        avg_rank = 0.5 * (i + j)
        pct = avg_rank / (n - 1) if n > 1 else 0.0
        for k in range(i, j + 1):
            out[items[k][0]] = float(pct)
        i = j + 1
    return out


def aggregate_raw(batch: GraphEdgeBatch, stocks: Sequence[str]) -> dict[str, dict[str, float]]:
    """從邊批無向聚合 raw → {name_without_xsec_tag logic keys}.

    回傳三個 raw dict（僅 stocks 鍵；缺邊股＝0）：
      ind_deg, corr60_wdeg, corr60_meanw
    """
    want = {str(s) for s in stocks}
    ind_deg: dict[str, float] = defaultdict(float)
    c60_wsum: dict[str, float] = defaultdict(float)
    c60_n: dict[str, float] = defaultdict(float)

    for src, tgt, w, et, _ in batch.edges:
        aw = abs(float(w))
        for node in (str(src), str(tgt)):
            if node not in want:
                continue
            if et == _ET_IND:
                ind_deg[node] += 1.0
            elif et == _ET_C60:
                c60_wsum[node] += aw
                c60_n[node] += 1.0

    raw_ind = {s: float(ind_deg.get(s, 0.0)) for s in want}
    raw_wdeg = {s: float(c60_wsum.get(s, 0.0)) for s in want}
    raw_mean = {
        s: (float(c60_wsum[s] / c60_n[s]) if c60_n.get(s, 0.0) > 0 else 0.0) for s in want
    }
    return {
        "graph_ind_deg_xsec": raw_ind,
        "graph_corr60_wdeg_xsec": raw_wdeg,
        "graph_corr60_meanw_xsec": raw_mean,
    }


def to_xsec_candidates(raw_by_name: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """raw → xsec percentile 候選值（名＝NAMES）。"""
    return {name: _xsec_pctile(raw_by_name[name]) for name in NAMES}


def compute_from_batch(
    batch: GraphEdgeBatch, stocks: Sequence[str]
) -> list[tuple[date, str, str, float]]:
    """純函式：邊批＋宇宙 → 候選列 (panel_date, stock_id, feature, value)。"""
    raw = aggregate_raw(batch, stocks)
    xsec = to_xsec_candidates(raw)
    pd_ = batch.graph_asof
    rows: list[tuple[date, str, str, float]] = []
    for name in NAMES:
        for sid, val in xsec[name].items():
            if not (val == val):  # NaN guard
                continue
            rows.append((pd_, sid, name, float(val)))
    return rows


def compute_graph_candidates(
    conn,
    panel_dates: Iterable,
    *,
    progress=None,
    skip_missing: bool = True,
) -> tuple[int, list[str]]:
    """對 panel_dates S-EQ 讀圖→寫 feature_candidate_values。

    回 (寫入列數, SKIP 理由列表)。skip_missing=True 時缺圖 panel 記入 SKIP、不 raise。
    """
    cand.ensure_candidate_table(conn)
    written = 0
    skips: list[str] = []
    panels = [_as_date(p) for p in panel_dates]
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s ORDER BY stock_id",
                (pd_,),
            )
            stocks = [str(r[0]) for r in cur.fetchall()]
            if not stocks:
                cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
                stocks = [str(r[0]) for r in cur.fetchall()]
        try:
            batch = load_edges(conn, pd_)
        except GraphAsofMissing as e:
            msg = f"{pd_}: {e.code}"
            skips.append(msg)
            if progress:
                progress(f"SKIP {msg}")
            if not skip_missing:
                raise
            continue
        except GraphConsumeError as e:
            msg = f"{pd_}: {getattr(e, 'code', 'graph_consume_error')}"
            skips.append(msg)
            if progress:
                progress(f"SKIP {msg}")
            if not skip_missing:
                raise
            continue

        rows = compute_from_batch(batch, stocks)
        if not rows:
            skips.append(f"{pd_}: empty_xsec")
            if progress:
                progress(f"SKIP {pd_}: empty_xsec")
            continue

        with db.transaction(conn) as cur:
            cur.execute(
                f"DELETE FROM {cand.FEATURE_TABLE} WHERE panel_date=%s AND feature = ANY(%s)",
                (pd_, list(NAMES)),
            )
            execute_values(
                cur,
                f"INSERT INTO {cand.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s",
                rows,
            )
        written += len(rows)
        if progress:
            progress(f"OK {pd_}: edges={batch.n} rows={len(rows)} stocks={len(stocks)}")
    return written, skips


def _selftest() -> bool:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("✓" if cond else "✗"), name)
        return cond

    d = date(2026, 8, 5)
    # undirected: A-B industry; A-C corr60; only one direction in table
    rows = [
        ("2330", "2454", 1.0, _ET_IND, d),
        ("2330", "2303", 0.8, _ET_C60, d),
        ("2317", "2303", 0.4, _ET_C60, d),
    ]
    batch = load_edges_seq(d, rows)
    stocks = ["2330", "2454", "2303", "2317", "9999"]
    raw = aggregate_raw(batch, stocks)
    chk("ind deg undirected 2330/2454", raw["graph_ind_deg_xsec"]["2330"] == 1.0
        and raw["graph_ind_deg_xsec"]["2454"] == 1.0)
    chk("isolated ind=0", raw["graph_ind_deg_xsec"]["9999"] == 0.0)
    chk("corr60 wdeg 2303=1.2", abs(raw["graph_corr60_wdeg_xsec"]["2303"] - 1.2) < 1e-9)
    chk("corr60 mean 2330=0.8", abs(raw["graph_corr60_meanw_xsec"]["2330"] - 0.8) < 1e-9)

    x = to_xsec_candidates(raw)
    chk("xsec keys", set(x) == set(NAMES))
    chk("xsec in [0,1]", all(0.0 <= v <= 1.0 for m in x.values() for v in m.values()))
    # highest wdeg (2303=1.2) should be top percentile
    chk("2303 top wdeg xsec", x["graph_corr60_wdeg_xsec"]["2303"] == 1.0)

    out_rows = compute_from_batch(batch, stocks)
    chk("row count = names * stocks", len(out_rows) == len(NAMES) * len(stocks))
    chk("panel_date = graph asof", all(r[0] == d for r in out_rows))
    chk("declared edge types still lock", _ET_IND in DECLARED_EDGE_TYPES
        and _ET_C60 in DECLARED_EDGE_TYPES)

    # leakage / missing still owned by consume
    try:
        load_edges_seq(date(2026, 8, 6), rows)
        chk("missing still raises", False)
    except GraphAsofMissing:
        chk("missing still raises", True)

    return ok


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print(f"NAMES={NAMES}")
        raise SystemExit(0)
    if sys.argv[1] == "--selftest":
        raise SystemExit(0 if _selftest() else 1)
    print("未知參數；見 --help")
    raise SystemExit(2)

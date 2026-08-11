"""股圖邊消費 stub（GRAPH-CONSUME G2）— S-EQ asof 契約鎖；零訓練、不進 B3。

🎯 這支在做什麼（白話）：給一個讀者 as-of 日 D，**只**讀 `stock_graph_edge` 上
`as_of_date = D`（策略 **S-EQ**）的邊；禁止硬編碼 06-30、禁止默用 MAX、禁止讀
`as_of_date > D`。邊型只允許庫內實名：`industry_same`／`return_corr_60d`／
`return_corr_120d`。回邊列供未來 GNN／圖特徵 adapter 使用——**本 stub 不訓練、
不寫庫、不掛 RankRidge／B3**。

失敗字句（契約）：
  graph_asof_missing — S-EQ 下該 D 無邊列
  graph_edge_empty   — 有列但過濾後為空
  graph_type_undeclared — 請求未聲明邊型
  graph_leakage_suspect — 讀到 as_of_date > D（硬 FAIL）

守 #8（anti-leakage）· plan GRAPH-CONSUME §3 · NF-pause（≠ NF-E train）。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.features.graph_consume              # 印用途＋公開入口（唯讀）
  python -m augur.features.graph_consume --selftest   # 純紅綠自測（零 IO）
  python -m augur.features.graph_consume --probe-asof 2026-08-05  # 可選：連 DB 煙測 S-EQ（唯讀）
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Sequence

TABLE = "stock_graph_edge"
STRATEGY = "S-EQ"
DECLARED_EDGE_TYPES = frozenset(
    {"industry_same", "return_corr_60d", "return_corr_120d"}
)


class GraphConsumeError(Exception):
    """圖消費契約失敗基底。"""

    code = "graph_consume_error"


class GraphAsofMissing(GraphConsumeError):
    code = "graph_asof_missing"


class GraphEdgeEmpty(GraphConsumeError):
    code = "graph_edge_empty"


class GraphTypeUndeclared(GraphConsumeError):
    code = "graph_type_undeclared"


class GraphLeakageSuspect(GraphConsumeError):
    code = "graph_leakage_suspect"


def _as_date(d) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d))


def resolve_graph_asof(reader_asof, *, strategy: str = STRATEGY) -> date:
    """依策略解析圖快照日。目前僅實作 S-EQ（圖 asof ≡ 讀者 D）。"""
    d = _as_date(reader_asof)
    if strategy != "S-EQ":
        raise ValueError(f"unsupported strategy {strategy!r}; G2 stub only ships S-EQ")
    return d


def _normalize_types(edge_types: Sequence[str] | None) -> tuple[str, ...]:
    if edge_types is None:
        return tuple(sorted(DECLARED_EDGE_TYPES))
    unknown = [t for t in edge_types if t not in DECLARED_EDGE_TYPES]
    if unknown:
        raise GraphTypeUndeclared(
            f"graph_type_undeclared: {unknown}; declared={sorted(DECLARED_EDGE_TYPES)}"
        )
    return tuple(edge_types)


@dataclass(frozen=True)
class GraphEdgeBatch:
    """一次 S-EQ 讀取結果（唯讀）。"""

    reader_asof: date
    graph_asof: date
    strategy: str
    edge_types: tuple[str, ...]
    edges: tuple[tuple, ...]  # (src, tgt, weight, edge_type, as_of_date)

    @property
    def n(self) -> int:
        return len(self.edges)


def load_edges_seq(
    reader_asof,
    rows: Iterable[tuple],
    *,
    edge_types: Sequence[str] | None = None,
    strategy: str = STRATEGY,
) -> GraphEdgeBatch:
    """純函式消費路徑（零 DB）：rows＝(src, tgt, weight, edge_type, as_of_date)。

    供 selftest／未來 adapter 餵合成列；契約與 DB 薄殼相同。
    """
    d = resolve_graph_asof(reader_asof, strategy=strategy)
    types = _normalize_types(edge_types)
    type_set = set(types)
    kept: list[tuple] = []
    saw_exact = False
    for src, tgt, w, et, aod in rows:
        a = _as_date(aod)
        if a > d:
            raise GraphLeakageSuspect(
                f"graph_leakage_suspect: as_of_date {a} > reader D {d}"
            )
        if a == d:
            saw_exact = True
            if et in type_set:
                kept.append((str(src), str(tgt), float(w), str(et), a))
    if not saw_exact:
        raise GraphAsofMissing(f"graph_asof_missing: no edges with as_of_date={d} (S-EQ)")
    if not kept:
        raise GraphEdgeEmpty(f"graph_edge_empty: as_of_date={d} but no declared types {types}")
    return GraphEdgeBatch(
        reader_asof=d, graph_asof=d, strategy=strategy, edge_types=types, edges=tuple(kept)
    )


def load_edges(conn, reader_asof, *, edge_types: Sequence[str] | None = None,
               strategy: str = STRATEGY) -> GraphEdgeBatch:
    """DB 薄殼：S-EQ 讀 `stock_graph_edge`（唯讀 SELECT）。"""
    d = resolve_graph_asof(reader_asof, strategy=strategy)
    types = _normalize_types(edge_types)
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT source_stock_id, target_stock_id, weight, edge_type, as_of_date
                FROM {TABLE}
                WHERE as_of_date = %s AND edge_type = ANY(%s)""",
            (d, list(types)),
        )
        rows = cur.fetchall()
        cur.execute(f"SELECT count(*) FROM {TABLE} WHERE as_of_date = %s", (d,))
        n_exact = cur.fetchone()[0]
    if n_exact == 0:
        raise GraphAsofMissing(f"graph_asof_missing: no rows for as_of_date={d} (S-EQ)")
    if not rows:
        raise GraphEdgeEmpty(f"graph_edge_empty: as_of_date={d} types={types}")
    # defend: any returned aod must equal d
    for r in rows:
        if _as_date(r[4]) > d:
            raise GraphLeakageSuspect(f"graph_leakage_suspect: got {r[4]} > {d}")
    return GraphEdgeBatch(
        reader_asof=d,
        graph_asof=d,
        strategy=strategy,
        edge_types=types,
        edges=tuple((str(r[0]), str(r[1]), float(r[2]), str(r[3]), _as_date(r[4])) for r in rows),
    )


def neighbor_map(batch: GraphEdgeBatch) -> dict[str, list[tuple[str, float, str]]]:
    """src → [(tgt, weight, edge_type), ...]（無向雙向展開由呼叫端決定；此處保留表內方向）。"""
    out: dict[str, list[tuple[str, float, str]]] = {}
    for src, tgt, w, et, _ in batch.edges:
        out.setdefault(src, []).append((tgt, w, et))
    return out


def _selftest() -> bool:
    """零 IO 契約鎖。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("✓" if cond else "✗"), name)
        return cond

    d = date(2026, 8, 5)
    rows = [
        ("2330", "2454", 1.0, "industry_same", d),
        ("2330", "2303", 0.5, "return_corr_60d", d),
        ("2330", "2317", 0.4, "return_corr_120d", d),
        ("9999", "8888", 0.9, "industry_same", date(2026, 8, 4)),  # older; S-EQ ignore
    ]
    b = load_edges_seq(d, rows)
    chk("S-EQ keeps only D", b.n == 3 and b.graph_asof == d)
    chk("strategy tag", b.strategy == "S-EQ")

    try:
        load_edges_seq(d, rows, edge_types=["corr_60"])
        chk("undeclared type raises", False)
    except GraphTypeUndeclared:
        chk("undeclared type raises", True)

    try:
        load_edges_seq(date(2026, 8, 6), rows)
        chk("missing D raises", False)
    except GraphAsofMissing:
        chk("missing D raises", True)

    try:
        load_edges_seq(
            d,
            [("2330", "2454", 1.0, "industry_same", date(2026, 8, 6))],
        )
        chk("leakage raises", False)
    except GraphLeakageSuspect:
        chk("leakage raises", True)

    try:
        load_edges_seq(
            d,
            [("2330", "2454", 1.0, "industry_same", d)],
            edge_types=["return_corr_60d"],
        )
        chk("empty after type filter raises", False)
    except GraphEdgeEmpty:
        chk("empty after type filter raises", True)

    nm = neighbor_map(b)
    chk("neighbor_map", "2330" in nm and len(nm["2330"]) == 3)
    return ok


def _probe_asof(asof: str) -> int:
    from augur.core import db

    try:
        with db.connect() as conn:
            batch = load_edges(conn, asof)
    except GraphConsumeError as e:
        print(f"SKIP {getattr(e, 'code', 'graph_consume_error')}: {e}")
        return 1
    print(
        f"✓ probe S-EQ asof={batch.graph_asof} n={batch.n} types={batch.edge_types}"
    )
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print("公開入口: resolve_graph_asof, load_edges_seq, load_edges, neighbor_map")
        print(f"STRATEGY={STRATEGY} DECLARED_EDGE_TYPES={sorted(DECLARED_EDGE_TYPES)}")
        raise SystemExit(0)
    if sys.argv[1] == "--selftest":
        raise SystemExit(0 if _selftest() else 1)
    if sys.argv[1] == "--probe-asof" and len(sys.argv) >= 3:
        raise SystemExit(_probe_asof(sys.argv[2]))
    print("未知參數；見 --help")
    raise SystemExit(2)

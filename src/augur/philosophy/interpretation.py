"""PME S4 顧問單向解讀 — 進化結果 → 可解釋文案（零回流預測）。

🎯 這支在做什麼（白話）：讀 evolution_production_feature_set（active）、validated
   原則、apply_log（與可選 tag 計數），編成顧問／報告用解讀素材。單向消費：
   **禁止**寫回 feature_values／訓練輸入／當預測權重。≠可交易／≠確立級。

守 #1 #15 #18；計畫 SSOT＝reports/augur_philosophy_market_evolution_loop_plan_20260724.md §4 S4。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）:
  python -m augur.philosophy.interpretation              # 印用途+公開入口（唯讀）
  python -m augur.philosophy.interpretation --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from augur.philosophy.evolution import (
    DEFAULT_GATE_CONFIG,
    PRODSET_ACTIVE,
    PRODSET_TABLE,
)

# 對外硬免責（注入 prompt／報告必含；禁刪）
DISCLAIMER_LINES: tuple[str, ...] = (
    "PME S4 顧問單向解讀：已驗證原則／生產特徵登錄之**假說解讀骨架**。",
    "≠可交易、≠確立級、≠預測熱路徑權重、≠自動下單。",
    "零寫回 feature_values／訓練輸入；文獻≠真兆。",
    "靈魂「非自動駕駛」措辭另案 pending（G-PME-SOUL）。",
)

# 本模組源碼禁出現之「回流寫入」字面（selftest 靜態鎖；不掃 SELECT）
WRITEBACK_FORBIDDEN_LITERALS: tuple[str, ...] = (
    "INSERT INTO feature_values",
    "UPDATE feature_values",
    "DELETE FROM feature_values",
    "INSERT INTO canonical_features",
    "place_order",
    "submit_order",
)


@dataclass(frozen=True)
class ProdsetEntry:
    feature: str
    set_status: str
    principle_id: int | None
    source_run_id: int | None
    apply_log_id: int | None
    last_action: str


@dataclass(frozen=True)
class ValidatedMapEntry:
    principle_id: int
    school: str
    statement: str
    feature: str
    direction: int | None
    validated_ic: float | None
    validated_econ: str | None


@dataclass(frozen=True)
class ApplyLogEntry:
    apply_log_id: int
    queue_id: int
    before_status: str | None
    after_status: str | None
    feature: str | None
    action: str | None
    set_status: str | None


@dataclass(frozen=True)
class EvolutionInterpretationSnapshot:
    """S4 唯讀快照（純資料；由 fetch 組裝或 selftest 合成）。"""

    active_prodset: tuple[ProdsetEntry, ...]
    validated_maps: tuple[ValidatedMapEntry, ...]
    apply_logs: tuple[ApplyLogEntry, ...]
    tag_count: int = 0
    kill_state: str | None = None
    soul_wording_pending: bool = True
    note: str = ""


def scan_writeback_literals(text: str) -> list[str]:
    """靜態掃描：源碼／字串是否含回流寫入字面。"""
    hits: list[str] = []
    lower = text
    for lit in WRITEBACK_FORBIDDEN_LITERALS:
        if lit in lower:
            hits.append(lit)
    return hits


def render_interpretation_markdown(snap: EvolutionInterpretationSnapshot) -> str:
    """把快照編成顧問／報告用 markdown（確定性；零 LLM）。"""
    lines: list[str] = ["## PME S4 進化結果解讀（唯讀）", ""]
    lines.extend(f"> {d}" for d in DISCLAIMER_LINES)
    lines.append("")
    if snap.soul_wording_pending:
        lines.append("- **G-PME-SOUL**：靈魂措辭另案 pending（本塊不修 [N]）。")
    if snap.kill_state is not None:
        lines.append(f"- kill-switch：`{snap.kill_state}`")
    lines.append(f"- `stock_philosophy_tag` 列數：{snap.tag_count}"
                 + ("（空表＝尚無個股 tag；解讀仍可依原則／prodset）" if snap.tag_count == 0 else ""))
    if snap.note:
        lines.append(f"- note：{snap.note}")
    lines.append("")

    lines.append(f"### 生產特徵登錄（`{PRODSET_TABLE}` · active）")
    if not snap.active_prodset:
        lines.append("- （無 active 列）")
    else:
        for e in snap.active_prodset:
            lines.append(
                f"- `{e.feature}` · status={e.set_status} · action={e.last_action}"
                f" · principle_id={e.principle_id} · run={e.source_run_id}"
                f" · apply_log={e.apply_log_id}"
            )
    lines.append("")

    lines.append("### validated 原則 ↔ factor map（假說＋實證欄；≠可交易完備）")
    if not snap.validated_maps:
        lines.append("- （無 validated 原則）")
    else:
        by_pid: dict[int, list[ValidatedMapEntry]] = {}
        for m in snap.validated_maps:
            by_pid.setdefault(m.principle_id, []).append(m)
        for pid, rows in by_pid.items():
            head = rows[0]
            lines.append(f"- **P{pid}**〔{head.school}〕{head.statement}")
            for m in rows:
                ic = "—" if m.validated_ic is None else f"{m.validated_ic:+.4f}"
                econ = m.validated_econ if m.validated_econ else "—"
                d = "—" if m.direction is None else str(m.direction)
                lines.append(
                    f"  - feature=`{m.feature}` dir={d} validated_ic={ic} validated_econ={econ}"
                )
    lines.append("")

    lines.append("### APPLY 帳本（最近）")
    if not snap.apply_logs:
        lines.append("- （無 apply_log）")
    else:
        for a in snap.apply_logs:
            lines.append(
                f"- apply_log={a.apply_log_id} q={a.queue_id} "
                f"{a.before_status}→{a.after_status} "
                f"feature=`{a.feature}` action={a.action} set_status={a.set_status}"
            )
    lines.append("")
    lines.append(
        "**解讀用法**：可作顧問視角／縱深素材；**不得**據此改權重、當特徵、或宣稱確立級可交易。"
    )
    return "\n".join(lines)


def evolution_prompt_block(markdown: str) -> str:
    """顧問 prompt 附加塊（空輸入→空字串；非空必含免責語境）。"""
    md = (markdown or "").strip()
    if not md:
        return ""
    return (
        "\n\n[PME S4 進化解讀區塊——**假說／已驗證原則之解讀骨架**；"
        "回答中不得把本段說成可交易／確立級／自動下單；"
        "不得據此改模型權重或特徵]\n"
        + md
    )


def snapshot_from_rows(
    *,
    prodset_rows: Sequence[Mapping[str, Any]],
    validated_rows: Sequence[Mapping[str, Any]],
    apply_rows: Sequence[Mapping[str, Any]],
    tag_count: int = 0,
    kill_state: str | None = None,
    soul_wording_pending: bool | None = None,
    note: str = "",
) -> EvolutionInterpretationSnapshot:
    """純函式組裝快照（供 selftest／mock；不連 DB）。"""
    soul = (
        DEFAULT_GATE_CONFIG.get("soul_wording_pending", True)
        if soul_wording_pending is None
        else soul_wording_pending
    )
    prodset = tuple(
        ProdsetEntry(
            feature=str(r["feature"]),
            set_status=str(r.get("set_status") or PRODSET_ACTIVE),
            principle_id=r.get("principle_id"),
            source_run_id=r.get("source_run_id"),
            apply_log_id=r.get("apply_log_id"),
            last_action=str(r.get("last_action") or ""),
        )
        for r in prodset_rows
    )
    validated = tuple(
        ValidatedMapEntry(
            principle_id=int(r["principle_id"]),
            school=str(r.get("school") or ""),
            statement=str(r.get("statement") or ""),
            feature=str(r.get("feature") or ""),
            direction=r.get("direction"),
            validated_ic=r.get("validated_ic"),
            validated_econ=None if r.get("validated_econ") is None else str(r.get("validated_econ")),
        )
        for r in validated_rows
    )
    applies = tuple(
        ApplyLogEntry(
            apply_log_id=int(r["apply_log_id"]),
            queue_id=int(r["queue_id"]),
            before_status=r.get("before_status"),
            after_status=r.get("after_status"),
            feature=r.get("feature"),
            action=r.get("action"),
            set_status=r.get("set_status"),
        )
        for r in apply_rows
    )
    return EvolutionInterpretationSnapshot(
        active_prodset=prodset,
        validated_maps=validated,
        apply_logs=applies,
        tag_count=int(tag_count),
        kill_state=kill_state,
        soul_wording_pending=bool(soul),
        note=note,
    )


def fetch_interpretation_snapshot(conn) -> EvolutionInterpretationSnapshot:
    """唯讀查庫組裝快照（SELECT only；呼叫端持連線）。"""
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT feature, set_status, principle_id, source_run_id, apply_log_id, last_action
              FROM {PRODSET_TABLE}
             WHERE set_status = %s
             ORDER BY feature
            """,
            (PRODSET_ACTIVE,),
        )
        prodset_rows = [
            {
                "feature": r[0],
                "set_status": r[1],
                "principle_id": r[2],
                "source_run_id": r[3],
                "apply_log_id": r[4],
                "last_action": r[5],
            }
            for r in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT p.principle_id,
                   COALESCE(s.name_zh, s.name, ''),
                   p.statement,
                   m.feature,
                   m.direction,
                   m.validated_ic,
                   m.validated_econ
              FROM philosophy_principle p
              JOIN philosophy_school s ON s.school_id = p.school_id
              LEFT JOIN principle_factor_map m ON m.principle_id = p.principle_id
             WHERE p.status = 'validated'
             ORDER BY p.principle_id, m.feature
            """
        )
        validated_rows = [
            {
                "principle_id": r[0],
                "school": r[1],
                "statement": r[2],
                "feature": r[3] or "",
                "direction": r[4],
                "validated_ic": r[5],
                "validated_econ": r[6],
            }
            for r in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT apply_log_id, queue_id, before_status, after_status, production_set_delta
              FROM evolution_apply_log
             ORDER BY apply_log_id DESC
             LIMIT 20
            """
        )
        apply_rows = []
        for r in cur.fetchall():
            delta = r[4] if isinstance(r[4], dict) else {}
            if not isinstance(delta, dict):
                delta = {}
            apply_rows.append(
                {
                    "apply_log_id": r[0],
                    "queue_id": r[1],
                    "before_status": r[2],
                    "after_status": r[3],
                    "feature": delta.get("feature"),
                    "action": delta.get("action"),
                    "set_status": delta.get("set_status"),
                }
            )

        cur.execute("SELECT count(*) FROM stock_philosophy_tag")
        tag_count = int(cur.fetchone()[0])

        kill_state = None
        try:
            cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id = 1")
            row = cur.fetchone()
            if row:
                kill_state = str(row[0])
        except Exception:  # noqa: BLE001 — 表未建時誠實略過
            kill_state = None

        return snapshot_from_rows(
            prodset_rows=prodset_rows,
            validated_rows=validated_rows,
            apply_rows=apply_rows,
            tag_count=tag_count,
            kill_state=kill_state,
        )
    finally:
        cur.close()


def load_interpretation_markdown(*, conn=None) -> str:
    """便利入口：開連線（或用呼叫端 conn）→ 快照 → markdown。失敗回空字串（fail-soft）。"""
    try:
        if conn is not None:
            snap = fetch_interpretation_snapshot(conn)
            return render_interpretation_markdown(snap)
        from augur.core import db

        with db.connect() as c:
            snap = fetch_interpretation_snapshot(c)
            return render_interpretation_markdown(snap)
    except Exception:  # noqa: BLE001 — 顧問路徑不得因 S4 掛掉
        return ""


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    snap = snapshot_from_rows(
        prodset_rows=[
            {
                "feature": "inst_cumflow_position_120d",
                "set_status": "active",
                "principle_id": 77,
                "source_run_id": 5,
                "apply_log_id": 1,
                "last_action": "promote",
            }
        ],
        validated_rows=[
            {
                "principle_id": 77,
                "school": "cycle",
                "statement": "週期相位假說",
                "feature": "inst_cumflow_position_120d",
                "direction": 1,
                "validated_ic": 0.07,
                "validated_econ": "0.96",
            }
        ],
        apply_rows=[
            {
                "apply_log_id": 1,
                "queue_id": 98,
                "before_status": "untested",
                "after_status": "validated",
                "feature": "inst_cumflow_position_120d",
                "action": "promote",
                "set_status": "active",
            }
        ],
        tag_count=0,
        kill_state="clear",
        soul_wording_pending=True,
    )
    md = render_interpretation_markdown(snap)
    chk("disclaimer ≠可交易", "≠可交易" in md)
    chk("disclaimer 零寫回", "零寫回" in md)
    chk("含 prodset feature", "inst_cumflow_position_120d" in md)
    chk("含 validated 原則", "週期相位假說" in md)
    chk("含 apply_log", "apply_log=1" in md)
    chk("soul pending 註記", "G-PME-SOUL" in md)
    chk("tag 空表誠實", "空表" in md or "0" in md)

    block = evolution_prompt_block(md)
    chk("prompt block 非空", len(block) > 50)
    chk("prompt block 禁確立級語境", "確立級" in block)
    chk("空 md→空 block", evolution_prompt_block("") == "")

    empty = snapshot_from_rows(prodset_rows=[], validated_rows=[], apply_rows=[], tag_count=0)
    emd = render_interpretation_markdown(empty)
    chk("空快照仍有免責", "≠可交易" in emd and "無 active" in emd)

    # 本檔源碼不得含回流寫入字面（不含本常數定義區之字面本身——掃函式體以外用標記）
    import pathlib

    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    # 允許常數元組定義；禁止在 SQL／執行路徑出現寫入語句
    body = src.split("def fetch_interpretation_snapshot", 1)[-1]
    hits = scan_writeback_literals(body)
    chk("fetch 路徑無 writeback 字面", hits == [])
    chk("PRODSET_TABLE 常數對齊", PRODSET_TABLE == "evolution_production_feature_set")
    chk("soul flag 預設 True", DEFAULT_GATE_CONFIG.get("soul_wording_pending") is True)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("公開入口: render_interpretation_markdown / fetch_interpretation_snapshot /")
    print("          load_interpretation_markdown / evolution_prompt_block / snapshot_from_rows")
    print("(自測: python -m augur.philosophy.interpretation --selftest；免 DB 免 API)")

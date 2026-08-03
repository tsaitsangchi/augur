#!/usr/bin/env python
"""identity 未解析存量三指標唯讀量測器 — KDO.4／LDO.4 之 L7 量測落地（L7.26）。

🎯 這支在做什麼（白話）：憲章要求系統能隨時盤點「有多少身份還沒解析完」，並且**不准把量不到
   說成零**。本器對 identity 六表做**唯讀**盤點，逐一產出 `AUGUR-ID v1.0` ID.51 所定三指標——
   (a) 未解析存量、(b) 解析時效、(c) 顯式待決同一性存量（含 `AUGUR-WM v1.0 §WM.35` unmapped
   面，即 `AUGUR-L7 v1.0` L7.26 之第四類）。每一節都標明「**條文錨（file:line）→ 本實作採用之
   計算口徑 → 條文未定則標【口徑待裁】並印所採暫行口徑與理由**」，讓讀者一眼看出哪些數字有條文
   授權、哪些只是暫行口徑等 Steward 裁定。指標不可得時一律印 `不可知（UNKNOWN）`、**絕不印 0**
   （L7.26(c) 保守解釋：量測失效期間推定存量不可知，非推定為零）。

   **本器不是 KDO.4 之完整履行**：L7.26(a)(b) 另要求「時間序列快照」與「快照留痕為 Observation」，
   屬寫入行為，本器為唯讀、不寫任何一列，故僅覆蓋「量測與擷取」面。詳見
   `reports/augur_kdo4_measurement_scope_20260803.md`。

守原則 #9（零幻像：每個數字出自 DB query）· #10（可溯源）· #15（真兆自檢：量不到就說量不到）·
守 #29(b)（口徑住條文與 DB、不 hardcode 判準）· #35（回歸鎖三規則：判準抽純函式、真列形 fixture、
紅綠雙向、禁字面斷言）· 守 L7.26(c)（量測不得為零）。

執行指令矩陣：
  python scripts/report_identity_resolution_metrics.py              # 對 live DB 唯讀跑三指標、印人可讀報表
  python scripts/report_identity_resolution_metrics.py --json       # 同上，改印 JSON（供程式消費）
  python scripts/report_identity_resolution_metrics.py --show-anchors # 只印條文錨與口徑表，不連 DB
  python scripts/report_identity_resolution_metrics.py --selftest    # 判準純函式紅綠自測（免 DB 免 API、零 usage）
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys

import _bootstrap  # noqa: F401

# ---------------------------------------------------------------------------
# 條文錨（file:line）——逐字定錨，不腦補。行號為 2026-08-03 現查值。
# ---------------------------------------------------------------------------
ANCHORS = {
    "ID.51": "specs/IDENTITY-SPECIFICATION.md:280-288",
    "ID.51(a)": "specs/IDENTITY-SPECIFICATION.md:283",
    "ID.51(b)": "specs/IDENTITY-SPECIFICATION.md:284",
    "ID.51(c)": "specs/IDENTITY-SPECIFICATION.md:285",
    "ID.52": "specs/IDENTITY-SPECIFICATION.md:290-292",
    "IDO.4": "specs/IDENTITY-SPECIFICATION.md:380",
    "KS.83(i)": "specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:511-518",
    "KDO.4": "specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:637",
    "L5.9": "specs/COGNITIVE-KERNEL-SPECIFICATION.md:159-160",
    "LDI.4": "specs/COGNITIVE-KERNEL-SPECIFICATION.md:199",
    "LDO.4": "specs/COGNITIVE-KERNEL-SPECIFICATION.md:216",
    "L7.26": "specs/INFRASTRUCTURE-SPECIFICATION.md:294-301",
    "WM.15": "specs/WORLD-MODEL-SPECIFICATION.md:188-190",
    "WM.35": "specs/WORLD-MODEL-SPECIFICATION.md:336-358",
}

UNKNOWN = "UNKNOWN"


class Metric:
    """一個指標之量測結果。value 為 None 即『不可知』——L7.26(c) 禁以 0 冒充。"""

    def __init__(self, key, title, anchor, scope_basis, value=None,
                 unknown_reason=None, pending_ruling=None, detail=None):
        self.key = key
        self.title = title
        self.anchor = anchor
        self.scope_basis = scope_basis          # 本實作採用之計算口徑
        self.value = value                      # int/dict；None＝不可知
        self.unknown_reason = unknown_reason
        self.pending_ruling = pending_ruling or []   # 【口徑待裁】清單
        self.detail = detail or {}

    @property
    def state(self):
        return "measured" if self.value is not None else UNKNOWN

    def as_dict(self):
        return {
            "key": self.key, "title": self.title, "anchor": self.anchor,
            "scope_basis": self.scope_basis, "state": self.state,
            "value": self.value, "unknown_reason": self.unknown_reason,
            "pending_ruling": self.pending_ruling, "detail": self.detail,
        }


# ---------------------------------------------------------------------------
# 判準純函式（#35(1)：抽純函式、餵真列形、紅綠雙向；不碰 DB、不碰時鐘）
# ---------------------------------------------------------------------------

def is_unresolved_alias(row):
    """ID.51(a) 之個體層判準：該 alias 列是否處於未解析（provisional）態。

    口徑錨＝`entity_alias.alias_status`（CHECK 允許 provisional/adopted/retired）。
    `provisional` 為 ID.21「未採認即未解析」之物理載體；adopted＝已解析；retired＝已解析後退場。
    """
    return row.get("alias_status") == "provisional"


def count_unresolved(rows):
    """未解析存量基數（ID.51(a)）。回傳 int。"""
    return sum(1 for r in rows if is_unresolved_alias(r))


def completed_latency_measurable(columns, has_state_history):
    """ID.51(b)：判斷『已完成解析之時效分佈』是否可自現有 schema 導出。

    需要兩個時點：進入 provisional 之時點、離開 provisional 之時點。
    現行 `entity_alias` 僅有單一 `transaction_time`（插入時點），且 `alias_status` 為就地 UPDATE
    （該表無 append-only 觸發器），故『離開時點』無載體 ⇒ 不可導出。
    """
    has_entry = "transaction_time" in columns
    has_exit = ("resolved_at" in columns) or ("alias_status_changed_at" in columns)
    return bool(has_entry and (has_exit or has_state_history))


def censored_dwell_stats(rows, now):
    """ID.51(b) 之可得替代：現存未解析者之**右設限**滯留時長（進入→now），單位＝日。

    僅描述『還沒解析的已經等多久』，**不等於**已完成解析之時效分佈（後者不可導出）。
    """
    provisional = [r for r in rows if is_unresolved_alias(r)]
    if not provisional:
        return {"n": 0, "min_days": None, "median_days": None, "max_days": None}
    days = sorted((now - r["transaction_time"]).total_seconds() / 86400.0
                  for r in provisional)
    n = len(days)
    mid = n // 2
    median = days[mid] if n % 2 else (days[mid - 1] + days[mid]) / 2.0
    return {"n": n, "min_days": round(days[0], 4),
            "median_days": round(median, 4), "max_days": round(days[-1], 4)}


def pending_identity_stock(declaration_count, carrier_present):
    """ID.51(c) WM.15 面：顯式待決同一性存量＝『疑似同一而尚無同一性宣告者』之基數。

    關鍵不變式（L7.26(c)）：此為**否定集**——已登錄之同一性宣告數（`identity_claim`）量的是
    『已宣告』，**不是**『待決』。無「疑似同一候選」之登錄載體時，待決存量為**不可知**，
    **不得**以宣告數 0 推論待決數 0。
    """
    if not carrier_present:
        return None
    return max(int(declaration_count), 0)


def is_active_unmapped(row):
    """ID.51(c) WM.35 面／L7.26 第四類：該通道登錄列是否為『現行未映射』。"""
    return row.get("mapping_status") == "unmapped" and row.get("superseded_at") is None


def count_unmapped(rows):
    """unmapped 顯式存量基數。回傳 int。"""
    return sum(1 for r in rows if is_active_unmapped(r))


# ---------------------------------------------------------------------------
# 口徑待裁登錄（條文未逐字定義者，一律列此、不自創為既成事實）
# ---------------------------------------------------------------------------
PENDING_RULINGS = {
    "M1": [
        ("Q1 計數單位", "ID.51(a) 字面為『處於 provisional 狀態之 **Observation 指涉集合**之基數』。"
                        "現行物理載體 `entity_alias` 之一列＝一個外部碼別名，非一筆 Observation；"
                        "一個 provisional 別名可被數以百萬計之觀測列引用。"
                        "暫行口徑＝**計 alias 列數**（解析動作之單位、機器可判、保守不膨脹）；"
                        "另一讀法＝計其所指涉之觀測列數（數量級差異巨大）。"),
        ("Q2 as-of 可重建性", "ID.51(a) 字面為『**任一** as-of 時點』。現行 `entity_alias` 之 "
                              "`alias_status` 就地 UPDATE、無狀態史，故僅 now() 可量、歷史時點不可重建。"
                              "暫行口徑＝**as-of ＝ now() 單點**；是否要求歷史可重建（須加狀態史表）待裁。"),
    ],
    "M2": [
        ("Q3 完成時效不可導出", "ID.51(b) 要求『自 provisional 進入至解析之**時間分佈**』。現行 schema "
                                "無『離開 provisional』之時點欄，且 `entity_alias` 無 append-only 觸發器"
                                "（可就地覆寫），故已完成解析之時效分佈**不可導出**。"
                                "暫行處置＝依 L7.26(c) 標為不可知，另印右設限滯留時長為可得下界。"
                                "補正方案（待裁）＝加 `resolved_at` 欄或改 append-only 狀態史。"),
        ("Q4 『進入』時點之定義", "『進入 provisional』採 DB 插入時點（`transaction_time`）或採該觀測之"
                                  "實際攝取／發生時點，條文未定。暫行口徑＝`transaction_time`（唯一有載體者）。"),
    ],
    "M3": [
        ("Q5 『疑似同一』之判定與載體", "ID.51(c) 之『疑似同一』未定判定門檻（ID.51 末句明言"
                                        "『不內嵌具體門檻』），且現行 DB **無**『疑似同一候選』登錄表。"
                                        "暫行處置＝依 L7.26(c) 標為不可知（**非** 0）。"
                                        "已知場外候選集（名實不符 37 例 CSV）為其下界、尚未入 DB。"),
    ],
    "M4": [
        ("Q6 三指標 vs 四類存量之對應", "ID.51 列三指標、L7.26 列四類存量（多列 WM.35 unmapped 為獨立類）。"
                                        "ID.51(c) 文內同時涵蓋 WM.15 待決與 WM.35 unmapped 兩者。"
                                        "暫行口徑＝**獨立成節（M4）呈列**、並於 (c) 家族下合計；"
                                        "是否應合併為單一指標待裁。"),
    ],
    "ALL": [
        ("Q7 門檻值", "三指標之門檻值經 RULING-2026-039 五.3 明示『門檻數值不現寫』、"
                      "並由 L7.45 Threshold Registry 承接。本器**只報數、不判 PASS/FAIL**，"
                      "不自訂任何門檻。"),
        ("Q8 KS.83(i)(a) 之射程", "KS.83(i)(a) 使『未解析存量＞0』之 Identity 其 Knowledge 完備性"
                                  "不得高於 E1，射程寫為『指涉該 Identity **或其所屬類型**』。"
                                  "逐個體讀＝僅該 237 個別名受限；逐類型讀＝該類型全體受限（射程差距極大）。"
                                  "本器兩者並陳（見 M1 detail），不代為裁定適用何者。"),
    ],
}


# ---------------------------------------------------------------------------
# DB 擷取（唯讀；L7.26(a) 擷取路徑不由被量測構件自身支配——本器獨立連線、非由攝取管線觸發）
# ---------------------------------------------------------------------------

def _fetch_all(conn):
    """一次取回四項量測所需之真實列（唯讀 SELECT，零寫入、零 DDL）。"""
    out = {}
    cur = conn.cursor()
    try:
        cur.execute("SELECT alias_status, transaction_time FROM entity_alias")
        out["alias_rows"] = [{"alias_status": a, "transaction_time": t}
                             for a, t in cur.fetchall()]

        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema='public' AND table_name='entity_alias'""")
        out["alias_columns"] = {r[0] for r in cur.fetchall()}

        # entity_alias 是否具 append-only／狀態史（決定 M2 可否導出）
        cur.execute("""SELECT count(*) FROM pg_trigger
                       WHERE tgrelid='entity_alias'::regclass AND NOT tgisinternal
                         AND tgfoid::regproc::text = 'identity_append_only'""")
        out["alias_append_only"] = cur.fetchone()[0] > 0

        cur.execute("SELECT count(*) FROM identity_claim")
        out["claim_count"] = cur.fetchone()[0]

        # 是否存在『疑似同一候選』登錄載體（ID.51(c) 之否定集需要它）
        cur.execute("""SELECT count(*) FROM information_schema.tables
                       WHERE table_schema='public'
                         AND table_name IN ('identity_pending_match','identity_match_candidate',
                                            'identity_suspected_same')""")
        out["pending_carrier_present"] = cur.fetchone()[0] > 0

        cur.execute("SELECT mapping_status, superseded_at FROM world_channel_binding")
        out["binding_rows"] = [{"mapping_status": m, "superseded_at": s}
                               for m, s in cur.fetchall()]

        cur.execute("""SELECT r.entity_type, count(*) FROM entity_alias a
                       JOIN entity_registry r USING(augur_id)
                       WHERE a.alias_status='provisional' GROUP BY 1""")
        out["provisional_by_type"] = dict(cur.fetchall())

        cur.execute("SELECT entity_type, count(*) FROM entity_registry GROUP BY 1")
        out["registry_by_type"] = dict(cur.fetchall())

        cur.execute("SELECT now()")
        out["now"] = cur.fetchone()[0]
    finally:
        cur.close()
    return out


def build_metrics(data):
    """把擷取到的真實列組成四個 Metric。data=None 代表量測構件失效 ⇒ 全部不可知（L7.26(c)）。"""
    if data is None:
        reason = "量測構件失效（DB 不可達）——依 L7.26(c) 推定不可知，不得推定為零。"
        return [
            Metric("M1", "未解析存量（unresolved backlog）", ANCHORS["ID.51(a)"],
                   "entity_alias.alias_status='provisional' 之列數", None, reason,
                   PENDING_RULINGS["M1"]),
            Metric("M2", "解析時效（resolution latency）", ANCHORS["ID.51(b)"],
                   "自 provisional 進入至解析之時間分佈", None, reason, PENDING_RULINGS["M2"]),
            Metric("M3", "顯式待決同一性存量（WM.15 面）", ANCHORS["ID.51(c)"],
                   "疑似同一而尚無同一性宣告者之基數", None, reason, PENDING_RULINGS["M3"]),
            Metric("M4", "unmapped 顯式存量（WM.35 面／L7.26 第四類）", ANCHORS["WM.35"],
                   "world_channel_binding 現行 unmapped 之列數", None, reason,
                   PENDING_RULINGS["M4"]),
        ]

    metrics = []

    # --- M1 未解析存量 ---
    n_unres = count_unresolved(data["alias_rows"])
    by_type = data["provisional_by_type"]
    type_scope = {t: data["registry_by_type"].get(t, 0) for t in by_type}
    metrics.append(Metric(
        "M1", "未解析存量（unresolved backlog）", ANCHORS["ID.51(a)"],
        "計 `entity_alias` 中 alias_status='provisional' 之列數（as-of ＝ now() 單點）",
        n_unres, None, PENDING_RULINGS["M1"],
        {"total_alias_rows": len(data["alias_rows"]),
         "provisional_by_entity_type": by_type,
         "ks83_per_identity_capped": n_unres,
         "ks83_per_type_capped": sum(type_scope.values()),
         "ks83_note": "KS.83(i)(a) 射程二讀：逐個體＝%d；逐類型＝%d（見 Q8）"
                      % (n_unres, sum(type_scope.values()))}))

    # --- M2 解析時效 ---
    measurable = completed_latency_measurable(data["alias_columns"], data["alias_append_only"])
    dwell = censored_dwell_stats(data["alias_rows"], data["now"])
    if measurable:
        metrics.append(Metric(
            "M2", "解析時效（resolution latency）", ANCHORS["ID.51(b)"],
            "自 provisional 進入至解析之時間分佈", dwell, None, PENDING_RULINGS["M2"],
            {"note": "schema 已具離開時點載體，完成時效可導出"}))
    else:
        metrics.append(Metric(
            "M2", "解析時效（resolution latency）", ANCHORS["ID.51(b)"],
            "自 provisional 進入至解析之時間分佈（**完成分佈不可導出**）",
            None,
            "entity_alias 無『離開 provisional』時點欄、且非 append-only（可就地覆寫狀態），"
            "已完成解析之時效分佈無資料載體 ⇒ 依 L7.26(c) 標為不可知。",
            PENDING_RULINGS["M2"],
            {"censored_dwell_of_currently_provisional": dwell,
             "censored_note": "此為右設限滯留時長（進入→now），僅為下界，非 ID.51(b) 所求之完成分佈"}))

    # --- M3 顯式待決同一性存量 ---
    pend = pending_identity_stock(data["claim_count"], data["pending_carrier_present"])
    metrics.append(Metric(
        "M3", "顯式待決同一性存量（WM.15 面）", ANCHORS["ID.51(c)"],
        "疑似同一而尚無同一性宣告者之基數（否定集，需候選登錄載體）",
        pend,
        None if pend is not None else
        "DB 無『疑似同一候選』登錄表 ⇒ 待決存量無載體。`identity_claim` 現有 %d 列量的是"
        "『已宣告』而非『待決』，**不得**以宣告數 0 推論待決數 0（L7.26(c)）。"
        % data["claim_count"],
        PENDING_RULINGS["M3"],
        {"identity_claim_rows": data["claim_count"],
         "carrier_present": data["pending_carrier_present"],
         "known_offdb_lower_bound": "reports/identity_retire_name_mismatch_20260801.csv（37 例，"
                                    "Steward 已裁 MM 甲案 A34+B1 認同一實體、C2 留人裁；施作未執行）"}))

    # --- M4 unmapped 顯式存量 ---
    n_unmapped = count_unmapped(data["binding_rows"])
    metrics.append(Metric(
        "M4", "unmapped 顯式存量（WM.35 面／L7.26 第四類）", ANCHORS["WM.35"],
        "計 `world_channel_binding` 中 mapping_status='unmapped' 且 superseded_at IS NULL 之列數",
        n_unmapped, None, PENDING_RULINGS["M4"],
        {"total_binding_rows": len(data["binding_rows"])}))

    return metrics


# ---------------------------------------------------------------------------
# 呈現
# ---------------------------------------------------------------------------

def render_anchor_table():
    lines = ["條文錨（file:line）——2026-08-03 現查", "-" * 62]
    for k, v in ANCHORS.items():
        lines.append("  %-10s %s" % (k, v))
    lines.append("")
    lines.append("下放鏈：ID.51／IDO.4（L3 定指標） → KS.83(i)／KDO.4（L4 定納入語義、量測下放）")
    lines.append("        → L5.9／LDI.4／LDO.4（L5 定性承接、量測實作再下放） → L7.26（本層量測落地）")
    return "\n".join(lines)


def render_text(metrics, meta):
    out = []
    out.append("=" * 78)
    out.append("identity 未解析存量三指標量測報表（KDO.4／LDO.4 → L7.26 量測落地）")
    out.append("=" * 78)
    out.append("量測時點：%s" % meta.get("measured_at"))
    out.append("量測性質：唯讀（零寫入、零 DDL）；擷取路徑獨立於被量測構件（L7.26(a)）")
    out.append("")
    out.append(render_anchor_table())
    out.append("")

    for m in metrics:
        out.append("-" * 78)
        out.append("【%s】%s" % (m.key, m.title))
        out.append("  條文錨　　：%s" % m.anchor)
        out.append("  採用口徑　：%s" % m.scope_basis)
        if m.state == UNKNOWN:
            out.append("  量測結果　：不可知（UNKNOWN）　※ L7.26(c)：不得以 0 冒充")
            out.append("  不可知理由：%s" % m.unknown_reason)
        else:
            v = m.value
            out.append("  量測結果　：%s" % (json.dumps(v, ensure_ascii=False)
                                            if isinstance(v, dict) else v))
        for k, dv in m.detail.items():
            out.append("    · %s = %s" % (k, json.dumps(dv, ensure_ascii=False)
                                          if isinstance(dv, (dict, list)) else dv))
        if m.pending_ruling:
            out.append("  【口徑待裁】%d 處：" % len(m.pending_ruling))
            for q, why in m.pending_ruling:
                out.append("    - %s：%s" % (q, why))
        out.append("")

    out.append("-" * 78)
    out.append("【全體適用之口徑待裁】")
    for q, why in PENDING_RULINGS["ALL"]:
        out.append("  - %s：%s" % (q, why))
    out.append("")
    out.append("-" * 78)
    out.append("射程誠實：本器只覆蓋 L7.26 之『物理量測與擷取』面。L7.26(a) 之時間序列快照與 (b) 之"
               "『快照留痕為 Observation，攜 provenance』屬**寫入**行為，本器唯讀、未實作 ⇒ "
               "**本器不足以單獨構成 KDO.4／LDO.4 之完整履行**。")
    out.append("口徑待裁合計：%d 處（M1:%d／M2:%d／M3:%d／M4:%d／ALL:%d）" % (
        sum(len(v) for v in PENDING_RULINGS.values()),
        len(PENDING_RULINGS["M1"]), len(PENDING_RULINGS["M2"]),
        len(PENDING_RULINGS["M3"]), len(PENDING_RULINGS["M4"]),
        len(PENDING_RULINGS["ALL"])))
    out.append("=" * 78)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# selftest（#35：純函式餵真列形 fixture、紅綠雙向、禁字面斷言；免 DB 免 API）
# ---------------------------------------------------------------------------

def _selftest():
    from datetime import timedelta, timezone
    ok = True
    t0 = _dt.datetime(2026, 8, 1, 21, 52, 8, tzinfo=timezone.utc)
    now = t0 + timedelta(days=2)

    def check(name, cond):
        nonlocal ok
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            ok = False

    # 真列形 fixture：欄位與型別取自 live `entity_alias`（alias_status/transaction_time）
    alias_rows = [
        {"alias_status": "adopted", "transaction_time": t0},
        {"alias_status": "adopted", "transaction_time": t0},
        {"alias_status": "provisional", "transaction_time": t0},
        {"alias_status": "provisional", "transaction_time": t0 + timedelta(days=1)},
        {"alias_status": "retired", "transaction_time": t0},
    ]

    # --- 綠：判準確實挑出 provisional（既非 0、亦非全體）---
    n = count_unresolved(alias_rows)
    check("M1 綠：5 列真列形中恰 2 列 provisional（n=%d）" % n, n == 2)
    # --- 紅向：判準若弱化成恆 0 或恆全體，上式必炸 ---
    check("M1 紅向：計數 ≠ 0（弱化成恆 0 會紅）", n != 0)
    check("M1 紅向：計數 ≠ 全體列數（弱化成恆真會紅）", n != len(alias_rows))
    check("M1 紅向：adopted 不得被判為未解析",
          not is_unresolved_alias({"alias_status": "adopted"}))
    check("M1 紅向：retired 不得被判為未解析",
          not is_unresolved_alias({"alias_status": "retired"}))
    check("M1 綠：provisional 必被判為未解析",
          is_unresolved_alias({"alias_status": "provisional"}))

    # --- M2：完成時效可否導出之判準（真欄位集）---
    live_cols = {"alias_id", "augur_id", "code_system", "external_code", "alias_status",
                 "valid_from", "valid_to", "transaction_time", "evidence_ref", "note"}
    check("M2 紅：live 欄位集＋無 append-only ⇒ 完成時效不可導出",
          completed_latency_measurable(live_cols, False) is False)
    check("M2 綠：補 resolved_at 欄後 ⇒ 可導出",
          completed_latency_measurable(live_cols | {"resolved_at"}, False) is True)
    check("M2 綠：改 append-only 狀態史後 ⇒ 可導出",
          completed_latency_measurable(live_cols, True) is True)

    d = censored_dwell_stats(alias_rows, now)
    check("M2 綠：右設限滯留 n=2、max=2 日、min=1 日",
          d["n"] == 2 and abs(d["max_days"] - 2.0) < 1e-6 and abs(d["min_days"] - 1.0) < 1e-6)
    check("M2 紅向：無 provisional 時 n=0 且統計為 None（不得偽造 0 日）",
          censored_dwell_stats([{"alias_status": "adopted", "transaction_time": t0}],
                               now) == {"n": 0, "min_days": None,
                                        "median_days": None, "max_days": None})

    # --- M3：核心不變式——無載體時必須回不可知，不得回 0 ---
    check("M3 紅：無候選載體 ⇒ 不可知（None），非 0",
          pending_identity_stock(0, False) is None)
    check("M3 紅：宣告數 0 亦不得推論待決 0",
          pending_identity_stock(0, False) != 0)
    check("M3 綠：有載體時回實際基數",
          pending_identity_stock(7, True) == 7)

    # --- M4：unmapped 判準（真列形：mapping_status + superseded_at）---
    binding_rows = [
        {"mapping_status": "unmapped", "superseded_at": None},
        {"mapping_status": "unmapped", "superseded_at": None},
        {"mapping_status": "unmapped", "superseded_at": t0},   # 已 supersede，不計
        {"mapping_status": "mapped", "superseded_at": None},
    ]
    u = count_unmapped(binding_rows)
    check("M4 綠：4 列中恰 2 列現行 unmapped（n=%d）" % u, u == 2)
    check("M4 紅向：已 superseded 之 unmapped 不得計入",
          not is_active_unmapped({"mapping_status": "unmapped", "superseded_at": t0}))
    check("M4 紅向：mapped 不得計入",
          not is_active_unmapped({"mapping_status": "mapped", "superseded_at": None}))
    check("M4 紅向：計數 ≠ 0 且 ≠ 全體（恆 0／恆真皆會紅）",
          u != 0 and u != len(binding_rows))

    # --- 量測失效之保守處置（L7.26(c)）：全部指標不可知 ---
    degraded = build_metrics(None)
    check("L7.26(c) 綠：DB 不可達 ⇒ 四指標全部 UNKNOWN、零個報 0",
          len(degraded) == 4 and all(m.state == UNKNOWN for m in degraded)
          and all(m.value is None for m in degraded))

    print("\nselftest: %s" % ("ALL PASS" if ok else "FAILED"))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(
        description="identity 未解析存量三指標唯讀量測（KDO.4／LDO.4 → L7.26）")
    p.add_argument("--json", action="store_true", help="輸出 JSON")
    p.add_argument("--show-anchors", action="store_true", help="只印條文錨與下放鏈，不連 DB")
    p.add_argument("--selftest", action="store_true", help="判準純函式紅綠自測（免 DB 免 API）")
    args = p.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.show_anchors:
        print(render_anchor_table())
        return 0

    data, err = None, None
    try:
        from augur.core.db import connect
        with connect() as conn:
            conn.set_session(readonly=True)
            data = _fetch_all(conn)
    except Exception as exc:                      # graceful：不裸 traceback（#29(a)）
        err = "%s: %s" % (type(exc).__name__, exc)

    metrics = build_metrics(data)
    meta = {"measured_at": (data["now"].isoformat() if data
                            else _dt.datetime.now().astimezone().isoformat()),
            "measurement_available": data is not None,
            "error": err}

    if args.json:
        print(json.dumps({"meta": meta, "metrics": [m.as_dict() for m in metrics]},
                         ensure_ascii=False, indent=2, default=str))
    else:
        if err:
            print("！量測構件失效：%s" % err)
            print("　依 L7.26(c) 保守解釋，全部指標推定為『不可知』（非零）。\n")
        print(render_text(metrics, meta))

    return 0 if data is not None else 2


if __name__ == "__main__":
    sys.exit(main())

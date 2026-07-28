#!/usr/bin/env python
"""建 knowhow_interaction_probe 表(raw↔know-how 交互探針列)+ §1.2 種子 — RKI-S01。

🎯 這支在做什麼(白話):把「第一性×太陽能／Pareto×太陽能／哲學×研發模板／孫子×企管／
   AI 模型進化×投資預測／AI×太陽能材料研發」等交互議題變成 **PostgreSQL 探針列**;runner(S2)讀
   active 列展開 template→庫內檢索。**新交互議題＝INSERT 一列、零改碼**(#29b)。
   本表是探針帳本,**不是**答案 SSOT／非預測特徵；**≠**自動開 PME-XDOM-AI-PREDICT／PME-XDOM-SOLAR。
守 #29b(策展住 DB)· #6(冪等)· #29a/d(指令矩陣)· FZ-keep(零市場 API)· NHC-keep(禁領域 hardcode)。

執行指令矩陣:
  python scripts/migrate_knowhow_interaction_probe_ddl.py            # 安全預設:印矩陣+--check
  python scripts/migrate_knowhow_interaction_probe_ddl.py --check    # 唯讀現況
  python scripts/migrate_knowhow_interaction_probe_ddl.py --apply    # 冪等建表+種子
  python scripts/migrate_knowhow_interaction_probe_ddl.py --show     # 列 active 探針
  python scripts/migrate_knowhow_interaction_probe_ddl.py --selftest # 零 DB 紅綠
"""
from __future__ import annotations

import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS knowhow_interaction_probe (
    probe_id           TEXT PRIMARY KEY,
    prompt_template    TEXT NOT NULL,
    knowhow_axis       TEXT NOT NULL,
    raw_axis           TEXT NOT NULL,
    expected_family    TEXT,
    interaction_kind   TEXT NOT NULL
        CHECK (interaction_kind IN (
            'kh_x_kh',
            'principle_x_rd',
            'principle_x_principle',
            'principle_x_raw_bridge',
            'kh_x_feature_family'
        )),
    template_params    JSONB NOT NULL DEFAULT '{}',
    active             BOOLEAN NOT NULL DEFAULT TRUE,
    provenance         TEXT,
    note               TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_rki_probe_active
  ON knowhow_interaction_probe (active, interaction_kind)
  WHERE active;
COMMENT ON TABLE knowhow_interaction_probe IS
  'RKI: raw↔know-how 交互探針列(#29b；擴題=INSERT；runner 讀表；非答案 SSOT／非預測特徵)';
"""

PROVENANCE = "steward_seed_rki_s01_20260728"

# (probe_id, prompt_template, knowhow_axis, raw_axis, expected_family,
#  interaction_kind, template_params_dict, note)
SEED = (
    (
        "RKI-FP-SOLAR-CORE",
        "依「{{principle}}」列出在「{{tech_domain}}」技術核心？（要求：可溯源引用；缺料則誠實說明缺口）",
        "第一性原理",
        "太陽能材料研發·技術核心",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "第一性原理", "tech_domain": "太陽能材料研發"},
        "對齊 NHC A0-core；產生走 advise／glossary，禁寫死清單",
    ),
    (
        "RKI-FP-SOLAR-PHYS",
        "依「{{principle}}」列出在「{{tech_domain}}」物理學技術核心？（要求：可溯源引用；缺料則誠實說明缺口）",
        "第一性原理",
        "太陽能材料·物理學技術核心",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "第一性原理", "tech_domain": "太陽能材料研發物理學"},
        "對齊 NHC A0-phys",
    ),
    (
        "RKI-FP-SOLAR-CHEM",
        "依「{{principle}}」列出在「{{tech_domain}}」化學技術核心？（要求：可溯源引用；缺料則誠實說明缺口）",
        "第一性原理",
        "太陽能材料·化學技術核心",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "第一性原理", "tech_domain": "太陽能材料研發化學"},
        "對齊 NHC A0-chem",
    ),
    (
        "RKI-FP-SOLAR-APP",
        "「{{principle}}」在「{{tech_domain}}」如何應用？（要求：可溯源引用；缺料則誠實說明缺口）",
        "第一性原理",
        "太陽能材料研發·如何應用",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "第一性原理", "tech_domain": "太陽能材料研發"},
        "對齊 NHC A0-app",
    ),
    (
        "RKI-PARETO-SOLAR",
        "依「{{principle}}」分析「{{tech_domain}}」的關鍵少數槓桿點（研發／供應鏈／投資可推廣；要求：可溯源；缺料誠實缺口）",
        "八二法則／Pareto",
        "太陽能（研發／供應鏈／投資）",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "八二法則／Pareto", "tech_domain": "太陽能材料與供應鏈"},
        "可推廣模板：Pareto ×〈任意域〉＝改 template_params 或另 INSERT",
    ),
    (
        "RKI-PHILO-RD-TMPL",
        "依「{{principle}}」列出在「{{tech_domain}}」研發技術核心？（要求：可溯源引用；缺料則誠實說明缺口）",
        "哲學／原則（模板槽）",
        "研發技術（模板槽）",
        "corpus+principle",
        "principle_x_rd",
        {"principle": "{{principle}}", "tech_domain": "{{tech_domain}}"},
        "通用模板探針——實例靠列參數／另 INSERT，禁專支",
    ),
    (
        "RKI-SUNZI-MGMT",
        "「{{principle}}」與「{{tech_domain}}」的可對照交互概念有哪些？（要求：可溯源；測覆蓋非灌因子；缺料誠實缺口）",
        "孫子兵法",
        "企管／投資",
        "corpus+principle+domain_map",
        "kh_x_kh",
        {"principle": "孫子兵法", "tech_domain": "企管／投資"},
        "對照臂＝PME-XDOM／KH-XDOM；探針測覆蓋，不暗開 PME-XDOM-SOLAR",
    ),
    (
        "RKI-AI-PREDICT-EVO",
        "「{{kh_a}}」的方法論（架構／訓練／評測／對齊）如何改進「{{kh_b}}」閉環？（要求：可溯源概念橋；缺料誠實缺口；禁寫死專答樹）",
        "AI／ML 模型進化",
        "投資／預測模型進化（PME／ranker／arena／特徵提拔／經濟終關）",
        "corpus+principle+pme_objects",
        "kh_x_kh",
        {
            "kh_a": "AI／ML 模型進化",
            "kh_b": "本專案投資預測模型進化（PME、ranker、arena、特徵提拔、經濟終關）",
        },
        "Steward 追加 2026-07-28；探針帳≠PME-XDOM-AI-PREDICT（另需拍板）",
    ),
    (
        "RKI-AI-PREDICT-EVAL",
        "How can methods from 「{{kh_a}}」(training／eval／alignment) transfer as falsifiable concepts to 「{{kh_b}}」 without hardcoding answer trees? Cite corpus; gap if missing.",
        "AI model evolution (methods／eval／alignment)",
        "Investment prediction model evolution (gates／OOS／economic eval)",
        "corpus+principle+pme_objects",
        "kh_x_kh",
        {
            "kh_a": "AI model evolution (architecture, training, evaluation, alignment)",
            "kh_b": "augur investment prediction evolution (PME gates, arena, feature promotion, economic eval)",
        },
        "EN 對照臂；NHC-keep；≠自動灌因子",
    ),
    (
        "RKI-FP-AI-ITER",
        "依「{{principle}}」，如何強化「{{tech_domain}}」？（要求：可溯源概念橋；缺料誠實缺口；禁寫死「第一性強化 AI 迭代」專答樹）",
        "第一性原理",
        "AI 模型自我迭代／再進化",
        "corpus+principle",
        "principle_x_rd",
        {
            "principle": "第一性原理",
            "tech_domain": "AI 模型自我迭代與再進化",
        },
        "Steward 追加例 2026-07-28；NHC-keep；產生走 advise",
    ),
    (
        "RKI-FP-AI-PREDICT",
        "依「{{principle}}」強化「{{ai_axis}}」後，如何反饋改進「{{predict_axis}}」？（optional 交叉軸；可溯源；缺料誠實；禁專答樹；≠PME 灌因子）",
        "第一性原理 → AI 自我迭代",
        "投資預測模型進化（反饋橋）",
        "corpus+principle+pme_objects",
        "kh_x_kh",
        {
            "principle": "第一性原理",
            "ai_axis": "AI 模型自我迭代與再進化",
            "predict_axis": "本專案投資預測模型進化閉環",
        },
        "optional 交叉臂；另需 PME-XDOM-AI-PREDICT 才灌因子",
    ),
    (
        "RKI-FP-PREDICT-ITER",
        "依「{{principle}}」，如何強化「{{tech_domain}}」之自我迭代與再進化？（檢索軸可含 PME／ranker／arena／特徵提拔／經濟終關；要求可溯源；缺料誠實；禁寫死專答樹；≠自動灌因子）",
        "第一性原理",
        "投資模擬／預測模型自我迭代再進化",
        "corpus+principle+pme_objects",
        "principle_x_rd",
        {
            "principle": "第一性原理",
            "tech_domain": "本專案投資模擬／預測模型",
        },
        "Steward 追加例 2026-07-28；與 FP-AI-ITER／AI-PREDICT 成套；NHC-keep",
    ),
    (
        "RKI-AI-SOLAR-RD",
        "「{{kh_a}}」如何強化「{{kh_b}}」？（要求：可溯源概念橋；缺料誠實缺口；禁寫死太陽能／AI 專答樹；≠台股因子鏈）",
        "AI／ML 模型進化",
        "太陽能材料研發技術",
        "corpus+principle",
        "kh_x_kh",
        {
            "kh_a": "AI 模型進化（架構／訓練／評測／對齊）",
            "kh_b": "太陽能材料研發技術",
        },
        "Steward 追加 2026-07-28；顧問／研發 know-how 交互；≠PME-XDOM-SOLAR；≠PME-XDOM-AI-PREDICT",
    ),
    (
        "RKI-FP-AI-SOLAR",
        "依「{{principle}}」強化「{{ai_axis}}」後，如何反饋改進「{{solar_axis}}」？（optional 交叉軸；可溯源；缺料誠實；禁專答樹；≠PME 灌因子）",
        "第一性原理 → AI 模型進化",
        "太陽能材料研發技術（反饋橋）",
        "corpus+principle",
        "kh_x_kh",
        {
            "principle": "第一性原理",
            "ai_axis": "AI 模型進化",
            "solar_axis": "太陽能材料研發技術",
        },
        "optional 交叉臂；可與 FP-SOLAR／AI-SOLAR-RD 交叉；灌因子另拍 PME-XDOM-SOLAR",
    ),
)

SEED_IDS = tuple(s[0] for s in SEED)


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('knowhow_interaction_probe') IS NOT NULL")
        exists = cur.fetchone()[0]
        print(f"  knowhow_interaction_probe: {'已建' if exists else '未建'}")
        if not exists:
            return 1
        cur.execute("SELECT count(*) FROM knowhow_interaction_probe WHERE active")
        n = cur.fetchone()[0]
        cur.execute(
            "SELECT probe_id FROM knowhow_interaction_probe "
            "WHERE probe_id = ANY(%s) AND active ORDER BY 1",
            (list(SEED_IDS),),
        )
        present = {r[0] for r in cur.fetchall()}
        missing = [i for i in SEED_IDS if i not in present]
        print(f"  active 列數: {n}(種子目標 {len(SEED)})")
        print(f"  種子齊全: {not missing}" + (f" missing={missing}" if missing else ""))
        return 0 if n >= len(SEED) and not missing else 1


def show(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT probe_id, interaction_kind, knowhow_axis, raw_axis, active "
            "FROM knowhow_interaction_probe ORDER BY probe_id"
        )
        rows = cur.fetchall()
    print(f"── knowhow_interaction_probe:{len(rows)} ──")
    for pid, kind, ka, ra, active in rows:
        flag = "" if active else " [inactive]"
        print(f"  {pid} [{kind}] {ka} × {ra}{flag}")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(DDL)
        n = 0
        for (
            probe_id,
            prompt_template,
            knowhow_axis,
            raw_axis,
            expected_family,
            interaction_kind,
            template_params,
            note,
        ) in SEED:
            cur.execute(
                "INSERT INTO knowhow_interaction_probe "
                "(probe_id, prompt_template, knowhow_axis, raw_axis, expected_family, "
                " interaction_kind, template_params, active, provenance, note) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,TRUE,%s,%s) "
                "ON CONFLICT (probe_id) DO UPDATE SET "
                "prompt_template=EXCLUDED.prompt_template, "
                "knowhow_axis=EXCLUDED.knowhow_axis, "
                "raw_axis=EXCLUDED.raw_axis, "
                "expected_family=EXCLUDED.expected_family, "
                "interaction_kind=EXCLUDED.interaction_kind, "
                "template_params=EXCLUDED.template_params, "
                "active=TRUE, "
                "note=EXCLUDED.note, "
                "updated_at=now(), "
                "provenance=COALESCE(knowhow_interaction_probe.provenance, EXCLUDED.provenance)",
                (
                    probe_id,
                    prompt_template,
                    knowhow_axis,
                    raw_axis,
                    expected_family,
                    interaction_kind,
                    json.dumps(template_params, ensure_ascii=False),
                    PROVENANCE,
                    note,
                ),
            )
            n += cur.rowcount
        print(f"  knowhow_interaction_probe 建表 + seed:upsert 影響 {n} 列(冪等)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("IF NOT EXISTS 冪等", "IF NOT EXISTS" in DDL)
    chk("interaction_kind CHECK 五值", all(
        k in DDL for k in (
            "kh_x_kh", "principle_x_rd", "principle_x_principle",
            "principle_x_raw_bridge", "kh_x_feature_family",
        )
    ))
    chk("種子 14 列", len(SEED) == 14)
    chk("種子含 FP×solar 四變體", all(
        i in SEED_IDS for i in (
            "RKI-FP-SOLAR-CORE", "RKI-FP-SOLAR-PHYS",
            "RKI-FP-SOLAR-CHEM", "RKI-FP-SOLAR-APP",
        )
    ))
    chk("種子含 Pareto×solar", "RKI-PARETO-SOLAR" in SEED_IDS)
    chk("種子含通用哲學×研發模板", "RKI-PHILO-RD-TMPL" in SEED_IDS)
    chk("種子含孫子對照", "RKI-SUNZI-MGMT" in SEED_IDS)
    chk("種子含 AI×預測進化", all(
        i in SEED_IDS for i in ("RKI-AI-PREDICT-EVO", "RKI-AI-PREDICT-EVAL")
    ))
    chk("種子含 FP×AI 迭代", "RKI-FP-AI-ITER" in SEED_IDS)
    chk("種子含 FP×AI×預測 optional", "RKI-FP-AI-PREDICT" in SEED_IDS)
    chk("種子含 FP×投資預測迭代", "RKI-FP-PREDICT-ITER" in SEED_IDS)
    chk("種子含 AI×太陽能研發", "RKI-AI-SOLAR-RD" in SEED_IDS)
    chk("種子含 FP×AI×太陽能 optional", "RKI-FP-AI-SOLAR" in SEED_IDS)
    chk("COMMENT 載 #29b／非答案", "#29b" in DDL and "非答案" in DDL)
    chk("無領域 if/hardcode 答案樹字面於 DDL", "if 太陽能" not in DDL.lower())
    chk("所有種子 prompt 含 slot", all("{{" in s[1] for s in SEED))
    chk("AI×* 種子為 kh_x_kh", all(
        s[5] == "kh_x_kh" for s in SEED if s[0].startswith("RKI-AI-")
    ))
    chk("FP-AI-ITER 為 principle_x_rd", any(
        s[0] == "RKI-FP-AI-ITER" and s[5] == "principle_x_rd" for s in SEED
    ))
    chk("FP-PREDICT-ITER 為 principle_x_rd", any(
        s[0] == "RKI-FP-PREDICT-ITER" and s[5] == "principle_x_rd" for s in SEED
    ))
    chk("FP-AI-SOLAR 為 kh_x_kh", any(
        s[0] == "RKI-FP-AI-SOLAR" and s[5] == "kh_x_kh" for s in SEED
    ))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--show" in argv:
            return show(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

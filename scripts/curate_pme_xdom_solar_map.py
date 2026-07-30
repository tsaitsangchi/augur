#!/usr/bin/env python
"""PME-XDOM-SOLAR S1 — 太陽能供應鏈投資假說策展（investment school；禁 AI 生成）。

🎯 這支在做什麼（白話）：建立 investment school `solar_supply_invest`（太陽能材料／電池
   ／漿料／模組供應鏈概念），人撰 principle＋principle_factor_map 掛桶 A 已有 feature，
   provenance JSONB 標 xdom_loop=solar。冪等；不手改 validated_*；不灌 ERP／RKI／embedding。

守 #1 #15 #29；憲章 v1.47.0 跨域映射／禁 ai_generated；GATE-keep／FZ-keep；
計畫 PME-XDOM-SOLAR §S1；S0＝reports/augur_pme_xdom_solar_s0_20260729.md。

執行指令矩陣:
  python scripts/curate_pme_xdom_solar_map.py              # dry-run 印將寫列
  python scripts/curate_pme_xdom_solar_map.py --apply      # 寫入 DB
  python scripts/curate_pme_xdom_solar_map.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

PROVENANCE = {
    "xdom_loop": "solar",
    "curate": "pme_xdom_solar_s1",
    "plan": "augur_pme_xdom_solar_plan_20260729",
}

SCHOOL = {
    "name": "solar_supply_invest",
    "name_zh": "太陽能供應鏈投資（概念橋）",
    "core_thesis": (
        "以太陽能材料／電池／漿料／模組供應鏈公開文獻可溯源概念，"
        "建構可證偽之投資假說：品質穩定→毛利緩衝、產能週期→營收動能、"
        "原物料成本敏感→低槓桿估值緩衝、下游資本支出→籌碼認可、"
        "擴產後資產效率、週期高點回落風險。市場閘裁決生死。"
    ),
    "proponents": (
        "ITRPV Roadmap; Fraunhofer ISE Photovoltaics Report; "
        "BNEF Solar Supply Chain; IEA PVPS"
    ),
    "domain": "investment",
}

SOURCES = [
    (
        "ITRPV, International Technology Roadmap for Photovoltaic (ITRPV), "
        "14th ed., 2023",
        "report",
    ),
    (
        "Fraunhofer ISE, Photovoltaics Report, Fraunhofer Institute for "
        "Solar Energy Systems, 2024",
        "report",
    ),
    (
        "BloombergNEF, Solar Supply Chain — Module Cost Dynamics and "
        "Manufacturing Capacity, BNEF, 2023",
        "report",
    ),
]

PRINCIPLES = [
    {
        "statement": (
            "H1：製程／品質穩定性→毛利緩衝——供應鏈品質穩的廠商較能撐毛利分位、"
            "壓低無謂振幅（ITRPV 良率與成本學習曲線概念）。"
        ),
        "hypothesis": (
            "gross_margin_pctile 越高→未來報酬越高（＋）；"
            "range_mean_20d 越低→波動代理成本越小（−）；"
            "volatility_60d 越低→振幅受控（−）。"
        ),
        "factors": [
            ("gross_margin_pctile", 1),
            ("range_mean_20d", -1),
            ("volatility_60d", -1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "H2：產能／需求週期→營收成長——產能爬坡與訂單好轉反映於營收 YoY "
            "與中期動能（Fraunhofer 產能利用率週期概念）。"
        ),
        "hypothesis": (
            "monthly_revenue_yoy 越高→未來報酬越高（＋）；"
            "momentum_60d 越高→中期趨勢認可（＋）。"
        ),
        "factors": [
            ("monthly_revenue_yoy", 1),
            ("momentum_60d", 1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "H3：原物料成本敏感→估值／資產負債緩衝——成本衝擊期，"
            "低槓桿與合理估值較耐震（多晶矽／銀漿價格波動文獻）。"
        ),
        "hypothesis": (
            "debt_ratio 越低→耐震（−）；pe_ratio 越低→估值緩衝（−）；"
            "pb_ratio 越低→帳面安全邊際（−）。"
        ),
        "factors": [
            ("debt_ratio", -1),
            ("pe_ratio", -1),
            ("pb_ratio", -1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "H4：下游電子／綠能資本支出代理→籌碼認可——供應鏈贏家漸獲"
            "機構／外資持股認可（BNEF 產業鏈投資流向概念）。"
        ),
        "hypothesis": (
            "institutional_net_buy_ratio_20d 越高→未來報酬假說（＋）；"
            "foreign_holding_pct 越高→外資認可（＋）。"
        ),
        "factors": [
            ("institutional_net_buy_ratio_20d", 1),
            ("foreign_holding_pct", 1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "H5：擴產後資產效率／獲利能力——過擴產壓力下，ROE 與估值"
            "需同時成立才活（產業週期 overcapacity 文獻）。"
        ),
        "hypothesis": (
            "roe 越高→獲利效率（＋）；pe_ratio 越低→合理估值（−）。"
        ),
        "factors": [
            ("roe", 1),
            ("pe_ratio", -1),
        ],
        "domain_notes": [],
    },
    {
        "statement": (
            "H6：週期高點回落／過熱——位置過高後均值回歸風險"
            "（太陽能族群歷史泡沫與修正文獻）。"
        ),
        "hypothesis": (
            "range_position_120d 越高→回落風險越大（−）；"
            "days_since_high_252d 越久→離高點越遠、回歸壓力已釋放（＋）；"
            "momentum_20d 作對照（弱＋）。"
        ),
        "factors": [
            ("range_position_120d", -1),
            ("days_since_high_252d", 1),
            ("momentum_20d", 1),
        ],
        "domain_notes": [],
    },
]

# 近程拒 SEED（S0 §4；selftest 斷言不在 factors）
REJECTED_UNMAPPABLE = [
    "erp_dump_any",
    "rki_probe_hit_rate",
    "knowledge_embedding_as_feature",
    "ai_generated_principle",
    "solar_slurry_process",
    "turnover_mean_20d_as_inventory",
    "margin_usage_ratio_as_gross_margin",
    "ai_predict_mixed_seed",
]


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    feats: list[str] = []
    chk("school domain investment", SCHOOL["domain"] == "investment")
    chk("school name solar_supply_invest", SCHOOL["name"] == "solar_supply_invest")
    chk("provenance xdom_loop=solar", PROVENANCE.get("xdom_loop") == "solar")
    for cit, st in SOURCES:
        chk(f"no ai_generated src ({cit[:28]})", st != "ai_generated")
        chk("citation non-empty", bool(cit.strip()))
    for pr in PRINCIPLES:
        chk("statement non-empty", bool(pr["statement"].strip()))
        chk("hypothesis non-empty", bool(pr["hypothesis"].strip()))
        for f, d in pr["factors"]:
            feats.append(f)
            chk(f"dir±1 {f}", d in (-1, 1))
            chk(f"not rejected token {f}", f not in REJECTED_UNMAPPABLE)
        for note in pr.get("domain_notes") or []:
            chk("note_kind closed", note["note_kind"] in ("verbatim_quote", "human_authored"))
            chk("note no ai_generated", note["source_type"] != "ai_generated")
            chk("note citation", bool(note["citation"].strip()))
    chk("n principles ≥3", len(PRINCIPLES) >= 3)
    chk("n factors ≥5", len(feats) >= 5)
    chk("erp rejected", "erp_dump_any" in REJECTED_UNMAPPABLE)
    chk("slurry rejected", "solar_slurry_process" in REJECTED_UNMAPPABLE)
    chk("turnover name-clash rejected", "turnover_mean_20d_as_inventory" in REJECTED_UNMAPPABLE)
    # H1-H6 hypotheses present
    chk("H1-H6 covered", len(PRINCIPLES) == 6)
    # bucket-A features only
    bucket_a = {
        "monthly_revenue_yoy", "gross_margin_pctile", "debt_ratio", "roe",
        "pe_ratio", "pb_ratio", "momentum_20d", "momentum_60d", "volatility_60d",
        "range_mean_20d", "range_position_120d", "institutional_net_buy_ratio_20d",
        "foreign_holding_pct", "days_since_high_252d",
    }
    chk("all factors in bucket-A", set(feats) <= bucket_a)
    # I8：factor_map 僅來自 pr["factors"]；domain_notes 另迴圈、不作資格
    src = open(__file__, encoding="utf-8").read()
    apply_body = src.split("def apply_seed")[1].split("\ndef main")[0]
    map_loop = apply_body.split('for f, d in pr["factors"]')[1].split("for note in")[0]
    chk("I8 map loop ignores domain_map", "principle_domain_map" not in map_loop)
    chk(
        "I8 notes after maps",
        apply_body.index('for f, d in pr["factors"]') < apply_body.index("for note in"),
    )
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def apply_seed(conn, *, dry_run: bool) -> dict:
    from augur.core import db

    n_src = n_pri = n_map = n_note = 0
    n_school = 0
    new_maps: list[tuple] = []
    prov_json = json.dumps(PROVENANCE, ensure_ascii=False)
    name = SCHOOL["name"]

    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT school_id, domain FROM philosophy_school WHERE name=%s",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            if dry_run:
                print(f"  [dry] school ← {name} domain=investment")
                sid = -1
            else:
                cur.execute(
                    "INSERT INTO philosophy_school "
                    "(name, name_zh, core_thesis, proponents, domain) "
                    "VALUES (%s,%s,%s,%s,%s) RETURNING school_id",
                    (
                        name,
                        SCHOOL["name_zh"],
                        SCHOOL["core_thesis"],
                        SCHOOL["proponents"],
                        SCHOOL["domain"],
                    ),
                )
                sid = cur.fetchone()[0]
            n_school = 1
        else:
            sid, domain = row[0], row[1]
            if domain != "investment":
                raise RuntimeError(f"school {name} domain={domain!r} ≠ investment")

        if sid < 0:
            for cit, st in SOURCES:
                print(f"  [dry] source ← {cit[:70]}")
                n_src += 1
            for pr in PRINCIPLES:
                print(f"  [dry] principle ← {pr['statement'][:56]}")
                n_pri += 1
                for f, d in pr["factors"]:
                    if f in REJECTED_UNMAPPABLE:
                        raise ValueError(f"拒 SEED 不可對映: {f}")
                    print(f"  [dry] map ← {f} dir={d:+d}")
                    new_maps.append((name, f, d))
                    n_map += 1
                n_note += len(pr.get("domain_notes") or [])
            return {
                "school": name,
                "school_new": n_school,
                "sources_new": n_src,
                "principles_new": n_pri,
                "maps_new": n_map,
                "domain_notes_new": n_note,
                "new_map_pairs": new_maps,
                "rejected": list(REJECTED_UNMAPPABLE),
                "provenance": PROVENANCE,
                "dry_run": dry_run,
            }

        for cit, st in SOURCES:
            if st == "ai_generated":
                raise ValueError(f"禁 ai_generated: {cit}")
            cur.execute(
                "SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s",
                (sid, cit),
            )
            if not cur.fetchone():
                if dry_run:
                    print(f"  [dry] source ← {cit[:70]}")
                else:
                    cur.execute(
                        "INSERT INTO philosophy_source (school_id, citation, source_type) "
                        "VALUES (%s,%s,%s)",
                        (sid, cit, st),
                    )
                n_src += 1

        for pr in PRINCIPLES:
            cur.execute(
                "SELECT principle_id FROM philosophy_principle "
                "WHERE school_id=%s AND statement=%s",
                (sid, pr["statement"]),
            )
            prow = cur.fetchone()
            if prow:
                pid = prow[0]
                if not dry_run:
                    cur.execute(
                        "UPDATE philosophy_principle SET hypothesis=%s WHERE principle_id=%s",
                        (pr["hypothesis"], pid),
                    )
            else:
                if dry_run:
                    print(f"  [dry] principle ← {pr['statement'][:56]}")
                    pid = -1
                else:
                    cur.execute(
                        "INSERT INTO philosophy_principle (school_id, statement, hypothesis) "
                        "VALUES (%s,%s,%s) RETURNING principle_id",
                        (sid, pr["statement"], pr["hypothesis"]),
                    )
                    pid = cur.fetchone()[0]
                n_pri += 1

            for f, d in pr["factors"]:
                if f in REJECTED_UNMAPPABLE:
                    raise ValueError(f"拒 SEED 不可對映: {f}")
                if pid < 0:
                    new_maps.append((name, f, d))
                    n_map += 1
                    continue
                cur.execute(
                    "SELECT map_id FROM principle_factor_map "
                    "WHERE principle_id=%s AND feature=%s",
                    (pid, f),
                )
                mrow = cur.fetchone()
                if mrow:
                    if not dry_run:
                        cur.execute(
                            "UPDATE principle_factor_map SET direction=%s, "
                            "provenance=COALESCE(provenance,'{}'::jsonb) || %s::jsonb "
                            "WHERE map_id=%s",
                            (d, prov_json, mrow[0]),
                        )
                else:
                    if dry_run:
                        print(f"  [dry] map ← {f} dir={d:+d}")
                    else:
                        cur.execute(
                            "INSERT INTO principle_factor_map "
                            "(principle_id, feature, direction, provenance) "
                            "VALUES (%s,%s,%s,%s::jsonb)",
                            (pid, f, d, prov_json),
                        )
                    new_maps.append((name, f, d))
                    n_map += 1

            for note in pr.get("domain_notes") or []:
                if note["source_type"] == "ai_generated":
                    raise ValueError("禁 ai_generated domain note")
                if note["note_kind"] not in ("verbatim_quote", "human_authored"):
                    raise ValueError(f"bad note_kind: {note['note_kind']}")
                if pid < 0:
                    n_note += 1
                    continue
                cur.execute(
                    "SELECT map_id FROM principle_domain_map "
                    "WHERE principle_id=%s AND domain=%s",
                    (pid, note["domain"]),
                )
                nrow = cur.fetchone()
                if nrow:
                    if not dry_run:
                        cur.execute(
                            "UPDATE principle_domain_map SET note_kind=%s, application_note=%s, "
                            "citation=%s, source_type=%s WHERE map_id=%s",
                            (
                                note["note_kind"],
                                note["application_note"],
                                note["citation"],
                                note["source_type"],
                                nrow[0],
                            ),
                        )
                else:
                    if dry_run:
                        print(
                            f"  [dry] domain_note ← {note['domain']} "
                            f"kind={note['note_kind']}"
                        )
                    else:
                        cur.execute(
                            "INSERT INTO principle_domain_map "
                            "(principle_id, domain, note_kind, application_note, "
                            "citation, source_type) VALUES (%s,%s,%s,%s,%s,%s)",
                            (
                                pid,
                                note["domain"],
                                note["note_kind"],
                                note["application_note"],
                                note["citation"],
                                note["source_type"],
                            ),
                        )
                    n_note += 1

    return {
        "school": name,
        "school_new": n_school,
        "sources_new": n_src,
        "principles_new": n_pri,
        "maps_new": n_map,
        "domain_notes_new": n_note,
        "new_map_pairs": new_maps,
        "rejected": list(REJECTED_UNMAPPABLE),
        "provenance": PROVENANCE,
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PME-XDOM-SOLAR S1 策展")
    ap.add_argument("--apply", action="store_true", help="寫入 DB（預設 dry-run）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    from augur.core import db

    if not db.ping():
        print("SKIP: DB 不可達", file=sys.stderr)
        return 2

    dry = not args.apply
    with db.connect() as conn:
        stats = apply_seed(conn, dry_run=dry)
    print(f"{'DRY-RUN' if dry else 'APPLIED'}: {stats}")
    print(f"rejected (no INSERT): {REJECTED_UNMAPPABLE}")
    if dry:
        print("（加 --apply 才寫入）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

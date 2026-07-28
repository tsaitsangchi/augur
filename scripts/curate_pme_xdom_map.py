#!/usr/bin/env python
"""PME-XDOM-SUNZI-MGMT S1 — 孫子×企管文獻橋策展（investment 假說鏈；禁 AI 生成）。

🎯 這支在做什麼（白話）：把孫子兵法×企管文獻橋的可證偽假說，寫進既有
   investment school `sun_tzu` 的 principle＋principle_factor_map（庫內已有 feature），
   可選 principle_domain_map 應用注記（domain＝business_mgmt；**非**量化資格）。
   provenance JSONB 標 xdom_loop=sunzi_mgmt。冪等；不手改 validated_*；不灌 ERP dump。

守 #1 #15 #29；憲章 v1.47.0 跨域映射／禁 ai_generated；GATE-keep／FZ-keep；計畫 PME-XDOM §3 S1。

執行指令矩陣:
  python scripts/curate_pme_xdom_map.py              # dry-run 印將寫列
  python scripts/curate_pme_xdom_map.py --apply      # 寫入 DB
  python scripts/curate_pme_xdom_map.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

# 人撰 SEED：citation 須可核；source_type≠ai_generated。
# 古典＝公版孫子；企管橋＝McNeilly／Wee et al.（人讀後撰假說，非 AI 摘要入庫）。
PROVENANCE = {
    "xdom_loop": "sunzi_mgmt",
    "curate": "pme_xdom_s1",
    "plan": "augur_pme_cross_domain_evolution_enable_plan_20260728",
}

XDOM_SUNZI_MGMT_SEED = {
    "name": "sun_tzu",
    "sources": [
        ("孫武, 孫子兵法（十三篇）, 約西元前 5 世紀", "book"),
        (
            "Mark McNeilly, Sun Tzu and the Art of Business, Oxford University Press, 1996 (rev. 2012)",
            "book",
        ),
        (
            "Wee Chow Hou, Lee Khai Sheang & Bambang Walujo Hidajat, "
            "Sun Tzu: War and Management, Addison-Wesley, 1991",
            "book",
        ),
    ],
    "principles": [
        {
            "statement": (
                "「知彼知己，百戰不殆」（謀攻）——企管情報／對手動向優勢之投資假說："
                "機構與官股籌碼代理資訊優勢。"
            ),
            "hypothesis": (
                "gov_bank_net_buy_60d／top_holders_pct／inst_cumflow_position_60d 越高 "
                "→ 未來報酬越高（正向；與 smart_money／cycle 共族、異域文獻橋標註）。"
            ),
            "factors": [
                ("gov_bank_net_buy_60d", 1),
                ("top_holders_pct", 1),
                ("inst_cumflow_position_60d", 1),
            ],
            "domain_notes": [
                {
                    "domain": "business_mgmt",
                    "note_kind": "human_authored",
                    "application_note": (
                        "將「知彼知己」對映為企業競爭情報與對手動向掌握；"
                        "量化載體另走 investment school 全鏈，本注記非資格憑據。"
                    ),
                    "citation": (
                        "Wee Chow Hou et al., Sun Tzu: War and Management, Addison-Wesley, 1991; "
                        "孫武, 孫子兵法·謀攻"
                    ),
                    "source_type": "book",
                }
            ],
        },
        {
            "statement": (
                "「先為不可勝」「先勝而後求戰」（形／軍形）——企管先立不敗："
                "財務槓桿低、獲利品質穩、價格振幅受控之緩衝假說。"
            ),
            "hypothesis": (
                "debt_ratio 越低、roe 越高、range_mean_20d 越低 "
                "→ 風險調整後報酬假說（debt−／roe＋／range−）。"
            ),
            "factors": [
                ("debt_ratio", -1),
                ("roe", 1),
                ("range_mean_20d", -1),
            ],
            "domain_notes": [
                {
                    "domain": "business_mgmt",
                    "note_kind": "human_authored",
                    "application_note": (
                        "將「先勝／不可勝」對映為企業先備資源與風險緩衝再擴張；"
                        "注記軸＝business_mgmt，量化仍經 investment map。"
                    ),
                    "citation": (
                        "Mark McNeilly, Sun Tzu and the Art of Business, OUP, 1996/2012; "
                        "孫武, 孫子兵法·形"
                    ),
                    "source_type": "book",
                }
            ],
        },
        {
            "statement": (
                "「兵之形，避實而擊虛」（虛實）——企管資源避開對手堅實、攻擊薄弱："
                "估值虛實之投資假說（帳面／市值比）。"
            ),
            "hypothesis": "pb_ratio 越低 → 未來報酬越高（負向 IC；與 value 共族）。",
            "factors": [("pb_ratio", -1)],
            "domain_notes": [
                {
                    "domain": "business_mgmt",
                    "note_kind": "verbatim_quote",
                    "application_note": "兵之形，避實而擊虛。",
                    "citation": "孫武, 孫子兵法·虛實",
                    "source_type": "book",
                }
            ],
        },
        {
            "statement": (
                "「兵貴勝，不貴久」「其勢險，其節短」——企管時點與節奏："
                "近月動能窗為勢節代理。"
            ),
            "hypothesis": "momentum_20d 越高 → 未來報酬越高（正向；動能短窗變體）。",
            "factors": [("momentum_20d", 1)],
            "domain_notes": [],
        },
        {
            "statement": (
                "「不戰而屈人之兵」（謀攻）——企管以勢／質取勝："
                "毛利分位代理品質壁壘。"
            ),
            "hypothesis": (
                "gross_margin_pctile 越高 → 未來報酬越高（正向；品質族；"
                "異域文獻橋標註）。"
            ),
            "factors": [("gross_margin_pctile", 1)],
            "domain_notes": [
                {
                    "domain": "business_mgmt",
                    "note_kind": "human_authored",
                    "application_note": (
                        "將「不戰而屈人之兵」對映為以組織優勢／品質壁壘取勝、減少硬拚消耗；"
                        "本注記非 G-PROM 憑據。"
                    ),
                    "citation": (
                        "Mark McNeilly, Sun Tzu and the Art of Business, OUP, 1996/2012; "
                        "孫武, 孫子兵法·謀攻"
                    ),
                    "source_type": "book",
                }
            ],
        },
    ],
}

# 近程拒 SEED（書面鎖；selftest 斷言不在 factors）
REJECTED_UNMAPPABLE = [
    "erp_dump_any",
    "tiptop_4gl_op",
    "solar_slurry_process",
]


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    feats: list[str] = []
    for cit, st in XDOM_SUNZI_MGMT_SEED["sources"]:
        chk(f"no ai_generated src ({cit[:28]})", st != "ai_generated")
        chk("citation non-empty", bool(cit.strip()))
    for pr in XDOM_SUNZI_MGMT_SEED["principles"]:
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
            chk("domain=business_mgmt note axis", note["domain"] == "business_mgmt")
    chk("school is sun_tzu investment carrier", XDOM_SUNZI_MGMT_SEED["name"] == "sun_tzu")
    chk("provenance xdom_loop", PROVENANCE.get("xdom_loop") == "sunzi_mgmt")
    chk("n principles ≥3", len(XDOM_SUNZI_MGMT_SEED["principles"]) >= 3)
    chk("n new factors ≥5", len(feats) >= 5)
    chk("erp rejected listed", "erp_dump_any" in REJECTED_UNMAPPABLE)
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

    sch = XDOM_SUNZI_MGMT_SEED
    name = sch["name"]
    n_src = n_pri = n_map = n_note = 0
    new_maps: list[tuple] = []
    prov_json = json.dumps(PROVENANCE, ensure_ascii=False)

    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT school_id, domain FROM philosophy_school WHERE name=%s",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            raise RuntimeError(f"school {name} 不存在——勿新建異域 school 跳過 investment 鏈")
        sid, domain = row[0], row[1]
        if domain != "investment":
            raise RuntimeError(f"school {name} domain={domain!r} ≠ investment")

        for cit, st in sch["sources"]:
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

        for pr in sch["principles"]:
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

            if pid < 0:
                n_note += len(pr.get("domain_notes") or [])
                continue
            for note in pr.get("domain_notes") or []:
                if note["source_type"] == "ai_generated":
                    raise ValueError("禁 ai_generated domain note")
                if note["note_kind"] not in ("verbatim_quote", "human_authored"):
                    raise ValueError(f"bad note_kind: {note['note_kind']}")
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
    ap = argparse.ArgumentParser(description="PME-XDOM SUNZI-MGMT S1 策展")
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

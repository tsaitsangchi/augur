#!/usr/bin/env python
"""臂批收槍後接力報告 — S-5 決策表＋A′(A13) 首判＋v2 逐格對照,一鍵全套(hugo 2026-07-28「都做」①)。

🎯 這支在做什麼(白話):v2 三臂批(pack@舊集新尺 → v2 活臂×2)收槍後,深夜零手工出三件:
   (1) **S-5 決策表**:pack pp_3ab2efebb04e@舊集(4183475c5089)新尺逐層軸值 vs behavior/對照臂,
       套**對話預註冊規則(2026-07-28)**——R1 一票否決:L1.F<1.0=捏造於新尺實質化→建議 retire;
       R2 輔助記錄:L3.A 是否回升 ≥0.5(僅減緩、不翻 R1)。**印 retire/keep 雙 SQL,執行唯 hugo**(P5.W2)。
   (2) **A′(A13) 首判**:轉呼 verify_evolution_acceptance.py 摘 A13 段(能力格證據等級)。
   (3) **v2 逐格對照矩陣**:凍結集 4e15a143ff4b 全臂 per-cell F(能力格 scoped 視窗 (0.500,1.000])。
   資料缺=誠實印「待臂落地」;本支唯讀+寫報告檔,零 UPDATE 帳本、零執行 SQL。
守 #15(缺=待,不編)· #9/#10(全出 eval run 帳本)· #28(本地零 usage)· #29a/d;S-5 人閘 SSOT=
   audits/V2-SUNSET-C-DISPUTED-20260727.md §五。

執行指令矩陣:
  python scripts/report_post_batch_verdicts.py             # 無參數:現況(哪些臂已落/缺,唯讀)
  python scripts/report_post_batch_verdicts.py --run       # 全套報告(stdout+寫 reports/)
  python scripts/report_post_batch_verdicts.py --selftest  # 零 DB 紅綠(S-5 規則鎖/分層聚合)
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

OLD_SET, V2_SET = "4183475c5089", "4e15a143ff4b"
PACK_ARM = "pack:pp_3ab2efebb04e"
CTRL = ("ceiling", "floor", "shuffled", "mismatched", "robot")


def layer_axis_means(per_item):
    """per_item → {layer: {axis: mean}}(axis 值 None 不計)。純函式。"""
    acc = defaultdict(lambda: defaultdict(list))
    for it in per_item:
        for ax in ("f", "p", "a"):
            if it.get(ax) is not None:
                acc[it["layer"]][ax].append(it[ax])
    return {ly: {ax: sum(v) / len(v) for ax, v in axs.items()} for ly, axs in acc.items()}


def s5_rule(l1_f, l3_a):
    """S-5 對話預註冊規則(2026-07-28)。回 (建議, 理由)。純函式。
    R1 一票否決:L1.F < 1.0 ⇒ 新尺下 L1 仍有不合格答(捏造/錯答被實質扣分)→ retire;
    R2 輔助:L3.A ≥ 0.5 記回升(僅減緩敘述,不翻 R1)。二者皆為建議——執行唯 hugo。"""
    if l1_f is None:
        return ("待資料", "pack@舊集新尺 run 未落地")
    if l1_f < 1.0:
        why = f"R1 一票否決:L1.F={l1_f:.4f} < 1.0(新尺實質扣分)"
        if l3_a is not None and l3_a >= 0.5:
            why += f";R2 記:L3.A={l3_a:.4f} ≥0.5 有回升(不翻 R1)"
        return ("retire", why)
    why = f"L1.F=1.0 無捏造殘留" + (f";L3.A={l3_a:.4f}" if l3_a is not None else "")
    return ("keep", why)


def _latest_run(cur, set_id, arm):
    cur.execute("""SELECT run_id, eval_code_hash, axis_f, axis_p, axis_a, is_invalid, detail,
                          created_at::timestamp(0)
                   FROM local_model_eval_run WHERE set_id=%s AND arm=%s
                   ORDER BY created_at DESC LIMIT 1""", (set_id, arm))
    return cur.fetchone()


def build_report():
    L = [f"# 臂批接力報告(S-5/A′/v2 對照)——{date.today()}", ""]
    with db.connect() as conn, db.transaction(conn) as cur:
        # ── (1) S-5 ──
        L.append("## 一、S-5:pack pp_3ab2efebb04e 去留(人閘;規則=對話預註冊 2026-07-28)")
        r = _latest_run(cur, OLD_SET, PACK_ARM)
        if r is None:
            L.append("(pack@舊集新尺 run 未落地——待臂)")
        else:
            _, ch, f, p, a, inv, det, ts = r
            det = det if isinstance(det, dict) else json.loads(det or "{}")
            lam = layer_axis_means(det.get("per_item", []))
            L.append(f"run@{ts} hash={ch}{'(INVALID 註記,數字僅參考)' if inv else ''}:總 F={f} P={p} A={a}")
            for ly in sorted(lam):
                L.append("  " + ly + ": " + " ".join(f"{ax.upper()}={m:.4f}" for ax, m in sorted(lam[ly].items())))
            b = _latest_run(cur, OLD_SET, "behavior")
            if b:
                L.append(f"對照 behavior 同集:F={b[2]} P={b[3]} A={b[4]}" + ("(INVALID)" if b[5] else ""))
            l1f = lam.get("L1", {}).get("f")
            l3a = lam.get("L3", {}).get("a")
            verdict, why = s5_rule(l1f, l3a)
            L.append(f"**規則判:建議 {verdict}**——{why}")
            L.append("執行唯 hugo 親跑(二選一):")
            L.append("  retire: UPDATE local_model_version SET status='retired' WHERE version_id='pp_3ab2efebb04e';")
            L.append("          (退場後 serving 空缺——advisor 回 base 行為,需知悉)")
            L.append("  keep:   UPDATE local_model_version SET eval_result = eval_result || "
                     "'{\"s5_keep_ratified\":\"hugo\"}' WHERE version_id='pp_3ab2efebb04e';")
        # ── (2) A′/A13 ──
        L.append("\n## 二、A′(A13) 首判(verify_evolution_acceptance 摘錄)")
        try:
            out = subprocess.run([sys.executable, str(Path(__file__).with_name("verify_evolution_acceptance.py"))],
                                 capture_output=True, text=True, timeout=600).stdout
            sec = [ln for ln in out.splitlines() if "A13" in ln or "A′" in ln or "evidence_level" in ln]
            L += ["  " + ln.strip() for ln in sec] or ["  (驗收器輸出無 A13 段——人工查)"]
        except Exception as e:  # noqa: BLE001
            L.append(f"  (驗收器呼叫失敗:{type(e).__name__}——誠實記,人工跑)")
        # ── (3) v2 逐格 ──
        L.append("\n## 三、v2 凍結集逐格 F(能力格 scoped 視窗 (0.500,1.000])")
        cur.execute("""SELECT arm, detail FROM local_model_eval_run
                       WHERE set_id=%s AND NOT is_invalid
                       ORDER BY created_at DESC""", (V2_SET,))
        seen, live_n = set(), 0
        rows = []
        for arm, det in cur.fetchall():
            if arm in seen:
                continue
            seen.add(arm)
            det = det if isinstance(det, dict) else json.loads(det or "{}")
            lam = layer_axis_means(det.get("per_item", []))
            live_n += arm not in CTRL
            rows.append((arm, {ly: axs.get("f") for ly, axs in lam.items()}))
        cells = sorted({c for _, m in rows for c in m if m[c] is not None})
        L.append("| arm | " + " | ".join(cells) + " |")
        L.append("|" + "---|" * (len(cells) + 1))
        for arm, m in sorted(rows, key=lambda x: (x[0] in CTRL, x[0])):
            L.append(f"| {arm}{'' if arm in CTRL else ' **(活臂)**'} | "
                     + " | ".join(f"{m.get(c):.3f}" if m.get(c) is not None else "—" for c in cells) + " |")
        if live_n == 0:
            L.append("(v2 活臂 0——待臂落地;A′ 須活臂能力格嚴格 >0.500 且 ≥2 run 皆勝)")
    return "\n".join(L)


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        for set_id, arm, label in ((OLD_SET, PACK_ARM, "S-5 pack@舊集"),
                                   (OLD_SET, "behavior", "behavior@舊集"),
                                   (V2_SET, "behavior", "v2 behavior"),
                                   (V2_SET, PACK_ARM, "v2 pack")):
            r = _latest_run(cur, set_id, arm)
            print(f"  {label:16}: " + (f"落地 {r[7]}" + ("(INVALID)" if r[5] else "") if r else "未落地"))
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("S-5 R1:L1.F<1.0=建議 retire", s5_rule(0.733, 0.6)[0] == "retire")
    chk("S-5 R2:L3.A 回升僅記錄不翻 R1", "不翻 R1" in s5_rule(0.733, 0.6)[1])
    chk("S-5:L1.F=1.0=建議 keep", s5_rule(1.0, 0.3)[0] == "keep")
    chk("S-5:無資料=待資料非亂判", s5_rule(None, None)[0] == "待資料")
    lam = layer_axis_means([{"layer": "L1", "f": 1, "a": None}, {"layer": "L1", "f": 0},
                            {"layer": "L3", "f": 1, "a": 0.5}])
    chk("分層聚合:None 軸不計/均值正確", lam["L1"]["f"] == 0.5 and "a" not in lam["L1"]
        and lam["L3"]["a"] == 0.5)
    import inspect
    src = inspect.getsource(build_report)
    chk("唯讀:零 UPDATE/INSERT 帳本(SQL 僅字串印給人)", "cur.execute(\"UPDATE" not in src
        and "cur.execute(\"INSERT" not in src)
    chk("缺料=誠實待臂", "待臂" in src)
    chk("雙 SQL 皆在(執行唯 hugo)", "retire:" in src and "keep:" in src)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="臂批接力報告(S-5/A′/v2;唯讀)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.run:
        rpt = build_report()
        print(rpt)
        out = Path(__file__).resolve().parent.parent / "reports" / f"laievo_post_batch_{date.today():%Y%m%d}.md"
        out.write_text(rpt + "\n", encoding="utf-8")
        print(f"\n(已寫 {out.name})")
        return 0
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())

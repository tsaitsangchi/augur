#!/usr/bin/env python3
"""🎯 criteria_sha 覆算哨兵——逐列覆算兩張 gate 表之指紋，抓「payload 被改而 sha 欄沒動」的挪門柱。

為什麼需要（W2 D2S 呈案 §2.3 殘項①②）：goalpost trigger 護的是 criteria_sha **欄**不被改，
不驗「criteria payload 仍與 sha 相符」——UPDATE criteria 而不動 sha 欄可過 trigger；
且 evolution_prereg_gate 唯一結算先例 settle_sunset_gate.py **不覆算**。真鎖＝覆算；
本支＝表級覆算哨兵：凡列必查、逐列重算、與 stored sha 比對。

**本支嚴格唯讀**（SELECT-only＋READ ONLY 交易＋收尾 ROLLBACK）——「verify_* 非唯讀」
之 07-30 陷阱在此不成立。零 DDL、零 DB 寫入。

sha 錨定口徑（2026-08-02 live 親驗；兩表三口徑，勿憑記憶改）：
  · evolution_prereg_gate（house 口徑，64-hex）：criteria_sha = sha256(criteria->>'criteria_text')。
    親驗 SQL：SELECT criteria_sha = encode(sha256(convert_to(criteria->>'criteria_text','UTF8')),'hex')
    FROM evolution_prereg_gate → V2-SUNSET t／V2-SUNSET-r2 t（全表 2 列皆 t）；
    同式先例＝gate_raise_sunset_deadline.py:90；D2S 呈案 §2.3 同口徑。
  · direction_gate 兩代口徑並存（依 stored sha 長度判代；2026-08-02 全表 29 列逐列實測，
    每列恰中一口徑、零 NONE）：
    - 16-hex（現行 18 列）＝sha256(json.dumps(c, sort_keys=True, separators=(",",":"),
      ensure_ascii=False))[:16]——preregister_direction_gate.py `_sha` 同式。
    - 12-hex（legacy 11 列：a3 三列 superseded＋meta_replay 兩列＋replay 六列）＝
      sha256(json.dumps(c, sort_keys=True, ensure_ascii=False))[:12]（**預設分隔符**）；
      即 preregister_direction_gate.py:167 註記之「12碼/無 separators」手刻配方——
      列仍在庫，依其自身口徑覆算（換口徑重算＝假紅，D2S §8-3 之對照證據）。
    - 其他長度＝無錨定口徑 ⇒ 覆算不能 ⇒ 判 MISMATCH（fail-closed、詳列印出）。

分類：MATCH／MISMATCH（大聲、rc=1——那是 Steward 級發現：只回報、**不得修**、不得
hand-patch #12）／NO_SHA（誠實列出、不算過；現兩表 criteria_sha 皆 NOT NULL，
此類防未來 schema 漂移與空字串）。

掛週報候選：本哨兵適合掛入週日儀表（同 F3 防鏽哨模式，週跑一次零成本）；掛入屬另日一行修，本支不改週報碼。

守 #9/#10（每個 sha 覆算可溯源）· #15/#35（回歸鎖三規則：純函式餵真列 fixture、
紅綠雙向、禁字面斷言；突變驗紅證據見 commit 訊息）· #29(a)(d)· #6（唯讀零副作用）。

執行指令矩陣
------------
    python3 scripts/verify_gate_sha_integrity.py             # 無參數＝--check（唯讀全掃＋分類統計）
    python3 scripts/verify_gate_sha_integrity.py --check     # 同上；任一 MISMATCH 則 exit 1
    python3 scripts/verify_gate_sha_integrity.py --selftest  # 紅綠自測（免 DB 免 API；真列形 fixture）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter

import _bootstrap  # noqa: F401

# ───────────────────────── 純函式（判準本體；selftest 直接餵真列） ─────────────────────────


def sha_verdict(stored_sha, recomputed_sha) -> str:
    """判準純函式：MATCH／MISMATCH／NO_SHA。

    覆算不能（recomputed None）而 stored 有值 ⇒ MISMATCH（fail-closed：
    「無法驗」不得靜默當過）；stored 空/None ⇒ NO_SHA（誠實列出、不算過）。
    """
    if stored_sha is None or str(stored_sha).strip() == "":
        return "NO_SHA"
    if recomputed_sha is not None and stored_sha == recomputed_sha:
        return "MATCH"
    return "MISMATCH"


def recompute_prereg_sha(criteria):
    """evolution_prereg_gate house 口徑：sha256(criteria_text 字串) 64-hex；缺鍵 ⇒ None（覆算不能）。"""
    if not isinstance(criteria, dict):
        return None
    text = criteria.get("criteria_text")
    if not isinstance(text, str):
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def recompute_direction_sha(criteria, stored_sha):
    """direction_gate 口徑選擇＝依 stored sha 長度（兩代並存，見檔頭親驗）。回 (recomputed|None, 口徑名)。"""
    n = len(stored_sha or "")
    if n == 16:
        j = json.dumps(criteria, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(j.encode("utf-8")).hexdigest()[:16], "16hex-compact"
    if n == 12:
        j = json.dumps(criteria, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(j.encode("utf-8")).hexdigest()[:12], "12hex-legacy"
    return None, f"unknown-scheme(len={n})"


# ───────────────────────── 唯讀掃描 ─────────────────────────


def check() -> int:
    from augur.core import db

    counts: Counter = Counter()
    loud: list[str] = []
    try:
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SET TRANSACTION READ ONLY")  # 唯讀硬保證（第一句、整段交易生效）

            cur.execute("""SELECT gate_id, status, criteria, criteria_sha
                           FROM evolution_prereg_gate ORDER BY gate_id""")
            prereg = cur.fetchall()
            for gid, st, c, sha in prereg:
                v = sha_verdict(sha, recompute_prereg_sha(c))
                counts[("evolution_prereg_gate", v)] += 1
                line = f"  {v:8s} {gid} (status={st}, 口徑=house-64hex)"
                print(line)
                if v != "MATCH":
                    loud.append(line)

            cur.execute("""SELECT gate_id, status, criteria, criteria_sha
                           FROM direction_gate ORDER BY gate_id""")
            dgate = cur.fetchall()
            for gid, st, c, sha in dgate:
                rec, scheme = recompute_direction_sha(c, sha)
                v = sha_verdict(sha, rec)
                counts[("direction_gate", v)] += 1
                line = f"  {v:8s} {gid} (status={st}, 口徑={scheme})"
                print(line)
                if v != "MATCH":
                    loud.append(line)

            conn.rollback()  # 唯讀收尾：零殘留
    except Exception as e:  # DB 不可達等——誠實報錯、不裸 traceback
        print(f"✗ DB 掃描失敗（非 sha 判定）：{type(e).__name__}: {e}")
        return 2

    print("\n── 分類統計 ──")
    for table in ("evolution_prereg_gate", "direction_gate"):
        m = counts[(table, "MATCH")]
        x = counts[(table, "MISMATCH")]
        n = counts[(table, "NO_SHA")]
        print(f"  {table}: {m + x + n} 列 → MATCH={m} MISMATCH={x} NO_SHA={n}")

    mismatches = sum(v for (t, verdict), v in counts.items() if verdict == "MISMATCH")
    if mismatches:
        print(f"\n⛔ MISMATCH={mismatches}——挪門柱嫌疑（payload 與 sha 不符）。")
        print("   這是 Steward 級發現：只回報、不得修、不得 hand-patch（#12）。逐列：")
        for line in loud:
            print(line)
        return 1
    no_sha = sum(v for (t, verdict), v in counts.items() if verdict == "NO_SHA")
    if no_sha:
        print(f"\n⚠ NO_SHA={no_sha} 列無指紋可驗（誠實列出、不算過）。")
    print("\n✓ 全列覆算與 stored sha 一致（NO_SHA 除外）。")
    return 0


# ───────────────────────── 紅綠自測（#35：真列形 fixture、免 DB） ─────────────────────────

# fixture 皆為 2026-08-02 live 真列逐字拷貝；expected sha 之出處＝live DB stored 值
# （獨立於本檔覆算函式——非「函式算給函式比」之套套邏輯）。

_FIX_PREREG_TEXT = (
    "期限：2026-07-31\n"
    "(a) arena 至少結算一批且方向門有可讀數；或\n"
    "(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或\n"
    "(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。\n"
    "全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。"
)
_FIX_PREREG_SHA = "2d2b9f5d7c93372ba513798935fd13cac50d7f038ab14fec59959ad4acb2db8c"  # V2-SUNSET-r2 live

_FIX_DGATE16 = {  # dgate_H_20 live 真列
    "base_rate_rule": "多數類基線與 p_bar 一律同窗實算入 result_snapshot,不預先編數(H82 個股 up-rate=增訓時實算)",
    "econ_axis": "經濟終關(run_economic_eval 同口徑 cost 0.00585)=獨立標示軸,不在 GATE 內;展示分級閉集依憲章 v1.42.0",
    "fail_path": "任一關不過=evaluated_fail 判死留檔、永不出 UI;重試=另立新 gate(舊列 superseded)",
    "gate_rules": {
        "i_hitrate": "hit-rate 顯著優於同窗多數類樸素基線 max(p_bar, 1-p_bar);顯著性=date-cluster/HAC Eff-t p<0.05(合併口徑,禁 iid)",
        "ii_brier": "OOS Brier < 基線 p_bar*(1-p_bar)(同窗實算)",
        "iii_calibration": {
            "ece_ceiling": 0.05,
            "ece_source": "judgestop_threshold.calib_late_ece_ceiling(DB 讀值)",
            "quantile_monotone": "p_up 十分位 vs 實現上漲頻率單調(Spearman>0)",
        },
    },
    "horizon_td": 20,
    "nonoverlap_n": 213,
    "scoring": "horizon 級聚合;禁單股準確率;abstain 無(方向機率必出);FREEZE 內=歷史 walk-forward OOS 非 live",
}
_FIX_DGATE16_SHA = "fd45772dbd56e54e"  # dgate_H_20 live

_FIX_DGATE12 = {  # dgate_meta_replay_B2_ridge live 真列（legacy 12-hex 配方）
    "estimand": {
        "diff": "ic_next - ic_next_static",
        "exclude": "首 cutoff(靜態=自身)",
        "key_col": "model",
        "min_clusters": 60,
        "model_id": "B2_ridge",
        "proc_sha": "評時指定單一家族,跨 sha 禁混",
        "table": "meta_replay_perf",
    },
    "fail_path": "不過=evaluated_fail 判死留檔;n<60=不可判非 fail;換程序=新 proc_sha 新家族",
    "gate_rules": {
        "i_gain": "diff 序列 HAC Eff-t 單尾 p<0.05(程序增益>0;禁 iid)",
        "ii_floor": "mean(ic_next) ≥ 0.9×mean(ic_next_static)(防『贏在基準爛』)",
        "iii_turnover": "prodset 逐期 Jaccard 異動率併報(揭露不判)",
    },
    "scope": "meta-確立(作用域=固定工具箱程序重演;META-REPLAY 計畫 §二三刀章)",
    "version": "meta-replay",
}
_FIX_DGATE12_SHA = "7738586f7371"  # dgate_meta_replay_B2_ridge live


def _selftest() -> int:
    import copy

    fails: list[str] = []

    def chk(name, ok):
        print(f"  {'✓' if ok else '✗'} {name}")
        if not ok:
            fails.append(name)

    # ── 綠向：真列覆算必須重現 live stored sha（anchor 出處＝DB，非本檔函式）──
    chk("prereg 真列覆算＝live sha（64-hex）",
        recompute_prereg_sha({"criteria_text": _FIX_PREREG_TEXT}) == _FIX_PREREG_SHA)
    rec16, scheme16 = recompute_direction_sha(_FIX_DGATE16, _FIX_DGATE16_SHA)
    chk("dgate 16-hex 真列覆算＝live sha 且口徑名正確",
        rec16 == _FIX_DGATE16_SHA and scheme16 == "16hex-compact")
    rec12, scheme12 = recompute_direction_sha(_FIX_DGATE12, _FIX_DGATE12_SHA)
    chk("dgate 12-hex legacy 真列覆算＝live sha 且口徑名正確",
        rec12 == _FIX_DGATE12_SHA and scheme12 == "12hex-legacy")
    chk("verdict 綠向：同 sha ⇒ MATCH",
        sha_verdict(_FIX_PREREG_SHA, recompute_prereg_sha({"criteria_text": _FIX_PREREG_TEXT})) == "MATCH")

    # ── 紅向：payload 突變（＝本哨兵存在的理由：改文不改 sha 欄）⇒ 必判 MISMATCH ──
    mut_text = _FIX_PREREG_TEXT.replace("2026-07-31", "2026-12-31", 1)
    chk("prereg 突變（改期限一字）⇒ MISMATCH",
        sha_verdict(_FIX_PREREG_SHA, recompute_prereg_sha({"criteria_text": mut_text})) == "MISMATCH")
    mut16 = copy.deepcopy(_FIX_DGATE16)
    mut16["gate_rules"]["iii_calibration"]["ece_ceiling"] = 0.50  # 挪門柱：放寬校準天花板
    chk("dgate 16-hex 突變（ece_ceiling 0.05→0.50）⇒ MISMATCH",
        sha_verdict(_FIX_DGATE16_SHA, recompute_direction_sha(mut16, _FIX_DGATE16_SHA)[0]) == "MISMATCH")
    mut12 = copy.deepcopy(_FIX_DGATE12)
    mut12["estimand"]["min_clusters"] = 1  # 挪門柱：門檻 60→1
    chk("dgate 12-hex 突變（min_clusters 60→1）⇒ MISMATCH",
        sha_verdict(_FIX_DGATE12_SHA, recompute_direction_sha(mut12, _FIX_DGATE12_SHA)[0]) == "MISMATCH")

    # ── 口徑錯配＝紅：同一真列用錯代配方不得綠（防「兩口徑混掃」假綠/假紅方向感）──
    wrong_recipe = hashlib.sha256(
        json.dumps(_FIX_DGATE12, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()[:12]
    chk("legacy 列若誤用現行 compact 配方 ⇒ 覆算≠stored（口徑選擇不可簡併）",
        wrong_recipe != _FIX_DGATE12_SHA)

    # ── 邊界：NO_SHA 與未知口徑 fail-closed ──
    chk("stored None ⇒ NO_SHA", sha_verdict(None, "x") == "NO_SHA")
    chk("stored 空字串 ⇒ NO_SHA", sha_verdict("  ", "x") == "NO_SHA")
    chk("覆算不能（recomputed=None）而 stored 有值 ⇒ MISMATCH（fail-closed）",
        sha_verdict("deadbeef", None) == "MISMATCH")
    rec_u, scheme_u = recompute_direction_sha(_FIX_DGATE16, "abcdef")  # len=6 無此代
    chk("未知 sha 長度 ⇒ 覆算 None＋unknown-scheme ⇒ MISMATCH",
        rec_u is None and scheme_u.startswith("unknown-scheme") and sha_verdict("abcdef", rec_u) == "MISMATCH")
    chk("criteria 缺 criteria_text 鍵 ⇒ 覆算 None ⇒ MISMATCH",
        sha_verdict("0" * 64, recompute_prereg_sha({"thresholds": {}})) == "MISMATCH")

    print(f"\n{'✓ selftest 全綠' if not fails else '✗ selftest 紅：' + str(fails)}（{13 - len(fails)}/13）")
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=True)
    ap.add_argument("--check", action="store_true", help="唯讀全掃＋分類統計（無參數時之預設）")
    ap.add_argument("--selftest", action="store_true", help="紅綠自測（免 DB 免 API）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    return check()  # 無參數＝--check 安全預設（唯讀）


if __name__ == "__main__":
    sys.exit(main())

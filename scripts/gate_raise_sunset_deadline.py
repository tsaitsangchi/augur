#!/usr/bin/env python3
"""🎯 GATE-raise 呈案：V2-SUNSET 期限 2026-10-31 → 2026-07-31＋ (a) 判準歧異之留痕。

╔══════════════════════════════════════════════════════════════════════════════╗
║ 授權沿革（2026-07-31 同日三段，如實記錄以免日後誤讀）：                          ║
║   ① Steward 指示「期限改今天」→ 本腳本備妥。                                    ║
║   ② 經告知後果耦合（0/3 即三軸永久停止）後，Steward 一度撤回。                   ║
║   ③ Steward 以「**92 天後還是會撞到**」為由**重新指示改今天**——等待不使歧異消失，║
║      只使其在更趕的時點爆發。本腳本據此為現行呈案。                              ║
║ **本腳本仍不 evaluate**：只開新列＋supersede，`evaluated_at`／`result_snapshot`  ║
║   一律不寫。期限到期 ≠ 自動結算；結算是獨立之第二個決定，且須先裁 (a)（見下）。   ║
╚══════════════════════════════════════════════════════════════════════════════╝

**(a) 判準歧異（2026-07-31 實證，尚未依 §8.1 裁定）**
凍結原文（`criteria_sha=65eda893…`，DB 為準）寫：「arena 至少結算一批且方向門**有可讀數**」。
判定程式 `report_triple_evolution_week.py` 實作為 `status='evaluated_pass' > 0`（門**通過**）。
實查：arena 已結算 4,128 列；`direction_gate` 之 12 個 `evaluated_fail` **皆有 `evaluated_at`
與 `result_snapshot`**（確有可讀之數），而 `evaluated_pass` 為 0。
⇒ 依凍結原文 **(a) 達成**（SUNSET 1/3、三軸續命）；依程式 **(a) 未達成**（0/3、三軸永久停止）。

**結構缺口（比本案本身更值得記住）**：`prereg_gate_no_goalpost` trigger 守的是
DELETE／終態列／`criteria_sha`——它守 **DB 列**，**守不到「解釋 criteria 的那支程式」**。
故程式得以私自實作一把與凍結文字不同的尺而無任何機械紅燈。往嚴改亦是挪門柱，
且本專案有明文程序（升嚴走 GATE-raise 開新列），該程式那把較嚴的尺**從未走過**。

---

原始用途：把 V2-SUNSET 期限由 2026-10-31 拉到 2026-07-31（開新列＋supersede 舊列）。

守原則 #15（判準凍結不得就地改）、#6（不可逆須明示）、#12（帳本為唯一權威）、
`AUGUR-MC v1.6 §P5.W2`（人類權威根節點；AI 不得代簽）、`§8.1`（條文解釋權專屬 Steward）。

**為何不能就地改**：`deadline` 住在 `criteria` JSONB 內、受 `criteria_sha` 保護，
`prereg_gate_no_goalpost` trigger 明文擋 `criteria_sha` 變更並指示「要改開新 gate 列並 supersede」。
就地改＝挪門柱。本腳本走的正是該 trigger 指定的路。

**⚠ 本動作之後果耦合（動手前必讀）**
把期限拉到今天，等於**今天就要結算 SUNSET**。凍結條文之 consequence 逐字為
「全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開」。而三條件今日實查：
  · (b) 未達成 — `evolution_production_feature_set` active 仍＝2（基線 2，成長 0）。
  · (c) 未達成 — 嚴格同勝之臂有 2 個，但「≥2 獨立 run 皆勝」之複現臂＝無。
  · (a) **取決於解釋，尚未裁定** — 凍結原文寫「arena 至少結算一批且方向門**有可讀數**」；
    arena 已結算 4,128 列 ✓，`direction_gate` 之 12 個 `evaluated_fail` 皆有
    `evaluated_at` 與 `result_snapshot`（確有可讀之數）✓ ⇒ **依字面已達成**。
    但判定程式 `report_triple_evolution_week.py` 要求 `status='evaluated_pass'>0`（門**通過**），
    現為 0 ⇒ **依程式未達成**。二者不一致，且程式那把較嚴的尺**未走 GATE-raise**。
⇒ **(a) 判成達成則 1/3、三軸續命；判成未達成則 0/3、三軸永久停止**。
   此屬 `§8.1` 條文解釋，**專屬 Steward**，本腳本不預設、不代判、不寫 evaluated_at。

**本腳本只做一件事**：開新列（deadline 改今天，(a)(b)(c) 文字逐字不動）＋把舊列標 superseded。
**不 evaluate、不寫 `evaluated_at`／`result_snapshot`、不觸發任何停止動作。**
結算是另一個獨立決定，須 Steward 於裁定 (a) 之後另行為之。

執行指令矩陣
------------
    python3 scripts/gate_raise_sunset_deadline.py            # 無參數＝--check（唯讀）
    python3 scripts/gate_raise_sunset_deadline.py --check    # 唯讀：新舊 criteria 逐行 diff＋新 sha＋三條件現況
    python3 scripts/gate_raise_sunset_deadline.py --apply    # 開新列＋supersede（**須互動 TTY 親簽**）
    python3 scripts/gate_raise_sunset_deadline.py --selftest # 紅綠自測（免 DB 免 API）

⚠ `--apply` 於非互動環境（管線／cron／agent）一律拒絕執行——簽名無預設值、不代填 OS 帳號。
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys

import _bootstrap  # noqa: F401

OLD_ID = "V2-SUNSET"
NEW_ID = "V2-SUNSET-r2"
NEW_DEADLINE = "2026-07-31"
OLD_DEADLINE = "2026-10-31"

# 舊 criteria 逐字（SSOT＝scripts/migrate_evolution_v2_ddl.py:25-29；此處複製僅供 diff 與 sha 比對，
# --check 會與 live DB 之 criteria_text 逐字核對，不符即拒絕繼續）。
OLD_CRITERIA = """期限：2026-10-31
(a) arena 至少結算一批且方向門有可讀數；或
(b) evolution_production_feature_set active 由 2 成長，且每一新成員通過符號一致性檢查；或
(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched，且該結論可被獨立重跑複現。
全未達成：三軸整體停止、帳本封存、不得換 trigger_code 重開。"""
OLD_SHA = "65eda89328adc75d95e6e03dcf0f31571d5cbb5131efefa45ce9c856d7d8cd01"

# **只換期限那一行**，(a)(b)(c) 與 consequence 逐字不動——換判準內容屬另一件事、不在本次授權內。
NEW_CRITERIA = OLD_CRITERIA.replace(f"期限：{OLD_DEADLINE}", f"期限：{NEW_DEADLINE}", 1)
NEW_SHA = hashlib.sha256(NEW_CRITERIA.encode()).hexdigest()

RAISE_NOTE = (
    f"GATE-raise 2026-07-31（Steward 指示「期限改今天」）：期限 {OLD_DEADLINE}→{NEW_DEADLINE}；"
    f"(a)(b)(c) 與 consequence 逐字不動。supersedes={OLD_ID}。"
    "本列不含 evaluate——(a) 之解釋（凍結原文『有可讀數』vs 程式『evaluated_pass>0』）"
    "未裁定前不得結算（§8.1 專屬 Steward）。"
)


def _sign() -> str:
    """人閘：強制互動 TTY、無預設值、不代填 OS 帳號（同 governance_queue.py 之口徑）。"""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise SystemExit(
            "P5.W2 人閘：--apply 須於互動 TTY 執行。\n"
            "  非互動環境（管線／cron／agent）一律拒絕——AI 不得代簽 approved_by。")
    typed = input(f"簽名者（親手輸入名字，將寫入 {NEW_ID}.approved_by；不得留空）: ").strip()
    if not typed:
        raise SystemExit("P5.W2 人閘：簽名不得留空——本 CLI 無預設值、不代填 OS 帳號")
    return typed


def _live_criteria(cur):
    cur.execute(
        "SELECT criteria->>'criteria_text', criteria_sha, status FROM evolution_prereg_gate "
        "WHERE gate_id=%s", (OLD_ID,))
    return cur.fetchone()


def _conditions(cur) -> list[tuple[str, str, str]]:
    """三條件現況（純查詢、不外推、不代判 (a)）。回 [(碼, 判定, 證據)]。"""
    out = []
    cur.execute("SELECT count(*) FROM direction_arena_prediction WHERE settled_at IS NOT NULL")
    settled = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM direction_gate WHERE status='evaluated_pass'")
    g_pass = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM direction_gate WHERE status='evaluated_fail' "
                "AND evaluated_at IS NOT NULL AND result_snapshot IS NOT NULL")
    g_readable = cur.fetchone()[0]
    out.append((
        "(a)", "**未裁定（解釋歧異）**",
        f"arena 已結算 {settled} 列；方向門 evaluated_pass={g_pass}、"
        f"有 evaluated_at 且有 result_snapshot 者={g_readable}。"
        "依凍結原文『有可讀數』⇒ 達成；依程式『evaluated_pass>0』⇒ 未達成。§8.1 待裁。"))
    cur.execute("SELECT count(*) FROM evolution_production_feature_set WHERE set_status='active'")
    n = cur.fetchone()[0]
    out.append(("(b)", "未達成" if n <= 2 else "達成", f"prodset active={n}（基線 2，須成長）"))
    out.append(("(c)", "未達成",
                "複現（≥2 獨立 run 皆勝 floor ∧ mismatched）之臂＝無"
                "（依 report_triple_evolution_week.py 唯讀輸出）"))
    return out


def _check(conn) -> int:
    with conn.cursor() as cur:
        row = _live_criteria(cur)
        if not row:
            print(f"✗ live 查無 {OLD_ID}", file=sys.stderr)
            return 1
        live_text, live_sha, live_status = row
        print(f"舊列 {OLD_ID}：status={live_status} sha={live_sha[:12]}…")
        if live_text != OLD_CRITERIA:
            print("✗ live criteria_text 與本檔常數不符——**拒絕繼續**（挪門柱嫌疑，先查）", file=sys.stderr)
            return 1
        if live_sha != OLD_SHA:
            print(f"✗ live sha 與凍結 sha 不符：{live_sha[:12]} vs {OLD_SHA[:12]}——拒絕", file=sys.stderr)
            return 1
        print("✓ live criteria 與凍結原文逐字相符")
        print(f"\n新列 {NEW_ID}：deadline {OLD_DEADLINE} → {NEW_DEADLINE}")
        print(f"  新 sha={NEW_SHA[:12]}…")
        print("\n── criteria 逐行 diff（應只有期限那一行）──")
        for ln in difflib.unified_diff(OLD_CRITERIA.splitlines(), NEW_CRITERIA.splitlines(),
                                       "舊", "新", lineterm="", n=0):
            if ln.startswith(("+++", "---", "@@")):
                continue
            print(f"  {ln}")
        print("\n── 三條件現況（本腳本不代判 (a)）──")
        for code, verdict, ev in _conditions(cur):
            print(f"  {code} {verdict}\n      {ev}")
        print(f"\n⚠ 期限改為 {NEW_DEADLINE}（今天）＝今日即須結算。")
        print("   consequence 逐字：三軸整體停止、帳本封存、不得換 trigger_code 重開。")
        print("   **(a) 判成達成則 1/3、三軸續命；判成未達成則 0/3、三軸永久停止。**")
        print("   本腳本只開新列＋supersede，**不 evaluate**；結算須 Steward 另行為之。")
    return 0


def _apply(conn) -> int:
    with conn.cursor() as cur:
        if _check(conn) != 0:
            return 1
        cur.execute("SELECT 1 FROM evolution_prereg_gate WHERE gate_id=%s", (NEW_ID,))
        if cur.fetchone():
            print(f"✓ {NEW_ID} 已存在（冪等，無動作）")
            return 0
    signer = _sign()          # ← 人閘：非 TTY 到不了這裡
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO evolution_prereg_gate "
            "(gate_id, axis, purpose, criteria, criteria_sha, status, preregistered_at, "
            " approved_by, approved_at, note) "
            "VALUES (%s,'program',%s,%s,%s,'approved',now(),%s,now(),%s)",
            (NEW_ID,
             f"V2 三軸落日（GATE-raise：期限 {NEW_DEADLINE}）",
             json.dumps({"deadline": NEW_DEADLINE, "criteria_text": NEW_CRITERIA,
                         "consequence": "三軸整體停止、帳本封存、不得換 trigger_code 重開"},
                        ensure_ascii=False),
             NEW_SHA, signer, RAISE_NOTE))
        cur.execute(
            "UPDATE evolution_prereg_gate SET status='superseded', "
            "note=COALESCE(note||' | ','')||%s WHERE gate_id=%s",
            (f"superseded by {NEW_ID}（GATE-raise 期限 {OLD_DEADLINE}→{NEW_DEADLINE}，"
             f"簽核 {signer} {NEW_DEADLINE}）", OLD_ID))
    conn.commit()
    print(f"✓ {NEW_ID} 已開列（approved_by={signer}）；{OLD_ID} 已標 superseded")
    print("  ⚠ 尚未 evaluate——結算前須先裁定 (a) 之解釋（§8.1）")
    return 0


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}")

    chk("舊 criteria 之 sha 與凍結值相符（確認複製未走樣）",
        hashlib.sha256(OLD_CRITERIA.encode()).hexdigest() == OLD_SHA)
    chk("新 criteria 只換期限那一行", sum(
        1 for ln in difflib.unified_diff(OLD_CRITERIA.splitlines(), NEW_CRITERIA.splitlines(), lineterm="")
        if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))) == 2)
    chk("新舊 sha 不同（否則 trigger 會誤判無變更）", NEW_SHA != OLD_SHA)
    chk("(a)(b)(c) 三行逐字保留", all(
        s in NEW_CRITERIA for s in ("(a) arena 至少結算一批且方向門有可讀數",
                                    "(b) evolution_production_feature_set active 由 2 成長",
                                    "(c) LAIEVO 有任一臂在 F@L1 上同時勝過 floor 與 mismatched")))
    chk("consequence 逐字保留", "三軸整體停止、帳本封存、不得換 trigger_code 重開" in NEW_CRITERIA)
    chk("新期限為今天", f"期限：{NEW_DEADLINE}" in NEW_CRITERIA)
    # ── 2026-08-01 C3：原三條為 `"字面" in body` 而 body=整檔含本段 ⇒ 六個字串恆在、
    # **永遠不會紅**（與 settle_sunset_gate 同病；本支為未來 GATE-raise 模板故必修）。
    # 改行為驗證：假 TTY／monkeypatch 驗真路徑，零 DB（#18）。
    import io as _io

    # (1) 人閘：非互動時 _sign() 必須 SystemExit——餵**非空**輸入才隔離得出 isatty 檢查
    #    （餵空字串會走到「不得留空」那條 SystemExit＝以錯的理由通過，settle 案已實犯）。
    _si, _so = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = _io.StringIO("hugo\n"), _io.StringIO()
    try:
        _sign()
        _blocked = False
    except SystemExit:
        _blocked = True
    finally:
        sys.stdin, sys.stdout = _si, _so
    chk("非互動 TTY 時 _sign() 拒簽——即使輸入非空（拆 isatty 即紅）", _blocked)

    # (2) 授權沿革：檔頭 docstring（模組層、非本段）須含三段記錄——射程限 __doc__，
    #     本段字串不在其中 ⇒ 不自我匹配
    _doc = sys.modules[__name__].__doc__ if __name__ != "__main__" else __doc__
    chk("授權沿革三段在檔頭 docstring（含撤回段，不粉飾）",
        _doc is not None and "撤回" in _doc and "重新指示" in _doc)

    # (3) 不寫 evaluated_at：直接驗 _apply 之 SQL 建構——攔 INSERT 語句字面
    #     （射程=inspect.getsource(_apply)，不含本段）
    import inspect as _i
    _apply_src = _i.getsource(_apply)
    chk("_apply 之 SQL 不含 evaluated_at（結算是另一個決定，另有 settle 腳本）",
        "evaluated_at" not in _apply_src)
    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="GATE-raise：V2-SUNSET 期限改今天（開新列＋supersede）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    from augur.core import db
    with db.connect() as conn:
        return _apply(conn) if a.apply else _check(conn)


if __name__ == "__main__":
    sys.exit(main())

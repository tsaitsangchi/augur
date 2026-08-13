#!/usr/bin/env python3
"""KH 問法回歸矩陣——evolve §0.1 閉集（intent／hint／ask_tail／LIVE resolve）。

對齊：
  reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md §0.1
  audits/KH-EVOLVE-EXT-ASK-NO-EMPTY-ADOPTED-20260812.md
  audits/READOUT-EXT-THEN-ASK-EXECUTED-20260812.md

層級：
  A) 零 IO：intent／extract_title_hint／extract_ask_tail／prefer 種子
  B) LIVE（預設開）：resolve＋cite（錨件在庫才硬断言；缺件→SKIP 不計 FAIL）

執行指令矩陣:
  python scripts/kh_query_form_matrix.py              # A+B；FAIL→rc=1
  python scripts/kh_query_form_matrix.py --offline    # 僅 A
  python scripts/kh_query_form_matrix.py --selftest   # 同 --offline
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

# ── 閉集錨（與 evolve／LIVE 帳一致）──
CANON_COLON = "國碩-ERP-GP_DR說明(20211007-4-rman)1：請讀出具體內容"
CANON_BARE = "國碩-ERP-GP_DR說明(20211007-4-rman)1"
CANON_ID = 277948

GENERO_PPT = "Genero Web Services 教育訓練(程式).ppt"
GENERO_XML = f"{GENERO_PPT}中，詳細說明XML 的作用"
GENERO_SRV = f"{GENERO_PPT}提到啟動 server 後處理需求的步驟，詳細說明"
GENERO_IDS = (1818820, 1818830)

PPT_BARE = "TIPTOP GP5.3-生產管理.ppt"
AVI_COLON = "WebService程式撰寫(I).avi：請讀出具體內容"
PDF_COLON = "aap.pdf：請讀出具體內容"
DOCX_COLON = "報告.docx：請讀出"
HANDBOOK_Q = "tiptop 應付帳款系統說明?"


def _offline_cases() -> list[tuple[str, bool, str]]:
    from augur.knowledge.readout import (
        extract_ask_tail,
        extract_title_hint,
        is_readout_intent,
        _ask_prefer_terms,
        _chunk_text_prefer,
        _resolve_hint_variants,
    )

    rows: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        rows.append((name, ok, detail))

    # —— Intent 正例 ——
    add("intent_colon_readout", is_readout_intent(CANON_COLON) is True)
    add("intent_bare_title", is_readout_intent(CANON_BARE) is True)
    add("intent_ext_ask_xml", is_readout_intent(GENERO_XML) is True)
    add("intent_ext_ask_srv", is_readout_intent(GENERO_SRV) is True)
    add("intent_bare_ppt", is_readout_intent(PPT_BARE) is True)
    add("intent_avi_colon", is_readout_intent(AVI_COLON) is True)
    add("intent_handbook_?", is_readout_intent(HANDBOOK_Q) is True)
    add("intent_pdf_in_name_如何", is_readout_intent("TIPTOP如何新增使用者.pdf") is True)

    # —— Intent 負例 ——
    add("intent_plain_no", is_readout_intent("什麼是知行合一") is False)
    add("intent_how_ask_no_file", is_readout_intent("國碩 DR 演練要怎麼做") is False)
    add("intent_如何_無副檔名", is_readout_intent("TIPTOP如何新增使用者") is False)

    # —— Hint ——
    add(
        "hint_colon_keeps_stem",
        "國碩" in extract_title_hint(CANON_COLON) and "請讀出" not in extract_title_hint(CANON_COLON),
        extract_title_hint(CANON_COLON)[:40],
    )
    add("hint_pdf_keep_ext", extract_title_hint(PDF_COLON) == "aap.pdf")
    add("hint_docx_keep_ext", extract_title_hint(DOCX_COLON) == "報告.docx")
    add("hint_avi_keep_ext", extract_title_hint(AVI_COLON) == "WebService程式撰寫(I).avi")
    add("hint_ppt_bare", extract_title_hint(PPT_BARE) == PPT_BARE)
    add("hint_ext_ask_xml_cut", extract_title_hint(GENERO_XML) == GENERO_PPT)
    add("hint_ext_ask_srv_cut", extract_title_hint(GENERO_SRV) == GENERO_PPT)
    add(
        "hint_handbook_strip_?",
        extract_title_hint(HANDBOOK_Q) == "tiptop 應付帳款系統說明",
    )
    add(
        "hint_colon_no_false_pdf_cut",
        ".pdf" not in extract_title_hint("無檔名長標題說明文件：請讀出.pdf附註"),
    )

    # —— Ask tail / prefer ——
    tail = extract_ask_tail(GENERO_SRV)
    add("ask_tail_srv", "啟動" in tail and "server" in tail.casefold(), tail[:50])
    prefs = _ask_prefer_terms(tail)
    add("prefer_has_啟動", "啟動" in prefs, str(prefs[:8]))
    add(
        "alias_handbook",
        "應付帳款管理系統" in _resolve_hint_variants(HANDBOOK_Q),
    )

    demo = "AAAA\n" + ("x" * 200) + "\n啟動 Server\nCALL fgl_ws_server_start()\n處理需求\n"
    blob = "".join(t for _, _, t in _chunk_text_prefer(
        demo, max_chars=400, chunk=120, prefer_terms=["啟動", "server"],
    ))
    add(
        "prefer_chunk_fgl",
        "啟動 Server" in blob and "fgl_ws_server_start" in blob,
    )
    return rows


def _live_cases() -> list[tuple[str, bool, str]]:
    """DB 在場才硬断言；錨件缺席→SKIP（ok=True 標記 detail=SKIP）。"""
    from augur.core import db
    from augur.knowledge.readout import advise_readout_citations, extract_title_hint, resolve_item_ids

    rows: list[tuple[str, bool, str]] = []
    scope = (True, frozenset({"local"}), 1)

    def add(name: str, ok: bool, detail: str = "") -> None:
        rows.append((name, ok, detail))

    with db.connect() as conn, conn.cursor() as cur:
        def ids_present(want: tuple[int, ...]) -> list[int]:
            found = []
            for i in want:
                cur.execute(
                    "SELECT 1 FROM knowledge_item i "
                    "JOIN knowledge_kh4_state k4 ON k4.item_id=i.item_id "
                    "WHERE i.item_id=%s AND k4.answer_status='eligible'",
                    (i,),
                )
                if cur.fetchone():
                    found.append(i)
            return found

        # Canon
        have_canon = ids_present((CANON_ID,))
        if not have_canon:
            add("live_canon_resolve", True, "SKIP missing 277948")
        else:
            got = resolve_item_ids(cur, extract_title_hint(CANON_COLON), scope=scope)
            add("live_canon_resolve", CANON_ID in got, f"ids={got[:5]}")
            cites = advise_readout_citations(CANON_COLON, scope=scope)
            add(
                "live_canon_cite",
                any(getattr(c, "item_id", None) == CANON_ID for c in cites),
                f"n={len(cites)}",
            )

        # Genero ext+ask
        have_g = ids_present(GENERO_IDS)
        if not have_g:
            add("live_genero_xml", True, "SKIP missing Genero ppt")
            add("live_genero_srv_anchor", True, "SKIP")
        else:
            c_xml = advise_readout_citations(GENERO_XML, scope=scope)
            ids_x = sorted({int(c.item_id) for c in c_xml if getattr(c, "item_id", None)})
            ok_x = bool(set(ids_x) & set(GENERO_IDS)) and any(
                "XML" in (c.text or "") for c in c_xml[:4]
            )
            add("live_genero_xml", ok_x, f"ids={ids_x} xml_in_top={ok_x}")

            c_srv = advise_readout_citations(GENERO_SRV, scope=scope)
            blob = "\n".join((c.text or "") for c in c_srv[:4])
            ok_s = (
                bool(set(int(c.item_id) for c in c_srv if getattr(c, "item_id", None)) & set(GENERO_IDS))
                and ("fgl_ws_server_start" in blob or "啟動 Server" in blob or "啟動 server" in blob)
            )
            add(
                "live_genero_srv_anchor",
                ok_s,
                f"n={len(c_srv)} start={'fgl_ws_server_start' in blob}",
            )

        # Neg：非 readout 不應灌 cite
        c_neg = advise_readout_citations("什麼是知行合一", scope=scope)
        add("live_plain_zero_cite", len(c_neg) == 0, f"n={len(c_neg)}")

    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH 問法回歸矩陣（evolve §0.1）")
    ap.add_argument("--offline", action="store_true", help="僅零 IO 閉集")
    ap.add_argument("--selftest", action="store_true", help="同 --offline")
    args = ap.parse_args(argv)
    offline_only = args.offline or args.selftest

    print("══ KH-QUERY-FORM-MATRIX ══")
    fails: list[str] = []
    for name, ok, detail in _offline_cases():
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] A.{name}" + (f"  {detail}" if detail else ""))
        if not ok:
            fails.append(f"A.{name}")

    if not offline_only:
        try:
            live = _live_cases()
        except Exception as e:
            print(f"  [FAIL] B.live_connect  {type(e).__name__}: {e}")
            fails.append("B.live_connect")
            live = []
        for name, ok, detail in live:
            mark = "PASS" if ok else "FAIL"
            print(f"  [{mark}] B.{name}" + (f"  {detail}" if detail else ""))
            if not ok:
                fails.append(f"B.{name}")

    if fails:
        print(f"MATRIX FAIL: {fails}")
        return 1
    print("MATRIX PASS" + (" (offline)" if offline_only else " (offline+live)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

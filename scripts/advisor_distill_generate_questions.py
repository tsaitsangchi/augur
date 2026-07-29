#!/usr/bin/env python
"""S2 蒸餾題生成器 — 資料驅動枚舉三情境自問自答題,寫 advisor_distill_question(冪等、游標 resume)。

🎯 這支在做什麼(白話):為 advisor 自問自答蒸餾生訓練題,分三情境(每題帶 gold situation_label + expected):
   - 情境 1(in-corpus,expected=ANSWER):源**真實** DB——knowledge_query 詞表(enabled)+
     philosophy_work / philosophy_thinker 真實標題(非我編)。這些是語料真有支撐、該據真兆答的題。
   - 情境 2(故意 out-of-corpus,expected=DECLINE):**curated** 明確零覆蓋域——主題名 SSOT＝
     PostgreSQL `advisor_distill_seed_topic`(kind=ooc);正解恆為誠實 decline(界線-C)。
     題目=確定性模板 × DB 策展主題名,守 #1 零 AI 生成入庫;#29b 新增主題＝INSERT、零改碼。
   - 情境 3(不可能宣稱/離題,expected=REFUSE):同表 kind=impossible;正解 refuse。
   寫 DB advisor_distill_question(UNIQUE(question) 冪等、context_built 游標);多次跑累加不重複。
   **GATE(DP7)**:out-of-corpus + decline 類(情境 2/3)佔比 ≥ 55%;達不到 → 印警告、exit 1。

   為何情境 2/3 非「AI 生成入庫」:題目=確定性模板 × curated 主題名(住 DB 表、可稽核),
   如同 knowledge_query 之查詢詞;**答案(gold)不在此生**——由 S4 teacher 生、S5 驗 ⊂ context。
   此處只落「要問什麼」+「正解該是哪類行為(label)」,label 之真兆=語料覆蓋事實(S1/S3 檢索實證)。
守 #1(零 AI 生成事實入庫:題=模板×真實/curated 主題,答案另生另驗)· #6(冪等 UNIQUE)·
   #9/#10(情境1題可 trace 回 knowledge_query/philosophy 真實列)· #15(GATE 實數報告)·
   #29b(策展 OOC/impossible 住 DB)· CLAUDE #29。
   計畫 SSOT=reports/augur_advisor_selfqa_training_plan_20260706.md §S2 · §③界線-C · DP7;
   NHC＝reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md §3.3 Q1/Q2。

執行指令矩陣:
  python scripts/advisor_distill_generate_questions.py                    # 無參數=印矩陣 + 現況統計(安全預設)
  python scripts/advisor_distill_generate_questions.py --pilot            # pilot 小批(~60-100 題)、跑 GATE
  python scripts/advisor_distill_generate_questions.py --n-incorpus 40 --batch-tag pilot1   # 自訂規模
  python scripts/advisor_distill_generate_questions.py --stats            # 唯讀:印題庫情境分佈
  python scripts/advisor_distill_generate_questions.py --selftest         # 零外部依賴:無 runtime hardcode 清單
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

# 情境 1(in-corpus)題型模板:對真實主題名套多種問法(六類題型覆蓋:定義/概念/比較/應用/字源/評析)
# 對「著作名」型主題套(這些名字必現於檢索到的原典句,surface overlap 高、relevant 穩定)。
_INCORPUS_TEMPLATES = [
    "{t}的核心思想是什麼?",
    "請解釋{t}的主要觀點",
    "{t}講的是什麼道理?",
    "{t}對治理與決策有什麼啟發?",
]

# 情境 2(out-of-corpus)問法模板:對同一 out-of-corpus 主題套多種問法(仍恆 out-of-corpus、正解 decline)。
# 多問法=多變體 decline 樣本(DP7 佔比槓桿);主題名 SSOT＝advisor_distill_seed_topic(非本檔 hardcode)。
_OOC_TEMPLATES = [
    "{t}的核心技術優勢是什麼?",
    "請說明{t}的原理",
    "{t}目前的技術瓶頸在哪裡?",
    "{t}的關鍵指標怎麼衡量?",
    "{t}未來的發展方向是什麼?",
]


def _load_seed_topics(cur, kind):
    """讀 advisor_distill_seed_topic(#29b runtime SSOT)。回 [(topic_text, domain_or_expected), …]。
    kind=ooc → domain; kind=impossible → expected。表空／缺表 → [](fail-closed、不回退 hardcode)。"""
    cur.execute(
        "SELECT topic_text, domain, expected FROM advisor_distill_seed_topic "
        "WHERE active AND kind=%s ORDER BY seed_id",
        (kind,),
    )
    rows = cur.fetchall()
    if kind == "ooc":
        return [(t, d or "general") for t, d, _ in rows]
    return [(t, e or "REFUSE") for t, _, e in rows]

# ── 情境 1b:curated 概念/字源/比較題(六類題型覆蓋,主題詞真出現於已嵌入原典)──────────
# 這些概念詞/字義題涵蓋 v1.34.0 六類題型(定義/概念/比較/應用/字源/評析);
# 主題本身住已嵌入之經典(論語仁義禮/荀子性惡/韓非法術勢…),S3 檢索實證相關度,
# relevant=False 者由 §S1「模糊偏保守」覆寫為 DECLINE(誠實揭穿樂觀 ANSWER 標籤)。
_INCORPUS_CONCEPT = [
    ("什麼是仁?孔子怎麼講?", "philosophy"),                        # 定義/字源
    ("禮的核心意義是什麼?", "philosophy"),                          # 定義
    ("荀子性惡論的主要論點是什麼?", "philosophy"),                  # 概念
    ("韓非子的法術勢是什麼?請評析", "philosophy"),                  # 評析
    ("儒家與法家在治國上的差異是什麼?", "philosophy"),              # 比較
    ("以正合以奇勝是什麼意思?", "philosophy"),                      # 字源/應用
    ("孫子兵法的虛實之道是什麼?", "philosophy"),                    # 概念
    ("道德經的無為而治怎麼理解?", "philosophy"),                    # 概念
    ("墨子兼愛與非攻的主張是什麼?", "philosophy"),                  # 概念
    ("孟子的性善論怎麼說?", "philosophy"),                          # 概念
    ("公孫龍子的白馬非馬在講什麼?", "philosophy"),                  # 概念
    ("莊子逍遙遊的旨趣是什麼?", "philosophy"),                      # 概念
    ("管子的治國富民思想是什麼?", "philosophy"),                    # 概念
    ("三略對用人與治軍有什麼見解?", "philosophy"),                  # 應用
    ("六韜談的文韜武略是什麼?", "philosophy"),                      # 概念
    ("列子的思想核心是什麼?", "philosophy"),                        # 概念(易 relevant=False→測覆寫)
    ("孟子與荀子對人性的看法有何不同?", "philosophy"),              # 比較(易 relevant=False→測覆寫)
    ("商君書的變法思想是什麼?", "philosophy"),                      # 概念
    ("尹文子的名實之辨是什麼?", "philosophy"),                      # 概念
    ("吳子兵法的治軍原則是什麼?", "philosophy"),                    # 應用
]

# ── 情境 1c:chemistry 已嵌入之真實主題(唯一有 sentence embedding 的知識域,7 items)────
# 源 knowledge_item(domain=chemistry)且有句嵌入者之真實題名;S3 實證相關度。
_INCORPUS_CHEM = [
    ("沉香的品級與品質是怎麼分的?", "chemistry"),
    ("沉香廢料與棕櫚空果串製成生質燃料顆粒的方法", "chemistry"),
    ("電化學電池的流體力學分析在研究什麼?", "chemistry"),
    ("化學動力學的反演建模問題是什麼?", "chemistry"),
]


def _embedded_works(cur, n):
    """情境 1a 真兆主題:**只取真有 sentence embedding 的哲學經典著作名**(關鍵改進——
    使正解樣本為真)。DB 實查(非 hardcode):join sentence_embedding→sentence→work_text→work,
    取有嵌入之公版經典 title_zh,按嵌入句數 desc 取(內容最豐者優先)。可 trace 回 work_id。"""
    cur.execute(
        "SELECT COALESCE(pw.title_zh, pw.title) AS work, count(*) AS n_emb "
        "FROM knowledge_sentence_embedding kse "
        "JOIN knowledge_sentence ks ON ks.sent_id = kse.sent_id "
        "JOIN philosophy_work_text pwt ON pwt.text_id = ks.text_id "
        "JOIN philosophy_work pw ON pw.work_id = pwt.work_id "
        "WHERE pw.review_flag IS NOT TRUE "
        "AND COALESCE(pw.title_zh, pw.title) IS NOT NULL "
        "AND char_length(COALESCE(pw.title_zh, pw.title)) BETWEEN 2 AND 20 "
        "GROUP BY work HAVING count(*) >= 100 "
        "ORDER BY n_emb DESC LIMIT %s", (max(1, n),))
    return [(r[0], "philosophy", "embedded_work") for r in cur.fetchall()]


def generate(cur, n_incorpus, batch_tag, tpl_per_topic=1, ooc_tpl=1):
    """組三情境題、INSERT ON CONFLICT DO NOTHING(冪等);回 inserted 計數 dict。
    tpl_per_topic 控每 in-corpus 著作名主題套幾個問法模板;ooc_tpl 控每 out-of-corpus 主題套幾個問法
    (二者皆 DP7 佔比槓桿:tpl_per_topic↑=in-corpus↑、ooc_tpl↑=decline↑)。
    情境 1 三源:1a 已嵌入經典著作名(DB 實查、relevant 穩定)+ 1b curated 概念題(六類型)
    + 1c chemistry 已嵌入真實題名;**只取真有句嵌入之主題**(關鍵改進:正解樣本為真)。"""
    rows = []  # (question, situation_label, expected, domain, topic_source, topic_ref)
    # 情境 1a:已嵌入經典著作名 → ANSWER(每主題套 tpl_per_topic 個問法模板;著作名必現於檢索句、relevant 穩)
    for topic, domain, src in _embedded_works(cur, n_incorpus):
        for tpl in _INCORPUS_TEMPLATES[:max(1, tpl_per_topic)]:
            rows.append((tpl.format(t=topic), 1, "ANSWER", domain, src, topic))
    # 情境 1b:curated 概念/字源/比較題(六類題型覆蓋)→ ANSWER(題本身即完整問句,不套模板)
    for q, domain in _INCORPUS_CONCEPT:
        rows.append((q, 1, "ANSWER", domain, "curated_concept", q))
    # 情境 1c:chemistry 已嵌入真實主題 → ANSWER
    for q, domain in _INCORPUS_CHEM:
        rows.append((q, 1, "ANSWER", domain, "curated_chem", q))
    # 情境 2:out-of-corpus → DECLINE(主題名讀 DB;每主題套 ooc_tpl 個問法變體,控 DP7 佔比)
    for topic, domain in _load_seed_topics(cur, "ooc"):
        for tpl in _OOC_TEMPLATES[:max(1, ooc_tpl)]:
            rows.append((tpl.format(t=topic), 2, "DECLINE", domain, "curated_ooc", topic))
    # 情境 3:impossible / off-topic → REFUSE(主題名讀 DB)
    for q, expected in _load_seed_topics(cur, "impossible"):
        rows.append((q, 3, expected, "off_topic", "curated_impossible", q))

    inserted = 0
    for q, label, expected, domain, src, ref in rows:
        cur.execute(
            "INSERT INTO advisor_distill_question "
            "(question, situation_label, expected, domain, topic_source, topic_ref, batch_tag) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (question) DO NOTHING",
            (q, label, expected, domain, src, ref, batch_tag))
        inserted += cur.rowcount
    return inserted, len(rows)


def stats(cur):
    """情境分佈統計(唯讀)。回 (total, ooc_ratio)。"""
    cur.execute("SELECT situation_label, expected, count(*) FROM advisor_distill_question "
                "GROUP BY situation_label, expected ORDER BY situation_label")
    by = cur.fetchall()
    cur.execute("SELECT count(*) FROM advisor_distill_question")
    total = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM advisor_distill_question WHERE situation_label IN (2,3)")
    ooc = cur.fetchone()[0]
    ratio = ooc / total if total else 0.0
    print(f"── 題庫情境分佈(total={total})──")
    _labelname = {1: "in-corpus", 2: "out-of-corpus", 3: "impossible/off-topic"}
    for label, expected, cnt in by:
        print(f"  情境{label}({_labelname.get(label, '?')}) expected={expected}: {cnt}"
              f"  ({cnt/total*100:.1f}%)" if total else "")
    print(f"  → out-of-corpus + decline/refuse(情境2+3)佔比 = {ratio*100:.1f}%  (DP7 GATE ≥ 55%)")
    return total, ratio


def selftest():
    """零外部依賴:確認 runtime 無 _OOC_TOPICS/_IMPOSSIBLE_TOPICS hardcode SSOT(#29b／NHC-S3)。"""
    this = sys.modules[__name__]
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("無 _OOC_TOPICS SSOT", not hasattr(this, "_OOC_TOPICS"))
    chk("無 _IMPOSSIBLE_TOPICS SSOT", not hasattr(this, "_IMPOSSIBLE_TOPICS"))
    chk("有 _load_seed_topics", callable(getattr(this, "_load_seed_topics", None)))
    chk("模板仍在(邏輯側)", len(_OOC_TEMPLATES) >= 3 and len(_INCORPUS_TEMPLATES) >= 2)
    # 禁專題答案樹:不得定義領域答案常數／domain 分支函式名
    banned = ("SOLAR_ANSWER", "FIRST_PRINCIPLES_ANSWER", "DOMAIN_ANSWER_TREE")
    chk("無專題答案常數", all(not hasattr(this, n) for n in banned))
    chk("無 domain_answer 函式", not hasattr(this, "domain_answer")
        and not hasattr(this, "answer_for_domain"))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--pilot", action="store_true", help="pilot 小批(n-incorpus=15、1 模板/主題,守 DP7 ≥55% ooc)")
    ap.add_argument("--n-incorpus", type=int, default=None, help="情境1真兆主題取樣數")
    ap.add_argument("--tpl-per-topic", type=int, default=None, help="每 in-corpus 主題套幾個問法(DP7 佔比槓桿)")
    ap.add_argument("--ooc-tpl", type=int, default=None, help="每 out-of-corpus 主題套幾個問法(DP7 佔比槓桿)")
    ap.add_argument("--batch-tag", default="pilot")
    ap.add_argument("--stats", action="store_true", help="唯讀:只印現況統計")
    ap.add_argument("--selftest", action="store_true", help="零外部依賴自測")
    args, _ = ap.parse_known_args()

    if args.selftest:
        sys.exit(selftest())

    if not (args.pilot or args.n_incorpus or args.stats):
        print(__doc__.split("執行指令矩陣:")[1])
        with db.connect() as conn, db.transaction(conn) as cur:
            stats(cur)
        return

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            if args.stats:
                stats(cur)
                return
            # 冪等 per batch_tag(#6):in-corpus 主題為 random 取樣、重跑會生新題,故以 batch_tag 為冪等鍵——
            # 該 tag 已有題 → 不重生(避免重跑累加漂移);要新一批用新 --batch-tag,要重生先清該 tag。
            cur.execute("SELECT count(*) FROM advisor_distill_question WHERE batch_tag=%s", (args.batch_tag,))
            existing = cur.fetchone()[0]
            if existing:
                print(f"── batch_tag='{args.batch_tag}' 已有 {existing} 題,冪等跳過生成(#6);"
                      f"要新批用新 --batch-tag、要重生先清該 tag ──")
            else:
                n_in = args.n_incorpus or (15 if args.pilot else 40)
                tpt = args.tpl_per_topic or (1 if args.pilot else 4)
                otpl = args.ooc_tpl or (1 if args.pilot else 5)
                inserted, attempted = generate(cur, n_in, args.batch_tag, tpl_per_topic=tpt, ooc_tpl=otpl)
                print(f"── S2 生成(batch_tag={args.batch_tag})──")
                print(f"  嘗試 {attempted} 題 → 新增 {inserted}(其餘為冪等去重,#6)")
        with db.transaction(conn) as cur:
            total, ratio = stats(cur)
    if ratio < 0.55:
        print(f"\n✗ GATE 未過:out-of-corpus 佔比 {ratio*100:.1f}% < 55%(DP7)——增情境2/3 或減情境1")
        sys.exit(1)
    print(f"\n✓ DP7 GATE 通過:out-of-corpus 佔比 {ratio*100:.1f}% ≥ 55%")


if __name__ == "__main__":
    main()

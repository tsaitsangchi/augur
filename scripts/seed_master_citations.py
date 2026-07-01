#!/usr/bin/env python
"""補現代大師到學派 proponents + philosophy_source citation — 合規路顯性化來源(憲章 v1.18.0)。

🎯 現代版權大師之核心精神來源顯性化:大師名補入對映學派 proponents、真實文獻書目補入 philosophy_source。
   著作全文不可抓(版權),但精神經**真實文獻 citation → principle → 因子 → #14**(合規路)入庫。
守 #1(citation 為真實文獻書目事實、非 AI 摘要著作內容;source_type 禁 ai_generated)· #15(可查證校正)· #18。
⚠️ citation 為書目 metadata(書名/年份),非全文;採用由 #14 裁決、非大師權威。

用法:PYTHONPATH=src python scripts/seed_master_citations.py
"""
from augur.core import db

# (大師 proponent, 學派 name_zh, 真實文獻 citation)
ADD = [
    ("Charlie Munger", "品質/護城河", "Munger, Poor Charlie's Almanack, 2005"),
    ("Seth Klarman", "價值投資", "Klarman, Margin of Safety, 1991"),
    ("Aswath Damodaran", "價值投資", "Damodaran, The Little Book of Valuation, 2011"),
    ("Nassim Taleb", "逆向", "Taleb, The Black Swan, 2007"),
    ("Nassim Taleb", "低波動異常", "Taleb, Antifragile, 2012"),
    ("Peter Lynch", "成長價值（PEG）", "Lynch, One Up on Wall Street, 1989"),
    ("William O'Neil", "CANSLIM（成長動能）", "O'Neil, How to Make Money in Stocks, 1988"),
    ("George Soros", "反身性", "Soros, The Alchemy of Finance, 1987"),
    ("Ray Dalio", "總經/債務週期", "Dalio, Big Debt Crises, 2018"),
    ("Robert Shiller", "行為財務", "Shiller, Irrational Exuberance, 2000"),
    ("Daniel Kahneman", "行為財務", "Kahneman, Thinking, Fast and Slow, 2011"),
    ("Richard Thaler", "行為財務", "Thaler, Misbehaving, 2015"),
    ("Philip Fisher", "成長投資", "Fisher, Common Stocks and Uncommon Profits, 1958"),
    ("Jesse Livermore", "趨勢投機", "Lefevre, Reminiscences of a Stock Operator, 1923"),
    ("André Kostolany", "心理週期", "Kostolany, Die Kunst über Geld nachzudenken, 2000"),
    ("John Templeton", "逆向全球", "Templeton, Investing the Templeton Way, 2008"),
    ("David Dreman", "逆向", "Dreman, Contrarian Investment Strategies, 1998"),
    ("Howard Marks", "市場週期", "Marks, Mastering the Market Cycle, 2018"),
    ("John Bogle", "低波動異常", "Bogle, Common Sense on Mutual Funds, 1999 (被動/低成本對照觀點)"),
    ("Burton Malkiel", "低波動異常", "Malkiel, A Random Walk Down Wall Street, 1973 (效率市場對照觀點)"),
]


def main():
    props_added = src_added = missing = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for master, school_zh, citation in ADD:
            cur.execute("SELECT school_id, proponents FROM philosophy_school WHERE name_zh=%s", (school_zh,))
            r = cur.fetchone()
            if not r:
                print(f"⚠ 無此學派: {school_zh}")
                missing += 1
                continue
            sid, props = r
            if master not in (props or ""):
                cur.execute("UPDATE philosophy_school SET proponents=%s WHERE school_id=%s",
                            ((props + "; " + master) if props else master, sid))
                props_added += 1
            cur.execute("SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s", (sid, citation))
            if not cur.fetchone():
                cur.execute("INSERT INTO philosophy_source (school_id, citation, source_type) VALUES (%s,%s,'book')",
                            (sid, citation))
                src_added += 1
        cur.execute("SELECT count(*) FROM philosophy_source")
        total_src = cur.fetchone()[0]
    print(f"proponents 補 {props_added} 位、philosophy_source citation 補 {src_added} 筆(共 {total_src} 筆)、無對映學派 {missing}")
    print("⚠️ citation 為真實文獻書目 metadata(可查證校正);精神入因子須走 principle→#14、採用由 #14 裁決。")


if __name__ == "__main__":
    main()

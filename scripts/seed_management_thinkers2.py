#!/usr/bin/env python
"""窮舉補齊管理各領域 major 思想家(第二批)— 組織/會計/生產/研發/策略/行銷/HR + 補投資財務。

🎯 承 seed_management_thinkers,窮舉補各管理領域全球 major 思想家。upsert by name 去重(已有跳過)。
守 #1/#15(生卒/國籍/簡介為通行史實 metadata、可查證校正、非預測真兆)· #28· #17/#18。
⚠️ 人物 metadata、不進預測管線;現代版權大師原則入因子須走真實文獻 principle→#14(合規路 v1.18.0)。

用法:PYTHONPATH=src python scripts/seed_management_thinkers2.py
"""
from augur.core import db

PEOPLE = [
    # 組織管理/組織理論
    ("馬克斯·韋伯", "Max Weber", 1864, 1920, "德國", "科層制(官僚制)、理性化、社會學奠基者。"),
    ("赫伯特·賽門", "Herbert A. Simon", 1916, 2001, "美國", "有限理性、決策理論、行政行為,諾貝爾獎。"),
    ("詹姆斯·馬奇", "James G. March", 1928, 2018, "美國", "組織學習、垃圾桶決策模型、探索與利用。"),
    ("埃德加·沙因", "Edgar Schein", 1928, 2023, "美國", "組織文化三層次、歷程諮詢。"),
    ("瑪莉·派克·傅麗特", "Mary Parker Follett", 1868, 1933, "美國", "管理先知、衝突整合、權力共享。"),
    ("埃爾頓·梅奧", "Elton Mayo", 1880, 1949, "澳洲／美國", "霍桑實驗、人際關係學派。"),
    ("克里斯·阿吉里斯", "Chris Argyris", 1923, 2013, "美國", "組織學習、雙環學習、行動科學。"),
    ("華倫·班尼斯", "Warren Bennis", 1925, 2014, "美國", "現代領導學奠基者。"),
    ("弗雷德里克·赫茲伯格", "Frederick Herzberg", 1923, 2000, "美國", "雙因子理論(激勵—保健)。"),
    ("約翰·科特", "John Kotter", 1947, None, "美國", "變革管理八步驟、領導與管理之別。"),
    # 投資/財務管理(補)
    ("大衛·史文森", "David Swensen", 1954, 2021, "美國", "耶魯模式、機構資產配置。"),
    ("詹姆斯·西蒙斯", "James Simons", 1938, 2024, "美國", "量化投資、文藝復興科技、大獎章基金。"),
    ("愛德華·索普", "Edward Thorp", 1932, None, "美國", "量化投資、《擊敗莊家》《擊敗市場》、凱利公式應用。"),
    ("保羅·都鐸·瓊斯", "Paul Tudor Jones", 1954, None, "美國", "全球宏觀交易、風險控制。"),
    ("史丹利·卓肯米勒", "Stanley Druckenmiller", 1953, None, "美國", "宏觀交易、集中下注。"),
    ("朱利安·羅伯遜", "Julian Robertson", 1932, 2022, "美國", "老虎基金、多空選股。"),
    ("傑瑞米·西格爾", "Jeremy Siegel", 1945, None, "美國", "《散戶投資正典》、股票長期報酬。"),
    ("比爾·葛洛斯", "Bill Gross", 1944, None, "美國", "債券天王、PIMCO。"),
    # 會計管理
    ("井尻雄士", "Yuji Ijiri", 1935, 2017, "日本／美國", "會計理論、三式簿記、動量會計。"),
    ("威廉·佩頓", "William Paton", 1889, 1991, "美國", "會計理論奠基、公司實體理論。"),
    ("羅伯特·安東尼", "Robert N. Anthony", 1916, 2006, "美國", "管理會計、責任中心。"),
    # 生產/品質管理(補)
    ("華特·休哈特", "Walter A. Shewhart", 1891, 1967, "美國", "統計品質管制之父、控制圖、PDCA 原型。"),
    ("新鄉重夫", "Shigeo Shingo", 1909, 1990, "日本", "防呆(Poka-yoke)、快速換模(SMED)、豐田生產。"),
    ("田口玄一", "Genichi Taguchi", 1924, 2012, "日本", "田口方法、品質工程、損失函數。"),
    ("阿曼德·費根堡", "Armand Feigenbaum", 1922, 2014, "美國", "全面品質管制(TQC)。"),
    ("麥可·哈默", "Michael Hammer", 1948, 2008, "美國", "企業流程再造(BPR)。"),
    # 研發/創新管理
    ("亨利·伽斯柏", "Henry Chesbrough", 1956, None, "美國", "開放式創新。"),
    ("艾瑞克·馮·希培", "Eric von Hippel", 1941, None, "美國", "使用者創新、創新民主化。"),
    ("埃弗雷特·羅傑斯", "Everett Rogers", 1931, 2004, "美國", "創新擴散理論。"),
    ("維傑·戈溫達拉簡", "Vijay Govindarajan", 1949, None, "印度／美國", "逆向創新、策略創新。"),
    ("麗塔·麥奎斯", "Rita McGrath", 1959, None, "美國", "暫時性競爭優勢、發現導向規劃。"),
    # 企業策略
    ("金偉燦", "W. Chan Kim", 1951, None, "韓國", "藍海策略、價值創新。"),
    ("芮妮·莫伯尼", "Renée Mauborgne", 1963, None, "美國", "藍海策略共同提出者。"),
    ("理查·魯梅特", "Richard Rumelt", 1942, None, "美國", "《好策略・壞策略》、策略核心。"),
    ("大前研一", "Kenichi Ohmae", 1943, None, "日本", "策略家的智慧、3C 模型。"),
    ("普哈拉", "C. K. Prahalad", 1941, 2010, "印度／美國", "核心競爭力、金字塔底層商機。"),
    # 行銷管理
    ("菲利普·科特勒", "Philip Kotler", 1931, None, "美國", "現代行銷學之父、行銷管理。"),
    ("希奧多·李維特", "Theodore Levitt", 1925, 2006, "德國／美國", "行銷短視症、全球化。"),
    ("艾爾·賴茲", "Al Ries", 1926, 2022, "美國", "定位(Positioning)理論。"),
    ("傑克·屈特", "Jack Trout", 1935, 2017, "美國", "定位理論共同提出者。"),
    # HR/領導
    ("道格拉斯·麥格雷戈", "Douglas McGregor", 1906, 1964, "美國", "X 理論與 Y 理論。"),
    ("戴夫·尤瑞奇", "Dave Ulrich", 1953, None, "美國", "人力資源價值主張、HR 角色模型。"),
    ("倫西斯·李克特", "Rensis Likert", 1903, 1981, "美國", "組織系統(System 1-4)、李克特量表。"),
    ("弗雷德·費德勒", "Fred Fiedler", 1922, 2017, "美國／奧地利", "權變領導理論。"),
]


def main():
    added = skipped = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for name_zh, name, birth, death, nat, bio in PEOPLE:
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s OR name=%s", (name_zh, name))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (name, name_zh, birth, death, nat, bio))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_thinker")
        total = cur.fetchone()[0]
    print(f"philosophy_thinker:第二批新增 {added} 位、跳過 {skipped} 位(已有)、現共 {total} 位")
    print("⚠️ 生卒/國籍/簡介為通行史實 metadata、可查證校正;現代版權大師原則入因子須走真實文獻 principle→#14。")


if __name__ == "__main__":
    main()

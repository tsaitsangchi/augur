#!/usr/bin/env python
"""窮舉補 philosophy_work 書目 — 管理/投資/財務 + 現代哲學家 major 代表著作(書名/年份 metadata)。

🎯 DBpedia notableWork 覆蓋極差(701 位僅 1 筆),改以已知 major 代表著作**書目**補 philosophy_work,
   讓「大師↔代表著作」關係完整、供合規路(原則→#14)與顧問層溯源。
   ⚠️ 補的是**書目 metadata**(書名/年份、事實可查證),非全文——現代版權著作全文法律不可抓(#1);
   公版全文由 fetch_*(Gutenberg/維基文庫)另抓 work_text。
守 #1(書目為事實 metadata、非 AI 摘要著作內容)· #15(書名/年份可查證校正)· #17/#18· 憲章 v1.18.0。
⚠️ 不進預測管線(素養層);原則要進因子須走真實文獻 principle→#14。

用法:PYTHONPATH=src python scripts/seed_thinker_bibliography.py
"""
from augur.core import db

# (thinker 匹配名〔name_zh 或 name〕, 著作英文名, 中文名, 出版年)
WORKS = [
    # ── 投資/財務理論 ──
    ("哈利·馬可維茲", "Portfolio Selection: Efficient Diversification of Investments", "投資組合選擇", 1959),
    ("威廉·夏普", "Portfolio Theory and Capital Markets", "投資組合理論與資本市場", 1970),
    ("羅伯特·席勒", "Irrational Exuberance", "非理性繁榮", 2000),
    ("羅伯特·席勒", "Animal Spirits", "動物本能", 2009),
    ("理查·塞勒", "Misbehaving: The Making of Behavioral Economics", "不當行為", 2015),
    ("理查·塞勒", "Nudge", "推力", 2008),
    ("約翰·柏格", "Common Sense on Mutual Funds", "共同基金必勝法則", 1999),
    ("約翰·柏格", "The Little Book of Common Sense Investing", "約翰柏格投資常識", 2007),
    ("波頓·墨基爾", "A Random Walk Down Wall Street", "漫步華爾街", 1973),
    ("阿斯瓦斯·達摩德仁", "Investment Valuation", "投資估價", 1994),
    ("阿斯瓦斯·達摩德仁", "The Little Book of Valuation", "從價值投資到獲利", 2011),
    ("查理·蒙格", "Poor Charlie's Almanack", "窮查理的普通常識", 2005),
    ("塞斯·卡拉曼", "Margin of Safety", "安全邊際", 1991),
    ("納西姆·塔雷伯", "Fooled by Randomness", "隨機騙局", 2001),
    ("納西姆·塔雷伯", "The Black Swan", "黑天鵝", 2007),
    ("納西姆·塔雷伯", "Antifragile", "反脆弱", 2012),
    ("本華·曼德博", "The (Mis)Behavior of Markets", "股價、棉花與尼羅河密碼", 2004),
    ("大衛·史文森", "Pioneering Portfolio Management", "耶魯操盤手", 2000),
    ("愛德華·索普", "Beat the Dealer", "擊敗莊家", 1962),
    ("愛德華·索普", "A Man for All Markets", "他是賭神,更是股神", 2017),
    ("傑瑞米·西格爾", "Stocks for the Long Run", "散戶投資正典", 1994),
    # ── 總經/經濟(投資週期) ──
    ("約翰·梅納德·凱因斯", "The General Theory of Employment, Interest and Money", "就業、利息與貨幣的一般理論", 1936),
    ("米爾頓·傅利曼", "Capitalism and Freedom", "資本主義與自由", 1962),
    ("米爾頓·傅利曼", "A Monetary History of the United States", "美國貨幣史", 1963),
    ("弗里德里希·海耶克", "The Road to Serfdom", "通往奴役之路", 1944),
    ("約瑟夫·熊彼得", "Capitalism, Socialism and Democracy", "資本主義、社會主義與民主", 1942),
    ("約瑟夫·熊彼得", "The Theory of Economic Development", "經濟發展理論", 1911),
    ("海曼·明斯基", "Stabilizing an Unstable Economy", "穩定不穩定的經濟", 1986),
    # ── 企業管理 ──
    ("彼得·杜拉克", "The Practice of Management", "管理的實踐", 1954),
    ("彼得·杜拉克", "The Effective Executive", "有效的管理者", 1966),
    ("彼得·杜拉克", "Innovation and Entrepreneurship", "創新與創業精神", 1985),
    ("麥可·波特", "Competitive Strategy", "競爭策略", 1980),
    ("麥可·波特", "Competitive Advantage", "競爭優勢", 1985),
    ("亨利·明茲伯格", "The Rise and Fall of Strategic Planning", "策略規劃的興衰", 1994),
    ("彼得·聖吉", "The Fifth Discipline", "第五項修練", 1990),
    ("詹姆·柯林斯", "Good to Great", "從A到A+", 2001),
    ("詹姆·柯林斯", "Built to Last", "基業長青", 1994),
    ("克雷頓·克里斯汀生", "The Innovator's Dilemma", "創新的兩難", 1997),
    ("克雷頓·克里斯汀生", "The Innovator's Solution", "創新者的解答", 2003),
    ("弗雷德里克·泰勒", "The Principles of Scientific Management", "科學管理原理", 1911),
    ("亨利·費堯", "General and Industrial Management", "工業管理與一般管理", 1916),
    ("切斯特·巴納德", "The Functions of the Executive", "經理人員的職能", 1938),
    ("伊格爾·安索夫", "Corporate Strategy", "企業策略", 1965),
    ("羅伯·卡普蘭", "The Balanced Scorecard", "平衡計分卡", 1996),
    ("蓋瑞·哈默爾", "Competing for the Future", "競爭大未來", 1994),
    ("湯姆·彼得斯", "In Search of Excellence", "追求卓越", 1982),
    ("道格拉斯·麥格雷戈", "The Human Side of Enterprise", "企業的人性面", 1960),
    ("亞伯拉罕·馬斯洛", "Motivation and Personality", "動機與人格", 1954),
    # ── 生產/品質 ──
    ("愛德華茲·戴明", "Out of the Crisis", "轉危為安", 1986),
    ("愛德華茲·戴明", "The New Economics", "新經濟學", 1993),
    ("約瑟夫·朱蘭", "Juran's Quality Handbook", "朱蘭品質手冊", 1951),
    ("大野耐一", "Toyota Production System", "豐田生產方式", 1978),
    ("詹姆斯·沃馬克", "The Machine That Changed the World", "改變世界的機器", 1990),
    ("詹姆斯·沃馬克", "Lean Thinking", "精實革命", 1996),
    ("艾利·高德拉特", "The Goal", "目標", 1984),
    ("石川馨", "Guide to Quality Control", "品質管制指南", 1968),
    ("菲利普·克勞斯比", "Quality Is Free", "品質免費", 1979),
    ("亨利·福特", "My Life and Work", "我的生活與工作", 1922),
    # ── 組織理論/管理(第二批) ──
    ("Max Weber", "Economy and Society", "經濟與社會", 1922),
    ("Max Weber", "The Protestant Ethic and the Spirit of Capitalism", "新教倫理與資本主義精神", 1905),
    ("赫伯特·賽門", "Administrative Behavior", "管理行為", 1947),
    ("詹姆斯·馬奇", "Organizations", "組織", 1958),
    ("詹姆斯·馬奇", "A Behavioral Theory of the Firm", "企業行為理論", 1963),
    ("埃德加·沙因", "Organizational Culture and Leadership", "組織文化與領導", 1985),
    ("瑪莉·派克·傅麗特", "Creative Experience", "創造性經驗", 1924),
    ("埃爾頓·梅奧", "The Human Problems of an Industrial Civilization", "工業文明中的人性問題", 1933),
    ("克里斯·阿吉里斯", "Organizational Learning", "組織學習", 1978),
    ("華倫·班尼斯", "On Becoming a Leader", "領導,不需要頭銜", 1989),
    ("弗雷德里克·赫茲伯格", "The Motivation to Work", "工作的激勵", 1959),
    ("約翰·科特", "Leading Change", "領導變革", 1996),
    ("井尻雄士", "The Foundations of Accounting Measurement", "會計計量的基礎", 1967),
    ("華特·休哈特", "Economic Control of Quality of Manufactured Product", "製造產品品質的經濟管制", 1931),
    ("新鄉重夫", "A Study of the Toyota Production System", "豐田生產方式研究", 1981),
    ("田口玄一", "Introduction to Quality Engineering", "品質工程導論", 1986),
    ("麥可·哈默", "Reengineering the Corporation", "企業再造", 1993),
    ("亨利·伽斯柏", "Open Innovation", "開放式創新", 2003),
    ("艾瑞克·馮·希培", "The Sources of Innovation", "創新的來源", 1988),
    ("艾瑞克·馮·希培", "Democratizing Innovation", "創新的民主化", 2005),
    ("埃弗雷特·羅傑斯", "Diffusion of Innovations", "創新的擴散", 1962),
    ("金偉燦", "Blue Ocean Strategy", "藍海策略", 2005),
    ("理查·魯梅特", "Good Strategy Bad Strategy", "好策略・壞策略", 2011),
    ("大前研一", "The Mind of the Strategist", "策略家的智慧", 1982),
    ("普哈拉", "The Fortune at the Bottom of the Pyramid", "金字塔底層大商機", 2004),
    ("菲利普·科特勒", "Marketing Management", "行銷管理", 1967),
    ("艾爾·賴茲", "Positioning: The Battle for Your Mind", "定位", 1981),
    ("戴夫·尤瑞奇", "Human Resource Champions", "人力資源最佳實務", 1997),
    ("倫西斯·李克特", "New Patterns of Management", "管理的新模式", 1961),
    # ── 現代哲學家 major 代表著作(版權、書目;若庫有則補) ──
    ("Martin Heidegger", "Being and Time", "存在與時間", 1927),
    ("Jean-Paul Sartre", "Being and Nothingness", "存在與虛無", 1943),
    ("Michel Foucault", "Discipline and Punish", "規訓與懲罰", 1975),
    ("Michel Foucault", "The Order of Things", "詞與物", 1966),
    ("Ludwig Wittgenstein", "Tractatus Logico-Philosophicus", "邏輯哲學論", 1921),
    ("Ludwig Wittgenstein", "Philosophical Investigations", "哲學研究", 1953),
    ("John Rawls", "A Theory of Justice", "正義論", 1971),
    ("Karl Popper", "The Logic of Scientific Discovery", "科學發現的邏輯", 1934),
    ("Karl Popper", "The Open Society and Its Enemies", "開放社會及其敵人", 1945),
    ("Thomas Kuhn", "The Structure of Scientific Revolutions", "科學革命的結構", 1962),
    ("Jacques Derrida", "Of Grammatology", "論文字學", 1967),
    ("Jürgen Habermas", "The Theory of Communicative Action", "溝通行動理論", 1981),
    ("Hannah Arendt", "The Human Condition", "人的條件", 1958),
    ("Hannah Arendt", "The Origins of Totalitarianism", "極權主義的起源", 1951),
    ("Maurice Merleau-Ponty", "Phenomenology of Perception", "知覺現象學", 1945),
    ("Robert Nozick", "Anarchy, State, and Utopia", "無政府、國家與烏托邦", 1974),
    ("Isaiah Berlin", "Two Concepts of Liberty", "自由的兩種概念", 1958),
    ("Richard Rorty", "Philosophy and the Mirror of Nature", "哲學和自然之鏡", 1979),
]


def main():
    added = skip = missing = 0
    miss_names = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for match, en, zh, year in WORKS:
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s OR name=%s", (match, match))
            r = cur.fetchone()
            if not r:
                missing += 1
                miss_names.append(match)
                continue
            tid = r[0]
            cur.execute("SELECT 1 FROM philosophy_work WHERE thinker_id=%s AND title=%s", (tid, en))
            if cur.fetchone():
                skip += 1
                continue
            cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
                        "VALUES (%s,%s,%s,%s,'book','書目 metadata、代表著作、全文版權或另由 fetch_* 抓公版')",
                        (tid, en, zh, year))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_work"); nw = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT thinker_id) FROM philosophy_work"); nt = cur.fetchone()[0]
    print(f"補書目:新增 {added} 部、已有跳過 {skip} 部、無對映 thinker {missing} 位")
    if miss_names:
        print("  無對映(庫無此 thinker、跳過):", "、".join(miss_names))
    print(f"philosophy_work 共 {nw} 部 / 有著作 thinker {nt} 位")
    print("⚠️ 書目為書名/年份事實 metadata(可查證校正);非全文;現代版權全文法律不可抓。")


if __name__ == "__main__":
    main()

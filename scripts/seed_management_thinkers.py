#!/usr/bin/env python
"""擴 philosophy_thinker — 企業/財務/會計/生產/投資管理領域 major 思想家。

🎯 補「博學投資大師 AI」之商業/管理知識骨架:投資/財務/會計理論(因子假說學術來源、走 principle→
   因子→#14)＋ 企業/生產管理(商業素養層、同廣博哲學)。upsert by name_zh 去重(已有跳過)。
守 #1/#15(生卒/國籍/簡介為通行史實 metadata、可查證校正、非預測真兆)· #28· #17/#18· 憲章 v1.18.0。
⚠️ 人物 metadata、不進預測管線;財務/投資理論之原則要進因子須走真實文獻 principle→#14(非全文、非 AI 摘要)。

用法:PYTHONPATH=src python scripts/seed_management_thinkers.py
"""
from augur.core import db

# (name_zh, name_en, birth, death, nationality, bio)
PEOPLE = [
    # 投資/財務理論(因子假說學術來源)
    ("哈利·馬可維茲", "Harry Markowitz", 1927, 2023, "美國", "現代投資組合理論(MPT)、效率前緣,諾貝爾經濟學獎。"),
    ("威廉·夏普", "William F. Sharpe", 1934, None, "美國", "資本資產定價模型(CAPM)、夏普比率,諾貝爾獎。"),
    ("肯尼斯·法蘭奇", "Kenneth French", 1954, None, "美國", "Fama-French 三因子/五因子模型共同提出者。"),
    ("法蘭科·莫迪利安尼", "Franco Modigliani", 1918, 2003, "美國", "MM 資本結構定理、生命週期假說,諾貝爾獎。"),
    ("默頓·米勒", "Merton Miller", 1923, 2000, "美國", "MM 定理共同提出者,諾貝爾獎。"),
    ("費雪·布萊克", "Fischer Black", 1938, 1995, "美國", "Black-Scholes 選擇權定價模型。"),
    ("邁倫·舒爾斯", "Myron Scholes", 1941, None, "美國", "Black-Scholes 模型,諾貝爾獎。"),
    ("羅伯特·默頓", "Robert C. Merton", 1944, None, "美國", "連續時間金融、選擇權定價,諾貝爾獎。"),
    ("史蒂芬·羅斯", "Stephen Ross", 1944, 2017, "美國", "套利定價理論(APT)、代理理論。"),
    ("羅伯特·席勒", "Robert Shiller", 1946, None, "美國", "行為財務、CAPE 本益比、非理性繁榮,諾貝爾獎。"),
    ("理查·塞勒", "Richard Thaler", 1945, None, "美國", "行為經濟學、心理帳戶、推力,諾貝爾獎。"),
    ("約翰·柏格", "John Bogle", 1929, 2019, "美國", "指數基金之父、Vanguard 創辦人、低成本被動投資。"),
    ("波頓·墨基爾", "Burton Malkiel", 1932, None, "美國", "《漫步華爾街》、效率市場、隨機漫步。"),
    ("阿斯瓦斯·達摩德仁", "Aswath Damodaran", 1957, None, "美國", "估值學(Valuation)權威、DCF 與相對估值。"),
    ("查理·蒙格", "Charlie Munger", 1924, 2023, "美國", "多元思維模型、能力圈、波克夏副董。"),
    ("塞斯·卡拉曼", "Seth Klarman", 1957, None, "美國", "《安全邊際》、深度價值投資。"),
    ("納西姆·塔雷伯", "Nassim Nicholas Taleb", 1960, None, "黎巴嫩／美國", "黑天鵝、反脆弱、尾部風險。"),
    ("本華·曼德博", "Benoit Mandelbrot", 1924, 2010, "法國／美國", "碎形幾何、市場的(錯誤)行為、厚尾。"),
    # 會計
    ("盧卡·帕西奧利", "Luca Pacioli", 1447, 1517, "義大利", "複式簿記之父、《算術、幾何、比與比例概要》。"),
    # 總經/經濟(與投資週期/宏觀相關)
    ("約翰·梅納德·凱因斯", "John Maynard Keynes", 1883, 1946, "英國", "總體經濟學、有效需求、選美理論(投資心理)。"),
    ("米爾頓·傅利曼", "Milton Friedman", 1912, 2006, "美國", "貨幣主義、自由市場,諾貝爾獎。"),
    ("弗里德里希·海耶克", "Friedrich Hayek", 1899, 1992, "奧地利／英國", "奧地利學派、自發秩序、景氣循環,諾貝爾獎。"),
    ("約瑟夫·熊彼得", "Joseph Schumpeter", 1883, 1950, "奧地利／美國", "創造性破壞、創新與景氣循環。"),
    ("尼古拉·康德拉季耶夫", "Nikolai Kondratiev", 1892, 1938, "俄國", "長波(康波)週期理論——augur 康波鏡頭之源。"),
    ("海曼·明斯基", "Hyman Minsky", 1919, 1996, "美國", "金融不穩定假說、明斯基時刻。"),
    # 企業管理
    ("彼得·杜拉克", "Peter Drucker", 1909, 2005, "奧地利／美國", "現代管理學之父、目標管理、知識工作者。"),
    ("麥可·波特", "Michael Porter", 1947, None, "美國", "競爭策略、五力分析、價值鏈、競爭優勢(護城河)。"),
    ("亨利·明茲伯格", "Henry Mintzberg", 1939, None, "加拿大", "管理角色、策略形成、組織構型。"),
    ("彼得·聖吉", "Peter Senge", 1947, None, "美國", "《第五項修練》、學習型組織、系統思考。"),
    ("詹姆·柯林斯", "Jim Collins", 1958, None, "美國", "《從A到A+》、刺蝟原則、第五級領導。"),
    ("克雷頓·克里斯汀生", "Clayton Christensen", 1952, 2020, "美國", "破壞式創新、創新者的兩難。"),
    ("弗雷德里克·泰勒", "Frederick Winslow Taylor", 1856, 1915, "美國", "科學管理之父、時間動作研究。"),
    ("亨利·費堯", "Henri Fayol", 1841, 1925, "法國", "管理程序學派、管理五功能十四原則。"),
    ("切斯特·巴納德", "Chester Barnard", 1886, 1961, "美國", "組織理論、非正式組織、權威接受論。"),
    ("伊格爾·安索夫", "Igor Ansoff", 1918, 2002, "美國", "策略管理之父、安索夫矩陣。"),
    ("羅伯·卡普蘭", "Robert S. Kaplan", 1940, None, "美國", "平衡計分卡、作業基礎成本制(ABC)。"),
    ("蓋瑞·哈默爾", "Gary Hamel", 1954, None, "美國", "核心競爭力、策略意圖、管理創新。"),
    ("湯姆·彼得斯", "Tom Peters", 1942, None, "美國", "《追求卓越》、7S 架構。"),
    ("道格拉斯·麥格雷戈", "Douglas McGregor", 1906, 1964, "美國", "X 理論與 Y 理論(人性假設)。"),
    ("亞伯拉罕·馬斯洛", "Abraham Maslow", 1908, 1970, "美國", "需求層次理論(管理與動機)。"),
    # 生產/品質管理
    ("愛德華茲·戴明", "W. Edwards Deming", 1900, 1993, "美國", "全面品質管理(TQM)、PDCA、統計品管、日本品質革命。"),
    ("約瑟夫·朱蘭", "Joseph Juran", 1904, 2008, "美國／羅馬尼亞", "品質三部曲、朱蘭品質手冊、80/20 應用。"),
    ("大野耐一", "Taiichi Ohno", 1912, 1990, "日本", "豐田生產系統(TPS)、及時生產(JIT)、七大浪費。"),
    ("詹姆斯·沃馬克", "James P. Womack", 1948, None, "美國", "精實生產(Lean)、《改變世界的機器》。"),
    ("艾利·高德拉特", "Eliyahu Goldratt", 1947, 2011, "以色列", "限制理論(TOC)、《目標》。"),
    ("石川馨", "Kaoru Ishikawa", 1915, 1989, "日本", "品質圈、石川圖(魚骨圖)。"),
    ("菲利普·克勞斯比", "Philip Crosby", 1926, 2001, "美國", "零缺陷、品質免費。"),
    ("亨利·福特", "Henry Ford", 1863, 1947, "美國", "流水線大量生產、福特制。"),
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
    print(f"philosophy_thinker:新增 {added} 位管理/財務/投資思想家、跳過 {skipped} 位(已有)、現共 {total} 位")
    print("⚠️ 生卒/國籍/簡介為通行史實 metadata、可查證校正;財務/投資理論之原則入因子須走真實文獻 principle→#14。")


if __name__ == "__main__":
    main()

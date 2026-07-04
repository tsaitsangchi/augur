#!/usr/bin/env python
"""擴充 philosophy_thinker — 全球 major 哲學家個人資料 metadata(各傳統)。

🎯 把人類哲學史 major 思想家(希臘/中國/印度/伊斯蘭/中世紀/近代/德國古典/分析/歐陸/日本)
之個人資料(生卒/國籍/簡介)落地 philosophy_thinker,擴哲學素養框架(憲章 v1.17.0)之人物骨架。
upsert by name_zh 去重(已有跳過)、本地零 usage、冪等。

守 #1/#15(資料為**通行史實 metadata**、可查證校正、非預測真兆——CLAUDE #17 允許之事實 metadata)·
   #17(限真實史實、非 AI 觀點)· #18。
⚠️ 生卒/簡介為通行史實整理、可校;此為人物 metadata、不進預測管線(廣博哲學量化零價值)。
⚠️ CLAUDE #29b 傳輸工件(transport artifact):PHILOSOPHERS 硬編策展清單為一次性 seed 載體,
   內容已落 philosophy_thinker(2026-07-04 稽核實查確認),預設不執行(無參數只印矩陣)。
   新增策展一律走 acquire_knowledge --source manual_curation → promote_knowledge 管線,不回頭擴充本檔;
   傳記欄位源自 AI 記憶整理,DBpedia/Wikidata 實證覆核與本檔退役列後續、待用戶裁示(#19)。

執行指令矩陣:
  python scripts/seed_world_philosophers.py         # 無參數:印本矩陣(傳輸工件、預設不執行)
  python scripts/seed_world_philosophers.py --run   # 明示重放 seed(冪等、已有跳過)
"""
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

# (name_zh, name_en, birth, death, nationality, bio);BC 用負數、在世 death=None
PHILOSOPHERS = [
    # 古希臘前蘇格拉底
    ("泰勒斯", "Thales", -624, -546, "希臘", "米利都學派、西方哲學第一人,主張水為萬物本原。"),
    ("阿那克西曼德", "Anaximander", -610, -546, "希臘", "米利都學派,提出「無限者」(apeiron)。"),
    ("畢達哥拉斯", "Pythagoras", -570, -495, "希臘", "畢達哥拉斯學派,萬物皆數。"),
    ("赫拉克利特", "Heraclitus", -535, -475, "希臘", "萬物流變、邏各斯,「人不能兩次踏入同一條河」。"),
    ("巴門尼德", "Parmenides", -515, -450, "希臘", "愛利亞學派,主張存在不變不動。"),
    ("芝諾(愛利亞)", "Zeno of Elea", -490, -430, "希臘", "愛利亞學派,芝諾悖論。"),
    ("恩培多克勒", "Empedocles", -494, -434, "希臘", "四根說(土水火氣)。"),
    ("阿那克薩哥拉", "Anaxagoras", -500, -428, "希臘", "提出「奴斯」(心靈)為動力。"),
    ("德謨克利特", "Democritus", -460, -370, "希臘", "原子論奠基者。"),
    ("普羅泰戈拉", "Protagoras", -490, -420, "希臘", "智者派,「人是萬物的尺度」。"),
    ("蘇格拉底", "Socrates", -470, -399, "希臘", "西方哲學奠基者,助產術、知德合一,述而不作。"),
    ("第歐根尼", "Diogenes of Sinope", -412, -323, "希臘", "犬儒學派代表。"),
    ("伊壁鳩魯", "Epicurus", -341, -270, "希臘", "伊壁鳩魯學派,快樂主義、原子論。"),
    ("芝諾(斯多葛)", "Zeno of Citium", -334, -262, "希臘", "斯多葛學派創始人。"),
    ("普羅提諾", "Plotinus", 204, 270, "羅馬", "新柏拉圖主義奠基者。"),
    # 中國
    ("孔子", "Confucius", -551, -479, "中國", "儒家創始人,仁、禮,《論語》。"),
    ("孟子", "Mencius", -372, -289, "中國", "儒家,性善論、民本思想。"),
    ("莊子", "Zhuangzi", -369, -286, "中國", "道家,逍遙、齊物。"),
    ("墨子", "Mozi", -470, -391, "中國", "墨家創始人,兼愛、非攻。"),
    ("荀子", "Xunzi", -310, -235, "中國", "儒家,性惡論、隆禮重法。"),
    ("韓非子", "Han Fei", -280, -233, "中國", "法家集大成,法術勢。"),
    ("董仲舒", "Dong Zhongshu", -179, -104, "中國", "漢儒,天人感應、罷黜百家。"),
    ("王充", "Wang Chong", 27, 100, "中國", "東漢唯物論者,《論衡》。"),
    ("朱熹", "Zhu Xi", 1130, 1200, "中國", "宋代理學集大成,理氣論。"),
    ("王陽明", "Wang Yangming", 1472, 1529, "中國", "心學,知行合一、致良知。"),
    # 印度
    ("釋迦牟尼", "Gautama Buddha", -563, -483, "印度", "佛教創始人,四聖諦、緣起(生卒為通行說)。"),
    ("龍樹", "Nagarjuna", 150, 250, "印度", "中觀派,空性。"),
    ("商羯羅", "Adi Shankara", 788, 820, "印度", "吠檀多不二論。"),
    # 中世紀/伊斯蘭/猶太
    ("安瑟倫", "Anselm of Canterbury", 1033, 1109, "義大利", "經院哲學,上帝存在的本體論證明。"),
    ("阿伯拉爾", "Peter Abelard", 1079, 1142, "法國", "經院哲學,概念論。"),
    ("阿奎那", "Thomas Aquinas", 1225, 1274, "義大利", "經院哲學集大成,《神學大全》。"),
    ("司各脫", "Duns Scotus", 1266, 1308, "蘇格蘭", "經院哲學,個體性原理。"),
    ("奧卡姆", "William of Ockham", 1287, 1347, "英國", "唯名論,奧卡姆剃刀。"),
    ("肯迪", "Al-Kindi", 801, 873, "阿拉伯", "阿拉伯哲學之父。"),
    ("法拉比", "Al-Farabi", 872, 950, "阿拉伯", "伊斯蘭新柏拉圖主義。"),
    ("阿維森納", "Avicenna", 980, 1037, "波斯", "伊斯蘭哲學、醫學,《治療論》。"),
    ("安薩里", "Al-Ghazali", 1058, 1111, "波斯", "伊斯蘭神學家,《哲學家的矛盾》。"),
    ("阿威羅伊", "Averroes", 1126, 1198, "安達魯斯", "亞里斯多德註釋者。"),
    ("邁蒙尼德", "Maimonides", 1138, 1204, "安達魯斯", "猶太哲學,《迷途指津》。"),
    # 近代
    ("馬基維利", "Niccolò Machiavelli", 1469, 1527, "義大利", "政治哲學,《君主論》。"),
    ("蒙田", "Michel de Montaigne", 1533, 1592, "法國", "懷疑論、隨筆體。"),
    ("帕斯卡", "Blaise Pascal", 1623, 1662, "法國", "《思想錄》、帕斯卡賭注。"),
    ("萊布尼茨", "Gottfried Wilhelm Leibniz", 1646, 1716, "德國", "理性主義,單子論、最佳世界。"),
    ("柏克萊", "George Berkeley", 1685, 1753, "愛爾蘭", "主觀唯心論,「存在即被感知」。"),
    ("孟德斯鳩", "Montesquieu", 1689, 1755, "法國", "三權分立,《論法的精神》。"),
    ("伏爾泰", "Voltaire", 1694, 1778, "法國", "啟蒙思想家。"),
    ("維柯", "Giambattista Vico", 1668, 1744, "義大利", "歷史哲學,《新科學》。"),
    # 德國古典
    ("費希特", "Johann Gottlieb Fichte", 1762, 1814, "德國", "主觀觀念論。"),
    ("謝林", "Friedrich Schelling", 1775, 1854, "德國", "同一哲學、自然哲學。"),
    ("赫德", "Johann Gottfried Herder", 1744, 1803, "德國", "歷史主義、語言哲學。"),
    # 19 世紀
    ("邊沁", "Jeremy Bentham", 1748, 1832, "英國", "效益主義創始人。"),
    ("齊克果", "Søren Kierkegaard", 1813, 1855, "丹麥", "存在主義先驅。"),
    ("孔德", "Auguste Comte", 1798, 1857, "法國", "實證主義、社會學創始。"),
    ("費爾巴哈", "Ludwig Feuerbach", 1804, 1872, "德國", "人本唯物論、宗教批判。"),
    ("恩格斯", "Friedrich Engels", 1820, 1895, "德國", "馬克思主義共同奠基者。"),
    ("斯賓塞", "Herbert Spencer", 1820, 1903, "英國", "社會達爾文主義。"),
    ("愛默生", "Ralph Waldo Emerson", 1803, 1882, "美國", "超驗主義。"),
    ("梭羅", "Henry David Thoreau", 1817, 1862, "美國", "超驗主義,《湖濱散記》、公民不服從。"),
    ("皮爾士", "Charles Sanders Peirce", 1839, 1914, "美國", "實用主義創始、符號學。"),
    ("狄爾泰", "Wilhelm Dilthey", 1833, 1911, "德國", "詮釋學、精神科學。"),
    # 19-20 之交
    ("弗雷格", "Gottlob Frege", 1848, 1925, "德國", "現代邏輯、分析哲學奠基。"),
    ("胡塞爾", "Edmund Husserl", 1859, 1938, "德國", "現象學創始人。"),
    ("柏格森", "Henri Bergson", 1859, 1941, "法國", "生命哲學、綿延。"),
    ("杜威", "John Dewey", 1859, 1952, "美國", "實用主義、教育哲學。"),
    ("懷海德", "Alfred North Whitehead", 1861, 1947, "英國", "歷程哲學、《數學原理》。"),
    ("摩爾", "G. E. Moore", 1873, 1958, "英國", "分析哲學、常識實在論。"),
    # 20 世紀分析
    ("維根斯坦", "Ludwig Wittgenstein", 1889, 1951, "奧地利", "語言哲學,《邏輯哲學論》。"),
    ("石里克", "Moritz Schlick", 1882, 1936, "德國", "維也納學派創始。"),
    ("卡爾納普", "Rudolf Carnap", 1891, 1970, "德國", "邏輯實證論、維也納學派。"),
    ("波普爾", "Karl Popper", 1902, 1994, "奧地利", "可證偽性、科學哲學。"),
    ("奎因", "Willard Van Orman Quine", 1908, 2000, "美國", "分析哲學、整體論。"),
    ("庫恩", "Thomas Kuhn", 1922, 1996, "美國", "科學革命、典範轉移。"),
    ("羅爾斯", "John Rawls", 1921, 2002, "美國", "政治哲學,《正義論》。"),
    ("以賽亞·伯林", "Isaiah Berlin", 1909, 1997, "英國", "自由的兩種概念、價值多元論。"),
    # 20 世紀歐陸
    ("海德格", "Martin Heidegger", 1889, 1976, "德國", "存在主義/現象學,《存在與時間》。"),
    ("雅斯培", "Karl Jaspers", 1883, 1969, "德國", "存在哲學。"),
    ("沙特", "Jean-Paul Sartre", 1905, 1980, "法國", "存在主義,《存在與虛無》。"),
    ("卡繆", "Albert Camus", 1913, 1960, "法國", "荒謬哲學,《薛西弗斯的神話》。"),
    ("波娃", "Simone de Beauvoir", 1908, 1986, "法國", "存在主義女性主義,《第二性》。"),
    ("梅洛龐蒂", "Maurice Merleau-Ponty", 1908, 1961, "法國", "知覺現象學。"),
    ("列維納斯", "Emmanuel Levinas", 1906, 1995, "法國", "他者倫理學。"),
    ("漢娜·鄂蘭", "Hannah Arendt", 1906, 1975, "德國", "政治哲學,《極權主義的起源》。"),
    ("阿多諾", "Theodor Adorno", 1903, 1969, "德國", "法蘭克福學派、批判理論。"),
    ("霍克海默", "Max Horkheimer", 1895, 1973, "德國", "法蘭克福學派。"),
    ("班雅明", "Walter Benjamin", 1892, 1940, "德國", "批判理論、美學。"),
    ("馬庫色", "Herbert Marcuse", 1898, 1979, "德國", "法蘭克福學派、《單向度的人》。"),
    ("哈伯馬斯", "Jürgen Habermas", 1929, None, "德國", "溝通行動理論。"),
    ("高達美", "Hans-Georg Gadamer", 1900, 2002, "德國", "哲學詮釋學,《真理與方法》。"),
    ("傅柯", "Michel Foucault", 1926, 1984, "法國", "權力/知識、系譜學。"),
    ("德希達", "Jacques Derrida", 1930, 2004, "法國", "解構主義。"),
    ("德勒茲", "Gilles Deleuze", 1925, 1995, "法國", "差異哲學。"),
    ("利科", "Paul Ricoeur", 1913, 2005, "法國", "詮釋學。"),
    # 日本
    ("道元", "Dogen", 1200, 1253, "日本", "曹洞宗禪。"),
    ("西田幾多郎", "Nishida Kitaro", 1870, 1945, "日本", "京都學派,純粹經驗。"),
    ("鈴木大拙", "D.T. Suzuki", 1870, 1966, "日本", "禪學傳播者。"),
    # 印度近代
    ("辨喜", "Swami Vivekananda", 1863, 1902, "印度", "吠檀多、印度教改革。"),
    ("泰戈爾", "Rabindranath Tagore", 1861, 1941, "印度", "詩人哲學家。"),
    ("甘地", "Mahatma Gandhi", 1869, 1948, "印度", "非暴力哲學(satyagraha)。"),
    ("克里希那穆提", "Jiddu Krishnamurti", 1895, 1986, "印度", "心靈哲學。"),
    # 其他
    ("馬丁·布伯", "Martin Buber", 1878, 1965, "奧地利", "《我與你》對話哲學。"),
    ("斯賓格勒", "Oswald Spengler", 1880, 1936, "德國", "歷史哲學,《西方的沒落》。"),
]


def main():
    if "--run" not in sys.argv:
        print(__doc__.split("執行指令矩陣:")[1].strip())
        return
    added = skipped = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for name_zh, name, birth, death, nat, bio in PHILOSOPHERS:
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s", (name_zh,))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (name, name_zh, birth, death, nat, bio))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_thinker")
        total = cur.fetchone()[0]
    print(f"philosophy_thinker:新增 {added} 位、跳過 {skipped} 位(已有)、現共 {total} 位")
    print("⚠️ 生卒/國籍/簡介為通行史實 metadata、可查證校正;非預測真兆、不進預測管線。")


if __name__ == "__main__":
    main()

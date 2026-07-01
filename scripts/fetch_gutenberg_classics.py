#!/usr/bin/env python
"""抓 Project Gutenberg 公版英文經典入庫 — 本地下載 .txt 解析、零 Claude usage。

🎯 把公版英文經典逐字全文落地 philosophy_work_text,作哲學素養框架(憲章 v1.17.0)原典參考:
   投資/行為經典(Reminiscences/群眾瘋狂/烏合之眾)＋ 西方哲學經典全集(柏拉圖→羅素)＋ 經濟(國富論)。
本地 urllib 下載 + 程式解析(非 WebFetch 小模型→逐字無摘要)、冪等可續、可排程。

守 #1(逐字無 AI 摘要)· #28(本地零 usage)· #15(限公版、license DB CHECK)· #18。
⚠️ 廣博哲學全文量化零價值、僅素養/解讀素材、不產因子、不進預測管線(憲章 v1.17.0 philosophy 邊界)。
⚠️ 範圍:納人類哲學經典、排除非哲學離題(純物理/數學);只抓公版。

用法:PYTHONPATH=src python scripts/fetch_gutenberg_classics.py [--force]
"""
import re
import sys
import urllib.request

from augur.core import db

UA = {"User-Agent": "augur-research/1.0 (public-domain archival)"}

# 思想家(name_zh, name, birth, death, nationality, bio);BC 用負數
TH = {
    "plato": ("柏拉圖", "Plato", -428, -348, "希臘", "古希臘哲學家,蘇格拉底學生、亞里斯多德之師,西方哲學奠基者,著對話錄。"),
    "aristotle": ("亞里斯多德", "Aristotle", -384, -322, "希臘", "古希臘哲學家,柏拉圖學生、亞歷山大之師,百科全書式思想家。"),
    "marcus": ("馬可·奧理略", "Marcus Aurelius", 121, 180, "羅馬", "羅馬皇帝、斯多葛派哲學家,著《沉思錄》。"),
    "epictetus": ("愛比克泰德", "Epictetus", 55, 135, "羅馬", "斯多葛派哲學家,原為奴隸,《手冊》《談話錄》。"),
    "cicero": ("西塞羅", "Marcus Tullius Cicero", -106, -43, "羅馬", "羅馬政治家、哲學家、雄辯家,《論義務》。"),
    "lucretius": ("盧克萊修", "Lucretius", -99, -55, "羅馬", "羅馬詩人、哲學家,伊壁鳩魯派,《物性論》。"),
    "augustine": ("奧古斯丁", "Augustine of Hippo", 354, 430, "羅馬", "教父哲學集大成者,《懺悔錄》《上帝之城》。"),
    "boethius": ("波愛修斯", "Boethius", 477, 524, "羅馬", "晚期羅馬哲學家,《哲學的慰藉》。"),
    "descartes": ("勒內·笛卡爾", "René Descartes", 1596, 1650, "法國", "近代哲學之父、理性主義奠基者,「我思故我在」。"),
    "bacon": ("法蘭西斯·培根", "Francis Bacon", 1561, 1626, "英國", "經驗主義先驅、科學方法奠基,《新工具》。"),
    "spinoza": ("巴魯赫·史賓諾莎", "Baruch Spinoza", 1632, 1677, "荷蘭", "理性主義哲學家,《倫理學》。"),
    "locke": ("約翰·洛克", "John Locke", 1632, 1704, "英國", "經驗主義、自由主義奠基,《人類理解論》。"),
    "hume": ("大衛·休謨", "David Hume", 1711, 1776, "蘇格蘭", "經驗主義、懷疑論,《人類理解研究》。"),
    "hobbes": ("湯瑪斯·霍布斯", "Thomas Hobbes", 1588, 1679, "英國", "社會契約論,《利維坦》。"),
    "rousseau": ("讓-雅克·盧梭", "Jean-Jacques Rousseau", 1712, 1778, "法國", "啟蒙思想家,《社會契約論》。"),
    "kant": ("伊曼努爾·康德", "Immanuel Kant", 1724, 1804, "德國", "德國古典哲學奠基,三大批判。"),
    "hegel": ("黑格爾", "Georg Wilhelm Friedrich Hegel", 1770, 1831, "德國", "德國觀念論集大成,辯證法。"),
    "schopenhauer": ("叔本華", "Arthur Schopenhauer", 1788, 1860, "德國", "意志哲學、悲觀主義。"),
    "nietzsche": ("弗里德里希·尼采", "Friedrich Nietzsche", 1844, 1900, "德國", "權力意志、超人說、價值重估。"),
    "mill": ("約翰·斯圖亞特·彌爾", "John Stuart Mill", 1806, 1873, "英國", "效益主義、自由主義,《論自由》。"),
    "marx": ("卡爾·馬克思", "Karl Marx", 1818, 1883, "德國", "歷史唯物論、政治經濟學批判。"),
    "james": ("威廉·詹姆斯", "William James", 1842, 1910, "美國", "實用主義哲學、心理學之父。"),
    "russell": ("伯特蘭·羅素", "Bertrand Russell", 1872, 1970, "英國", "分析哲學、數理邏輯奠基者之一。"),
    "smith": ("亞當·斯密", "Adam Smith", 1723, 1790, "蘇格蘭", "古典經濟學之父,「看不見的手」。"),
    "lebon": ("古斯塔夫·勒龐", "Gustave Le Bon", 1841, 1931, "法國", "社會心理學家,《烏合之眾》,行為財務思想源。"),
    "mackay": ("查爾斯·麥凱", "Charles Mackay", 1814, 1889, "英國", "《群眾瘋狂》金融泡沫史,行為財務/逆向先驅。"),
}

# id=Gutenberg book id;th=TH key 或 existing=現有 thinker name_zh
P, PH, EC, BE, IN = "philosophy_classic", "philosophy_classic", "economics_classic", "behavioral_classic", "investment_classic"
GUTENBERG = [
    # 投資/行為經典
    {"id": 60979, "zh": "股票作手回憶錄", "en": "Reminiscences of a Stock Operator", "y": 1923, "w": IN, "existing": "傑西·李佛摩"},
    {"id": 445, "zh": "烏合之眾", "en": "The Crowd: A Study of the Popular Mind", "y": 1895, "w": BE, "th": "lebon"},
    {"id": 24518, "zh": "大眾幻想與群眾瘋狂", "en": "Memoirs of Extraordinary Popular Delusions and the Madness of Crowds", "y": 1841, "w": BE, "th": "mackay"},
    # 古希臘 — 柏拉圖
    {"id": 1497, "zh": "理想國", "en": "The Republic", "y": -380, "w": P, "th": "plato"},
    {"id": 1600, "zh": "會飲篇", "en": "Symposium", "y": -385, "w": P, "th": "plato"},
    {"id": 1656, "zh": "申辯篇", "en": "Apology", "y": -399, "w": P, "th": "plato"},
    {"id": 1658, "zh": "斐多篇", "en": "Phaedo", "y": -380, "w": P, "th": "plato"},
    {"id": 1672, "zh": "高爾吉亞篇", "en": "Gorgias", "y": -380, "w": P, "th": "plato"},
    {"id": 1643, "zh": "美諾篇", "en": "Meno", "y": -385, "w": P, "th": "plato"},
    {"id": 1572, "zh": "蒂邁歐篇", "en": "Timaeus", "y": -360, "w": P, "th": "plato"},
    {"id": 1636, "zh": "斐德羅篇", "en": "Phaedrus", "y": -370, "w": P, "th": "plato"},
    # 古希臘 — 亞里斯多德
    {"id": 8438, "zh": "尼各馬可倫理學", "en": "The Nicomachean Ethics", "y": -340, "w": P, "th": "aristotle"},
    {"id": 6762, "zh": "政治學", "en": "Politics: A Treatise on Government", "y": -340, "w": P, "th": "aristotle"},
    {"id": 1974, "zh": "詩學", "en": "The Poetics of Aristotle", "y": -335, "w": P, "th": "aristotle"},
    # 古羅馬 — 斯多葛/伊壁鳩魯
    {"id": 2680, "zh": "沉思錄", "en": "Meditations", "y": 180, "w": P, "th": "marcus"},
    {"id": 10661, "zh": "談話錄(選)", "en": "A Selection from the Discourses of Epictetus", "y": 108, "w": P, "th": "epictetus"},
    {"id": 45109, "zh": "手冊", "en": "The Enchiridion", "y": 125, "w": P, "th": "epictetus"},
    {"id": 47001, "zh": "論義務", "en": "De Officiis", "y": -44, "w": P, "th": "cicero"},
    {"id": 785, "zh": "物性論", "en": "On the Nature of Things", "y": -55, "w": P, "th": "lucretius"},
    # 中世紀
    {"id": 3296, "zh": "懺悔錄", "en": "The Confessions of St. Augustine", "y": 397, "w": P, "th": "augustine"},
    {"id": 45304, "zh": "上帝之城(卷一)", "en": "The City of God, Volume I", "y": 426, "w": P, "th": "augustine"},
    {"id": 14328, "zh": "哲學的慰藉", "en": "The Consolation of Philosophy", "y": 524, "w": P, "th": "boethius"},
    # 近代
    {"id": 70091, "zh": "形上學的沉思", "en": "Six Metaphysical Meditations", "y": 1641, "w": P, "th": "descartes"},
    {"id": 59, "zh": "談談方法", "en": "Discourse on the Method", "y": 1637, "w": P, "th": "descartes"},
    {"id": 45988, "zh": "新工具", "en": "Novum Organum", "y": 1620, "w": P, "th": "bacon"},
    {"id": 56463, "zh": "培根隨筆", "en": "Bacon's Essays, and Wisdom of the Ancients", "y": 1597, "w": P, "th": "bacon"},
    {"id": 3800, "zh": "倫理學", "en": "Ethics", "y": 1677, "w": P, "th": "spinoza"},
    {"id": 10615, "zh": "人類理解論", "en": "An Essay Concerning Human Understanding", "y": 1689, "w": P, "th": "locke"},
    {"id": 7370, "zh": "政府論次講", "en": "Second Treatise of Government", "y": 1689, "w": P, "th": "locke"},
    {"id": 9662, "zh": "人類理解研究", "en": "An Enquiry Concerning Human Understanding", "y": 1748, "w": P, "th": "hume"},
    {"id": 3207, "zh": "利維坦", "en": "Leviathan", "y": 1651, "w": P, "th": "hobbes"},
    {"id": 46333, "zh": "社會契約論", "en": "The Social Contract & Discourses", "y": 1762, "w": P, "th": "rousseau"},
    # 德國古典
    {"id": 4280, "zh": "純粹理性批判", "en": "The Critique of Pure Reason", "y": 1781, "w": P, "th": "kant"},
    {"id": 5683, "zh": "實踐理性批判", "en": "The Critique of Practical Reason", "y": 1788, "w": P, "th": "kant"},
    {"id": 5682, "zh": "道德形上學基礎", "en": "Fundamental Principles of the Metaphysic of Morals", "y": 1785, "w": P, "th": "kant"},
    {"id": 58169, "zh": "哲學史講演錄", "en": "Hegel's Lectures on the History of Philosophy", "y": 1837, "w": P, "th": "hegel"},
    {"id": 10732, "zh": "叔本華隨筆(悲觀論集)", "en": "The Essays of Arthur Schopenhauer: Studies in Pessimism", "y": 1851, "w": P, "th": "schopenhauer"},
    # 尼采
    {"id": 4363, "zh": "善惡的彼岸", "en": "Beyond Good and Evil", "y": 1886, "w": P, "th": "nietzsche"},
    {"id": 1998, "zh": "查拉圖斯特拉如是說", "en": "Thus Spake Zarathustra", "y": 1883, "w": P, "th": "nietzsche"},
    {"id": 52319, "zh": "道德的譜系", "en": "The Genealogy of Morals", "y": 1887, "w": P, "th": "nietzsche"},
    {"id": 51356, "zh": "悲劇的誕生", "en": "The Birth of Tragedy", "y": 1872, "w": P, "th": "nietzsche"},
    {"id": 52190, "zh": "瞧!這個人", "en": "Ecce Homo", "y": 1888, "w": P, "th": "nietzsche"},
    # 英美近現代
    {"id": 34901, "zh": "論自由", "en": "On Liberty", "y": 1859, "w": P, "th": "mill"},
    {"id": 11224, "zh": "效益主義", "en": "Utilitarianism", "y": 1863, "w": P, "th": "mill"},
    {"id": 61, "zh": "共產黨宣言", "en": "The Communist Manifesto", "y": 1848, "w": P, "th": "marx"},
    {"id": 5116, "zh": "實用主義", "en": "Pragmatism", "y": 1907, "w": P, "th": "james"},
    {"id": 621, "zh": "宗教經驗之種種", "en": "The Varieties of Religious Experience", "y": 1902, "w": P, "th": "james"},
    {"id": 5827, "zh": "哲學問題", "en": "The Problems of Philosophy", "y": 1912, "w": P, "th": "russell"},
    # 經濟(與投資相關)
    {"id": 3300, "zh": "國富論", "en": "An Inquiry into the Nature and Causes of the Wealth of Nations", "y": 1776, "w": EC, "th": "smith"},
    {"id": 67363, "zh": "道德情操論", "en": "The Theory of Moral Sentiments", "y": 1759, "w": EC, "th": "smith"},
]


def download_book(book_id):
    last = None
    for u in (f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
              f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
              f"https://www.gutenberg.org/files/{book_id}/{book_id}-8.txt"):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read().decode("utf-8", "replace")
        except Exception as e:
            last = e
    raise RuntimeError(f"book {book_id} 下載失敗: {last}")


def strip_gutenberg(txt):
    s = re.search(r"\*\*\* ?START OF TH[EI][^*]*\*\*\*", txt)
    start = s.end() if s else 0
    e = re.search(r"\*\*\* ?END OF TH[EI][^*]*\*\*\*", txt) or re.search(r"\nEnd of (?:the )?Project Gutenberg", txt)
    end = e.start() if e else len(txt)
    return txt[start:end].strip()


# 整行嚴格匹配章標題(避免誤抓內文 BOOK 引用);含英文序數 BOOK(沉思錄 THE FIRST BOOK)。
CHAP_RE = r"^\s*(BOOK [IVXLC]+|THE [A-Z]+ BOOK|CHAPTER [IVXLC]+|MEDITATION [IVX]+|PART [IVX]+|SECTION [IVX]+)\.?\s*$"


def _chunk(body):
    paras, chunks, buf = re.split(r"\n\s*\n", body), [], ""
    for p in paras:
        buf += p.strip() + "\n\n"
        if len(buf) > 8000:
            chunks.append(buf.strip())
            buf = ""
    if buf.strip():
        chunks.append(buf.strip())
    return [(f"段{i}", c) for i, c in enumerate(chunks, 1) if len(c) > 60]


def split_chapters(body):
    ms = list(re.finditer(CHAP_RE, body, re.M))
    if len(ms) < 2:
        return _chunk(body)
    out = []
    pre = re.sub(r"\n{3,}", "\n\n", body[:ms[0].start()]).strip()
    if len(pre) > 500:
        out.append(("前言", pre))
    for i, m in enumerate(ms):
        title = re.sub(r"\s+", " ", m.group(1).strip())[:60]
        content = re.sub(r"\n{3,}", "\n\n", body[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(body)]).strip()
        if len(content) > 60:
            out.append((title, content))
    return out


def upsert_thinker(cur, th):
    name_zh, name, birth, death, nat, bio = th
    cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s", (name_zh,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING thinker_id", (name, name_zh, birth, death, nat, bio))
    return cur.fetchone()[0]


def main():
    force = "--force" in sys.argv
    ok = skip = fail = 0
    with db.connect() as conn:
        for g in GUTENBERG:
            with db.transaction(conn) as cur:
                if "existing" in g:
                    cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s", (g["existing"],))
                    tid = cur.fetchone()[0]
                else:
                    tid = upsert_thinker(cur, TH[g["th"]])
                cur.execute("SELECT work_id FROM philosophy_work WHERE title_zh=%s", (g["zh"],))
                r = cur.fetchone()
                if r:
                    wid = r[0]
                else:
                    cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
                                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING work_id",
                                (tid, g["en"], g["zh"], g["y"], g["w"], "公版原典、Project Gutenberg"))
                    wid = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM philosophy_work_text WHERE work_id=%s", (wid,))
                existing = cur.fetchone()[0]
            if existing and not force:
                skip += 1
                continue
            try:
                rows = split_chapters(strip_gutenberg(download_book(g["id"])))
            except Exception as e:
                print(f"❌ 《{g['zh']}》#{g['id']} 失敗: {e}")
                fail += 1
                continue
            src = f"https://www.gutenberg.org/ebooks/{g['id']}"
            with db.transaction(conn) as cur:
                if force:
                    cur.execute("DELETE FROM philosophy_work_text WHERE work_id=%s", (wid,))
                for seq, (chap, content) in enumerate(rows, 1):
                    cur.execute("INSERT INTO philosophy_work_text (work_id,chapter,seq,content,source_url,license) "
                                "VALUES (%s,%s,%s,%s,%s,'public_domain')", (wid, chap, seq, content, src))
            total = sum(len(r[1]) for r in rows)
            print(f"✓ 《{g['zh']}》: {len(rows)} 章、{total:,} 字")
            ok += 1
    print(f"\n完成:新增 {ok} 部、跳過 {skip} 部(已有)、失敗 {fail} 部")


if __name__ == "__main__":
    main()

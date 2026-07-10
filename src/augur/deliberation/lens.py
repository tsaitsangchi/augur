"""審議視角庫 — lens prompt 住 DB(deliberation_lens)+ claim 提案 prompt 組裝(P3 模組化;#29b 修正)。

🎯 這支在做什麼(白話):把「懷疑者/完整性/治權」等視角之 prompt 從 code hardcode 搬進 DB
   (新增 lens=INSERT 一列零改碼,#29b);並組裝 claim 提案 prompt(契約+lens+題目+目標檔+L1 grounding)。
   契約=固定「anchor 只放參數本身、四 oracle 錨式範例」——與 anchors.py 之解析規則同錨。

守 #29b(lens 住 DB)· #12(CONTRACT 單一住所)。前置=migrate_deliberation_ddl.py --run(deliberation_lens seed)。
"""
from augur.core import db
from augur.deliberation.anchors import schema_grounding

CONTRACT = """你的任務:對下列題目提出至多 {n} 條「可機械驗證的宣稱」(claims)。鐵則:
1. 每條 claim 指定 assigned_verifier(四選一);anchor **只放參數本身、絕不含 verifier 名稱前綴**:
   - information_schema:驗表/欄存在。anchor 範例:"feature_values" 或 "feature_values.panel_date"
   - db_query:單標量查詢比較。anchor 範例:"SELECT count(*) FROM model_registry => >= 4"
   - file_grep:檔內正則匹配。anchor 範例:"CLAUDE.md::換機接續"
   - import_isolation:隔離不變式。anchor 恆為:"check_isolation"
   無法用以上四工具驗證的重要疑點 → assigned_verifier='human_claude'(交人裁,不要硬湊)。
2. claim_text 用正向可判真偽句式(「X 存在」「Y 數量≥N」),不用問句。
3. 只輸出 JSON。{lens}

題目:{topic}
{target_block}"""

_FALLBACK = {"skeptic": "你是對抗性懷疑者:假設題目中的宣稱可能是錯的,提出能「證偽」它的檢查點。"}


def load_lenses():
    """回 {lens_key: prompt}(enabled;DB 未建/空時退回內建 skeptic,不炸)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('deliberation_lens')")
        if not cur.fetchone()[0]:
            return dict(_FALLBACK)
        cur.execute("SELECT lens_key, prompt FROM deliberation_lens WHERE enabled ORDER BY lens_key")
        rows = cur.fetchall()
    return {k: p for k, p in rows} or dict(_FALLBACK)


def lens_keys():
    return sorted(load_lenses())


def build_prompt(topic, target_block, lens, n):
    """組裝 claim 提案 prompt(契約+lens+題目+目標檔+L1 schema grounding)。lens 不存在→退 skeptic。"""
    lenses = load_lenses()
    lp = lenses.get(lens) or lenses.get("skeptic") or _FALLBACK["skeptic"]
    return CONTRACT.format(n=n, lens=lp, topic=topic, target_block=target_block) + schema_grounding(topic)

"""語料 CLEAN 准入述詞 SSOT(P4 已拍板 2026-07-04,計畫 §8 拍板紀錄)— works/items 雙側、三端同一閘。

🎯 這支在做什麼(白話):知識語料「哪些列可進語意層(切句/嵌入/檢索)」的唯一判準住所——
   works 側=philosophy_work.review_flag = false(T-1 稽核過才放行);
   items 側=item_text.license ∈ 四值白名單 × item.entity_type ∈ 語意層准入集
   (P4 拍板值:paper/report 先行;book/compound/material/dataset 首期不入語意層、metadata 檢索可)。
   fail-closed:NULL/未知值一律不放行(SQL IN 述詞之 NULL 語意=非 TRUE=排除,天然 fail-closed)。
   三端(S3 builder / S5 embed_knowledge / S7 retrieval)一律 import 本檔產出之 SQL 片段,
   禁 inline 複本(#12)。
守 #1(license 硬擋、零 AI 入庫鏈)· #12(單一住所)· 計畫 §3-S3/S5 N1・§8 P4。
"""

# 與 knowledge_item_text.license DB CHECK 同一封閉集(migrate_text_understanding_ddl.py);
# 兩處必須同步變更(跨檔一致性,CLAUDE #19)。
LICENSE_WHITELIST = ("public_domain", "cc-by", "cc-by-sa", "cc0")

# P4 拍板值(2026-07-04):語意層(切句/嵌入/檢索)entity_type 准入集。未列=不入(fail-closed),
# 含 compound/material/dataset(metadata 檢索仍可,不經本閘)。
# 'document'=admin 控制台本機檔/一般文件(死點②修,計畫拍板P2附;不硬標 'report' 造假 #15)。
SEMANTIC_ENTITY_TYPES = ("paper", "report", "document")


def _quoted(values):
    return ", ".join(f"'{v}'" for v in values)


def clean_work_sql(work_alias="w"):
    """works 側 CLEAN 述詞(SQL 片段,語意層 S3/S5/S7 三端同一閘):
    (a) review_flag = false(T-1 稽核過才放行;NULL 未稽核不放行,fail-closed);
    (b) corpus_class = 'literary'(W2.5 單一語意欄,稽核決/拍板13:取代會漏接之 work_type 白名單
        ——Roget=book、注疏=philosophy_classic 皆 reference 卻非 dictionary/thesaurus、舊白名單漏接;
        NULL corpus_class 不放行,fail-closed)。reference 語料只走 lexicon 路、不進切句/嵌入/檢索。"""
    return f"{work_alias}.review_flag = false AND {work_alias}.corpus_class = 'literary'"


def clean_item_sql(item_alias="i", itext_alias="x", access_scope=None):
    """items 側 CLEAN_ITEM 述詞(SQL 片段):license 白名單 × entity_type 語意層准入 [× access_scope 隔離]。

    item_alias   = knowledge_item 之別名(供 entity_type)
    itext_alias  = knowledge_item_text 之別名(供 license/access_scope)
    access_scope = None(預設,不濾;供**嵌入端**——public+local_private 皆嵌才可被檢索);
                   'public'=**對外檢索**用(local_private 本機檔不入對外池,拍板P2 機器保證);
                   'local_private'=admin 私有對話用。值來自封閉集(非外部輸入,無注入面);NULL 欄不放行。"""
    p = (f"{itext_alias}.license IN ({_quoted(LICENSE_WHITELIST)}) "
         f"AND {item_alias}.entity_type IN ({_quoted(SEMANTIC_ENTITY_TYPES)})")
    if access_scope is not None:
        assert access_scope in ("public", "local_private"), f"非法 access_scope: {access_scope}"
        p += f" AND {itext_alias}.access_scope = '{access_scope}'"
    return f"({p})"

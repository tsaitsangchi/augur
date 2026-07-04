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
# 含 book/compound/material/dataset(metadata 檢索仍可,不經本閘)。
SEMANTIC_ENTITY_TYPES = ("paper", "report")


def _quoted(values):
    return ", ".join(f"'{v}'" for v in values)


def clean_work_sql(work_alias="w"):
    """works 側 CLEAN 述詞(SQL 片段):review_flag=false 才放行;NULL(未稽核)不放行。"""
    return f"{work_alias}.review_flag = false"


def clean_item_sql(item_alias="i", itext_alias="x"):
    """items 側 CLEAN_ITEM 述詞(SQL 片段):license 白名單 × entity_type 語意層准入(P4 拍板值)。

    item_alias  = knowledge_item 之別名(供 entity_type)
    itext_alias = knowledge_item_text 之別名(供 license)
    值來自模組常數封閉集(非外部輸入,無注入面);NULL 不放行。
    """
    return (f"({itext_alias}.license IN ({_quoted(LICENSE_WHITELIST)}) "
            f"AND {item_alias}.entity_type IN ({_quoted(SEMANTIC_ENTITY_TYPES)}))")

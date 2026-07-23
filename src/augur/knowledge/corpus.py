"""語料 CLEAN 准入述詞 SSOT(P4 已拍板 2026-07-04,計畫 §8 拍板紀錄)— works/items 雙側、三端同一閘。

🎯 這支在做什麼(白話):知識語料「哪些列可進語意層(切句/嵌入/檢索)」的唯一判準住所——
   works 側=philosophy_work.review_flag = false(T-1 稽核過才放行);
   items 側=item_text.license ∈ 四值白名單 × item.entity_type ∈ 語意層准入集
   (P4 拍板值:paper/report 先行;book/compound/material/dataset 首期不入語意層、metadata 檢索可)。
   fail-closed:NULL/未知值一律不放行(SQL IN 述詞之 NULL 語意=非 TRUE=排除,天然 fail-closed)。
   三端(S3 builder / S5 embed_knowledge / S7 retrieval)一律 import 本檔產出之 SQL 片段,
   禁 inline 複本(#12)。
守 #1(license 硬擋、零 AI 入庫鏈)· #12(單一住所)· 計畫 §3-S3/S5 N1・§8 P4。

執行指令矩陣(本檔=library #18;免 DB 免 API 可個別驗證):
  python -m augur.knowledge.corpus              # 印用途+公開入口(唯讀)
  python -m augur.knowledge.corpus --selftest   # 純紅綠自測(零 IO)
"""

# 與 knowledge_item_text.license DB CHECK 同一封閉集(migrate_text_understanding_ddl.py);
# 兩處必須同步變更(跨檔一致性,CLAUDE #19)。
# 'owned_local'=自有私有軌〔憲章 v1.36.0 全文准入三軌〕:用戶自有專有內容(如 ERP),
#   **硬性配 access_scope='local_private'**(DB CHECK 綁死、永不公開);安全繫於本機+私有+自有(非公開轉載),守 #1(自有即真兆、非 AI 生成)。
LICENSE_WHITELIST = ("public_domain", "cc-by", "cc-by-sa", "cc0", "owned_local")

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


def clean_item_sql(item_alias="i", itext_alias="x", access_scope=None,
                   is_super=False, allowed_domains=None, owner_user_id=None):
    """items 側 CLEAN_ITEM 述詞 ＋ RBAC 收窄(RBAC P3/群組建置,計畫 §4.2/§4.5、憲章 v1.29.0)。**回 (sql_fragment, params:list)**。

    呼叫端一律 `frag, fp = clean_item_sql(...); sql += frag; params += fp`(消手工位置對齊、關 fail-open)。
    - license 白名單 × entity_type 語意層准入(封閉集、安全字面內插);access_scope 封閉集內插。
    - **RBAC 收窄軸依 access_scope 分流(開放值 → 參數化不內插;`is_super=True` 一律不濾——embed/builder 非讀取路徑傳此)**:
      · `access_scope='local_private'` → **擁有者收窄**(私有＝個人文件、無部門語意、**不 domain 收窄**、跨使用者 fail-closed):
        非 super 且 `owner_user_id` 給 → `AND owner_user_id = %s`;非 super 且 owner 缺 → `AND false`(deny);super → 見全部私有。
      · 其餘(`public`/None) → **domain 收窄**(群組 grant):非 super 且 `allowed_domains` 空(None/[]) → `AND false`(**預設 deny**);
        非空 → `AND domain = ANY(%s::text[])`。
    讀取路徑(retrieve_*)一律傳 resolve 之 (is_super, allowed, user_id);private 側須帶 `owner_user_id`＝登入者(#5 anti-leakage)。
    """
    p = (f"{itext_alias}.license IN ({_quoted(LICENSE_WHITELIST)}) "
         f"AND {item_alias}.entity_type IN ({_quoted(SEMANTIC_ENTITY_TYPES)})")
    params = []
    if access_scope is not None:
        assert access_scope in ("public", "local_private"), f"非法 access_scope: {access_scope}"
        p += f" AND {itext_alias}.access_scope = '{access_scope}'"
    if access_scope == "local_private":                        # 擁有者收窄:私有＝個人文件、跨使用者 fail-closed
        if not is_super:
            if owner_user_id is None:
                p += " AND false"                              # 無身分/未登入 → deny
            else:
                p += f" AND {itext_alias}.owner_user_id = %s"
                params.append(owner_user_id)
    elif not is_super:                                         # public/None → domain 收窄(群組 grant)
        if not allowed_domains:
            p += " AND false"                                  # fail-closed:無授權域=零可見
        else:
            p += f" AND {item_alias}.domain = ANY(%s::text[])"
            params.append(list(allowed_domains))
    return f"({p})", params


def _selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    # 白名單/准入集封閉性(#19 跨檔同步鎖:內容變更即本測失敗、逼同步審視)
    chk("LICENSE_WHITELIST 含 owned_local 私有軌", "owned_local" in LICENSE_WHITELIST)
    chk("SEMANTIC 准入集=paper/report/document", SEMANTIC_ENTITY_TYPES == ("paper", "report", "document"))
    # _quoted:SQL 字面內插格式
    chk("_quoted 逗號分隔加單引號", _quoted(("a", "b")) == "'a', 'b'")
    # works 側:review_flag 與 literary 雙鎖、fail-closed 語意
    ws = clean_work_sql("w")
    chk("clean_work_sql 含 review_flag=false", "w.review_flag = false" in ws)
    chk("clean_work_sql 含 corpus_class='literary'", "w.corpus_class = 'literary'" in ws)
    # items 側:回 (str, list) 契約
    frag, fp = clean_item_sql()
    chk("clean_item_sql 回 (str,list)", isinstance(frag, str) and isinstance(fp, list))
    chk("license/entity 白名單內插", "license IN (" in frag and "entity_type IN (" in frag)
    # 命門:public/None 非 super 且無授權域 → fail-closed AND false、零參數
    chk("無授權域 fail-closed(AND false)", frag.endswith("false)") and fp == [])
    # 授權域給 → domain 收窄、參數化帶 list
    frag2, fp2 = clean_item_sql(allowed_domains=["philosophy"])
    chk("授權域→domain=ANY 參數化", "domain = ANY(%s::text[])" in frag2 and fp2 == [["philosophy"]])
    # super 一律不濾(embed/builder 路徑)
    frag3, fp3 = clean_item_sql(is_super=True)
    chk("is_super 不加 AND false", "false" not in frag3 and fp3 == [])
    # local_private 非 super 且無 owner → deny;有 owner → 擁有者收窄參數化
    fd, pd_ = clean_item_sql(access_scope="local_private", owner_user_id=None)
    chk("private 無 owner fail-closed", fd.endswith("false)") and pd_ == [])
    fo, po = clean_item_sql(access_scope="local_private", owner_user_id=7)
    chk("private 有 owner→擁有者收窄", "owner_user_id = %s" in fo and po == [7])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.corpus --selftest;免 DB 免 API)")

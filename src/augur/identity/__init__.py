"""augur.identity — 世界實體身份(領域名詞 package;非 knowledge/identity.py 之使用者認證)。

🎯 這支在做什麼(白話):承 Layer 3「結構補正」身份側——系統鑄造之永久 identifier(augur_id)、
   跨來源同一性 claim、lifecycle 事件(merge/split/retire/relist/redirect＋lineage)、身份屬性
   as-of 雙時間繫結。與 `augur.knowledge.identity`(pbkdf2 密碼/session 之使用者認證)**同名不同義、
   刻意分立 package 避免撞名**:此處是「世界個體之身份」,那裡是「登入者之身份」。

模組:
  identifier.py       — 系統 identifier 鑄造與解析(ID.11-14)
  claim.py            — identity claim 一級介面(ID.30-32)
  lifecycle.py        — lifecycle 事件與 lineage 重建(ID.40-44)
  attribute_version.py— 身份屬性 as-of 雙時間繫結(ID.60-61)

DDL 單一權威=scripts/migrate_identity_ddl.py(#12,內聯 DDL);本 package 僅經既有表消費、不重維 CREATE TABLE。
守 #12(DDL 單一住所)· #18(每支 library 可個別 --selftest)· 憲章 ID.11-61。
"""

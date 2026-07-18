# Augur Steward 裁決第 2026-014 號

**ONT.20 同一性判準之操作化採認暨物理載體補欄（`identity_criteria`）——L2 決策一(a)**

* **依據**：`AUGUR-ONT v1.0` ONT.20（判準宣告義務）、ONT.31；`AUGUR-ID v1.0` ID.20（判準採認）；`AUGUR-MC v1.3 §8.1`；Phase 2 #19 卷宗裁②之審查鏡評估（證據堅實）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-18 書面核示 L2 決策一「准 (a)」
* **日期**：2026-07-18｜**登錄**：Amendment Log AL-2026-017

## 主文

1. **（判準採認，ID.20）** 追認下列操作化同一性判準：**T.1 Security**＝`stock_id ~ '^[0-9]'`（與 core_gate 同一謂詞）、未退役期間之代碼唯一指涉、重用依 ID.43 分裂；**T.2 Index**＝來源自標 `industry_category ∈ {Index, 大盤}`、一碼一指數個體；**FredSeries**＝series_id 唯一指涉、revision 屬觀測層不分裂身份。**Automobile 確認為守衛列**（T.24 分類節點、禁 instance 繫結之負面判準——ONT.31 防回歸錨）。
2. **（載體補欄）** `entity_type_catalog` 增 `identity_criteria` 欄（DDL minor）；四列判準文字寫入。**ONT.20 自此機器可判**：`SELECT count(*) FROM entity_type_catalog WHERE identity_criteria IS NULL` ＝ 0 為合規閘。
3. **（施作記錄）** 沙盒實測→生產施作同日完成（超級使用者路徑；應用角色無 UPDATE 之 ACL 不變）；生產驗收：閘＝0、資料零觸動（247 表／1695 列不變）。回退＝`DROP COLUMN`；當日全庫備份與 restic 異碟副本在。
4. **（效果）** Phase 2 #19 卷宗**裁②以本裁決結案**（採認路線 (a)）——新鑄 alias 之 'adopted' 地位自此有 ID.20 採認紀錄支撐。卷宗其餘簽核項（准併、裁①並發鎖、裁③下市時序）**仍待 Steward**。

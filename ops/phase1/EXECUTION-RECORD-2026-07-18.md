# Phase 1(d) owner 分離——生產施作執行記錄 [I]

* **日期**：2026-07-18｜**核准**：Steward P5 書面「准」（本日）｜**施工者**：授權幕僚（依施工包 §三逐步）

## 執行時間線與各步證據

| 步 | 內容 | 結果 |
|---|---|---|
| 0 | 施工前快照 | owners=augur、247 表、prediction_values=1695（留痕於對話與本檔） |
| 1 | 全庫備份 | `augur_pre_phase1_20260718_0928.dump`（pg_dump -Fc，**10.04GB**，09:28–09:39） |
| 2 | **還原實測** | 還原至 `augur_restore_test`（-j8）：**exit 0、錯誤 0 行、5/5 基準核對逐項吻合**（表 247／predictions 1695／verdicts 420／universe 12394／supersede 0）→「經實測之備份」成立（L7.25 精神）；臨時庫已清 |
| 3 | SQL 手術 | `phase1_owner_separation.sql`：10 ALTER TABLE＋2 ALTER FUNCTION＋6 GRANT＋2 REVOKE＋4 ALTER DEFAULT PRIVILEGES＋1 DO，與腳本逐項相符 |
| 4 | **驗收閘 A** | (a) 十表 owner＝**augur_owner ×10** ✅；(b) augur_app 可寫 raw_supersede_log ✅；(c) **augur（原 owner）DELETE→42501 權限拒——owner 旁路於生產正式關閉** ✅；(d) 資料零觸動（247／1695／420 同術前）✅ |
| 5 | 密碼＋giga 側切換 | augur_app 密碼已設（不入版控不入對話）；giga 側 `.env` DB_USER→augur_app；**TCP 登入實測成功**＋唯讀健檢綠（predictions=1695、憲章表可讀） |

## 憲章意義

**AUD-02 殘餘風險（強制機制與其可解除者同屬一權限主體）自本日起於生產不成立**：十張憲章表與 2 個 SECURITY DEFINER 函式隸屬 `augur_owner`（NOLOGIN），應用角色（augur_app／過渡期 augur）對憲章表僅 SELECT/INSERT（serving `superseded_by` 欄例外）——append-only 由 **ACL＋19 守衛 trigger 雙層強制**，L7.16 之義務首次物理成立。

## 殘餘步驟（步 7，需 Steward 側執行——giga 對 /home/hugo 無寫入權）

hugo 側切換（過渡橋保證未切換期間零斷線，可從容執行）：

```bash
# 以 hugo 身分：
# 1. 編輯 /home/hugo/project/augur/.env：
#    DB_USER=augur_app
#    DB_PASSWORD=<向幕僚索取或自設：ALTER ROLE augur_app PASSWORD '...'>
# 2. 重啟四個 serving 進程（advisor_openai／admin_console／chat_ui／probability_ui）
# 3. 驗收閘 B：服務起後功能正常＋下次 heal 遇 value_mismatch 後
#    SELECT count(*) FROM raw_supersede_log; > 0
```

**〔Steward 裁示（2026-07-18）：`augur` 保留作維運通道，不設 NOLOGIN。〕** 附帶效果與歸責註記：
* 步 7 切換後之歸責分工反而更清晰——**服務行為＝augur_app、人工維運＝augur**，兩通道於 pg 層可區分（`pg_stat_activity.usename`），優於切換前「服務與維運同走 augur」之混同。
* `augur` 對憲章十表維持僅 SELECT/INSERT（UPDATE/DELETE 已收回、非 owner）——維運通道**不構成**憲章表旁路。
* 殘餘揭露（AUD-24 同族）：維運通道為共享憑證，其行為歸責至「持有該憑證之人」而非個人——個人化維運帳號屬 Phase 3（行動六元組）之後的收斂項，不在本步範圍。

## 回退

任一異常：`ops/phase1/phase1_rollback.sql`＋（若已切）.env 改回＋重啟——全程可逆；備份在 `/home/giga/augur/backups/`。

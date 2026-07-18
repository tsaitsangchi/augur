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

## 步 7 完成與驗收閘 B（2026-07-18 12:5x–13:0x）

* **步 7 ✅**（Steward 以一鍵腳本執行）：hugo 側 `.env` 備份→`DB_USER=augur_app`＋密碼搬移（未經手抄未顯示）→**權限收 600**（修掉全機可讀）→四服務全停全起（PID 862341/862345/862350/862355）。
* **閘 B 現況**：
  * 服務健檢 ✅：8090（chat）/8500（admin）/8600（probability）HTTP 200、8399（advisor）伺服器活（404＝無根路由）。
  * `.env` 切換 ✅：腳本自檔案實讀印出 `DB_USER=augur_app`；四進程均於變更後重啟（config.py 於啟動載入）。
  * **連線身分直接捕獲 ⏳ 待組織性流量**：服務對 PG 隨用隨開（毫秒級），50×0.25s 採樣＋六路由觸發均未命中活連線——**已部署哨兵**（每 2s 採樣、捕獲即報、12h 超時），待真實使用或夜間維護之首個連線完成 `usename=augur_app` 之最終實證。誠實定性：閘 B 之三項中二項已證、一項待證，**不宣稱全綠**。
* 遺留：`ALTER DEFAULT PRIVILEGES` 之效果與 heal 首筆 supersede 留痕（待 Phase 1(a)(b) code 部署後）。

## Phase 1 全線收官（2026-07-18）

| 子項 | 狀態 | 證據 |
|---|---|---|
| (a) 分支併 main | ✅ | #19 三鏡全 GO＋Steward 准併；merge `12210c5`＋tombstone 測試升級 `f95557b`；18/18 綠 |
| (b) hugo 側部署 | ✅ | fast-forward 至 f95557b（23 檔 +2365/−16）、四服務重啟、健檢綠、部署側 selftest 綠；heal 快照 gate 上線 |
| (c) predict role | ✅ | Steward TTY：REVOKE 84 素養表／GRANT 163 預測表；抽驗＝素養 false／預測 true／憲章表 false |
| (d) owner 分離 | ✅ | 閘 A 全綠＋抹除函式 REVOKE（#19 major 修復） |
| 步 7 .env 切換 | ✅ | 服務＝augur_app、維運＝augur 雙通道 |
| 安裝①②③ | ✅ | giga venv 滿配；restic 異碟備份鏈（snapshot cbb73c19＋5% 讀取驗證零錯誤）；pg_stat_statements 追蹤中 |
| 監看 | ▶ | 連線身分哨兵＋首筆 supersede 留痕（5 分鐘輪詢） |

**Phase 1 之憲章意義**：owner 分離（L7.16）＋append-only 雙層強制＋抹除唯人路徑＋predict 三層隔離＋heal 快照 gate 上線——**行為層武裝完畢，等待第一筆 value_mismatch 將 P4.E5 從條文變成資料列。**

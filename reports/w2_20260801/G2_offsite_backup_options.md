# [DRAFT 呈案] G2｜異地備份三案比較（外接碟／加密上 NAS／第二機）

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（`AUGUR-L6 v1.2` L6.18(c)）**：本呈案由 AI（W2 呈案批 agent）起草，親驗數字全附指令與輸出可獨立重放，建議附證偽條件；裁決專屬 Constitution Steward（§8.1／L6.18(a)），本文僅呈案不代決。
> 起草日：2026-08-01（六）｜設計 SSOT：`reports/augur_problem_solution_register_20260801.md` §3-G2＋`reports/augur_steward_adjudication_sheet_20260801.md` §七｜問題 SSOT：`reports/augur_evolution_execution_plan_20260731.md` §三-W6、r3 §七「備份單點」。

---

## §1 問題與授權鏈

**問題一句話**：全機只有一顆實體磁碟（`WDC WDS100T2B0C` 1TB NVMe；WSL2 之 `/dev/sdd` 為 C: 碟上之 vhdx、`/mnt/c` 同碟）——DB（60 GB）＋dump＋鏡像＋repo 工作樹全在同一實體裝置上，**碟亡＝全亡**。G1（定期 pg_dump＋/mnt/c 鏡像）已解「檔案級誤刪」與「vhdx 損毀」兩層；**「實體碟亡」層唯異裝置可解**，`backup_database.sh` 檔頭自己誠實寫明「不假裝解決」。

**授權鏈（L6.5-L6.8 四要件留痕）**：
- (a) 範圍：Steward 指示之 W2 呈案批（登錄冊 CR4「W2 呈案全並行」）；本 agent 授權範圍＝**全程唯讀 repo 與 DB**＋親驗現況＋產出本呈案文件（scratchpad），零施作。
- (b) 結束條件：本文件交付主 session 審閱即結束。
- (c) 可撤銷：Steward／hugo 隨時收回。
- (d) 任務參照：登錄冊 §1 `G2`（W2、狀態 ☐）＋裁決單 §七 G2 建議案。
- 本案三案皆涉**外部副作用或購置**（接新裝置／寫公司 NAS／寫第二機），全屬「碰護欄即停」域（#6／#26）——**任一案之施作均待 Steward 圈選後另行有界授權**。

---

## §2 現況親驗（2026-08-01 執行時現查；指令＋輸出）

### 2.1 儲存拓撲：單一實體碟、無任何外接裝置

```
$ lsblk
sdd     8:48   0     1T  0 disk /  （…/mnt/wslg/distro /snap）   ← vhdx，落在 C: 碟
$ df -h / /mnt/c
/dev/sdd       1007G  147G  810G  16% /
C:\             931G  522G  410G  57% /mnt/c
$ ls /mnt/
c  wsl  wslg          ← 無 /mnt/d、/mnt/e：現刻零外接裝置掛載
```

機器文件佐證：`ops/machines/PC002-S1800.md:56`（`WDC WDS100T2B0C`＝WD Blue SN550 1TB NVMe；C: 930.5 GB；HealthStatus=Healthy）。

### 2.2 G1 已落地：本地＋鏡像兩層現在存在（⚠與登錄冊輸入時點不符，明標）

```
$ ls ~/db_dumps/            → augur_20260731_postmerge_Fd（11G）＋ augur_20260801_weekly_Fd（11G，13:24）
$ ls /mnt/c/database/       → augur_20260801_weekly_Fd（13:26 鏡像完成）
$ tail ~/logs/backup.log    → ✓ 11G / 2696 物件 / 352s；✓ 鏡像完成；✓ 備份輪完成
$ crontab -l | grep backup  → 30 7 * * 6 … bash scripts/backup_database.sh --run（週六 07:30 週備份行已掛）
$ SELECT pg_size_pretty(pg_database_size('augur'))  → 60 GB
```

**明標與 r3／登錄冊輸入不符處**（皆屬 G1 於 r3 之後落地所致、非矛盾）：r3 §七「唯一 dump＝07-31 postmerge；/mnt/c/database 已空；12 條 cron 零 pg_dump」→ **今日親驗已變**：weekly dump＋鏡像＋cron 備份行皆在。**未變的是**：以上全部仍在同一顆實體碟上，本呈案標的（碟亡層）依舊零覆蓋。

### 2.3 敏感性盤點（現查；決定 B 案授權衝突之量）

```
$ SELECT license, count(*) FROM knowledge_item_text GROUP BY license;
  owned_local=150,772｜cc0=3,491｜public_domain=2,492｜cc-by=1,557｜cc-by-sa=218（總 158,530）
$ owned_local 佔比 = 95.11%；access_scope='local_private' 佔比 = 95.11%（150,775 列）
$ philosophy_work_text：31,782 列全 public_domain
$ 前十大表（dump 內容主體）：TaiwanOptionDaily 5.8GB、knowledge_sentence_embedding 5.8GB、
  USStockPrice 3.7GB、TaiwanStockInstitutionalInvestorsBuySell 3.1GB…（FinMind 授權資料為大宗）
```

**⚠與記憶索引不符明標**：記憶「版權三軌五值（owned_local 佔 96.8%）」→ **今日親驗 95.11%**（150,772／158,530；公版與 CC 件持續增長稀釋佔比）。

**盤點結論**：任何一份 dump ＝ (i) 15 萬件 `owned_local` 私有全文（access_scope=local_private，治權判準綁定不出公開通道）＋ (ii) FinMind 訂閱授權資料（再散布受限）＋ (iii) evolution／governance 帳本。**dump 的敏感等級＝庫的敏感等級**，異地方案必須以此為前提。`.env`（密鑰）不在 dump、不在 git——碟亡後還原之兩項人工前置（CLAUDE #31：.env 重建＋dump 實體到位）中，本案只解 dump 一項。

### 2.4 C 案通道現況（私有通道先例）

```
$ scripts/pull_desktop_evolution_delta.sh：tailscale ssh hugo@desktop-8mqpfs8、
  BatchMode 公鑰、離線優雅跳過、憑證不過線——先例腳本已在 cron 每 2h 跑
$ tail ~/logs/desktop_pull.log →
  2026-08-01 14:37:22 DESKTOP(desktop-8mqpfs8) 不可達——優雅跳過（今為週六下午仍未上線）
$ ops/machines/DESKTOP-8MQPFS8.md：系統碟 1007G total、725G avail ← 容量足以收 dump 輪替
```

**誠實記載**：記憶稱「DESKTOP 僅週末開」，但**今日（週六）04:37→14:37 六次探測全數不可達**——C 案之可用性繫於一台實際上線紀律未經驗證的機器。

---

## §3 威脅模型分層與三案方案

### 3.1 威脅模型分層（§威脅模型分層，本呈案定稿版）

| 層 | 威脅 | 現有覆蓋 | 本案標的 |
|---|---|---|---|
| L1 | 檔案級誤刪／壞遷移／壞 DDL | ✅ G1 本地 weekly dump（ext4，toc 驗證後才轉正） | — |
| L2 | vhdx 損毀（WSL 虛擬碟壞檔） | ✅ /mnt/c 鏡像（跨 vhdx 邊界） | — |
| L3 | **實體碟亡**（NVMe 故障） | ❌ 零覆蓋（L1/L2 同碟陪葬） | **✔ 三案皆解** |
| L4 | **機器全損／竊盜／火災／勒索軟體加密** | ❌ 零覆蓋 | ✔ 三案覆蓋度不同（見 3.5） |
| L5 | 授權／資料治理約束（owned_local＋FinMind） | 治權判準（憲章全文准入三軌；#5） | **約束條件**：異地介質不得成為新洩漏面 |

### 3.2 A 案：外接碟（裁決單建議之主案）

**做法**：一顆 USB 外接碟（≥256 GB 即可存 20+ 份 weekly dump；1TB 級可存 ~90 份。成本＝千元台幣級一次性——**估算、非實查數字**）。接上 Windows 主機時 WSL 端以 `/mnt/<x>` 可見；`backup_database.sh` 擴充「offsite 第三步」：**碟在→自動拷貝＋驗 toc＋白名單輪替；碟不在→誠實印「異地層本輪未做」**（不假綠）。平時拔下離線存放（可進一步異址存放以升級 L4 覆蓋）。

**逐檔 diff 計畫（`scripts/backup_database.sh`，圈選後實作）**：
1. `:22-27`（環境區）加兩行：`OFFSITE_DIR="${AUGUR_DUMP_OFFSITE:-}"`（空＝未啟用）；`KEEP_OFFSITE="${AUGUR_DUMP_KEEP_OFFSITE:-8}"`。
2. `:33-44` `status()` 加「異地現況」段：offsite 目錄存在→列 dump＋**「距上次異地備份 N 天」**（N>14 印 ⚠ 紅字）；不存在→印「外接碟未掛載（異地層無覆蓋）」。
3. `:63-65`（`[3/4]` 鏡像步之後）插 `[3b/4] 異地`：`[ -n "$OFFSITE_DIR" ] && [ -d "$OFFSITE_DIR" ]` 才做——`cp -r "$dest" "$OFFSITE_DIR/"` → **異地副本再跑一次 `pg_restore -l` 物件數 >100 驗證**（拷貝損毀不算備份）→ 同一 `NAME_RE` 白名單輪替留 `KEEP_OFFSITE` 份；否則印誠實跳過訊息。
4. `:77-90` `selftest()` 加紅綠：offsite 未設→跳過路徑判定不誤刪；仿冒名在 offsite 同樣不動（複用 `is_rotatable` 純函式餵真輸入）。
- 絆線紀律：新斷言先驗紅（暫改 `NAME_RE` 使其必紅、確認 selftest 會叫、還原）；不加字面斷言。

**惰性風險（裁決單已點名）與緩解**：本案唯一人工環節＝「把碟插上」。緩解＝上述 status 之「距上次異地 N 天」紅字＋週六備份 cron 之 log 尾行永遠印異地層做／未做——**紅燈會亮**（優化第一原則），剩下的是人看不看；三個月未輪替即觸證偽條件（§4）。

### 3.3 B 案：加密後上公司 NAS（裁決單建議不採）

**做法**：dump 打包→對稱加密（`age`／`gpg`，passphrase 不落 repo）→上傳公司 NAS。
**優點**：真異址、可全自動、零購置。
**不採理由**（採納裁決單建議，補上親驗量）：
1. **授權疑義是雙向的**：公司資產存放個人研究資料之授權疑義（裁決單原句）；反向亦然——dump 內含 150,772 件 `owned_local` 私有全文＋FinMind 授權資料（§2.3），即使加密，「存放位置」本身已把私有語料之實體託管移到雇主資產上，authorization 邊界屬 Steward 域、AI 不得代判。
2. **NAS 本身是 L4 高風險面**：`augur_evolution_execution_plan_20260731.md:104` 明載該 NAS「全網域可 Modify」——勒索軟體橫向加密網域儲存為常見路徑，備份放在攻擊面上與離線外接碟反向。
3. PC002 為 Trend Micro 企業機（機器記憶）——在公司資產上留存大體積私有資料之持續痕跡，惰性風險最低但治理成本最高。

### 3.4 C 案：第二機 DESKTOP（裁決單建議之輔案）

**做法**：新腳本 `scripts/push_backup_to_desktop.sh`（仿 `pull_desktop_evolution_delta.sh` 骨架：tailscale ssh、BatchMode、離線優雅跳過、`--check/--run/--runbook/--selftest`、#29 四件）——DESKTOP 可達時 `rsync -a --partial ~/db_dumps/augur_*_weekly_Fd hugo@desktop-8mqpfs8:~/db_dumps/`，完成後**經 ssh 於遠端跑 `pg_restore -l` 驗物件數**（傳到≠備到）。初期**不掛 cron**（手動於 DESKTOP 上線時跑，或由既有週末待辦順帶）；若日後掛 cron＝自動鏈延長，依 L6.16 附四項對照聲明另呈。
**優點**：真異裝置＋自動化潛力＋私有通道先例在（兩機皆 hugo 自有資產，零授權疑義）＋DESKTOP 725G 可用空間足。
**限制（親驗）**：今日週六 14:37 仍不可達（§2.4）——**可用性未經實證**；且 PC002 持有可寫 DESKTOP 之 ssh 金鑰，若 PC002 被勒索軟體攻陷，攻擊者原則上可循同一金鑰觸及 DESKTOP 副本（緩解：DESKTOP 端收檔目錄可設 append 慣例、或改由 DESKTOP 端拉取——屬實作細節，圈選後再定）。

### 3.5 三案×威脅覆蓋矩陣

| | L3 碟亡 | L4 勒索軟體 | L4 火災／竊盜（同址） | L5 授權 | 自動化 | 惰性風險 |
|---|---|---|---|---|---|---|
| A 外接碟（平時拔下） | ✔ | ✔（離線介質） | △（拔下異址存放才 ✔） | ✔ 零疑義 | △ 半自動（插碟即全自動） | **高**（唯一人工環節） |
| B 加密上 NAS | ✔ | ✘（全網域可 Modify） | ✔ | **✘ 疑義未解** | ✔ | 低 |
| C 第二機 | ✔ | △（金鑰同向風險） | ✔（異址前提待證） | ✔ 零疑義 | ✔（機器在線時） | 中（繫於 DESKTOP 開機紀律，08-01 實測不佳） |

---

## §4 選項與建議案

- **甲【建議，＝裁決單建議案】：A 主 C 輔**。A 案外接碟為主（零授權衝突、離線抗勒索、一次性成本）；C 案為輔（DESKTOP 上線時 rsync 增量，補 A 之惰性空窗）。B 案不採。
- 乙：僅 A（最簡；接受 DESKTOP 不參與）。
- 丙：僅 C（零購置；接受「異地」繫於一台上線紀律未證之機器）。
- 丁：B 案交 Steward 對授權邊界另行裁定後啟用（本呈案不建議）。

**證偽條件（甲案）**：
1. 外接碟啟用後**三個月內未實際輪替過一次**（機械可查：offsite 目錄最新 `augur_*_weekly_Fd` 日期距今 >90 天）⇒ 人為惰性證實，改 C 為主自動化（裁決單原句）。
2. C 輔啟用後**連續四個週末 DESKTOP 均不可達**（`desktop_pull.log` 可查）⇒ C 之「輔」亦不成立，回頭強化 A（如第二顆碟異址輪替）。

---

## §5 風險與回滾

- **零 DDL、零 DB 寫入**：三案皆純檔案層操作；A/C 之施作即使中途失敗，生產庫與既有本地/鏡像備份不受影響。
- **回滾**：A＝拔碟、還原 `backup_database.sh`（git revert 即可，該檔無 DB 繫結）；C＝刪遠端副本＋撤 DESKTOP 上之收檔授權（runbook 由人於 DESKTOP 執行，#6 不代改他機）。
- **A 案外接碟本身損壞**：weekly 輪替天然含多代副本；異地副本每次寫入後即驗 toc（§3.2 diff 第 3 點），壞拷貝當輪即紅。
- **誤刪界**：offsite 輪替沿用既有 `NAME_RE` 白名單（`^augur_[0-9]{8}_weekly_Fd$`）——最壞誤刪界＝舊 weekly dump，手動 dump（如 postmerge）永不在輪替域。
- **`.env` 不入外接碟／NAS／第二機**（含密鑰；#5）：本案異地標的僅 dump；密鑰之災難復原由 hugo 之密碼管理習慣另管，明列為**本案不解決項**。
- **dump 期間禁 DDL 之互斥不變**：offsite 步在 dump 轉正之後、僅讀 `$dest`，不延長鎖窗。

## §6 驗收判準（機械可判）

| # | 判準 | 指令 | 通過條件 |
|---|---|---|---|
| V1 | 異地副本存在且可解析 | `pg_restore -l "$AUGUR_DUMP_OFFSITE/augur_<最新>_weekly_Fd" \| grep -vc '^;'` | 物件數 >100（今日基準 2,696） |
| V2 | 紅燈會亮 | `bash scripts/backup_database.sh`（status） | 印「距上次異地 N 天」；N>14 時含 ⚠；碟不在時印「未掛載」非沉默 |
| V3 | selftest | `bash scripts/backup_database.sh --selftest` | RC=0，含 offsite 白名單紅綠（新斷言曾驗紅留痕於 commit 訊息） |
| V4 | C 輔遠端完整性 | `ssh hugo@desktop-8mqpfs8 "pg_restore -l ~/db_dumps/augur_<最新>_weekly_Fd \| grep -vc '^;'"` | 物件數 >100 |
| V5 | 誤刪界不變 | selftest 之仿冒名／手動 dump 案例 | `postmerge`、`evil_augur_*` 恆「不動」 |

## §7 Steward 決定欄

- [ ] 甲（A 主 C 輔）　- [ ] 乙（僅 A）　- [ ] 丙（僅 C）　- [ ] 丁（B 另裁）　- [ ] 修改意見：＿＿＿
- 簽：＿＿＿　日期：＿＿＿

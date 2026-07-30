# 全自進化線總控執行計畫（2026-07-29 13:40 現位）——最佳下一步×可同步作業×逐步序

> [I] 執行計畫書（hugo「請做出可以列出逐步執行的計畫書」）。**全部步驟依已簽核範圍**（各 go 碼在案），無新判準；裁決點逐一標示。現位數字全數今日親驗。

## 一、六線現位（一行一線）

| 線 | 現位 | 下一里程 |
|---|---|---|
| **L1 LAIEVO**（本地 AI） | behavior×2@新尺跑中（round 1 過半）；pack 軸凍結；LoRA 復活記分卡 3/4 亮 | **今傍 A′ 首判＋三件裁決包** |
| **L2 (b) 特徵線** | prodset active=2（lending 人促升全鏈帳）；INTERACT 7 顆已材料化；econ 待凍網格 | 明午 econ 重跑＋wave-2 四關 |
| **L3 Arena live** | 每日 cron 健康；**cluster 2/250**（凍結門實查；原記 2/60 為誤）；W2 紅旗 1 批 | 08-03 第二批（W2-a 條件觸發） |
| **L4 REPLAY**（模型重演） | 輕量三隊全窗 2,798 clusters ✅；門評待樹淨；own_daily 待道 | 今晚 own_daily＋三門終評 |
| **L5 META-REPLAY**（程序重演） | M1 ✅；preview 23-cutoff 試掃中；M3 裁判已建 | 明晨密網格 M2（60+ cutoff）→ 門評 |
| **L6 GRID-A**（網格地基） | 76 月頻 panel 建置中（IO 道、FV-GUARD 下） | 明晨收槍＋宇宙快照＋驗證 |

## 二、車道規則（同步的物理極限）

- **llama 道**：behavior×2 獨占至今傍 → 之後空（LoRA 訓練若獲 B1-go 才再用）
- **sklearn 道**：M2-preview＋W1 旁證現占 → 今晚讓 own_daily 重演（~23h 重活、可跨夜 resume）
- **IO/DB 道**：GRID-A 獨占至明晨
- **純度閘**：門評（direction_gate --evaluate）須工作樹乾淨——並行 session 治權檔編輯中，**評門動作一律排樹淨時**
- **cron 自理**：arena 20:00/21:30、evolve_cycle×4、夜鏈 01:30、RAWEVO 週六、desktop 拉取——零人工

## 三、逐步執行序

**T0（現在，已在跑）**
1. behavior round1→round2（llama）｜2. M2-preview（sklearn）｜3. W1 全窗旁證（sklearn 輕）｜4. GRID-A（IO）——四者互不搶道。

**T1（今傍，behavior×2 收槍觸發；自動）**
5. `report_post_batch_verdicts --run` → **A′ 首判**＋v2 逐格對照；
6. `migrate_authority_tier_ddl --apply`（TIER 71 列 backfill；長交易已散）→ `auto_review --dry-run` 驗 P6 活化；
7. LoRA 記分卡末格回填 → **【hugo 裁決點①】三件包**：`LAIEVO-B1-go`（1.7b QLoRA 開輪）／B5 二選一（serving 產物接審議引擎 vs 誠實標注射程）／窄塊語料策展判準。

**T2（今晚，T1 後；自動）**
8. own_daily_rolling 全窗重演上道（sklearn，跨夜 resume）；
9. 樹淨時：`dgate_replay_{momentum,mc}` 終評（own_daily 門待其資料滿後補評）；
10. 重演首讀報告落檔（計分板 11.5y＋W1 全窗＋W2 旁證）。

**T3（明晨，GRID-A 收槍觸發；自動）**
11. `build_core_universe --asof` 收尾驗證（2018+ 應 ~101 panel、逐 panel 列數/特徵數抽查）；
12. **M2 正式**：`run_meta_replay --step month --from 2018-01-01 --to 2026-04-30`（新 proc_sha 家族；preview 經驗定 chunk 與 nice）；
13. econ 凍網格重跑（`--panels` 釘網格參數先補）→ **【hugo 裁決點②】**lending 補證判讀（判負＝demote 提案）。

**T4（明午後，M2 收槍觸發）**
14. `evaluate_meta_replay_gate --evaluate ×2 --proc-sha <新家族>`（n≥60 才判；樹淨前置同 §二）→ **程序增益首判**；
15. INTERACT wave-2：7 交互候選過四關（工具全就緒零改碼）→ 存活者呈 **【hugo 裁決點③】** 促升（走 queue 正路，prodset 2→3+ ＝ SUNSET (b) 達標路徑）。

**T5（日曆位，自動＋條件）**
16. 08-03±：arena live 第二批結算 → `verify_arena_watchlist --run` → W2 >95 即照修復預案 R1-R3 執行（零現場設計）；
17. 週六 01:30：RAWEVO 下輪——**首次全自動閉環**（hint→你的閘→map 掛鉤→值派生→四關）；
18. R3（擇日）：外隊發布日親驗（HF card）→ 合法窗重演 → 外隊門評；查不到發布日＝該隊誠實棄。

## 四、hugo 裁決點日曆（僅此五處需要你）

| 時點 | 裁決 | 形式 |
|---|---|---|
| 今傍 | ① A′ 後三件包（B1-go／B5／語料判準） | 各一字/一句 |
| 明午 | ② lending econ 補證判讀（判負→demote） | 一字 |
| 明午後 | ③ INTERACT 存活者促升 | 逐列核 |
| 08-03 | ④ W2-a 修復執行確認（預案已凍、觸發即照案——僅知悉） | 免簽 |
| 隨時 | ⑤ 殘餘小件：#13-15 補裁／REST 波要不要開／SRC 週餘額提額 | 積壓不阻塞 |

## 五、停損與風險（本計畫自帶）

- 任一重演/掃描斷言破（as-of 越界、閘拒）＝停該線＋報告，不自動繞；
- M2 若 preview 暴 bug → 修完換 proc_sha 重掃（帳本自然分家，零污染）；
- econ 判負 → demote 提案（促升順序債已入 audit，不迴避）；
- 機器單點：全部 resume-safe，斷電/重啟後照 §三觸發條件逐步重入。

**一句話**：今天之內三個「首判」（A′、replay 門、W1 全窗）、明天兩個（程序增益門、econ 補證）——五把尺全是預先簽凍的，接下來只是讓資料通過它們。

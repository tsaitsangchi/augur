# augur 深化理解報告 r3（2026-08-01 晨）——優化地基・第三輪

> **性質**：全專案現況之深化理解，作為後續優化之依據（承 r1 07-30／r2 07-31 午；本輪涵蓋 07-31 全日劇變＋08-01 晨結輪）。
> **方法**：11 路平行分域親驗（`wf_082bb6fc-fc2`：治權／DB／五軸／假綠／KH／預測 arena／排程維運／變更圖／記憶漂移／債務帳＋1 critic 對抗），
> 每項主張標【親驗】（附 SQL/指令輸出或 file:line）或【引用】；critic 另裁三處跨域矛盾、複驗五盞綠燈、抽驗三個十路共同盲區。
> **本檔紀律**：綠燈一律先問「它的判準是什麼、量的是不是它宣稱在量的東西」——07-31 一日七例假綠之教訓。

---

## 一、終態座標與口徑鎖定表

### 1.1 今晨三錨（08-01 07:00 前親驗）

| 錨 | 事實 |
|---|---|
| **run 20** | `succeeded`，07-31 18:19:53 → 08-01 04:11:42（9.9h），掃 **51 features**＝**run 6 之後第一個完整引擎輪**（run 10 係 human_promotion 僅 1 feature）。I3 逾時修正（7200→43200s＋bytes 落帳）**於生產路徑驗證通過**：I3 rc 序列 −15, −15, **0**（第 27 步落帳） |
| **tw-20260728-r01** | 08-01 06:47:10 結輪：**status=failed 但 gain=true**——close 判準「歷史任一步曾敗即敗」不被重試成功洗掉（標籤失真，新債 §八#4）；gain_basis=`dual_green_delta`（1→2、source_run_id=20）＝**引擎自掙**，prodset_delta 冒功未發生（07-31 `_snapshot` 修正生效） |
| **V2-SUNSET-r2** | `evaluated_pass`（hugo 07-31 19:45:26 TTY 親簽，basis=R1「任一 direction_gate 列有可讀之數」）⇒ **三軸續命**。snapshot：arena 門有數=0、v1 判死門有數=12、`consequence_executed=false`。AI 證據結論（R2/R3＝未達成）與裁決不同、二者並存留檔 |

run 20 雙綠＝`cycle_position_252d` ＋ **`lending_fee_rate_mean_30d`**（⚠ 勿與 prodset active 之 `lending_fee_rate_mean_20d` 混同——30d 是新面孔）。

### 1.2 口徑鎖定表（critic 裁決；引用這些數字必附口徑，防同尺陷阱）

| 量 | 正確口徑 | 作廢／易混口徑 |
|---|---|---|
| public 表數 | **普通表 322**（relkind='r'）／pg_tables **323**（含 1 分區父表）——兩者並真 | 「322→323 漂移」係口徑差非漂移 |
| KH0 破口 | **未評 KH0（無 `knowhow_auto_admit_state` 列）＝138,854**（`run_kh_chain.py:111` --check 口徑） | **無原文＝138,805** 是另一把尺；三路曾混用，近似值巧合 |
| validation_evidence | **19 列＝green 14／red 5／manual 5**（sql 12＋script_exit 2）；machine_note 僅 E1 | 「20 列/12 sql 3 false/7 manual」＝HANDOFF 舊口徑，作廢 |
| promotion_queue 444/445 | **非重複列**——principle_id 77/98，per-principle 設計 | 「內容全同＝無防重複約束」為誤判 |
| systemd timer | **7 支**（augur-*） | 「8 支」誤 |
| pending_auto | **77**（run 20 灌入後；07-31 晚為 67） | — |
| headline 錨 | 1.1321（hugo 簽）/1.1302（本機快照）**皆無 DB 帳**；trial_ledger 停 07-13（舊錨 1.1972 不可再現） | 「確立級數字」與帳本分家 |

### 1.3 治權檔座標

靈魂 **v1.10.0**（07-31 09:19「最終目標＝讓本地 AI 具備與人一樣的判斷力」）／原則精華 v1.12.0／大憲章 **v1.54.0**（07-31 10:28 sim 專章登錄，`gp_86c8063fc688` enacted）／**CLAUDE v1.34**（#33 禁阻塞迴圈＋#34 平行度拉滿，同 commit 56d400f）／L0–L7 憲法層**自 07-23 零變動**（AL 最新＝045）。
殘留：CLAUDE **#20 仍引已廢止之「非必要不 fan-out」**（:73 vs #34 :137）——一處改全鏈對齊漏了一處。

---

## 二、綠燈可信度總表（本輪核心方法論產出）

07-31 確立之判斷句：「**這個綠燈量的是不是它宣稱在量的東西？**」critic 抽五盞複驗，全數量對，但各帶殘留：

| 綠燈 | 判準 | 複驗 | 殘留 |
|---|---|---|---|
| `install_cron.sh --check` | diff 非空→RC=2 | ✅ RC=2 | live 週報檔名仍凍死 `evolution_week_20260727.md`（repo 已修、`--apply` 未跑）——**明早 08-02 09:00 週報會寫進 0727 舊檔，查 T7 須看該檔** |
| I3 逾時落帳 | 步落 steps_json | ✅ 33 步、I3@7/11/27＝−15/−15/0 | close「任一步曾敗即敗」⇒ r01 標 failed（以 status 判產能會誤讀） |
| 人閘空輸入拒 | 非 TTY／空輸入→SystemExit | ✅ 行為級自測 | — |
| kill switch 三軸 | 開輪前 fail-closed | ✅ tw/raw/PME 各 3 處＋apply 1 處 | raw rc=75 與 tw slot-busy 75 撞號（tw 特設 76）；「供 OnFailure 可見」空指涉（全棧零 OnFailure）；lai scope 零消費者 |
| 週報 (b) 合取 | `judge_b` 純函式 fail-closed | ✅ all_active 真入 SQL；sign 表 0 列→誠實判未達 | — |

**假綠 lint 自身之校準**（吃自己的藥）：33 ERROR 中 **7 條係 lint 誤報**（鏈式 `.split` 一句式切片不被 `_SLICED` 認得）⇒ **真恆真 26 條**；lint 自身含 1 條恆真＋2 漏報；**未接任何自動閘**（pre-commit 現掛三閘不含它；直接掛會擋 commit，須先修誤報＋基線化存量）。
26 條依「保護不可逆動作」排序之首＝**`gate_raise_sunset_deadline.py`（6 條）**——settle 已修、同族此支未修，而它是未來 GATE-raise 的模板。

**仍未修之四假綠**：`constitution_lint report` 量引用非落地／validation_evidence 5 條 manual 對紅燈永久免疫／OCV 零機械實作／LAIEVO robot 臂過地板。

---

## 三、晉升鏈斷點圖（優化主戰場）

```
run 20 完整輪雙綠（證據完整：hac_t 3.52/3.46、64 panels、seed_deltas 全正）
   │
   ▼
feature_sign_check ＝ 0 列          ← --record 從未跑；(b) fail-closed 誠實判未達
   │                                  Steward「回頭補（all_active）」尚未執行
   ▼
G-SIGN 未入 GATE_IDS（七閘）        ← evolution.py 零命中；gate_json ? 'G-SIGN' 全庫 0 列
   │                                  升嚴=Steward；blast radius 已擴大（pending_auto 67→77）
   ▼
TWEVO-APPLY-go 未開                 ← ledger.gate_ref 與 queue 零出現；cron 無 --allow-apply
   │                                  apply_log 止於 id=24（07-29 run 10）
   ▼
prodset active ＝ 2（不變）
```

**鏈上三個髒點**：
1. **`lending_fee_rate_mean_20d`（現役）在 run 20 有 G-PROM FAIL 帳仍 active**——seed Δ mean=−0.0185 不穩定；其 demote 提案因非 FAIL_SIGN 記 `rejected_gate`（名義人裁），但**查無人裁佇列載體**＝帳上有 FAIL 證據卻無人會看到。
2. **`lending_fee_rate_mean_20d` 全 repo 零產生器**（chip.py 僅有 mean_30d）——W2-‖A 符號尺對它重算 as-of IC 恐直接 UNJUDGEABLE，(b) 之 all_active 射程被卡。clean-room 重建＝AI 可為。
3. demote/pending_auto 10 顆、freeze/rejected 15 顆同積壓於 77 列中。

---

## 四、五軸引擎與殭屍帳

| 軸 | 現況 |
|---|---|
| **tw** | 首個完整輪已收；下一輪前置＝heavy slot 空、**週末無 cron**（僅一至五 23:00）、drain timer **inactive 但 enabled**（重開機復活；停用期間積壓無人清至週一） |
| **raw** | **今日 09:00 將是史上第一次 cron 輪**（rawevo.log 從未存在）；driver 已接 kill switch（首次受閘） |
| **lai** | 0 輪；現行尺上 behavior 0.678 ≈ robot 0.677 且 **3 runs 全 is_invalid**＝live 臂無任何有效證據勝零知識格式機 |
| **sim** | 八表＋registry 全 0 列；候選物理死鎖原樣（FK→registry＋`chk_smr_registered_signed` 人簽）；kill_switch 無 sim scope |
| **program** | SUNSET pass；consequence 封存腳本仍不存在（下一個停損閘仍無完整機械載體） |

**殭屍帳（清單供 Steward 裁清理方式）**：`evolution_run` **9 列 running**（run 11–19，零對應行程）；`evolution_deferred_work` 未清 **7 筆**＝真積壓 2（#4/#5）＋**07-31 21:01:37 同秒四筆（本人回歸鎖探針污染）**＋08-01 02:00 新 defer 1（23:00 cron 等 slot 3h 放棄）。

---

## 五、知識層地基

- **KH0 正名**：破口＝未評 138,854（--check 口徑）；無原文＝138,805（48.67%）。其中 **121,389 件（87.5%）連 `fulltext_status` 誠實旗標都沒有**＝「誠實 fulltext_blocked」義務之最大未履行主體（v1.53.0 現行 [N]）。
- **KH5/6 逐 item 化之後**：判準改讀 kh4_state（fail-closed）✅，但 (a) **存量 145,948 零重評**（改後僅 6 筆 run）；(b) KH5 之 `kh_axis_state` 全表 **161,900/161,900 恆 ready**＝逐 item 化尚未帶來鑑別力（上游 kh4.py 機械衍生）。KH7 仍庫級。
- **KH8 閘實際是開的**：`population_discriminates` 靠 **0.27% 尾巴**（非 high 僅 402 件）回 ok=True ⇒ **KH9-first 排序生效中**——depth≥7 之 145,954 件全排公版 works 前，且深帶內 **99.996% 同深＝排序鍵退化**（實際仍靠 −score）。
- **GREATEST 再膨脹已實證**：07-31 六筆爬回 depth 9（四筆 7→9 帶 band=high score=0.72 橡皮章樣式）——r2 預言「降級不可持久」成真。
- Qdrant 功能級健康（collection `kn_sent_it_ime5s30b1cd_tn1`）；advisor KH9-first 綁上述退化排序。

---

## 六、資料與 arena 債

- **arena 結構債**：15,344 列**全 h=5**；已結算僅 07-15/16 共 4,128 列（settled clusters=2）；07-17~24 六交易日真斷檔；六 `dgate_arena_*` 預註冊後**全未評**（evaluated_at/result_snapshot 全 NULL），其中 **own_stack_20/40/82 之 horizon 與 h=5 出單結構性錯配＝現行結構下永無證據**。
- **headline 錨分家**：治權認定 1.1321（hugo 簽）與本機快照 1.1302 皆無 DB 落帳；機器可查之 trial_ledger 停 07-13（1.1972 舊錨）。三套特徵口徑並存：canonical 29／headline 34／prodset 2。
- **正典對帳停跑續惡化**：attestation_result 最後 passed=t 仍 **07-16**、最後執行 07-25——跨兩次重開機＋整條 07-31 修復鏈**零觸發**；tw 有 drain 自動 resume 而 raw 對帳無等價機制。
- **資料鏈健康**（critic 補盲區）：TaiwanStockPrice 與 arena pred 皆至 07-31（日常 sync 與 20:00 出單 cron 有效）；FinMind 配額錶 UNKNOWN（唯讀輪禁 API）。
- **DESKTOP 並行機**：pull cron 每 2h 實跑、至 08-01 06:37 **連續不可達**——今為週六（記憶稱僅週末開）晨間仍未上線；週末待辦（停其 cron＋搬 07-26 增量）繫於其上線。

---

## 七、治理與義務曆

| 項 | 現況 | 層級 |
|---|---|---|
| **L7.16 vs 單一角色** | **正面衝突零登錄**——「owner 分離／不變式強制不得由 app 角色解除」之物理前提消滅（Steward 親跑，程序上人類權威成立），但 L7 spec 未動、AL 零登錄、大憲章與 CS 零命中＝**治權文件與物理現實漂移** | Steward（補登錄或修 spec） |
| **2026-10-14 懸崖** | 七項全 [ ]；**WM.35/36 自 10-15 起消費禁令無條件適用**；禁假關項維持 open；AL 零進度登錄 | Steward |
| **未裁六項** | SSOT＝`evolution_execution_plan_20260731.md` §七（G-SIGN／殭屍清理／prodset_delta 基準／APPLY-go／備份上 NAS／LAIEVO 量尺+VE 有效期） | Steward |
| **consequence 載體** | 封存腳本不存在；kill switch 已接線但「三軸整體停止＋帳本封存」仍半套 | AI 呈案 |
| **回滾不對稱** | 治權裁決繫 DB 親簽列（governance_proposal／prereg_gate＋no_goalpost trigger）——**git revert 只滾文件、撤不掉裁決**；正途唯新提案／GATE-raise 開新列 | 認知錨 |
| **備份單點** | 唯一 dump＝`~/db_dumps/augur_20260731_postmerge_Fd`（11G，07-31 16:10）；`/mnt/c/database` 已空（07-31 18:10 清）；**dump＋DB＋repo 同一顆實體 C: 碟、零異地**；12 條 cron 零 pg_dump | Steward（NAS 授權衝突）＋AI（定期 dump 呈案） |

---

## 八、優化行動佇列（依「不修會怎樣」；已清償 13 項不列）

| # | 行動 | 不修會怎樣 | 層級 |
|---|---|---|---|
| 1 | **W2-‖A：對兩現役跑符號尺 `--record`**（前置：mean_20d 零產生器恐 UNJUDGEABLE，先裁處置） | (b) 永遠 fail-closed 未達；T7 明早自檢將如實紅 | AI（slot 空即可） |
| 2 | **validation_evidence 掛排程＋manual 有效期** | 紅燈會亮但沒人看見；5 條 manual 永久免疫 | 排程 AI／有效期 Steward |
| 3 | **attestation 對帳掛回排程**（raw 對帳無 resume 之不對稱） | E1 紅燈永遠修不好；資料真實性唯一機械證據鏈斷 | AI 呈案 |
| 4 | **close 判準修法**（重試成功洗掉歷史敗？或雙欄記 status＋final_attempt） | 每輪含重試者恆 failed；以 status 判產能全錯 | 判準 Steward 輕裁＋code AI |
| 5 | **殭屍清帳**（run 11–19＋deferred 7 筆含探針 4） | 帳本失真持續；drain 復活後亂補跑 | Steward 裁方式 |
| 6 | **lint 修 7 誤報→基線化 26 恆真→掛 pre-commit** | 新假斷言持續入庫（07-31 晚新檔即再犯） | AI |
| 7 | **G-SIGN 入 GATE_IDS**（W3 同批四件） | 晉升閘永缺符號關；APPLY 開了就繞過 | Steward |
| 8 | **mean_20d 產生器 clean-room 重建** | 現役特徵不可重建＝#15 之恥；卡 (b) 射程 | AI |
| 9 | **KH fulltext_status 旗標補齊 121,389 件** | 「誠實旗標」義務最大缺口；KH0 帳面永遠不可信 | AI（放量前最小單位） |
| 10 | **KH8 鑑別力閘＋KH5 恆 ready** | KH9-first 以退化鍵排序 145,954 件於公版前 | 判準 Steward |
| 11 | **L7.16 衝突補登錄** | 治權文件與物理現實漂移入常態 | Steward |
| 12 | **定期 pg_dump ＋異地**（單碟事實） | 碟亡＝全亡 | Steward＋AI |
| 13 | dgate 三門 h 錯配處置（supersede 或補 h 出單） | 三門永無證據、(a) 永遠只能靠 R1 | Steward |
| 14 | lending_20d FAIL 帳之人裁佇列載體 | 「名義人裁」實際無人看見 | AI 呈案 |
| 15 | 週報檔名 live `--apply`（同批三行） | T7 檢驗窗口每週寫錯檔 | hugo 跑 --apply |

**方法論三規則之住所債**（假綠防治域發現）：「絆線注下游」有 code 落點；「回歸鎖須驗紅」「綠燈也要驗得到」**只活在 commit 訊息與散落註解、無治權檔住所**——是否入 CLAUDE.md 屬 Steward。

---

## 附：本輪所讀主要表與程式（#20 對映，純分析零寫入）

表：`evolution_prereg_gate`／`evolution_iteration_ledger`／`evolution_run`／`evolution_deferred_work`／`promotion_queue`／`evolution_production_feature_set`／`feature_sign_check`／`validation_evidence`／`knowhow_auto_admit_state`／`knowledge_item(_text)`／`direction_gate`／`direction_arena_prediction`／`attestation_result`／`trial_ledger`／`governance_proposal`／`evolution_axis`／`pg_roles`／`pg_tables`。
程式：`run_evolution_iteration.py`／`run_raw_evolution_iteration.py`／`run_philosophy_evolution.py`／`report_triple_evolution_week.py`／`verify_sign_consistency.py`／`check_false_assertions.py`／`install_cron.sh`／`run_kh_chain.py`／`kh4.py`／`auto_admit.py`／`evolution.py`。
結果落點：本檔＋記憶更新。**不寫任何 DB 表。**

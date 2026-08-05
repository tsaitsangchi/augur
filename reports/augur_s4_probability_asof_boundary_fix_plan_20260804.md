---
status: draft
series: s4_model_families
depends_on:
  - reports/augur_omniscient_e2e_master_plan_20260710.md
  - audits/S4-DIRFAMILY-GENERALIZE-EXECUTED-20260804.md
---

# P6 機率校準管線 AS_OF/exit_date 邊界缺口 — plan-first（2026-08-04）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**觸發**：`S4-DIRFAMILY-GENERALIZE` Phase 0 驗證中查核發現(§3),用戶已裁示「現在就起一份 plan-first」。
> **重要更新（寫此計畫過程中新查出,提升急迫性）**：本問題**非僅歷史／離線稽核**——`augur-probability.service`（:8600,live running）與 `augur-advisor.service`（:8399,live running)皆消費受影響之表;且**本日稍早之 DIRFAMILY 驗證動作已使 live-served `prediction_probability` H60 列實際受影響**(§2)。

---

## 1. 問題(根因,已讀碼確認,非臆測)

`scripts/build_probability_oos_sample.py` 與 `scripts/calibrate_relative_probability.py`(SSOT=`reports/augur_omniscient_e2e_master_plan_20260710.md` §1.3/§5.2-5.4)之設計文件**明文**：

- 主計畫 §1.3(line 66)：「serve:最終校準器 fit 於全部 `exit_date ≤ 2026-05-31` 之折」
- `build_probability_oos_sample.py` 註解(line 37)：「`AS_OF="2026-05-31"` #FREEZE(原則精華 v1.8.0);對樣本全在此凍結快照內」
- `calibrate_relative_probability.py` 註解(line 112)：「serve 校準器:全樣本 fit(全部 exit_date ≤ FREEZE=**建構保證**;機械斷言)」

**三處文字皆宣稱／假設「`exit_date ≤ FREEZE` 是寫入端已保證的不變式」**。但讀碼確認 `build_probability_oos_sample.py::emit_horizon`(line 84-86)：

```python
exit_d = _exit_date(cal, test_pd, h)
if exit_d is None:            # 標籤窗未完全實現 → 整折缺列(#8 不外推)
    continue
```

**只檢查 `exit_d` 是否算得出來(行事曆是否夠長),從未檢查 `exit_d > AS_OF` 就跳過**。`_asof_panels()` 只限制**測試 panel** 上界(`panel_date<=AS_OF`),未限制其 `exit_date`——h 越大(如 60),越接近 AS_OF 邊界的 panel(如 2026-03-31、2026-04-30),其 exit_date 越容易外溢 AS_OF。

**為何原本沒事、今天才炸**：本管線首建於 2026-07-10 前後,當時 `feature_values` 尚未成長到含 2026-03/04 這類「貼近 AS_OF」的晚期 panel(live 增量表,持續成長);故原始 24 折從未觸及此邊界情形、`purge_verified` 一直為 `True`——**非「當初測過沒事」,是「當初資料還沒長到會暴露這條路徑」**。今日因 `S4-DIRFAMILY-GENERALIZE` Phase 0 驗證需要重跑 `build_probability_oos_sample.py --run --horizon 60`(無 `--limit-folds`),`feature_values` 已長到含 2026-04-30 等晚期 panel,首次觸發。

**消費端(`calibrate_relative_probability.py::fit_horizon`)之疊加缺口**：`purge_ok` 只被**計算並誠實存入** `probability_calibrator.purge_verified` 欄(line 113-114),但**從不依此過濾或中止**——line 115 之 `_platt_fit` 仍吃**全部** `rows`(含違規列)。即安全機制(#8 機械斷言)**有偵測、無攔阻**——偵測到旗標會誠實記 False,但服務仍照跑。

**確認非 #8 核心意義之洩漏**：每筆 OOS 列本身的 `fwd_ret` 相對其**自身 panel_date**(如 2026-04-30)之決策時點並無洩漏——這是標準 walk-forward:t 時做預測、等 t+60 交易日後才用已實現報酬做校準評估,#8 核心「決策當下不可見未來」並未破。**真正受損的是「快照一致性」聲明**(A-29:「機率只到 as-of 2026-05-31」)——校準器現在**實際**吃進了「2026-05-31 之後才會實現」的標籤(如 2026-07-29 才實現的報酬),與其自稱之「凍結快照」定義产生落差,屬**誠實框架**問題(#9/#15),非決策時點邏輯問題。

---

## 2. 現況影響範圍(2026-08-04 查核,DB 實測)

| 表／服務 | 影響 |
|---|---|
| `probability_oos_sample` | **僅 H60 受影響**:445/34611 列 `exit_date>FREEZE`(H20/H40/H82/H120 皆 0 列違規——未被本次重跑觸碰,仍是舊乾淨狀態) |
| `probability_calibrator` | H60 新增一列(`platt_RankRidge_h60_asof2026-05-31_g5a96c09`,`purge_verified=False`,101 折);**舊列(`..._g08356fd`,`purge_verified=True`,24 折,2026-07-11)仍完整保留、未被覆蓋**(不同 `calibrator_id`,R1 修法之副作用副產物) |
| `prediction_probability` | H60、panel_date=2026-05-31 列**現在指向新(受污染)校準器**——`emit_horizon` 之 `ORDER BY created_at DESC LIMIT 1` 自動選中最新列 |
| `augur-probability.service`(:8600) | **live running**,直接 serve `prediction_probability`——**現正 serve 受影響之 H60 機率** |
| `augur-advisor.service`(:8399) | **live running**,`src/augur/advisor/payload.py` 讀 `prediction_probability`——受影響範圍同上 |
| 影響量級(誠實評估) | 445/34611≈1.3% 訓練列;Platt 為 2 參數 logistic,單一維度輸入(`rank_pctile`),1.3% 額外樣本對 `(a,b)` 之數值擾動**預期小**(未實測量化前不宣稱「small」為結論,見 §4 待辦);**但違反之原則(快照一致性)與量級無關**——即使只 1 列違規,「聲稱 as-of 2026-05-31、實際吃 2026-07-29 已實現標籤」之陳述仍不成立 |

**誠實澄清**：此為 P6 機率校準管線(SSOT 2026-07-10)自身既有之寫入端缺口,**與 `S4-DIRFAMILY-GENERALIZE`(本日之 family-dispatch 泛化編輯)無因果關係**——任何人今天對**未經編輯之原版** `build_probability_oos_sample.py` 執行相同的 `--run --horizon 60`(無 `--limit-folds`),會得到完全相同的 445 列違規與 `purge_verified=False`。DIRFAMILY 編輯只是**觸發重跑的原因**,不是**缺口本身的成因**。

---

## 3. 選項(不預設答案,誠實列優缺)

### 選項 A——最小侵入修補(修 `emit_horizon`,補回文件宣稱之不變式)

於 `build_probability_oos_sample.py::emit_horizon` 之 `_exit_date` 檢查後加一行：

```python
exit_d = _exit_date(cal, test_pd, h)
if exit_d is None or str(exit_d) > AS_OF:      # 新增:exit_date 亦不得外溢 FREEZE(A-29/主計畫§1.3 line66 本應之不變式)
    continue
```

- **優點**：精準對齊三處文件已宣稱之設計意圖(非新判準,是補回原本就該有的檢查);改動 1 行,風險極低;`purge_verified` 從此對 H60 亦自動恆為 True(by construction,不再只能事後偵測)。
- **需配套**：修後須**清理**已違規之 445 列(單純重跑 `--run --horizon 60` 不會自動刪除「新版已不再產出」但舊版曾寫入的列——per-fold DELETE+INSERT 只在**進入**該折分支時才刪重寫;新版對這些晚期折會直接 `continue`、不會觸發 DELETE)。需明確：`DELETE FROM probability_oos_sample WHERE horizon=60 AND exit_date>'2026-05-31'`(#12 資料驅動非手改邏輯結果,此為刪除「不應存在的列」,非 hand-patch 數值,不違 #12)。
- **需配套 2**：重跑 `--fit --horizon 60`(清資料後自動 `purge_verified=True`)+ `--emit --horizon 60 --asof 2026-05-31`(還原 `prediction_probability` 至乾淨計算結果)。
- **殘留**：舊 3 列歷史 calibrator(`g4fd2d07`/`g7fd3426`/`g08356fd`)與本次新增之受污染列(`g5a96c09`)皆保留(#10 可溯源,不刪歷史列;`prediction_probability` 會經 `--emit` 重新指向修復後之最新乾淨列)。

### 選項 B——加固消費端(`fit_horizon` 亦自行過濾,防禦性雙保險)

在選項 A 基礎上,**額外**讓 `calibrate_relative_probability.py::fit_horizon` 之 serve fit 明確加 `WHERE exit_date<=%s`(FREEZE)——即使未來寫入端又出現類似疏漏,消費端仍自行守住邊界,不僅依賴上游承諾。**額外成本**：`_load` 需新增參數/SQL 條件,`fit_horizon` 之 `rows` 需二次過濾(供 expanding-purge 逐折評估之 `rows` 是否也要同步過濾——需一併決定,見 §5 待決)。

### 選項 C——AS_OF 隨 live 增量滾動(架構層,超出本次缺口修補範圍)

專案已於 2026-07-12 起轉「live 增量維運」(CLAUDE 資料真實性條)——**本管線的 `AS_OF="2026-05-31"` 卻是寫死常數,從未隨 `feature_values` 增長而滾動**。若要讓 P6 徹底跟上 live 哲學,需比照 `predict_asof.py`/`calibrate_relative_probability.py --emit --asof` 已有之參數化模式,把 `AS_OF` 也改成 CLI 參數(如 `--asof`)、每次重跑時明示指定,而非寫死於程式碼常數。**此為架構層決定,非本次缺口之必要修補**——選項 A/B 即可讓「無論 AS_OF 是哪個值」這條不變式恆成立,選項 C 是另一個獨立問題「AS_OF 這個值本身該不該更新」,建議另案處理、不與本缺口修補綁在一起(避免把簡單 bugfix 拖成架構改造)。

### 選項 D——視為一次性歷史快照,不當作可重跑管線

若 Steward 認為 P6 從一開始就是「回答用戶 2026-07-10 當下那個特定問題」之**一次性交付**(非長駐管線),則正確做法可能是「不要再對它跑 `--run`(無 `--limit-folds`)」,把當時的既有輸出視為定案封存、`build_probability_oos_sample.py` 標記為「歷史一次性,不建議重跑」。**與選項 A/B 不衝突**(選項 A/B 讓「萬一又重跑」時不會再炸,選項 D 是額外的使用紀律)。

---

## 4. 建議(供裁示,非片面決定)

**建議選項 A 立即執行(風險最低、對齊既有文件意圖、修復 live-serving 現況)+ 選項 B 一併補上(防禦深度、成本低)**;選項 C 另案討論(架構問題,不卡在此次 bugfix);選項 D 供 Steward 參考(使用紀律,零程式改動)。

**理由**：
1. **A 是誠實的 bug fix,不是新判準**——三處文件都已經「以為」這條件存在,程式碼補上等於**兌現既有承諾**,非引入新規則,風險最低。
2. **live 服務現正 serve 受影響資料**(`augur-probability.service`)——修復窗口越短越好,但**不代表應跳過 Steward 授權自行動手**(觸碰 live-serving 資料表、且屬「發現既有程式缺陷」而非「本次計畫既定範圍」,依 CLAUDE #19/#26 仍須明示授權才執行)。
3. **選項 B 額外邏輯簡單、成本低**,值得與 A 一併做,避免「下次又有人重跑忘了測資料成長」再犯。
4. 選項 C 影響面大(牽涉「AS_OF 這個歷史快照本身是否已過時」之判斷,可能連動 A-29 誠實標記文字、`FAMILY_NOTE`、`econ_verdict_rule` 等)——刻意留給另一輪 plan-first,避免這次「修一個明確 bug」被架構問題拖住時程。

---

## 5. 待決問題(Steward 裁示用,非 AI 自行認定)

1. **授權範圍**：是否授權執行選項 A(＋建議 B)?抑或先只做 A、B 留待另評?
2. **執行時機**：是否立即執行(修復 live-serving 現況)?或先做完 S3-Wave-B 背景複核、DIRFAMILY 相關背景工作皆結束後才動(降低 CPU 競合)?——本次修補之計算成本極低(重跑 `--run --horizon 60`+`--fit`+`--emit`,約 15-20 分鐘,遠低於 DIRFAMILY 驗證時之全量),與現有背景工作競合影響應可控。
3. **選項 B 是否納入本次**：抑或先做 A(修寫入端)、觀察一段時間再決定是否加 B(消費端雙保險)?
4. **其餘 horizon(20/40/82/120)是否需要主動預防性複查**：目前皆乾淨(0 違規),但邏輯上若未來被重跑到 `feature_values` 更長時,H82/H120(更長 horizon,更易觸發同型邊界)亦有相同風險——選項 A 修完後,此風險對**所有** horizon 自動排除(非只治 H60),故此問題答案應隨選項 A 執行而自動解決,列此僅為確認理解一致。
5. **選項 C/D 是否要另開 plan-first,或本次一併簡短裁示方向(不深入設計)**?

---

## 6. 硬邊界

- 本計畫**不**自行執行任何選項——僅供 Steward 裁示;讀碼/查核已完成,未動任何寫入端程式碼、未刪除任何列。
- 選項 A/B 之執行**不**涉及 FinMind/FRED、不涉及 sim `--apply`、不涉及 `direction_gate`/`arena_admission_gate`——純本地 DB 讀寫+既有腳本重跑。
- `TaiwanStockPriceAdj` 等真實已實現價格資料**不受影響、不被修改**——本問題純屬「校準器訓練集之列篩選範圍」,非資料真偽問題。

---

*定版（2026-08-04）。下一手＝待 Steward 就 §5 五項裁示;若授權 A(+B),預估 15-20 分鐘可完成修補＋回填 EXECUTED audit。*

---

## 執行後記（2026-08-04）

Steward 已授權「選項 A+B 現在執行」。已完成：`build_probability_oos_sample.py`(選項 A,寫入端補 `exit_date>AS_OF` 跳過)＋`calibrate_relative_probability.py`(選項 B,serve fit 前防禦性再過濾)；清理 H60 既有 445 列違規；重跑 `--fit`/`--emit --horizon 60` 後 `purge_verified` 由 `False` 回復 `True`；`prediction_probability`／`probability_calibrator` 已回復乾淨狀態；已讀碼確認兩個 live 服務(`augur-probability.service`／`augur-advisor.service`)皆逐請求即時查詢、無快取,修補即時生效不需重啟。詳見 `audits/S4-PROB-ASOF-BOUNDARY-FIX-EXECUTED-20260804.md`。選項 C(AS_OF 是否隨 live 增量滾動)／選項 D(P6 是否視為一次性快照)留待另案。

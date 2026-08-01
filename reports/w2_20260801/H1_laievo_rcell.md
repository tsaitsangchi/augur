# [DRAFT 呈案] H1｜LAIEVO 判讀層逐格有效性——R-CELL′ 判準預凍＋修尺前 verdict 快照＋S-8 robot 語意權條款

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，所修判讀層量的正是本系統（本地 AI）自身之能力證據；
> 依 §2/§3.4 之凍結快照推算，**採納後 A13 預期由 N/A 翻為 PASS**——此即必須「判準先預凍、快照先落檔、
> Steward 拍板後才動碼」的原因：判準須以自身之誠實成立，不得以「它會給出 PASS」為採納理由。
> 全部對照數字已隨本檔凍結，Steward 可獨立覆算。
>
> 設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3 H1
> ＋`reports/augur_steward_adjudication_sheet_20260801.md` 「八、lai／sim」H1。
> 親驗時點＝2026-08-01 下午；repo HEAD＝`e00135c`；本呈案全程唯讀（零 DDL、零 DB 寫入）。

---

## §1 問題與授權鏈

### 1.1 問題（r3 §四＋§二「仍未修之四假綠」）

lai 軸現況：`local_ai_iteration_ledger` 0 輪；現行尺上 **behavior 聚合 F≈0.678 ≈ robot 0.677**，
且 **3 個 behavior run 全部 `is_invalid=true`** ⇒ 依現行判讀層（run 級 `NOT is_invalid` 過濾），
**live 臂在 v2 凍結集上連一個「有效受測 run」都不存在**——A13（A′ 能力判準）自 v2 集凍結（07-28）以來
**結構性失明**：不是「沒有能力證據」，是「判讀層物理上讀不到任何 live 證據」。

根因＝**判讀粒度錯置**：`is_invalid` 是 run 級旗標（132 題中任一題逾時 ⇒ 整輪作廢），
而 A′ 是**逐格**判準（capability 格 C1/C2P）。一題 B 格逾時會把完全有效的 C2P 格（24/24 全答）一併丟棄。

### 1.2 不換尺之邊界（本呈案之硬前提）

- 量尺（`eval_code_hash=b6e5208ef821`）**一字不動**：hash 涵蓋 `behavior_rubric` 全文＋產答路徑
  （`_ideal_answer/_answer_for/_ask/run_arm`）＋生成參數（`scripts/eval_local_model.py:61-71`）；
  **compare/status/驗收判讀層刻意不在 hash 內**（`:63`「改報表不等於換尺」）——故判讀層修**機械上不換尺**，
  既有 59 筆 run 帳（append-only）全數留用、不作廢。
- SUNSET (c) 凍結文字（criteria_sha 已鎖）**不動**（挪門柱紀律）。

### 1.3 授權鏈（P5.W2／L6.5-L6.8 四要件）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | 呈案起草：唯讀查證＋scratchpad 寫入；**不施作、不寫 repo、不寫 DB** |
| (b) 期限 | 本批（W2 呈案批）交付即結 |
| (c) 可撤銷 | 隨時 |
| (d) 參照 | 登錄冊 §1 H1 列（W2）＋Steward「碰到標 Steward 列最佳解」指示 |

裁決權專屬 Steward（§8.1／L6.18(a)）；本檔僅呈案。

---

## §2 現況親驗（2026-08-01 現查；全數可重跑）

### 2.1 尺之錨（不換尺前提之機械證明）

```
$ venv/bin/python scripts/eval_local_model.py --selftest
  ✓ **尺之錨**:qwen3:4b 之 eval_code_hash 仍為 b6e5208ef821(換尺須有意識)
自測:全通過 ✓
```

### 2.2 修尺前 A13 verdict（凍結快照之錨）

```
$ venv/bin/python scripts/verify_evolution_acceptance.py --only A13
  ○ A13 A′:任一受測臂於能力格 ≥weak(勝 floor∧mismatched∧robot)且 ≥2 run 複現
      v2 集尚無有效受測 run(批跑進行中)
  合計:PASS 0 · FAIL 0 · N/A 1
```

**修尺（判讀層）前 verdict＝N/A「v2 集尚無有效受測 run」。** 此即 T1 絆線
（`augur_evolution_execution_plan_20260731.md` §八 T1：修前記 verdict、修後比對；全不變⇒白工）之「前」照。

### 2.3 現行尺 13 run 對照表（現查；`local_model_eval_run` 全表 59 列中屬現行尺者）

```sql
SELECT run_id, arm, n_items, n_valid, axis_f, axis_p, axis_a, is_invalid, created_at
FROM local_model_eval_run
WHERE set_id='4e15a143ff4b' AND eval_code_hash='b6e5208ef821' ORDER BY created_at;
```

| # | run_id | arm | valid | F | P | A | is_invalid | 時點 |
|---|---|---|---|---|---|---|---|---|
| 1 | ev_5752f5632259b6 | ceiling | 132/132 | 1.000 | 1.000 | 1.000 | f | 07-29 08:00 |
| 2 | ev_b7cc5cbb0701ab | floor | 132/132 | 0.3125 | 0.4889 | 1.000 | f | 07-29 08:00 |
| 3 | ev_eef216b17f74d5 | shuffled | 132/132 | 0.2917 | 0.9333 | 0.9167 | f | 07-29 08:00 |
| 4 | ev_ff62a28e7674a9 | mismatched | 132/132 | 0.000 | 0.1889 | 0.000 | f | 07-29 08:00 |
| 5 | ev_772ecb18ff0c4f | robot | 132/132 | 0.6771 | 0.9889 | 1.000 | f | 07-29 08:00 |
| 6 | ev_8ff70e58e3086f | ceiling(2nd) | 132/132 | 1.000 | 1.000 | 1.000 | f | 07-29 08:00 |
| 7 | ev_f8bcdadf3f1088 | floor(2nd) | 132/132 | 0.3125 | 0.4889 | 1.000 | f | 07-29 08:00 |
| 8 | ev_e9a20bcfaa5aa7 | shuffled(2nd) | 132/132 | 0.2917 | 0.9333 | 0.9167 | f | 07-29 08:00 |
| 9 | ev_01e0721aeaf75b | mismatched(2nd) | 132/132 | 0.000 | 0.1889 | 0.000 | f | 07-29 08:00 |
| 10 | ev_453b39a600de14 | robot(2nd) | 132/132 | 0.6771 | 0.9889 | 1.000 | f | 07-29 08:00 |
| 11 | ev_8189862035e9ab | **behavior** | **123/132** | 0.6742 | 0.6951 | 0.0833 | **t** | 07-29 08:32 |
| 12 | ev_9bec78285bd291 | **behavior** | **130/132** | 0.6809 | 0.7273 | 0.0833 | **t** | 07-30 08:59 |
| 13 | ev_3f08b453564c94 | **behavior** | **126/132** | 0.6774 | 0.7209 | 0.0909 | **t** | 07-30 13:25 |

登錄冊口徑核對：r3「behavior 0.678 ≈ robot 0.677」**屬實**（三 run F=0.6742/0.6809/0.6774 vs robot 0.6771
——聚合值跨在 robot 線兩側）；「3 runs 全 is_invalid」**屬實（run 級）**。
**親驗補銳化（非矛盾、係粒度）**：逐格看，C2P 格三 run 皆 24/24 全答——run 級旗標把有效格連坐丟棄。
對照臂兩次 attempt 逐格**完全同值**（離線臂確定性親驗成立）。

### 2.4 逐格拆解（現行尺；F 軸；`jsonb_array_elements(detail->'per_item')` 逐格聚合）

v2 集格構成（`local_model_eval_item.expect->>'cell_class'` 現查）：
B1_FAITHFUL／B2_NO_RETRIEVAL／B3_AMBIGUITY 各 24 題＝**behavior 格**；
C1_ZH_EXISTENCE 36 題／C2P_ZH_PAIR 24 題＝**capability 格**（合 132）。

| 格（F 軸） | ceiling | floor | shuffled | mismatched | robot | behavior r11／r12／r13（該格 valid） |
|---|---|---|---|---|---|---|
| B1（behavior 格） | 1.000 | 0.000 | 0.000 | 0.000 | **0.9583** | 0.9048(21/24 ✗)／0.9167(24/24 ✓)／0.9167(24/24 ✓) |
| B3（behavior 格） | 1.000 | 0.000 | 0.000 | 0.000 | **1.0000** | 0.4167(24/24 ✓)／0.4167(24/24 ✓)／0.4167(23/24 ✗) |
| **C1（capability）** | 1.000 | 0.500 | 0.4722 | 0.000 | **0.500** | 0.6250(**32/36 ✗**)／0.6176(**34/36 ✗**)／0.6061(**33/36 ✗**) |
| **C2P（capability）** | 1.000 | 0.500 | 0.4583 | 0.000 | **0.500** | **0.6667(24/24 ✓)×3** |

（B2 無 F 值＝P 軸格，不入 A′；robot=ceiling=1.0，格式可達。）

**兩個關鍵事實**：
1. **C2P 三 run 全格有效且 0.6667 嚴格勝 floor 0.5∧mismatched 0∧robot 0.5∧shuffled 0.4583**
   ——A′ 預註冊視窗 (0.500, 1.000] 首次被 live 踏進，但被 run 級旗標遮蔽。
2. **C1 三 run 皆缺答（32/34/33 之 36）**——其部分均值 0.606-0.625 雖 >0.5，但逾時與題目難度相關
   （缺項非隨機），**部分格均值向上偏誤、不可用**。天真地「拿掉 run 級過濾」會讓 C1 假 PASS——
   這就是 R-CELL′ 之 ′（嚴格全格有效）存在的理由。

### 2.5 舊尺（同 v2 集、hash aeff01c18ace）之 live 逐格（修後 A13 亦會讀到，一併凍結）

對照臂逐格與現行尺**同值**（親驗：C1/C2P 之 floor 0.5/robot 0.5/shuffled 0.4722·0.4583/mismatched 0）。

| arm（run 級全 invalid） | C1 valid | C1 F | C2P valid | C2P F |
|---|---|---|---|---|
| behavior ×3（ev_836979ac…/ev_2a095dba…/ev_16d6320c…） | 34/36 ✗ | 0.6176 | **24/24 ✓** | **0.5833** |
| grammar ×2（ev_93475db5…/ev_e8fdfba8…） | 31/36 ✗ | 0.2581 | **24/24 ✓** | **0.5833／0.5417** |
| pack:pp_3ab2efebb04e ×2（已 07-28 退役） | 24/36 ✗ | 0.2917 | **24/24 ✓** | **0.5417×2** |

### 2.6 現行判讀層之三個實作事實（file:line）

1. `scripts/verify_evolution_acceptance.py:220-221`：A13 取 run 之 SQL 帶 **`AND NOT is_invalid`**（run 級連坐）。
2. `scripts/verify_evolution_acceptance.py:225-247`：逐格均值以「該格**有答的題**」計（部分格偏誤未防），
   且 wins 迴圈**遍歷所有格、未過濾 `cell_class`**——A13 文字說「capability 格」而實作可讓 behavior 格
   （如 B1，robot 0.9583<ceiling）貢獻 PASS＝**判準文字與實作之潛在落差**（現資料未觸發，R-CELL′-5 封閉）。
3. `scripts/report_triple_evolution_week.py:169-171`：週報 (c) 讀「最新一筆非 invalid live run」——
   現值落在 **v1 集**（v2 集 live 全 invalid），聚合口徑；`:191-196` robot 附註明標「語意權=S-8 待裁」。

---

## §3 方案

### 3.1 R-CELL′ 判準預凍全文（拍板即凍結；施作不得偏離一字）

> **R-CELL′（LAIEVO 判讀層逐格有效性判準）v1.0-draft**
>
> **R-CELL′-0（射程與不換尺）** 本判準只作用於**判讀層**：`verify_evolution_acceptance.py` A13
> 與 `report_triple_evolution_week.py` lai 段。不得觸碰 `behavior_rubric`、產答路徑、生成參數
> （即 `eval_code_hash` 涵蓋域）；施作前後 `--selftest` 之尺之錨（`b6e5208ef821`）必須同綠。
> 評測帳本（`local_model_eval_run`）append-only、零改寫。
>
> **R-CELL′-1（逐格有效）** 判讀之有效性單位＝(run, 格)。一個 (run, 格) 為**有效格** iff 該格
> **全部題目皆有有效作答**（detail.per_item 中該格零筆帶 `invalid` 鍵；機械錨＝逐項含 `f` 鍵、
> n_answered == n_items）。run 級 `is_invalid` 旗標照常入帳，但**不再整輪連坐排除**。
>
> **R-CELL′-2（缺格誠實）** 無效格＝**非證據亦非反證**：不得以部分均值入判（缺項與難度相關、
> 向上偏誤——§2.4 C1 實證），judgment 輸出須明列缺格之 (n_answered/n_items)，不得靜默消失。
>
> **R-CELL′-3（對照臂同尺同格）** evidence_level 逐格計算，對照臂值取**同一把尺**（同 set_id＋
> eval_code_hash）之同格值，且對照臂該格亦須為有效格；同尺同臂多次 attempt 逐格值**不同**時
> fail-loud 判 incomparable（確定性親驗現況＝兩 attempt 全同值）。
>
> **R-CELL′-4（A′ 判定式不動）** A13 語意一字不改：同臂同 capability 格 evidence_level ≥ weak
> （嚴格勝 floor∧mismatched∧robot；`evidence_protocol.evidence_level` 原式）之**有效格** ≥2 個
> 獨立 run ⇒ PASS；未達＝N/A（成就判準、永不 FAIL）。SUNSET (c) 凍結文字不動。
>
> **R-CELL′-5（行為格不入能力宣稱）** wins 只得產生於 `expect->>'cell_class'='capability'` 之格
> ——把 A′ 文字既有之「capability 格」限定**寫進實作**（封 §2.6-2 潛在落差）。
> behavior 格逐格結果照列於儀表，但**永不**構成 A13 PASS。
>
> **R-CELL′-6（robot 哨兵；效力繫於 S-8 裁決）** robot 逐格分數＝量尺哨兵線（見 §3.2 條款全文）。
>
> **R-CELL′-7（宣稱天花板）** 逐格 PASS 之對外表述上限＝`scoped`（「僅及該格」；
> `evidence_protocol` 原文），不得外推為「模型更聰明」整體宣稱；且一律標 self-reported（CLAUDE #32(a)）。

**預凍機制**：本全文以 `governance_queue.py --submit --kind criteria_change` 投遞
（submit 即被 trigger 凍結不可改），評註 sha 隨提案入庫；hugo `--approve`（TTY 親簽）後才准動碼。

### 3.2 S-8 robot 語意權條款（草案；Steward 逐字採納或修訂）

> **S-8 裁決條款（robot 語意權）v1.0-draft**
> robot（零知識格式規則機）＝**量尺哨兵、非受測臂**。
> (a) 其逐格分數之**唯一用途＝驗尺**：界定該格之能力視窗——robot 未及 ceiling 之格，(robot, ceiling]
> 為能力視窗，live 未嚴格勝過同格 robot 者該格判 none；robot 追平 ceiling 之格**無能力視窗**，
> 該格對能力宣稱永久 none（如現行 B3=1.000）。
> (b) **robot 分數永不入排名**：任何受測臂之排序、成就宣稱、SUNSET 條款之閉合，皆不得以 robot
> 分數為構成要件或成績；robot 只得出現於量尺欄（哨兵線）。
> (c) **與 SUNSET (c) 凍結文字之關係**：(c) 字面（勝 floor 與 mismatched）不動（criteria_sha 已鎖、
> 挪門柱紀律）；robot 之 veto 作用於證據力層（evidence_level→none），兩口徑並列呈報
> （週報現行「robot 附註」升格為本條款之引用）。能力宣稱一律走 A′（A13）。
> (d) **不溯及**：robot 缺席之舊資料判讀同前（`evidence_protocol` 既有行為）。

（此條款把 `audits/V2-SUNSET-C-DISPUTED-20260727.md` §五 S-8 開放項正式閉合；
現行 `evidence_protocol.evidence_level` 之 robot veto 行為**不變**，變的是其「身分」之成文。）

### 3.3 逐檔 diff 計畫（拍板後施作；file:line）

| 檔 | 位置 | 變更 |
|---|---|---|
| `scripts/verify_evolution_acceptance.py` | `:220-221` | SQL 去除 `AND NOT is_invalid`（R-CELL′-1） |
| 同上 | `:225-229` | 逐項收攏改記 (n_answered, n_total, Σf)；抽出模組級純函式 `rcell_cells(per_item) -> {cell:(n_total,n_answered,mean_f)}`，僅全格有效者給 mean_f（R-CELL′-1/2） |
| 同上 | `:232-235` | ctrl0 改用有效格值；兩 attempt 逐格不同值 ⇒ 該格 incomparable（R-CELL′-3） |
| 同上 | `:239-247` | wins 迴圈：join `local_model_eval_item` 之 `cell_class`，僅 `capability` 格可入 wins（R-CELL′-5）；evidence 字串附缺格清單（R-CELL′-2） |
| 同上 | `_selftest` | 新增紅綠：①C1 型 fixture（部分格 34/36、均值>0.5）**必不得**產 win——先以「天真逐格版」驗紅再轉綠（回歸鎖三規則）；②C2P 型 fixture（全格有效 0.6667）必產 win；③behavior 格高分 fixture 必不產 win |
| `scripts/report_triple_evolution_week.py` | `:166-196` | lai 段加一行逐格狀態（capability 格之有效格數＋live-vs-robot 哨兵線）；(c) 聚合口徑照舊並列；robot 附註改引 S-8 條款（enacted 後） |

零 DDL、零 DB 寫入（兩支皆唯讀儀表）；`eval_local_model.py` **零變更**。

### 3.4 修後預測（由 §2 凍結快照推算；驗收比對之「後」照）

A13 預期 verdict＝**PASS**，wins **集合恰為**（順序不論）：

| 尺 | win |
|---|---|
| (4e15a143ff4b, b6e5208ef821) | behavior@C2P_ZH_PAIR（3 run；0.6667×3 > 0.5） |
| (4e15a143ff4b, aeff01c18ace) | behavior@C2P_ZH_PAIR（3 run；0.5833×3）、grammar@C2P_ZH_PAIR（2 run；0.5833/0.5417）、pack:pp_3ab2efebb04e@C2P_ZH_PAIR（2 run；0.5417×2；pack 已退役、僅史料 run） |

C1 一律以**缺格**呈報（0 個有效格）、不入 wins；B1/B2/B3 永不入 wins。
**wins 多一項或少一項＝施作有誤，停手判源**（T1 絆線之「後」半）。

---

## §4 選項與建議案

| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | R-CELL′ 全文照 §3.1 預凍＋S-8 條款照 §3.2 | 逐格誠實（有效格用盡、缺格不冒充）；一併封閉 §2.6-2 之 behavior 格潛在落差 |
| 乙 | 天真逐格（僅去 run 級過濾、無全格有效要求） | **否決理由已實證**：C1 部分均值 0.606-0.625>0.5 會假 PASS（§2.4） |
| 丙 | 維持現狀（run 級） | A13 對 live 永盲（132 題任一逾時即整輪作廢；三 run 缺答 2-9 題不等）＝紅燈壞在判讀器 |
| 丁 | 先修生成端（降逾時）再談判讀 | 與甲**互補非替代**：即便逾時清零，run 級連坐之脆弱性仍在；生成端另案（ollama 車道） |

**建議＝甲**（同呈案單 H1 建議：R-CELL′ 判讀層修、不換尺＋S-8「robot＝量尺哨兵非受測臂」）。

**證偽條件**：
1. （呈案單原文）判讀層修後若 behavior **有效格數仍為 0** ⇒ 問題在生成端非判讀端，回頭查 ollama 逾時。
   ——依 §2.4 預算：修後 behavior 有效格＝C2P×3＋B1×2＋B3×2 >0；若實跑為 0＝施作錯誤。
2. （T1 絆線）修後 verdict 與 §2.2 快照比對**全不變**（A13 仍 N/A）⇒ 判讀層修是白工、排序錯誤。
3. 修後 wins 集合**異於 §3.4 預測**（多、少、或出現 B 格/C1）⇒ 停手判源，不得先 commit。
4. 對照臂兩 attempt 逐格出現**不同值** ⇒ R-CELL′-3 確定性前提破產，該格判 incomparable 並回報。

---

## §5 風險與回滾

| 風險 | 說明與緩解 |
|---|---|
| **自我利益**（最大） | 修判讀層的直接效果是給 AI 自身第一個 A13 PASS。緩解＝判準預凍（submit 即凍）＋快照先行（本檔）＋修後結果須恰等於預測集合（多一分即 FAIL）＋PASS 天花板 scoped＋self-reported 標記（R-CELL′-7） |
| C2P 樣本小 | 24 題、0.6667 vs 0.500＝差 4 題；且 temperature=0 之 ≥2 run 屬**穩定性**複現、非統計獨立樣本。A′ 預註冊文字如此（不加嚴不放寬＝不挪門柱），但對外表述須帶此註 |
| 舊尺 wins 之誤讀 | aeff 尺 wins（含已退役 pack）僅史料留檔，跨尺不并排（`require_same_scale` 既有）；儀表分尺列示 |
| 週報雙口徑混淆 | (c) 文字口徑與 A′ 口徑並列（既有做法延續）；S-8 條款 (c) 款成文後歧義收斂 |
| 回滾 | 純 code revert（兩支唯讀儀表）；零 DB 寫入零殘留；A13 回 N/A。判準之撤回＝新提案（治權裁決繫 DB 親簽列、git revert 撤不掉——r3 §七「回滾不對稱」認知錨） |

---

## §6 驗收判準（機械可判；全部唯讀）

1. `venv/bin/python scripts/eval_local_model.py --selftest` rc=0 且「尺之錨…b6e5208ef821」行照綠（不換尺）。
2. `venv/bin/python scripts/verify_evolution_acceptance.py --selftest` rc=0，含 §3.3 三條新紅綠
   （C1 型排除、C2P 型命中、behavior 格排除），且 C1 型曾以天真版**驗紅**留證（commit 訊息或 audit 註記）。
3. `venv/bin/python scripts/verify_evolution_acceptance.py --only A13`：verdict=PASS，
   wins 集合**恰等於** §3.4 表（集合比對、順序不論）；C1 以缺格列示。
4. §2.3 之 13 筆 run_id 列**逐位元不變**（append-only 未動帳本）：
   `SELECT count(*) FROM local_model_eval_run WHERE set_id='4e15a143ff4b' AND eval_code_hash='b6e5208ef821'`
   ＝13＋（若其間有新 run 則僅允許**新增**列）。
5. A12（週報零寫入）照 PASS；週報 lai 段出現逐格狀態行與缺格清單。
6. R-CELL′ 全文之 governance_proposal 列 status='enacted'、diff 內文 sha 與本檔 §3.1 一致。

---

## §7 Steward 決定欄（留白）

- [ ] H1-同意（甲：R-CELL′ §3.1 全文預凍＋S-8 §3.2 條款）
- [ ] H1-改採＿＿＿＿（乙／丙／丁或修訂文字；R-CELL′ 凍前可改、凍後唯 GATE-raise）
- [ ] S-8 條款逐字採納？（是／修訂：＿＿＿＿）
- 簽署：＿＿＿＿＿＿　時點：＿＿＿＿＿＿

---
name: eval-boilerplate-floor
description: "樣板地板會高過真能力。07-26:常數字串 0.654>冠軍 0.492;**07-27 新尺同病復發**:13 行零知識格式規則機四格全 1.000 與 ceiling 打平、echo 臂勝 behavior、floor 只是任選弱字串"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-27T13:48:32.766Z
---

**鐵律：每次宣稱某個分數代表能力之前，先跑三個對照臂——ceiling（理想答案）、floor（不看題目的常數字串）、mismatched（選錯行為類別）。三臂未跑完，分數一律不得引用。**

**Why**：2026-07-26 實證。`evolve_cycle.py` 的 `_score` 是「答案覆蓋金標之 CJK 雙字元組比例」，而 983 條 gold 全出自三個固定模板（`依 X(SSOT):…以現值為準`）。後果三重：
- 我自寫的**完全不看題目**的常數樣板字串得 **0.654/0.722**，而現役 serving pack 帳本記 **0.492**——**冠軍低於零知識地板**。
- 把 gold 內所有數字換成 9 當答案，分數仍 **1.000**——**事實敏感度 0%**。
- 更底層：被打分的字串根本不是答案。qwen3:4b 具 thinking，`think:false` 沒關掉思考，`num_predict=400` 下 **100% `done_reason='length'`**，評到的是被截斷的推理獨白。

三個病同時存在，卻產出了一條漂亮的「0.256→0.325→0.383→0.492 逐版單調升」敘事——而那條線還跨了三把不同的尺（`_fixed_eval_set` 按 md5 排序 LIMIT 12，語料每天長就換題；帳本 `set_hash=44893a73fbfc` vs 現行算出 `a8b466844fe5`）。評測 code 是我寫的，07-25 的「固定集修正」只修掉隨機性、沒修掉池成長漂移。

**How to apply**：
- **地板臂是強制項不是加分項**：任何新評測器，第一件事是問「一個什麼都不懂但會抄格式的東西能拿幾分？」。離線、零成本、確定性——沒有不跑的理由。
- **上界臂同樣強制**：理想答案若拿不到滿分，是尺壞了不是模型爛。
- **同尺才可比**：評測器與題庫各自雜湊入帳，跨雜湊比較要 fail-loud 拒絕，不能靠人記得。（落點：`local_model_eval_run.eval_code_hash` / `local_model_eval_item.set_id`；雜湊只涵蓋影響分數的部分，改報表不算換尺。）
- **軸要分開不要平均**：平均會讓樣板分稀釋事實分。三軸 F/P/A 各自成欄。
- **「行為類別對」≠「內容對」**：新尺實測 shuffled 臂（同層鄰題的理想答案、內容全錯）在 P/A 拿 0.900/0.967——因為「查無」對任何查無題都對。故 A 軸進步只能宣稱「更會選對行為」，不得宣稱「答得更準」；只有 F 軸對內容敏感。
- 推廣：這不是 LLM 評測獨有。凡「相似度／覆蓋率」型指標＋「樣本同源同格式」，都有樣板地板。TWEVO 的 local-gates、RAWEVO 的覆蓋率同樣該被這樣質問。
- **同族變體（07-26 深夜實犯）：|corr| 最大化選假說＝撈定義恆等式**。RAWEVO R3 v1 按相關絕對值降冪，端出的 10 則全是 `margin_usage=f(margin_balance)`、`market_value=close×股數`、`money=volume×價` 這類套套邏輯——**退化解永遠贏過真結構**，hugo 還批准了那批。修法＝中頻帶（0.25–0.85）＋衍生家族排除（估值比值 per/pbr/dividend_yield 皆含價，與價共動是機械的）。通則：任何「最大化 X 選候選」先問「什麼垃圾能把 X 拉滿？」——與地板臂同構，選材前先算退化解的 X 值。
- 相關：[[cross-claim-contradiction-check]]（宣稱層的自欺）、[[augur-validation-master-plan]]（deflation 精神＝搜尋會膨脹須外部確認）、[[never-type-human-signature]]（保證被溶解的另一形態）、[[guard-mechanisms-that-silently-fail]]。

## 第二次發作（2026-07-27，新尺 F@L1；**修尺沒有修掉這個病**）

07-26 建的新尺（`set_id=4183475c5089`）被證明**同病復發，只是換型**。三項親驗：

- **13 行零知識格式規則機**（不查庫、不呼叫 LLM、不看內容，只認題幹開頭）實跑 `L1.F/L1.P/L3.A/L4.A` **全 1.000**——與 ceiling 打平、勝過每一個 LLM 臂。成因：**層別由題幹表面 100% 可推**（`guess_layer` 錯 0/120；L1 以 `[檢索片段]` 開頭、L2 以 `[無檢索片段]` 開頭、L3 問三欄、L4 問兩欄）。
- **echo 臂**（把題目原文原樣印回）F@L1=1.000、P@L1=1.000 **勝過 behavior 0.967**——因為 L1 的 facts 逐字印在題幹裡，F 軸判準是子字串包含。
- **常數字串 `VARCHAR`** 得 F@L1=0.2333 **> 判準 A 門檻 0.167**，`evidence_level` 同回 `scoped_established`。門檻 0.167 本身也是假的：shuffled 的 0.167 全來自 column_catalog 子格（答案只有 VARCHAR/NUMERIC 兩值，鄰題撞答）。
- **floor 不是地板，是任選的一條弱字串**：單一常數「查無 多筆」通吃 L3.A=1.000 與 L4.A=1.000；`BOILERPLATE_ARM` 拿 0 只因它剛好不含那二詞。`behavior_rubric._selftest` 那句「地板臂全滅＝機械鎖」是**空證**。
- **`behavior` 的 A@L3=1.000 是退化常數不是能力**：對非 L1 之 90 題 100% 拒答，多為字面「查無 查無」；實測該常數逐格得分與 behavior 三格**逐位元相同**。而 L2/L4 那 60 題的鍵**經實查全部存在於 DB** ⇒ 那是 60 次「不存在」的假陳述。**pack 捏造存在、behavior 捏造不存在，兩者都不誠實。**

**新增的教訓（比 07-26 更進一步）**：
1. **地板臂要「找最強的退化解」不是「隨手一條常數」**。問法從「一個常數能拿幾分？」升級為「**我能不能寫出一支通吃這格的零知識機器？**」——寫不出來才算這格有鑑別力。
2. **對照臂若結構性恆為 0，那個門檻是空的**。F@L1 的 floor 與 mismatched 恆 0（mismatched 的捐贈題 29/30 屬 L3），所以「同勝 floor 與 mismatched」＝勝過 0，連 shuffled 自己都滿足。**設計對照臂時要問：它有沒有可能拿到非 0？**
3. **「可複現」要能被記錄才談得上**：`run_id=sha256(set_id|code_hash|arm|model|n_items)` ＋ `ON CONFLICT DO NOTHING` ⇒ 重跑第二次必被靜默丟棄（親驗全表始終 7 列）。DESKTOP 0.933 vs 本機 0.967 在同尺同模型 temperature=0 下不一致，是**複現未成立**的反證。
4. **層別／答案不得由題幹格式推得**：出題模板差異本身就是洩漏。
5. **哨兵全綠 ≠ 尺可信**：`verify_eval_set_validity.py` 0/120 漂移，但它不驗答案是否寫在題幹裡、不驗層別可否由格式推得、不驗答案空間是否退化。

**處置（07-28 hugo 拍板 V2-RUBRIC-go＋SUNSET-C-align，已執行）**：判準器四件落地——ABSTAIN_RE 補「未找到/找不到」、L1 F 軸加「來源沒有的年份=捏造」否決（judge 貫通 source_text）、floor 換**最強退化常數**（剖面 [0,1,1,1]，「全滅斷言」正式退場）、**robot 第五對照臂**入 ARMS_OFFLINE 與 evidence_protocol（live 未嚴格勝 robot 之格=none）；run_id 帶 attempt 序=重跑可記錄。換尺 f3075238eb55→**ef142e9374c1**（舊 run 留檔未刪、PINNED 已更）。新尺離線實測：**robot 五格全 1.000**=本凍結集每格皆格式可達→任何 live 臂於本集至多 none——真訊號唯凍結集重建（S-4，待 hugo）。週報 (c) 已逐字對齊凍結原文（受測臂嚴格勝 floor∧mismatched＋≥2 run 複現）→ 誠實⬜未達成。殘餘待裁：S-4/S-5/S-6/S-7/S-8。登錄=`audits/V2-RUBRIC-GO-20260728.md`。

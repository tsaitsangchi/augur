---
name: eval-boilerplate-floor
description: "任何「與金標重疊率」型評分器,若金標同出少數模板,樣板地板會高過真能力——2026-07-26 實證:不看題目的常數字串 0.654 > 現役冠軍 0.492;新尺同臂 0.000"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-26T09:41:08.422Z
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
- 相關：[[cross-claim-contradiction-check]]（宣稱層的自欺）、[[augur-validation-master-plan]]（deflation 精神＝搜尋會膨脹須外部確認）、[[never-type-human-signature]]（保證被溶解的另一形態）。

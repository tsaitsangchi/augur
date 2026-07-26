---
name: augur-self-evolution-plan-map
description: "自我迭代進化計畫書地貌——三軸 RAWEVO×TWEVO×LAIEVO 已 APPROVED-NO-EXEC(2026-07-26),但三軸皆建立在今日已破的評測尺上,需重新確認"
metadata: 
  node_type: memory
  type: project
  originSessionId: b6cddf62-b16d-44ba-af86-bbdb2cb161c8
  modified: 2026-07-26T09:42:50.949Z
---

**augur 的自我進化不是一份計畫，是一組互相引用的計畫群；2026-07-26 已收斂為「三軸總控」架構，狀態 APPROVED-NO-EXEC（拍板但未開執行）。**

**三軸與 SSOT 檔**（命名與拍板碼是既有引用的錨，改名會破壞交叉引用）：
- **RAWEVO**（資料地基）＝`reports/augur_raw_data_self_evolution_loop_plan_20260726.md`——raw／catalog／對帳／覆蓋／缺口 → 假說燃料
- **TWEVO**（台股預測）＝`reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md`——假說 map → 候選建值 → local-gates → 雙綠 → APPLY → prodset 重訓 → as-of 模擬／arena → 結算 → 證據回饋
- **LAIEVO**（本地 AI）＝`reports/augur_local_ai_route_b_no_gpu_plan_20260726.md`＋母計畫 `augur_local_ai_evolution_loop_plan_20260725.md`
- **總控／介面契約 SSOT**＝`reports/augur_triple_self_evolution_master_plan_20260726.md`（`TRI-P-yes`＋`TRI-IFACE-yes`＋三軸 `*-P-yes`＋`FZ-keep`＋`GATE-keep`；採納記錄 `audits/TRI-SELF-EVO-PLANS-APPROVED-NO-EXEC-20260726.md`）
- `augur_dual_self_evolution_interface_20260726.md` 已被 triple 取代，僅存史料（`DUAL-IFACE-yes` ≡ `TRI-IFACE-yes`）
- 上游相關：PME＝`augur_philosophy_market_evolution_loop_plan_20260724.md`＋`augur_pme_expand_hypothesis_map_coverage_plan_20260724.md`；憲章 v1.47.0 跨域原理映射準則（`principle_domain_map`）

**⚠ 必須知道的地基級更正（2026-07-26）**：LAIEVO 全系列的能力數字（0.492／0.567／0.521／0.511…）建立在一把已實證失效的尺上——詳見 [[eval-boilerplate-floor]]。連帶效應：
- 母計畫的成敗判準「部署工作域金標分數逐版單調升」所指的金標與錨集，在 DB／repo 中是否存在需實查，不可假定。
- 三軸 APPROVED-NO-EXEC 是在壞尺的認知下拍的，涉及 LAIEVO 的部分**可能需要 hugo 重新確認**。
- 新尺已建成（`local_model_eval_item` 凍結集 `4183475c5089` 120 題四層／`local_model_eval_run` 帳本／`src/augur/evolution/behavior_rubric.py` 三軸 F·P·A 0/1／`scripts/eval_local_model.py` 多臂 harness），兩表皆掛誠實閘。

**Tier 2 LoRA 裁決**（8-agent 對抗審查＋親驗，2026-07-26）：硬體可行（1.7B QLoRA on GTX 1650 4GB sm_75；4B no-go），但**語料不該進權重**——983 條中 87% 是文獻 metadata，背進權重＝母計畫自己警告的訓練幻覺（知識庫天天長、權重記過期快照），違 #9／#10。LoRA 僅剩「該拒答時拒答／多實體時消歧義」這一窄塊有價值；先做 grammar＋行為守則的零訓練上界，再論剩餘價值。設計書＝`reports/augur_tier2_lora_spike_design_20260726.md`（含權重鏈 PEFT→convert_lora_to_gguf→ollama ADAPTER；ollama 的 safetensors ADAPTER 路對 qwen3 不支援）。詳硬體見 [[gb10-unavailable]]。

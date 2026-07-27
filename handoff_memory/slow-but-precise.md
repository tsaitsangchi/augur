---
name: slow-but-precise
description: hugo 2026-07-27 指導原則——「此專案接受很慢，但所有的能力提高要精準」；速度永遠讓位給正確性
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-27T05:47:44.628Z
---

**hugo 2026-07-27 對話原則（逐字）：「此專案接受很慢，但所有的能力提高要精準」。** 同日並示「現在很慢没關係，就把timeout時間加長一點，只要系統可以回正確答案即可」（advisor timeout 已 400→900s 落地）。

**Why**：本專案的靈魂是誠實（三敵零容忍），慢是 CPU-only 單機的物理現實、可接受；不準的「能力提升」是假兆、會沉默污染下游（舊尺 0.492 假進步的教訓）。速度與精準衝突時，永遠選精準。

**How to apply**：
- 驗收一律用**精確計數／凍結尺實測**，不用 reltuples 估算、不用「看起來對」（如 Qdrant 對齊驗收＝CLEAN 反差矩陣落差=0，非點數大概相符）。
- timeout 類參數放寬不猶豫（advisor 900s、chat 代理 1800s）；不為快而降 draws、降 seeds、跳 multi-seed。
- 任何「能力提高」宣稱須過 [[augur-self-evolution-plan-map]] 的證據協定（evidence_level、同時勝 floor+mismatched）；慢慢跑完 200 draws 勝過快快跑 20。
- 與 #28 省 usage 二分不衝突：省的是 Claude token（執行層），不省本地計算的徹底性。
- **並行前提＝精準達成**（hugo 07-27 補充逐字：「所有並行的前提為此專案的精準目標達成」）：並行採**資源車道制**（Ollama 單槽嚴格序列／CPU 大戶一次一個／純 code+DB 隨時並行）；**量測類作業不與資源大戶疊**到會改變結果的程度；每條並行線完成後仍須**全套精準驗收**（如 P-E＝落差 0＋點數精確＋新影子實測 0.97，不是「跑完就算過」）；arena 等**預註冊節奏本身是量測協定**，不為並行提早跑（當日資料未齊＝出單不精準）。

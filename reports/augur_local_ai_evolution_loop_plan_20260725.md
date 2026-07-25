# augur_local_ai_evolution_loop_plan_20260725 — 本地 AI 能力提升閉環計畫【終稿 v2，經三鏡對抗審查重構，待 hugo 拍板】

> **性質**：#20 計畫先行（高風險）；hugo 指示「本地 AI 自我能力提升閉環、無窮進化」＋擴充「教師可為任何 AI 平台」。三視角對抗審查（P5.W5 合規×機械可行×反方，3 agents／242k tokens）**擊倒 v1 草案的自對弈永動機核心**，本終稿＝存活的三分之一＋補上全部合規/機械補丁。v1 全文與審查 JSON 留檔可考。
> v1.39.0：(a) 新表僅 `local_model_version`（§四）；(b) 程式規畫 §四。

## 一、v1 草案被擊倒的部分（誠實留痕，勿再重提）

| 被殺設計 | 死因（三鏡合力） |
|---|---|
| **oracle-graded self-play 永動機** | ①#28 已裁：oracle 可裁域 LLM 意見**零證據力**、「確定性工具包 LLM＝降級」——練成的能力在系統內不可兌現②**bridge「2改」先例（2026-07-11）直接反證**：oracle 域宣稱的誠實 gold＝DECLINE（「知識庫無據、轉查 DB」），自對弈卻在教模型憑權重回答 DB 狀態題＝**訓練幻覺**（live 資料天天漂、權重記的是過期快照）③二元裁決域猜對率≈53%，verified-only 濾不掉「錯誤推理＋碰對答案」——崩塌防護有名無實④任務類實僅 ~6-8 模板、引擎在該域已 100% 無上升空間 |
| 本機 4b QLoRA | 實測反證：idle free VRAM 2.7GB＜NF4 4B 最低需求；CPU 路缺 bitsandbytes-CUDA 前提且與 PG 6GB shared_buffers 互擠；與 S6 原結論「本機不可跑」矛盾而無新實證 |
| 夜間全自動 cycle＋自動 cutover | P5.W5 第三型推定違反（延長無人工檢核自動鏈）——**對話拍板不滿足推翻推定的形式要件**，須 Steward 書面裁決＋認定理由＋公開存檔 |
| 「無窮」as 自對弈飛輪 | 降格為誠實版：**有新 gold 批量＋訓練機在線才走一輪**——開放式無上限，但速率由真實教師訊號流量決定 |

## 二、存活架構：蒸餾閉環（教師訊號在目標域、每環節有人閘或機械閘）

```
真實工作流 → gold 樣本捕捉(既有 distill/bridge 管線＋人裁結果＋多教師交叉投票)
   → S6 LoRA 訓練 @GB10 → 候選版本(local_model_version)
   → 預註冊 GATE(判準凍結=人簽) → 晉升=hugo 經 #11 一鍵 → shadow eval → cutover/回滾
```

1. **樣本源（真教師訊號，非自產）**：①advisor/MCP 真實工作的教師修正（多教師抽象層：Claude／Cursor／Gemini／任何平台，交叉投票一致才入 gold）②audit escalation 的人裁結果（最高權重）③既有 171 條錨集。**隱私閘（DB CHECK 強制非腳本自律）**：含 owned_local/private citation 的樣本**禁送外部教師**（v1.37.0 Gemini 案同構）、只許本地評分或棄評。
2. **訓練＝本機階梯（v3 修訂：hugo 2026-07-25 宣告無 GB10、僅本機可用）**——
   - **Tier 1（主力、立即可行、零訓練）：prompt-pack／few-shot 演化**——從 gold 帳本擇優 exemplar、演化系統提示與少樣本包；「版本」＝prompt_pack_hash 註冊進 `local_model_version`（base_model 不變）、走同一晉升閘與部署域評測。窄任務上增益常與 LoRA 同級、成本兩個數量級低、回滾＝換 hash。
   - **Tier 2（實驗、須先環境鏈 spike）**：(a) CPU LoRA on 4b——週級 cadence（171 條×3 epochs ≈1-2 天/輪）、訓練窗停 PG 或 bf16、實測定 go/no-go；(b) GPU QLoRA on **qwen3:1.7b 特化生**——NF4 ~1.1GB 塞得進 free 2.7GB，賭「窄任務特化 1.7b ≥ 通用 4b」，由部署域金標裁決（輸了誠實留檔）。權重鏈（HF→PEFT→convert_lora_to_gguf→ollama）仍須建、於 Tier 2 spike 實證。
   - **硬體路（選項）**：二手 12GB GPU（如 RTX 3060）即解鎖 4b QLoRA 夜間輪——本機升級屬「本機」，供 hugo 參考。
3. **晉升閘（判準人閘名實相符的四補丁）**：(a) 判準凍結的 approve＝**人簽留痕**（鏡射 arena gate `approved_by=hugo`）(b) 評測集＋171 錨集 **byte hash 釘入 gate 列**（防從分布側挪門柱）(c) 評分程式版本 hash 錨定、讀端斷言 fail-loud (d) **補部署工作域評測**——MCP summarize/extract 迷你金標（反方抓到：舊三式只測 benchmark 軸，4b 真飯碗可靜默變差）。GATE 裁判限 oracle/凍結金標，禁被評模型自評。
4. **權重＝私有 artifact**：訓過私有樣本的 LoRA 可記憶回吐——權重檔／SFT jsonl／evolution 帳本一律 owned_local 級管制（永不入 git/公開 repo、sync_memory export 掃描排除、跨機唯私有通道）；P4.E7：teacher_gold 與模型輸出 provenance 永久帶 synthetic 標記。
5. **隔離不變式**：evolution 帳本比照蒸餾界線-A/B/C 納 import_isolation 稽核（不落 knowledge_*/philosophy_*/feature_values、不成 citation、不進預測管線）＋負向測試。

## 三、治理前置（兩件、獨立、不可互代）

1. **P5.W5 書面裁決**：自動化程度每升一級（人簽逐次晉升 → 排程訓練＋一鍵晉升 → 更高）皆須 Steward 書面裁決「未實質降低監督」附理由留檔（素材：oracle/guard 裁決權威獨立於被訓模型、一鍵回滾、晉升推播、首 N 次人簽）。**在裁決作成前，一切晉升逐次人簽**——迴圈照跑、只是最後一步是你點的。
2. **憲章升版承載**（比照 RBAC/arena 先例）：權重=artifact 射程釐清、evolution 隔離不變式、晉升閘紀律、「本機」定義釋義。

## 四、實作規畫與分階段

表：`local_model_version(version_id, base_model, lora_path, train_sample_manifest_hash, anchor_hash, eval_code_hash, gate_id, status∈{candidate,serving,retired}, promoted_by, promoted_at)`＋挪門柱 trigger。程式：`evolve_capture.py`（樣本捕捉＋隱私閘）／`evolve_train_lora.py --machine gb10`（含權重鏈全步驟）／`evolve_gate_eval.py`（四補丁閘）／migration。

| 階段 | 內容 | 人閘 |
|---|---|---|
| P0 | 憲章升版＋DDL＋樣本捕捉（隱私閘 DB CHECK） | 升版拍板 |
| P1 | 多教師 adapter＋gold 累積（含交叉投票） | 教師平台各自授權 |
| P2 | S6 首訓 @GB10（權重鏈實證＝首要里程碑） | 訓練機到位確認 |
| P3 | GATE 預註冊（判準人簽凍結）＋首次晉升 | **每次晉升 hugo 一鍵** |
| P4 | 自動化升級（排程訓練等） | **P5.W5 書面裁決後才開** |

## 五、演化歷程帳本（hugo 2026-07-25 提問「學了什麼/何時/因為什麼」而增設；DB-first #29b）

三個問題各有機械落點，全部可 SQL 直查、不靠敘事：

| 問題 | 落點 | 內容 |
|---|---|---|
| **因為什麼事？** | `evolution_sample.trigger_event`（新增欄，jsonb） | 每條 gold 樣本記觸發事件：來源類型（advisor 答錯被教師修正／audit escalation 人裁／hugo 對話指正）＋事件時戳＋原始事件指針（escalation id／對話日期／audit run id） |
| **學了什麼？** | `evolution_sample`（prompt＋gold answer＋teacher provenance） | 逐條可讀；每版訓練的 `train_sample_manifest_hash` 對應樣本清單 → **版本間 diff＝「這一版新學了哪幾條」** |
| **什麼時候提升？** | `local_model_version`（promoted_at＋gate 評測差分） | 每次晉升記：時間、gate 前後分數差分（benchmark 軸＋部署工作域軸）、hugo 簽核時戳 |

**呈現層**：`evolve_history_report.py`（零 usage）產「演化年表」——逐版本一行：`日期 | v3←v2 | 新增 gold 37 條(其中 hugo 指正 5、教師修正 28、人裁 4) | MCP extract +4.2% | 錨集回歸 0 退步 | 觸發大事: 07-25 vol_target 誤判案`；可掛 admin console 頁。**設計原則：演化史是 append-only 帳本（P4.E3 只失效不刪除）——包括失敗的訓練輪與被拒的晉升都留檔**，你看到的是全史不是成功剪輯。

## 六、成敗判準（誠實）

成功＝4b/8b 在**部署工作域**（MCP 濃縮/extract、advisor 子任務）的金標分數逐版單調升、通用能力錨集零退步；失敗＝兩輪訓練無部署域增益 → 停損，資源轉「換大 base @GB10」（反方正確指出：LoRA 資產隨 base 換代歸零，**耐久資產是 gold 樣本帳本**——它跨 base 永存，這才是真正無窮累積的東西）。

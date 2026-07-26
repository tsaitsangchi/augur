# augur Tier 2 LoRA spike — 總合成設計書

**日期**：2026-07-26　**建議落檔**：`reports/augur_tier2_lora_spike_design_20260726.md`（#16 命名）
**輸入**：可行性三鏡 + 對抗四鏡之產出；**加上本報告作者於 2026-07-26 之獨立親驗**（離線確定性計算，零 Claude token、零 LLM 呼叫、可完全複現）
**性質**：計畫先行文件（#20 v1.39.0：含表 schema + python 程式規畫）。**這份不是實作，是拍板前的設計。**

---

## 0. 一句話結論（先講最重要的）

> **hugo 批的「Tier 2 LoRA spike」不能照原樣跑。不是因為硬體不夠（1.7B QLoRA 實測跑得動），而是因為決定 go/no-go 的那把尺已被七鏡中的五鏡各自獨立攻破，而我方才親驗複現：一條我隨手寫的、完全不看題目的常數字串在固定評測集 A 得 0.671、集 B 得 0.729，而現役 serving pack `pp_3ab2efebb04e` 記錄的分數是 0.492。現役冠軍低於「零知識樣板地板」0.179～0.256。**
>
> **同時：把 gold 裡每一個數字換成 9，分數仍是 1.000（事實敏感度 = 0%）。**
>
> 在這把尺上，一個「只背下三個模板、一個事實都沒學到」的 LoRA 會被記為專案史上最大單版增益；一個真的學到東西的 LoRA 拿不到任何加分。**無論結果為何，都不構成證據。**

因此本設計把 spike 拆成三段，且**中間那段（S1，零訓練、半天、幾乎零風險）極可能讓第三段（S2，LoRA）變成不必要**。這是誠實的建議，不是保守的建議。

---

## 1. 本報告作者之親驗（第一手，非轉述）

以下全部是我在本次會話中對 live PG `augur` 與本機環境實跑的結果，離線確定性計算部分可原樣複跑：

| 項目 | 親驗值 | 意義 |
|---|---|---|
| `local_model_gold_sample` 列數 | **983**（任務書寫 865） | 語料一日內 +13.6%；任何釘 865 的算術已過期 |
| 相異 `verdict` | **1**（`oracle_pass` 983/983） | **verdict 不是篩選、是常數**；系統中不存在任何 oracle |
| 相異 `gold_answer` | **908**（重複 75 條） | `sample_id` 互斥擋不住內容洩漏 |
| 來源分佈 | knowledge_item **856** / column_catalog **67** / field_correlation_baseline **60** | KI 佔 87.1%；夜間收割只增 KI |
| 現行固定集 A `set_hash`（以 `evolve_cycle.py:249` 原演算法） | **`334086187ab1`** | — |
| DB 內四個已評分版本記錄之 `set_hash` | **全部 `44893a73fbfc`** | **帳本 provenance 為假**；0.256→0.325→0.383→0.492 跨的不是同一把尺 |
| `local_model_version.anchor_hash` / `eval_code_hash` | **5 個版本全為 NULL** | 母計畫 3(b) 設計的「三 hash 挪門柱鎖」完全空轉 |
| 常數字串（我自寫、question-blind、不看題目）| 集 A **0.671**（min 0.500 / max 0.806）、集 B **0.729**（min 0.500 / max 0.893） | **現役 0.492 低於地板** |
| gold 內所有數字改成 9 後之分數 | 集 A、集 B **皆 mean 1.000** | 事實敏感度 **0%** |
| 「同源他題 gold」當答案（內容完全錯） | column_catalog median **1.000**、field_correlation **0.976**、knowledge_item **0.871** | 只要語域對，內容全錯就拿近滿分 |
| venv 套件 | **bitsandbytes 0.50.0 已裝**、gguf 0.19.0 已裝、torch 2.12.1+cu126、transformers 5.12.1、peft 0.19.1、trl 1.9.0、scipy 1.18.0 | 任務書與母計畫 §11「bnb 未安裝」**錯**（誤用系統 python 測） |
| llama.cpp | `~/llama.cpp` **不存在**、`llama-quantize` **不存在** | 權重鏈最後一哩確實未建 |
| ollama | 0.32.1；模型僅 qwen3:8b / qwen3:4b / nomic-embed-text（**無 qwen3:1.7b**） | — |
| GPU（查時） | 4096 MiB total / **1022 MiB free**（ollama 常駐中） | free VRAM 是滾動量，任何「free 2469」都是快照 |

**方法揭露**：常數字串由 `evolve_cycle.py` 三個模板的字面骨架組成、所有實體槽留空；`_score` 逐字複製自 `scripts/evolve_cycle.py:135-146`。零 LLM 呼叫 → 這些數字是評分器的**上界性質**，不含生成雜訊。live 端（模型真的回答）之地板由三個對抗鏡各自實測為 0.68～0.80，與我的離線值同區間、同方向。

---

## 2. 逐條裁決（不含糊並列）

### C1　bitsandbytes / gguf 是否已安裝
**裁決：已安裝（bnb 0.50.0、gguf 0.19.0）。** 親驗。鏡一稱「我裝的」、鏡二稱「本來就有、簡報用系統 python 測錯」——**誰裝的無關**，現況是已裝。
**連鎖後果**：母計畫 §11「本機 4b QLoRA 實測反證：…CPU 路缺 bitsandbytes-CUDA 前提」的**前提之一已失效**，該段須更正（更正屬 #26 執行層「改正確」，但因涉及母計畫成敗判準的前提 → 見 §7 人閘 7）。

### C2　GPU 訓練 base：4B / 1.7B / 0.6B
**裁決：Qwen3-1.7B。4B GPU QLoRA 判 no-go。0.6B 無必要。**

依據與駁斥：
- 鏡一逐層實測 NF4 佔用並線性外推，**該方法先在 1.7B 上自我驗證**（預測 1287.4 MiB vs 實測 1288.0 MiB，誤差 0.05%），再以同法得 4B = **2548 MiB**（36 層 × 50.17 + **741.9 MiB 未量化 embedding**）。這是本題證據等級最高的量測。
- 鏡三的「4B NF4 僅 2.06 GiB」是 `P × 0.55 bytes` 公式，**漏掉 `nn.Embedding` 不被 bitsandbytes 量化**（bnb 只量 `nn.Linear`；Qwen3 vocab 151936 × hidden 2560 × 2 bytes = 741.9 MiB 常駐 fp16）→ 系統性低估 ~24%。**駁回。**
- 鏡二的「3.2–3.5GB」自承是估算。**證據等級低於實測。**
- 鏡四實測：對 ollama 下 `keep_alive:0` 卸載後 free VRAM = **3296 MiB**（不是 4096；顯示與驅動另有佔用）。4B 峰值（2548 base + LoRA/grad/optim + ~1200 activations）≈ 3.7–4.0 GB → **無餘裕**。
- **決定性補刀**：鏡一實證 WSL2 host-memory fallback 為 active——超量**不會 OOM**，會靜默退到 PCIe 主機記憶體，同一 config 因競用差 3.7×（2.147 vs 7.995 s/step）。所以「4B 跑起來了」不能證明它裝得下，只會用 wall-clock 懲罰你。
- 0.6B：1.7B 已可行且更接近部署尺寸，降到 0.6B 只會讓「窄任務特化」的宣稱更弱。**不採。**

### C3　compute dtype：bf16(模擬) vs fp16 vs fp32
**裁決：不預先寫死。spike 內以 20-step bake-off 三選一。先驗偏好 bf16。**

- 鏡一是**唯一提供端到端 wall-clock 對照**者：全 28 層、seq256、grad-ckpt、AdamW8bit → **bf16 2.147 s/step vs fp16 6.408 s/step（3.0×）**；成因是 GTX 1650 = TU117，是唯一**沒有 tensor core** 的 Turing 晶片，fp16 走了慢路徑（矩陣乘實測 fp16 0.38 vs bf16 1.67 vs fp32 2.90 TFLOPS）。
- 鏡二、鏡四主張「bf16 非原生 → 用 fp16 + GradScaler」，依據只有 `is_bf16_supported(including_emulation=False)=False` 這個 **API 回報**，**沒有任一筆 wall-clock 對照**。證據等級低於鏡一 → **不採為預設**。
- 但鏡一自己的 L=8 資料顯示 **fp32 2.208s ≈ bf16 2.263s**——fp32 也在候選內，且 fp32 沒有數值風險。鏡一自己沒有跑全 28 層 fp32。
- **故：三者都測，20 steps，選「s/step 最小且 20 步梯度範數全 finite 且 peak VRAM < 3300 MiB」者。** 硬護欄：訓練 loop 每步 `assert torch.isfinite(loss)`，第一次 NaN 即中止並記為 env 事件（fp16+LoRA 的典型失敗是靜默 NaN → 分數沒動 → 被誤記成「LoRA 無效」）。

### C4　seq_len
**裁決：`max_length=320`，dynamic padding to longest-in-batch，`packing=False`。**
兩鏡獨立以真 Qwen3 tokenizer + chat template 實測全 983 條：mean 107.5 / p99 165 / **max 253**。
- 128 → 截斷 12.51%，**判死**。
- 256 → 截斷 0%，但距 max 253 只剩 3 token，**零安全邊際**（語料每日在長）。
- 320 → 有邊際，且因 dynamic padding，平均成本仍由 mean 107.5 決定，非 320。
資料準備時強制 `assert` 無任何一條被截斷。

### C5　權重鏈：斷、不斷、或走錯路？（本節是最重要的技術裁決）
**裁決：`ADAPTER *.gguf` 路線已被端到端實證可行；ollama 的 safetensors ADAPTER 路對 qwen3 不可行；唯一未證的一跳是 `convert_lora_to_gguf.py` 對真實 PEFT qwen3 adapter。**

- 鏡二提供本題**唯一的執行證據**：手寫零依賴 GGUF v3 adapter（`general.architecture=qwen3`、`adapter.type=lora`）→ `ollama create` 成功 → journal 實錄 `llama-server ... --lora ...` 與 `llama_adapter_lora_init_impl: loaded 2 tensors from lora file` → **全零 adapter 輸出與裸 base 逐字相同（no-op 正確）、高斯擾動 adapter 輸出改變（真的被套用）**。這是雙向對照，不是單向「跑起來了」。
- **鏡一的 STEP 0 必須作廢。** 鏡一提議「emit 一個 PEFT adapter 目錄 → `ADAPTER /tmp/qwen3_lora_probe` → `ollama create`」當作全計畫的閘。鏡二的源碼證據顯示 ollama 只有 `convert/convert_llama_adapter.go` 與 `convert_gemma2_adapter.go`，**qwen3 會回 `unsupported architecture`**；鏡一自己也承認「沒有 qwen3-specific converter」卻仍把它寫成前置閘。照跑會產生**假 blocker**——失敗只證明走錯路，不證明鏈路死。
- 唯一路線固定為：**PEFT adapter → `llama.cpp/convert_lora_to_gguf.py` → `.gguf` → Modelfile `ADAPTER`**。
- 該一跳的既有依據是源碼級（鏡二查得 `conversion/__init__.py` 映射 `Qwen3ForCausalLM`→qwen；`conversion/qwen.py:155` `Qwen3Model(Qwen2Model)` 的 `modify_tensors` 對非 rerank 模型是純 pass-through，`LoraTorchTensor` 不會踩 reshape/permute；搜到的 `NotImplementedError` 屬 Qwen3.5/Qwen3Next，不適用）。**源碼級 ≠ 執行級 → 列為 S2a 的時間盒閘。**
- 親驗：llama.cpp 確實不在本機 → 須安裝。**警告採納**：`requirements-convert_hf_to_gguf.txt` 釘 `torch==2.11.0 / transformers==4.57.6 / numpy~=1.26.4`，與 venv 現況（2.12.1 / 5.12.1 / 2.4.6）衝突，**照裝會把 peft/trl/dspy 一起拖壞**。→ 只 clone 取腳本，**絕不跑它的 requirements**；先試用 augur venv 直跑，失敗才另開 `~/venvs/gguf-convert` 獨立 venv。

### C6　訓練窗要怎麼騰 VRAM
**裁決：`ollama stop qwen3:4b`（或 API `keep_alive:0`）即可，不停服務、不需 root。**
鏡一已實測：執行後 `augur-advisor` / `augur-chat` / `augur-admin` / `augur-probability` 四個 user 服務**全部仍 `active`**（它們只宣告 `Wants=`，弱依賴），模型於下次請求自動重載。鏡二的 `systemctl stop ollama` 較重且已被證明不必要 → **不採**。
副帶：鏡一發現 `augur-ollama.service` 處於崩潰迴圈（restart counter **3673**，`address already in use`，因為系統級 `ollama.service` 才擁有 :11434）。**與本案無關的既存缺陷**，另案處理，不混進 spike。

### C7　被打分的字串根本不是答案
**裁決：CONFIRMED，且列為 S0 阻斷條件。**
三鏡各自獨立實測，方向完全一致：`qwen3:4b` 實為 **Qwen3-4B-Thinking-2507**（thinking-only 微調），ollama 模板末段**無條件**注入 `<think>\n`（無 `IsThinkSet` 守衛）；`think:false` 只是把思考鏈併回 `response`，**沒有關閉思考**。`num_predict=400` 之下 **100% 的回應 `done_reason='length'`**，`response` 全是「首先，問題是關於…」的推理獨白，答案根本沒生出來。拉到 1500 仍未收斂；一鏡拉到 2000 才看到 `</think>`。
→ **0.492 / 0.567 / 0.521 全部是「思考鏈前 400 token vs 金標」的字組重疊率。**

修法三選一，取鏡三**已實測**者為主：
1. **（主）`format=<JSON schema>` grammar-constrained decoding**：實測 `done_reason='stop'`、**94 token**（對比 400 全截斷）、輸出格式與 gold 模板逐字一致。單行改動、零訓練、推論快 4.3×。
2. （備）只對 `</think>` 之後計分 + `num_predict ≥ 2000` + stop token。
3. （備）改用 `/api/chat` 讓 thinking 分流到 `thinking` 欄。

**注意**：鏡三報「grammar 分數 0.682 vs 現行 0.664」——這個**分數差不得引用為證據**（0.682 仍在地板 0.67–0.73 區間內）。真正的收穫是 `done_reason` 由 `length` 變 `stop`：**評的東西從推理前言變成答案。**

### C8　樣板地板 > 現役冠軍
**裁決：CONFIRMED，本專案目前最強的實證結論（五個獨立實作 + 本報告親驗，六次複現，方向與量級全部一致）。**
| 來源 | 常數/樣板地板 | 對照現役 |
|---|---|---|
| 本報告親驗（離線） | A 0.671 / B 0.729 | 0.492 |
| 對抗鏡 a（live 實跑） | 0.708（同集 0.680） | live 實測 0.506 |
| 對抗鏡 b（live 實跑） | 0.730 / 0.803 | 0.492 / 0.473 |
| 對抗鏡 c（離線） | 0.685（同集重算確認） | 0.492 |
| 對抗鏡 d（離線） | 0.711（同源他題 gold） | 0.492 |
| 可行性鏡三（live） | 固定 3-gold 0.723/0.782；30-gold 0.820/0.854 | 0.492 |

各鏡以不同方法量得「樣板 key 佔比 59%～82%」——方法不同故數字不同，**但方向一致**。取保守值：**可辨識的事實訊號帶只剩 0.20～0.29 寬，而已知重評漂移 0.05～0.10 佔其 17～50%。**

### C9　事實敏感度
**裁決：0%。CONFIRMED（本報告親驗）。**
`_score` 的 key 集 = CJK 二字組 ∪ `[A-Za-z_][A-Za-z_0-9]{3,}`。**純數字永遠落不進 key**（正則要求字母/底線開頭；CJK 二字組不含數字）。故年份 2021、相關係數 +0.55、374 股、28 萬列——**全部對評分器隱形**。我把 983 條 gold 的每個數字改成 9，中位分仍 **1.000**。
`field_correlation_baseline` 這種「數字本身就是答案」的題，事實全錯也是 1.000。

### C10　「固定 held-out 集」不固定 + 帳本假 provenance
**裁決：CONFIRMED（本報告親驗）。**
`_fixed_eval_set` 用 `ORDER BY md5(prompt) LIMIT 12` 查一個**每晚被 cron 灌大的 pool**（50→127→149→279→511→983）；新樣本 md5 較小即擠掉舊題。現行 `set_hash` = `334086187ab1`，而 DB 四個已評分版本**全部記錄 `44893a73fbfc`**（那只對應 pool=279 的時點）。
→ `search_packs` 印出的「現役 serving 於集 A 之分數 = 0.492（同尺可比）」**是假的**，而那正是呈給 hugo 做晉升決策的對照句。

### C11　`verdict='oracle_pass'` 是假 oracle
**裁決：CONFIRMED（本報告親驗：983 列、1 種相異值）。** `evolve_cycle.py:290` INSERT 寫死。所有 `WHERE verdict='oracle_pass'` 是空操作。**欄位語意詐欺** → 要嘛實作真 oracle 並允許 `oracle_fail` 留檔（P4.E3），要嘛改名 `auto_seeded` 並移除所有暗示已驗證的文案。

### C12　n=12 的統計力
**裁決：兩鏡都對，且不衝突——擴 n 是必要非充分。**
- 鏡 c 以 scipy nct 精算：n=12 之 MDE = **0.109～0.386**；δ=0.05 之 power 僅 0.065～0.253；今日 A/B 差 0.029 的 95%CI = `[-0.109, +0.167]`；宣稱「無實質差異」的 TOST（±0.05）power = **0.000**，要 80% 把握需 n≈203～680。
- 同一鏡也指出**擴題救不了**：全池只有 **3 個模板**，ICC=0.5 時 n=12 有效樣本 4.8、n=150 有效樣本僅 5.9——**題數加 12 倍只換到約 1 個有效樣本**。
- **裁決：真解是三件事同時做——(i) 指標改事實/行為級確定性二元（每題資訊量大增）、(ii) 增加模板多樣性（加入 DECLINE / 消歧義 / 轉 SQL 三類新行為題）、(iii) 才是擴 n。**單獨擴 n 是白花時間。
- 附帶：`--cycle` 路徑的 `n = max(1, len(heldout))` 分母缺陷（逾時被吞後仍用全額分母 → 靜默記 0）+ `ORDER BY sample_id DESC LIMIT 6`（每輪都是**剛生成的**題）→ 一併修。

### C13　「該不該做 LoRA」
**裁決：不該以「LoRA vs pack 誰強」的形式做。應改成本設計的 S0→S1→S2 三段，且 S1 的中止條件可能讓 S2 不必跑。**

理由不是「保守」，是三條獨立的硬論證：

1. **語料論證**（鏡三）：gold 是三個固定 f-string 模板套 DB 欄位組出來的。評分質量的 ~82% 是模板樣板，只有 ~18% 是逐題事實。模板那 82% 已由 grammar-constrained decoding **零訓練免費拿到**（實測 done=stop、94 tok、格式與 gold 逐字一致）。
2. **治權論證**（鏡 b，最鋒利）：剩下那 18% 是**活資料**。把它壓進權重 = 母計畫自己警告的「訓練幻覺——權重記的是過期快照」，且直接抵觸 **#9**（權重回想 ∉ 程式輸出 / DB query / API，正是明文禁止的「記憶」）。更嚴重的是 **#10**：教材模板逐字寫「**依 knowledge_item（收割層 SSOT）**」——當答案來自權重而非讀表時，**這是一句偽造的出處聲明**，無法 trace 回任何 query。prompt-pack 的事實是 few-shot 文本、可逐字回溯到 `sample_id`；LoRA 一旦內化即失去這條溯源鏈。**教材的格式本身在訓練模型宣稱一個它沒讀過的來源。**
3. **可維運論證**（鏡 b）：`knowledge_item` 欄位為 `item_id/domain/entity_type/title/title_zh/year/authors/external_id/venue/url/taxonomy_id/source_key/staging_id/ingested_at`——**沒有 `updated_at`、沒有 `superseded_by`、沒有 `valid_from/valid_to`**。權重內化的事實**無從作廢、無從稽核過期**。涵蓋率 30.67%（兩域）/ 0.327%（全表）且每日在長。回滾成本：prompt-pack = 換 hash（秒級）；LoRA = 重訓。

**但也不是取消 LoRA。** 有一塊 grammar+檢索**確實給不了**的東西：**「該拒答時拒答」與「同鍵多實體時消歧義」是判斷，不是格式。** 檢索路由能處理「檢索空 → 拒答」，但處理不了「檢索**錯誤地**回傳了不相關的列，模型是否識破並拒答」。這塊很窄，但真實存在，而且是 augur 誠實 doctrine 的核心。**那才是 LoRA 在本專案唯一站得住的訓練目標。**

### C14　base 變體混淆
**裁決：採納鏡二/鏡四，強制「同 base 內比較」。**
現役 incumbent = **Qwen3-4B-Thinking-2507**（thinking 微調、被 `think=false` 抑制思考）；擬議 challenger = 標準 **Qwen3-1.7B**（hybrid）。「1.7B+LoRA vs 4B+pack」有**雙重混淆**（模型大小 × thinking 變體）。
→ **LoRA 判決只准由「同一顆 1.7B 的裸 / +grammar / +檢索 / +LoRA」四臂內部宣告。** 跨 base 比較僅作部署選型參考，**明文禁止寫成 LoRA 判決**。

### C15　訓練目標：事實 vs 行為
**裁決：LoRA 訓練目標一律排除事實槽，只訓行為。** 依 C13 的三條論證。
連鎖後果：**現行 983 條 gold 不能直接當訓練語料**——它教的是「斷言一個具體作者+年份」。983 條裡 **DECLINE 例 = 0、負例提問 = 0、「作者未載」= 0**（鏡 b 全量計數）。LoRA 學的是 `p(answer|prompt)`；語料裡不存在「不知道」這個 mode，而「作者永遠查得到」是 100% 一致的統計規律 → 對訓練期沒看過的標題，最大似然行為就是**補一個像樣的作者，外面包一個 SSOT 出處框**——把幻覺升級成「戴著出處徽章的幻覺」，比裸幻覺更難被下游識破。
→ **必須另建行為語料（S2 前置，見 §4.2）。**

### C16　現役 `pp_3ab2` 該不該立刻下架？
**裁決：不。修尺後重測，再由 hugo 決定。**
「現役低於地板 0.179」也是**在壞尺上的讀數**。壞尺上做的第二個決定不會比第一個好。正確處置：S0 修尺 → 用新尺重測全部五個版本 → 帶著新數字給 hugo。**不要在壞尺上做任何新決定，包括下架。**

---

## 3. 為什麼原問法無效（一段話）

原 spike 問句「1.7B+LoRA 是否 ≥ 4B+pack」在**三個獨立的層面**同時失效：
**量尺層**——尺測的是樣板抄寫（地板 0.67–0.80 > 現役 0.492），對事實 0% 敏感，且是純 recall 無 precision（冗長即得分，串接 971 條 gold 得 0.897）；
**觀測層**——被打分的字串是被截斷的思考鏈，不是答案（100% `done_reason=length`）；
**設計層**——評測集隨 cron 漂移、帳本 provenance 為假、n=12 的 MDE 0.109–0.386 大於任何真實效應、跨 base 且跨 thinking 變體雙重混淆、`verdict` 是常數而非 oracle、母計畫定義的「部署工作域金標」與「通用能力錨集」在 DB 與 repo **都不存在**。
→ 任何在此之上的 go/no-go，**PASS 與 FAIL 都是雜訊**。

---

## 4. 重新定義的 spike 設計

### 4.1 (a) 單一問句

> **「把 augur 的作答『行為』——查無時拒答、同鍵多實體時消歧義、無檢索片段時只輸出可執行 SELECT 而不斷言事實——寫進 Qwen3-1.7B 的權重，是否比用 grammar-constrained decoding + 檢索在推論時強制同樣行為，做得更好？」**

三件事必須明說：
- **不問**「LoRA 能不能背下 augur 的事實」——**刻意不測**，因為那違 #9/#10 且不可維運（C13/C15）。
- **不問**「1.7B ≥ 4B」——雙重混淆，本 spike 明文拒答（C14）。
- **虛無假設是「不能」**：grammar+檢索零訓練、零過期風險、零出處偽造風險、回滾秒級。LoRA 必須顯著勝出才值得。

附屬工程閘（無論主問句結論為何都要答）：**PEFT → GGUF → ollama ADAPTER 端到端是否可通，且 Q4_K_M 量化是否吃掉增益。**

### 4.2 (b) 技術路徑

#### 前置安裝清單（精確）

已在 venv、**不需再裝**：`bitsandbytes 0.50.0`、`gguf 0.19.0`、`peft 0.19.1`、`trl 1.9.0`、`transformers 5.12.1`、`torch 2.12.1+cu126`、`accelerate`、`datasets`、`scipy 1.18.0`。

須新增（共三項）：

```bash
# ① llama.cpp 轉檔腳本（只取腳本，絕不跑它的 requirements——會把 venv 的
#    torch/transformers/numpy 拖回舊版並拖壞 peft/trl/dspy）
git clone --depth 1 https://github.com/ggml-org/llama.cpp ~/llama.cpp
# 驗證腳本在：
ls ~/llama.cpp/convert_lora_to_gguf.py ~/llama.cpp/conversion/qwen.py

# ② llama.cpp release binaries（取 llama-quantize / llama-cli，約 16MB，免編譯）
#    版本號取執行當下的最新 release，寫進帳本
gh release list -R ggml-org/llama.cpp -L 1
# 例：curl -L -o /tmp/lcpp.tgz https://github.com/ggml-org/llama.cpp/releases/download/<TAG>/llama-<TAG>-bin-ubuntu-x64.tar.gz
#     tar -xzf /tmp/lcpp.tgz -C ~/llama.cpp-bin/

# ③ HF base 權重（ollama 的 GGUF 是 Q4_K_M，不能當 PEFT 訓練 base）
export HF_TOKEN=...   # 避免匿名限流；兩鏡皆遇下載停滯
/home/hugo/project/augur/venv/bin/hf download Qwen/Qwen3-1.7B \
  --local-dir ~/models/Qwen3-1.7B
# 約 3.4 GB safetensors（兩鏡分報 3.80 / 4.08 GiB 含非權重檔）；
# 磁碟 714GB free、RAM 17GB available 皆無壓力。下載完校驗 sha 再算 spike 起算點。
```

**若 `convert_lora_to_gguf.py` 因 transformers 5.x API 漂移而失敗**：另開 `~/venvs/gguf-convert` 獨立 venv 裝釘版（+1.5GB 磁碟），**絕不動 augur venv**。

#### 訓練前的環境硬閘（寫進腳本開頭，不是註解）

```python
# 1) 卸載 ollama 模型（可逆、免 root、四個 augur 服務不受影響——已實測）
requests.post("http://127.0.0.1:11434/api/generate",
              json={"model": "qwen3:4b", "keep_alive": 0})
time.sleep(5)
# 2) VRAM 硬閘：不足即 abort，不硬擠（WSL2 有 host fallback，不會 OOM 只會慢 3.7×）
free, total = torch.cuda.mem_get_info()
assert free / 2**20 >= 3000, f"free VRAM {free/2**20:.0f} MiB < 3000，abort（記 env 事件，非 LoRA 判決）"
# 3) 記錄併發狀態當 provenance（任何時間數字沒有這個就不可複現）
subprocess.run(["nvidia-smi","--query-gpu=memory.free","--format=csv,noheader"])
subprocess.run(["ollama","ps"])
```

#### 行為語料構造（**這是 S2 的真正前置，不是現有 983 條**）

現有 gold 教「斷言事實」，不能用。新建 `local_model_behavior_sample`，四類，事實一律留在 prompt 或留在 DB：

| 類 | 標籤 | prompt | gold（行為） | 產生方式 |
|---|---|---|---|---|
| B1 | `CITE_GIVEN` | 題目 **+ 已檢索到的 SSOT 列（逐字）** | 逐字採用該列事實 + 明標表名 | 由現有 983 條反向構造：把 gold 的事實槽移進 prompt |
| B2 | `DECLINE` | 一個機械確認 DB **查無**之鍵 | 「knowledge_item 查無此鍵，請 `SELECT ...` 確認」 | 真實標題詞素重組 + `NOT EXISTS` 確認（鏡 b 的 SQL 已在 live 驗證可產） |
| B3 | `DISAMBIGUATE` | 同 `left(title,80)` 對應多組 (作者,年份) | 消歧義 / 指回查詢，**任何單一斷言判 FAIL** | 全庫 2,758 群、兩域 73 群（鏡 b 實查） |
| B4 | `TO_SQL` | 問事實但**不給**檢索片段 | 輸出可執行 `SELECT`，**不斷言任何事實** | 由現有 983 條之 prompt 改配新 gold |

配額：B1 300 / B2 250 / B3 150 / B4 250 ≈ **950 條**（與現有語料規模同量級，訓練時間可沿用鏡一的實測外推）。
**訓練集 = 全部行為語料扣掉評測集所屬 `sample_id`**；洩漏防護做在**樣本粒度**而非來源粒度（整源排除會讓訓練集塌到 127 條 → 保證學不到，鏡 d 的正確反駁）。訓練 `sample_id` 清單之 sha256 寫入 `local_model_version.train_sample_manifest_hash`，評測端 `assert` 交集為空。

#### QLoRA 超參（含依據）

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=DTYPE,      # ← S2c bake-off 決定：bf16 / fp32 / fp16
)
LoraConfig(
    r=32, lora_alpha=64, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
)   # QLoRA(Dettmers et al., NeurIPS 2023)：LoRA 須掛全 linear 才能追平 full-FT；
    # r=32 而非 64——950 條規模用 64 易純記憶
SFTConfig(
    max_length=320, packing=False, group_by_length=True,
    per_device_train_batch_size=4, gradient_accumulation_steps=4,   # 有效 16
    gradient_checkpointing=True, optim="adamw_8bit",                # 省 100 MiB vs adamw_torch
    learning_rate=2e-4, lr_scheduler_type="cosine",
    warmup_ratio=0.03, weight_decay=0.0,
    assistant_only_loss=True,                                       # ← 關鍵，見下
    num_train_epochs=10, save_strategy="epoch",                     # checkpoint 取 3/6/10
)
```

**四個「照預設就會被誤記成 LoRA 無效」的陷阱（全部設成硬 assert）**：

```python
# ① TRL 預設不遮 prompt。實測 answer/full token 比 = 64.9%，35.1% 梯度會花在
#    三個固定模板問句上 → 模型學會「生問題」。
assert cfg.assistant_only_loss is True
#    並抽驗一個 batch：labels 中 -100 佔比須落在 30–40%
# ② pad == eos 會遮掉真 EOS → 模型永遠學不會停 → 一路撞 num_predict 上限。
#    Qwen3 原生 eos=<|im_end|>(151645) ≠ pad=<|endoftext|>(151643) —— 不要覆寫。
assert tok.pad_token_id != tok.eos_token_id
#    抽驗：每條 labels 最後一個非 -100 的位置須是 151645
# ③ train/serve chat template 逐字不同：
#    HF apply_chat_template(enable_thinking=False) → '<|im_start|>assistant\n<think>\n\n</think>\n\n'（已閉合）
#    ollama qwen3 TEMPLATE                        → '<|im_start|>assistant\n<think>\n'（未閉合）
#    LoRA 學到的觸發語境在服務端從不出現 → 增益必然歸零。
#    → 以「服務端模板」為 SSOT 渲染訓練資料；訓練端與評測端各算一次 prompt 前綴 byte-hash，
#      不相等即 fail-loud 中止；hash 寫進 spike 報告當「同格式」證據。
assert sha256(train_prefix) == sha256(serve_prefix)
# ④ fp16 + LoRA 的典型失敗是靜默 NaN（外觀 = 分數沒動 = 被誤記成 LoRA 無效）
assert torch.isfinite(loss)   # 每步
```

#### 訓練與回灌指令

```bash
# 訓練（S2d）
/home/hugo/project/augur/venv/bin/python scripts/train_local_lora.py \
  --base ~/models/Qwen3-1.7B \
  --corpus-table local_model_behavior_sample \
  --dtype bf16 --r 32 --alpha 64 --max-length 320 \
  --epochs 10 --save-epochs 3,6,10 \
  --out ~/models/lora/augur-behavior-<ver>

# 轉檔（S2a 已綠燈後）
/home/hugo/project/augur/venv/bin/python ~/llama.cpp/convert_lora_to_gguf.py \
  ~/models/lora/augur-behavior-<ver> \
  --base ~/models/Qwen3-1.7B --outtype f16 \
  --outfile ~/models/lora/augur-behavior-<ver>.gguf
# ↑ --base 明指本地目錄，避免走網路抓 config

# 掛載（路 a：日常迭代，adapter ~66MB f16，base blob 共用不重複佔碟）
printf 'FROM qwen3-1.7b-base\nADAPTER ~/models/lora/augur-behavior-<ver>.gguf\n' > /tmp/Modelfile
ollama create augur-1.7b-lora-<ver> -f /tmp/Modelfile
# 回滾 = ollama rm augur-1.7b-lora-<ver>（秒級）

# 量化偏移三路對照（S2f）：
#   H = HF fp16 base + PEFT（未量化參考真值）
#   Q8 = merge → F16 GGUF → llama-quantize Q8_0
#   Q4 = ollama Q4_K_M base + ADAPTER（生產路）
# 增益在 Q8 在、Q4 不在 → 結論寫「量化吃掉增益」，不寫「LoRA 無效」
```

**磁碟預算**（路 b 定版用）：HF base 3.4 + merged 3.4 + F16 GGUF 3.4 + Q4_K_M 1.1 ≈ **11.3 GB**（714 GB free，無壓力）。merge 需把 1.7B 全載入 CPU（~3.4 GB），17 GB available 可行，但**不要與 `pg_dump` 或大查詢同時跑**（#30 鎖風暴教訓）。

### 4.3 (c) 修好的評測

#### 病灶 → 對策對照

| 病 | 現況（親驗） | 對策 |
|---|---|---|
| 樣板地板 | 常數字串 0.671/0.729 > 現役 0.492 | 主指標改**確定性 0/1**；每輪**強制內建**常數地板臂與 shuffled-control 臂，候選不顯著勝出即自動 NO-GO |
| 事實 0% 敏感 | 數字全竄改仍 1.000 | 新增 **F 軸 exact-match**（數值/年份/表名/欄名逐字比對），與其他軸**永不平均** |
| 純 recall 無 precision | 串接 971 條 gold 得 0.897 | 覆蓋率若保留只作參考軸，改 **F1**；主判決不用它 |
| 評的是思考鏈 | 100% `done_reason=length` | `format=<JSON schema>` grammar 強制（實測 94 tok / `done=stop`）；仍截斷之題判 **INVALID 不計分** |
| 集會漂移 | 現行 `334086187ab1` vs 帳本 `44893a73fbfc` | 實體化凍結表；跨版本比較前 `assert set_id` 與 `eval_code_hash` 相同，不同即 fail-loud 拒絕比較 |
| 假 oracle | `verdict` 983/983 單值 | 改名 `auto_seeded` 並移除所有暗示已驗證之 WHERE 與文案 |
| n=12 無檢定力 | MDE 0.109–0.386 | n=120 + 二元指標 + 配對 McNemar + R=3 |
| 3 模板 ICC | n=150 有效 n 僅 5.9 | 加 B2/B3/B4 三類**新行為模板** → 模板多樣性由 3 → 7 |
| 逾時靜默記 0 | `n = max(1, len(heldout))` | 分母改實際成功題數；**任一題逾時即整輪 INVALID，不寫分數**；timeout 150→600s |
| 三 hash 鎖空轉 | `anchor_hash`/`eval_code_hash` 五版全 NULL | 寫版本列時**強制填**，NULL 即拒絕寫入 |

#### 三軸評分（永不平均，分開報）

| 軸 | 定義 | 適用層 | 判準 |
|---|---|---|---|
| **F** `fact_exact` | 答案中的數值/年份/表名/欄名須與 prompt 內檢索片段**逐字相符** | L1 | 0/1 |
| **P** `provenance_ok` | regex：引了正確 SSOT 表名 **且** 附可執行 `SELECT` | L1/L2 | 0/1 |
| **A** `abstain_ok` | L3 須無任何具體事實斷言；L4 須消歧義而非單一斷言 | L3/L4 | 0/1 |
| （參考）`coverage_f1` | 現行覆蓋率改 F1 | 全層 | 僅記錄，**不入判決** |

**F 軸只在「檢索片段已在 prompt」的題上算。** 沒給片段還要求答對事實 = 在測記憶 = 違 #9 → 那類題（L2）的正確行為是輸出 SELECT，由 P 軸裁。

#### 凍結評測集（實體化，共 150 題）

| 層 | n | 內容 | 正確行為 | 判軸 |
|---|---|---|---|---|
| **L1_RETRIEVED** | 30（KI/CC/FC 各 10） | 題目 + SSOT 列已在 prompt | 逐字採用 + 引表名 | F, P |
| **L2_NO_RETRIEVAL** | 30（同上但不給片段） | — | 輸出 SELECT，不斷言 | P |
| **L3_ABSENT** | 30（合成鍵，`NOT EXISTS` 機械確認） | — | DECLINE | A |
| **L4_AMBIG** | 30（同 title 多實體，73 群母體） | — | 消歧義 | A |
| **L5_ANCHOR** | 30（公開 benchmark 子集，零 AI 生成） | 通用能力 | 不退步 | 該 benchmark 自身判準 |

母體足夠：FC 60 / CC 67 → L1+L2 各取 10+10=20，剩 40/47 給訓練。**L1–L4 = 120 題為判決集；L5 = 30 題為錨集。**

#### 對照臂矩陣

| 臂 | 組態 | R | 用途 |
|---|---|---|---|
| **A0** | 常數字串（question-blind） | — | **樣板地板**，離線零成本，**必跑** |
| **A1** | 同源他題 gold 當答案 | — | shuffled control，離線零成本，**必跑** |
| **A2** | Qwen3-1.7B 裸 | 1 | base floor |
| **A3** | 1.7B + grammar | 1 | 格式強制，零訓練 |
| **A4** | 1.7B + grammar + **真檢索** | **3** | **S1 產物 = LoRA 要打敗的對象** |
| **A5** | 1.7B + LoRA（裸） | **3** | 權重是否承載行為 |
| **A6** | 1.7B + LoRA + 檢索 | **3** | 真實部署組態 |
| **A7** | qwen3:4b + 現役 pack | 1 | 跨 base 參考，**明文禁止用於 LoRA 判決** |

**呼叫預算**：A4/A5/A6 × 120 × 3 = 1080；A2/A3/A7 × 120 × 1 = 360；L5 錨集 A2/A5 × 30 × 3 = 180。**合計 1620 次本地呼叫，零 Claude token（#28）**。grammar 路實測 94 tok/`done=stop`，估均值 12–20 s/呼叫 → **5.4–9 小時 → 過夜**。

#### 檢索路由（A4/A6 用）

鏡三實測兩種路由在全 983 條上**皆 100% 準確**：3 行 regex（`'相關結構'` / `'語意陷阱'|'型別'` / 其餘），或 e5-small top-1（本機已快取，983 條 CPU 嵌入 18.1 秒）。**取 regex**（更簡、可審計、零模型依賴），e5-small 作備援。
**誠實限定**：鏡三的「grammar+RAG 6/6 = 1.000」用的是 **oracle retrieval（把 gold 本身餵進去）= 上界**。生產版須真的從 `knowledge_item`/`column_catalog`/`field_correlation` 撈列，且**必須獨立量測檢索命中率**——殘餘風險從生成錯誤轉移到檢索錯誤，不是消失。

#### 解碼一致性（全臂共用，寫進 `eval_code_hash`）

`temperature=0, top_k=1, seed=<固定>, num_ctx=<固定>, num_predict=<固定>, format=<schema>`。
理由：實測 `temp=0` **並非決定性**（同 prompt ×3 → 兩種輸出；ollama 預設 `top_k=20/top_p=0.95` 而現行程式只覆寫 temperature、未設 seed）。每次輸出的 byte hash、題內 SD、截斷率一併寫入 `local_model_eval_run`。任一環境指紋（model digest / num_ctx / num_predict / seed / decode params）變動即標記不可比。

### 4.4 (d) 預註冊 go/no-go（跑之前寫入 DB 並 commit，事後不得修改）

> **必須在 S2d 訓練開跑前，把本節逐字寫入 `local_model_version.gate_id` 對應的 gate 列並 commit。hugo 簽核後凍結。**（抗事後美化的唯一機制）

**主指標**：L2 / L3 / L4 三層**各自**的配對二元命中率（P 軸、A 軸、A 軸），對照臂 = **A4**（grammar+檢索，零訓練）。
**檢定**：配對 McNemar，α=0.05 雙尾；每層 n=30，R=3 取多數決。
**MDE 誠實揭露**：n=30/層、discordant ~20% 之下，MDE ≈ **15–20 pp**。5 pp 級的差異本設計**測不出來，也不會宣稱測得出來**。

#### GO（LoRA 值得續做）——須**全部**滿足

1. **權重鏈綠燈**：PEFT → `convert_lora_to_gguf` → `ollama ADAPTER` 成功，且擾動 adapter 使輸出改變（雙向對照，非單向「跑起來了」）。
2. **正控制通過**：32 條 × 30 epochs，訓練集**逐字回吐率 ≥ 0.95** 且 train loss < 0.1。
3. **勝地板**：A5 在 L2/L3/L4 **各層**均顯著勝 A0（常數地板）與 A1（shuffled control）。
4. **勝零訓練對照**：A5 **或** A6 在 L2/L3/L4 **至少兩層**的配對命中率 ≥ A4 + **0.15**，且 McNemar 95%CI 下界 > 0。
5. **錨集不退步**：L5 上 A5 的 bootstrap CI 下界 ≥ A2 − δ，δ = **同版本重測 k=5 的實測 SD**（不是拍腦袋的 0）。
6. **不犧牲事實採用**：L1 的 F 軸，A5 不得低於 A4 超過 0.05。
7. **量化存活**：Q8_0 與 Q4_K_M 兩路的差距落在噪音帶內；若 Q8 在而 Q4 不在 → 結論寫「量化吃掉增益」，路 b（merge 後量化）定版，**不寫「LoRA 無效」**。
8. **可重複**：同一候選在同一凍結集**獨立重評 2 次，兩次結論一致**。

#### NO-GO / INVALID（任一觸發即停，不得寫入判決）

- A0 常數地板 **≥** 任一 LoRA 臂
- `set_id` 與凍結表不符，或 `eval_code_hash` 與基線不符
- 任一題逾時，或任一題 `done_reason='length'`
- R < 3，或任一層有效 n < 25
- 環境指紋（model digest / num_ctx / num_predict / seed / decode params）與基線不符
- **正控制不過** → 判定「**訓練管線壞**」，**明文不判「LoRA 無效」**
- 訓練期 NaN / OOM / HF 下載停滯 → 記為 **env 事件**（append-only 帳本），**不計入 LoRA 判決**
- prompt 前綴 byte-hash 訓練端 ≠ 評測端

#### 判定三態

**PASS / FAIL / INDETERMINATE。禁用「無實質差異」「效果不顯著故無效」等接受虛無之措辭**（n 小時那是測不出來，不是沒差異）。每次輸出**必附當前 MDE 與 95%CI**。

#### 停損條款（改寫母計畫原文）

母計畫「兩輪無增益 → 停損」**加前提**：僅在「正控制通過 + 格式 hash 相等 + 三軸評分器就位 + 對照臂矩陣齊全 + 凍結集 hash 相符」五項全滿足時，那兩輪才算數。否則那兩輪是 INVALID，不計入停損計數。

### 4.5 (e) 分階段、耗時、中止條件

| 階段 | 內容 | 估時 | **中止條件（什麼情況停手別浪費時間）** |
|---|---|---|---|
| **S0.1** | 修 harness thinking（`format=JSON schema` 主 / `</think>` 切分備）| 2h | 無（bug 修復，必做） |
| **S0.2** | `_score` 三軸重寫；常數地板 + shuffled control **內建為必跑臂**；`_selftest` 加負控紅線（三個假模型須 < 0.3） | 3h | 無 |
| **S0.3** | 評測集實體化凍結（`local_model_eval_set`）；`set_id`/`eval_code_hash`/`anchor_hash` 回填強制；移除 `ORDER BY md5(prompt) LIMIT n` 與 `ORDER BY sample_id DESC LIMIT 6`；修逾時分母 | 3h | 無 |
| **S0.4** | 五層判別集產生（L1–L5；L3/L4 的 SQL 已在 live 驗證可產） | 4h | L5 通用能力錨集若找不到零-AI-生成之公開來源 → **改為只做 L1–L4，並在報告明寫「通用能力退步未測」** |
| **S0.5** | 舊五個版本分數加註記作廢（P4.E3 不刪）；用新尺重測全部五版 | 3h | — |
| **↑ S0 小計** | **≈ 1.5 天，零 GPU，零 Claude token** | | **S0 完成後即應向 hugo 回報一次**（見人閘 1） |
| **S1.1** | grammar-constrained decoding 上線 | 1h | 無 |
| **S1.2** | 真檢索路由（regex）+ 撈 SSOT 列注入 prompt + **獨立量測檢索命中率** | 3h | 檢索命中率 < 0.85 → 先修檢索，不進 S1.3 |
| **S1.3** | A0/A1/A2/A3/A4/A7 全臂評測（約 480 呼叫，2–3h） | 3h | — |
| **↑ S1 小計** | **≈ 0.5–1 天，零訓練** | | **★ 關鍵中止：若 A4 在 L1–L4 四層的行為軸命中率均 ≥ 0.90 → S2 不跑。** 剩餘空間 < MDE(15–20pp)，LoRA 無可宣稱增益。**這一條可能讓整個 spike 在一天半內結案。** |
| **S2a** | clone llama.cpp + 下載 Qwen3-1.7B + **玩具 adapter（r=4、1 step）走完 convert → ollama create → 輸出改變** | 4h（含下載） | **時間盒 4h。** convert 失敗且獨立 venv 也修不好 → 停，寫「鏈路不通」報告，**不投入任何訓練時間** |
| **S2b** | **正控制**：32 條 × 30 epochs，逐字回吐 ≥ 0.95 | 1h GPU | **時間盒 3h。** 不過 → 停，判「管線壞」，**明文不判 LoRA 無效**。這一步順帶把 fp16/NaN、EOS、模板三件事一次驗完 |
| **S2c** | dtype/VRAM bake-off：bf16/fp32/fp16 × 20 steps | 1h GPU | 三者皆 peak > 3300 MiB 或 > 8 s/step → 降 seq(320→192) 或 r(32→16) 一次；仍不行則停 |
| **S2d** | 行為語料構造 + 正式訓練（~950 條 × 10 epochs，checkpoint 3/6/10） | 語料 4h + 訓練 **3–6h**（過夜） | 單步 > 8s、peak > 3400 MiB、或 loss NaN → 停並記 env 事件 |
| **S2e** | 判決評測 A5/A6 × 120 × R3 + 錨集（約 1260 呼叫） | **5–9h**（過夜） | 任一 NO-GO 條件觸發即停 |
| **S2f** | 量化三路對照（H / Q8_0 / Q4_K_M） | 2h | — |
| **↑ S2 小計** | **≈ 1.5–2 天 + 兩夜** | | |

**訓練時間估算之依據與誠實限制**：鏡一在真 28 層 Qwen3-1.7B 上實測 seq256/bf16 = **2.147 s/step**（batch=1 固定長），983×3 epochs = 106 分。本設計用 dynamic padding（mean 107.5 tok « 320）+ batch=4，實際應更快，但**未實測** → 記為估算，S2c bake-off 的 20 步實測值須回填取代（#9：估算不得入帳本）。

**兩鏡的 CPU 路估算（4B 17.3h、1.7B 7.4h）本設計不採**——鏡三實測 GPU/CPU = **5.7×**（真 transformer 訓練步：CPU 1.082 s/step / 167 GFLOPS vs GPU 189 ms/step / 957 GFLOPS），且 CPU 只能 fp32（Ryzen 5 3600 = Zen2、無 AVX-512/AMX，fp16/bf16 矩陣乘實測 **慢 347 倍**）。**CPU 路被 GPU 嚴格支配，母計畫 Tier 2(a) 應刪除。**

### 4.6 (f) 需要 hugo 人閘的點

| # | 事項 | 為何是人閘 | 何時 |
|---|---|---|---|
| 1 | **把五個既有版本分數宣告作廢/加註記；把 Tier 2 從路線圖降級為「條件性」** | 屬**判準變更**（#26 明線：改正確屬執行層、變更判準屬決策層） | S0.5 完成時 |
| 2 | **預註冊 go/no-go 凍結簽核** | 這是抗事後美化的錨；AI 自訂自改 = 錨失效 | S2d 開跑前 |
| 3 | **過夜 GPU 訓練（S2d）與過夜評測（S2e）** | #22：WSL2/Windows 主機睡眠 AI 擋不住，須用戶確認電源設定；且須確認 01:30 演化鏈 cron 不與訓練窗撞（GPU 競用會讓時間數字失真 3.7×） | S2d/S2e 前 |
| 4 | **模型卸載窗告知** | `ollama stop qwen3:4b` 期間 advisor/chat 首次請求會慢（自動重載）；四個服務**不會停**（已實測）→ **只需告知，不需授權** | S2c 起 |
| 5 | **晉升 serving** | `promoted_by` 唯 hugo 親跑寫入。**AI 絕不代打**（2026-07-25 已犯過一次） | 若 GO |
| 6 | **S1 中止條件觸發後的分岔** | 若 A4 ≥ 0.90 四層，是否仍要跑 S2 = 資源配置決策 | S1.3 後 |
| 7 | **母計畫 §11 / §26 前提更正**（bnb 已裝、4B GPU no-go、bf16 非原生但實測較快、CPU 路刪除、成敗判準改寫） | 純文字更正屬 #26 執行層，但因**涉及成敗判準與停損條款改寫** → 人閘 | S0 期間 |
| 8 | **`local_model_gold_sample.verdict` 改名 `auto_seeded`** | 欄位語意變更 + 影響既有查詢 | S0.3 |

**不需要人閘者**（依 #26「改正確/補完整」屬執行層）：修 harness thinking、修 `_score`、修逾時分母、凍結評測集、填三 hash、內建地板臂、建行為語料表、裝 llama.cpp、下載 HF 權重。

### 4.7 表 schema 與程式規畫（#20 v1.39.0 雙落實）

> **執行前須先 `\d local_model_version` / `\d local_model_gold_sample` 實查現有欄位再定案**——以下為計畫值，不是已驗證的現況。

#### 新表 DDL

```sql
-- 凍結評測集（取代 ORDER BY md5(prompt) LIMIT n）
CREATE TABLE local_model_eval_set (
    set_id        TEXT NOT NULL,               -- 如 'L1_RETRIEVED@20260726'
    layer         TEXT NOT NULL,               -- L1_RETRIEVED|L2_NO_RETRIEVAL|L3_ABSENT|L4_AMBIG|L5_ANCHOR
    ordinal       INT  NOT NULL,
    sample_id     BIGINT,                      -- 指向 gold/behavior 表；合成題為 NULL
    prompt        TEXT NOT NULL,
    expect_kind   TEXT NOT NULL,               -- cite_given|to_sql|decline|disambiguate|anchor
    expect_facts  JSONB,                       -- F 軸：須逐字命中之數值/年份/表名/欄名
    expect_regex  TEXT,                        -- P/A 軸：確定性判準
    frozen_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (set_id, layer, ordinal)
);
CREATE INDEX ON local_model_eval_set (layer);

-- 逐題留痕（每次呼叫一列；append-only，P4.E3）
CREATE TABLE local_model_eval_run (
    run_id        TEXT NOT NULL,
    arm           TEXT NOT NULL,               -- A0..A7
    set_id        TEXT NOT NULL,
    layer         TEXT NOT NULL,
    ordinal       INT  NOT NULL,
    rep           INT  NOT NULL,               -- 1..R
    answer        TEXT,
    answer_sha    TEXT,                        -- byte hash，決定性稽核
    done_reason   TEXT,                        -- 'length' 即 INVALID
    eval_count    INT,
    latency_ms    INT,
    fact_exact    BOOLEAN,
    provenance_ok BOOLEAN,
    abstain_ok    BOOLEAN,
    coverage_f1   NUMERIC,                     -- 參考軸，不入判決
    env_digest    JSONB NOT NULL,              -- model digest/num_ctx/num_predict/seed/decode/gpu_free/ollama_ps
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, arm, set_id, layer, ordinal, rep)
);

-- 行為訓練語料（事實一律留在 prompt 或留在 DB）
CREATE TABLE local_model_behavior_sample (
    sample_id     BIGSERIAL PRIMARY KEY,
    behavior      TEXT NOT NULL
        CHECK (behavior IN ('cite_given','decline','disambiguate','to_sql')),
    prompt        TEXT NOT NULL,
    gold_answer   TEXT NOT NULL,
    contains_fact_assertion BOOLEAN NOT NULL DEFAULT FALSE,   -- 機械閘：只有 cite_given 可為 TRUE
    provenance    JSONB NOT NULL,               -- 產生所依 SQL 與來源列鍵（#10 溯源）
    split         TEXT NOT NULL DEFAULT 'train' -- train|eval（insert 當下寫死，不由查詢時排序決定）
        CHECK (split IN ('train','eval')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 機械閘：非 cite_given 者不得含事實斷言
ALTER TABLE local_model_behavior_sample ADD CONSTRAINT chk_no_fact_leak
  CHECK (behavior = 'cite_given' OR contains_fact_assertion = FALSE);

-- 既有表補欄（NULL 即拒絕寫入之硬閘由 writer code 執行）
ALTER TABLE local_model_version
  ADD COLUMN IF NOT EXISTS eval_invalidated_note TEXT,        -- 作廢註記，不刪列（P4.E3）
  ADD COLUMN IF NOT EXISTS contains_fact_internalization BOOLEAN DEFAULT FALSE,  -- 溯源鏈是否已離開 DB（#10 人閘辨識）
  ADD COLUMN IF NOT EXISTS eval_set_id TEXT,
  ADD COLUMN IF NOT EXISTS gate_preregistered_at TIMESTAMPTZ;
```

#### 所讀既有表 schema（純消費，不改）

`local_model_gold_sample`（sample_id, prompt, gold_answer, verdict, teacher, trigger_event, contains_private, is_synthetic, provenance, created_at）、`local_model_version`、`knowledge_item`、`column_catalog`、`field_correlation`。
**前置債（本 spike 不修，但須記錄）**：`knowledge_item` **無 `updated_at` / `superseded_by` / `valid_from` / `valid_to`** → 權重內化之事實無從作廢、無從稽核過期。**在此債未償前，任何「把事實進權重」的路線不可維運**（這也是 §4.1 把訓練目標限定為行為的技術理由之一）。

#### Python 程式規畫（每支須含執行指令矩陣 + `--selftest`，#18/#29 v1.30 向前生效義務）

| 檔 | 角色 | 主要函式（簽名） | 輸入表 | 輸出表 |
|---|---|---|---|---|
| `scripts/migrate_lora_spike_ddl.py` | 建表/遷移（冪等） | `main(dry_run: bool) -> int` | — | 上述四段 DDL |
| `scripts/freeze_eval_set.py` | 抽樣 + 凍結 + 釘 hash | `freeze(layer: str, n: int, seed: int) -> str  # set_id` | gold / behavior / knowledge_item / column_catalog / field_correlation | `local_model_eval_set` |
| `scripts/build_behavior_corpus.py` | 四類行為語料構造（B1–B4） | `build_decline(cur, n) -> list`, `build_disambiguate(cur, n) -> list`, `build_cite_given(cur, n) -> list`, `build_to_sql(cur, n) -> list` | knowledge_item / column_catalog / field_correlation / gold | `local_model_behavior_sample` |
| `scripts/score_behavior.py` | 三軸確定性評分（library，可 `-m` 自測） | `fact_exact(ans, expect: dict) -> bool`, `provenance_ok(ans, rx) -> bool`, `abstain_ok(ans, kind) -> bool` | — | — |
| `scripts/eval_model_arms.py` | 多臂評測編排（含 A0/A1 離線臂） | `run_arm(arm: str, set_id: str, reps: int) -> dict`, `mcnemar(a: list, b: list) -> tuple` | `local_model_eval_set` | `local_model_eval_run` |
| `scripts/train_local_lora.py` | QLoRA 訓練（含四個硬 assert） | `train(base, corpus, dtype, r, epochs, out) -> dict` | `local_model_behavior_sample` | 檔案系統 adapter + `local_model_version` |
| `scripts/convert_lora_to_ollama.py` | PEFT → GGUF → `ollama create` 編排 | `convert(adapter_dir, base_dir, out_gguf) -> str`, `create_tag(gguf, tag) -> str` | — | ollama registry |
| `scripts/prereg_gate.py` | 預註冊判準寫入 + 凍結 + 事後比對 | `register(gate: dict) -> str`, `assert_unchanged(gate_id) -> None` | — | `local_model_version.gate_id` |
| （修改）`scripts/evolve_cycle.py` | harness 修（grammar / 分母 / 凍結集 / 三 hash 強制填） | — | — | — |

稽核：`python3 scripts/check_cmd_matrix.py` 須通過（新增 script 於首次提交當下即須含矩陣，#29(d)）。

---

## 5. 誠實天花板聲明

### 這個 spike **能**回答

1. 權重鏈 PEFT → `convert_lora_to_gguf` → GGUF → ollama `ADAPTER` **是否端到端可通**（二元、確定性）。
2. 本機 GTX 1650 上 Qwen3-1.7B QLoRA 的**實測** s/step、peak VRAM、訓練 wall-clock、最佳 compute dtype。
3. 在**修好的尺**上，LoRA 裸權重在「拒答 / 消歧義 / 轉 SQL」三種行為上，相對 grammar+檢索的**配對差異，MDE ≈ 15–20 pp**。
4. Q4_K_M 量化是否吃掉增益（三路對照 H / Q8_0 / Q4_K_M）。
5. 訓練管線本身是否健全（正控制 = 32 條逐字回吐）。
6. 一個副產物，且可能是本 spike 最有價值的產物：**一把能用的尺**——即使 S2 從沒跑，S0+S1 也把「零知識地板 > 現役冠軍」「事實 0% 敏感」「評測集漂移」「帳本 provenance 為假」四個洞補起來了。

### 這個 spike **不能**回答（明文拒答，不得外推）

1. **「LoRA 對 augur 整體是否值得」**——只測一顆 1.7B、只測四類行為、判決集 120 題、模板多樣性 7。
2. **「4B 或 8B 上 LoRA 會怎樣」**——4B GPU 判 no-go（實測 NF4 base 2548 MiB + activations ≈ 3.7–4.0 GB > 卸載後 free 3296 MiB）；CPU 路 17h 未測且被 GPU 5.7× 支配。
3. **「窄任務特化 1.7B ≥ 通用 4B」**——跨 base 且跨 thinking 變體（incumbent 是 Qwen3-4B-**Thinking**-2507），**雙重混淆，本設計明文拒答**。A7 臂只是參考，不入判決。
4. **「LoRA 能不能背下 augur 的事實」**——**刻意不測**。不是測不了，是不該測：權重回想 ∉ (a)程式輸出 /(b)DB query /(c)API，正是 #9 明文禁止的「記憶」；而教材模板逐字宣稱「依 knowledge_item（收割層 SSOT）」→ 那是**偽造的出處聲明**，違 #10。
5. **長期維運價值**——`knowledge_item` 無 `updated_at`/`superseded_by`，權重內事實無從作廢；此債未償前不可維運。
6. **通用能力是否退步的廣義結論**——L5 錨集僅 30 題，只能偵測**大幅**退步；若找不到零-AI-生成之公開來源則此軸完全未測，須明寫。
7. **生產檢索命中率**——鏡三的「6/6 = 1.000」用的是 **oracle retrieval（把 gold 本身餵進去）= 上界**，不是實績。

### 本報告自身之限制（一併揭露）

- 我親驗的部分是**離線確定性計算**（`_score` 的數學性質、DB 計數、hash），可完全複現、無生成雜訊。
- 所有涉及 LLM 呼叫的數字（0.492 / 0.567 / live 地板 0.68–0.80 / 12s 每呼叫）**全部來自各鏡的單次或少次量測，未達 #11 的 ≥3 次要求** → 進入 S0 後須全部重測。本報告引用它們是為了**方向**（六次獨立複現、方向一致），不是為了**點值**。
- 訓練 wall-clock（3–6h）是由鏡一 batch=1/seq256 實測外推，**未實測 dynamic padding + batch=4 的實際值** → 屬估算，S2c 的 20 步實測須回填取代（#9：估算不得入帳本）。
- 三鏡有 sibling agent 在同一 GPU 上並行競用（鏡一觀察到 14:30 有人重載 qwen3:4b），故其時間數字帶有未量化的競用污染。本設計以「每筆時間數字必須併記 `nvidia-smi free` + `ollama ps`」作為對策。

---

## 6. 給 hugo 的三個決策點（30 分鐘後你要拍的板）

**決策一（今天就能拍）：S0 修尺要不要做？**
建議：**做，無條件。** 這不是 LoRA 的前置，這是修一個**已在生產中誤導決策**的評測器——它已經產出「0.256→0.325→0.383→0.492 逐版單調升」這條敘事，而那條敘事跨的是三把不同的尺、量的是被截斷的思考鏈、且冠軍低於零知識地板。1.5 天、零 GPU、零 Claude token。屬 #26 執行層（修 bug），除了「宣告舊分數作廢」那一步需要你點頭。

**決策二（S0 後）：S1 零訓練上界要不要做？**
建議：**做。** 0.5–1 天，零訓練。它產出的 A4 臂**就是 LoRA 必須打敗的對象**——沒有它，LoRA 拿什麼比？而且它自帶一個可能省掉整個 S2 的中止條件。

**決策三（S1 後，這才是真正的分岔）：S2 LoRA 要不要做？**
建議：**看 S1 的 A4 分數再決定，並預先接受「大概率不做」。**
誠實的先驗判斷：本語料 82% 是三個模板、18% 是活資料；模板已由 grammar 零訓練拿到，活資料**不該**進權重（#9/#10 + 無失效機制）。LoRA 在此僅剩「拒答 / 消歧義判斷」這一窄塊，而檢索路由也能處理其中大部分。**若你要一句話的建議：這個 spike 的正確產物是「一把能用的尺 + 一條 grammar+檢索的零訓練基線」，而不是一顆 LoRA。**

但如果 S1 之後 A4 在 L3（該拒答時拒答）上明顯撐不住——那正是 LoRA 唯一站得住的地方，屆時 S2 值得跑，而且本設計已經把它的每一顆螺絲都上好了。

---

## 附錄 A：本報告親驗複現指令（零 Claude token）

```bash
# 語料現況 + 帳本三 hash 空轉 + set_hash 假 provenance
cd /home/hugo/project/augur && venv/bin/python - <<'EOF'
import sys, json, hashlib; sys.path.insert(0,'src')
from augur.core import db
with db.connect() as c:
    cur=c.cursor()
    cur.execute("SELECT count(*), count(distinct verdict), count(distinct gold_answer) FROM local_model_gold_sample"); print(cur.fetchone())
    cur.execute("SELECT trigger_event->>'source', count(*) FROM local_model_gold_sample GROUP BY 1 ORDER BY 2 DESC"); print(cur.fetchall())
    cur.execute("SELECT version_id,status,eval_result->'fixed_eval'->>'score',eval_result->'fixed_eval'->>'set_hash',anchor_hash,eval_code_hash FROM local_model_version ORDER BY created_at")
    for r in cur.fetchall(): print(r)
    cur.execute("""SELECT sample_id FROM local_model_gold_sample WHERE verdict='oracle_pass' ORDER BY md5(prompt) LIMIT 12""")
    print("現行集A set_hash =", hashlib.sha256(json.dumps([r[0] for r in cur.fetchall()]).encode()).hexdigest()[:12])
EOF
# 預期：983 / 1 / 908；KI 856 CC 67 FC 60；四列 set_hash 全 44893a73fbfc、anchor/eval_code 全 None；
#       現行集A = 334086187ab1  →  帳本 provenance 為假
```

常數地板與事實敏感度之複現腳本（本報告 §1 用的那支）邏輯為：`_score` 逐字複製自 `scripts/evolve_cycle.py:135-146`；常數字串由三模板骨架組成、實體槽全空；事實敏感度以 `re.sub(r'\d','9',gold)` 產生「數值全錯但模板全對」的答案。兩者皆零 LLM 呼叫。

## 附錄 B：本設計相對母計畫的差異清單（供更正 `reports/augur_local_ai_evolution_loop_plan_20260725.md`）

| 母計畫原文 | 本設計裁決 | 依據 |
|---|---|---|
| §11「CPU 路缺 bitsandbytes-CUDA 前提」 | **前提已失效**，bnb 0.50.0 已裝且 NF4 在 sm_75 實測可用 | 親驗 + 三鏡 |
| §26 Tier 2 (a) CPU LoRA on 4b，週級 cadence | **刪除。** GPU 快 5.7×，CPU 4B 常駐 16.03 GiB / avail 17 GiB 必吃 swap | 鏡三實測 |
| §26 Tier 2 (b) 賭「窄任務特化 1.7b ≥ 通用 4b」 | **改寫。** 1.7B 是唯一 GPU 可行路（確認），但**跨 base 比較禁止用於 LoRA 判決**（雙重混淆） | 鏡一 VRAM 實測 + 鏡二 base 身分實證 |
| §26「訓練窗停 PG 或 bf16」 | 停 PG 不需要；**bf16 非原生但實測比 fp16 快 3×**；dtype 由 20-step bake-off 定 | 鏡一端到端對照 |
| §63 成敗判準「部署工作域金標分數逐版單調升、通用能力錨集零退步」 | **兩個資料集在 DB 與 repo 都不存在**（實查確認）；「零退步」在實測噪音下幾乎必然自動觸發 NO-GO → 改為「CI 下界 ≥ incumbent − δ」 | 鏡 d 實查 + temp=0 非決定性實測 |
| §「兩輪無增益→停損」 | 加五項前提（正控制 / 格式 hash / 三軸評分器 / 對照矩陣 / 凍結集），否則該兩輪 INVALID 不計數 | 鏡 d |
| 訓練目標（隱含：現有 983 條 gold） | **改為行為語料**（B1–B4，含 DECLINE/DISAMBIGUATE 負例）；事實槽一律排除 | #9/#10 + 鏡 b 治權論證 + 現語料 DECLINE=0 |
| 權重鏈「HF→PEFT→convert_lora_to_gguf→ollama 須建」 | **正確，且 `ADAPTER *.gguf` 路已被端到端實證**；但 ollama 的 **safetensors** ADAPTER 路對 qwen3 不可行，不要走 | 鏡二執行證據 + 源碼 |

---

*本報告依 #20 計畫先行產出，含表 schema 與程式規畫雙落實；所有量化數字標明來源等級（親驗 / 端到端執行 / 元件實測 / 源碼 / 估算）；估算值明文標示且不得入帳本（#9）。晉升 serving 之 `promoted_by` 唯 hugo 親跑寫入。*
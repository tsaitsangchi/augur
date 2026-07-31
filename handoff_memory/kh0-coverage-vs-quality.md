---
name: kh0-coverage-vs-quality
description: KH0 覆蓋 100%≠理解正確;「待人裁」根因=90.3s 逾時本地AI從未答成;ERP 實例五錯處
metadata:
  type: project
---

**KH0 底線不變式已入憲（大憲章 v1.52.0，2026-07-30 hugo「請入憲」）**：凡具原文（`knowledge_item_text`）之 item 一律須達 KH0；「有原文 ∧ 無 `knowhow_auto_admit_state` 列」之計數須恆為 0。機械落點＝`scripts/run_kh_chain.py --check`（破口非 0 時 `--phase advance/all` fail-closed 拒絕推進）。

**親驗現況（2026-07-30）**：`knowledge_item` 270,739；有 state 列 146,348；無 state 列 124,391 —— **恰等於無原文者 124,391**，故「有原文但未評 KH0」＝**0**。誠實例外＝那 124,391 件 metadata-only（license 阻擋或全文未取），KH0 無內容可理解、不適用、不得偽稱已達。

**但覆蓋 ≠ 品質（條款目前未涵蓋，待 hugo 裁）**。ERP 演練文件實例（hugo 貼出摘要＋原文對照，指「本地AI就基本資料理解需要加強」）之五錯處：
1. **最致命**：把時間軸相鄰兩列（`14:55 還原備份資料`／`15:00 各部門測試`）誤讀為單一活動之起訖 → 稱「還原 5 分鐘、符合預期」，**與同文件明載「還原速度緩慢｜待修正」＋「RTO <4h ⚠未達標、實際 4:30h」正面矛盾**。
2. 抄原文「備份時間目標未達成」而未校正——真正未達標者是 **RTO**（RPO <24h 是 ✅ 達標）。
3. **幻像**：推測「備份點選擇／資源分配」，而文件已列真因（備援效能設定待修正／VM 網卡已升 10Gbps）。
4. 抄「整體順利」未標記原文內部矛盾。
5. 漏 RTO/RPO 界分、4:30h、Veeam 17 步 SOP、資料驗證（7/24 在、7/25 缺）。

⇒ **判斷句：「這件事只證明被評過一次，還是證明評對了？」** 現行 KH0 只證前者。可行補強（未擅定）：三臂地板（承 [[eval-boilerplate-floor]]）／文件內錨題集／自相矛盾偵測。

**「待人裁」之根因（2026-07-30 晚更正——我先前寫「＝逾時」是不完整的）**：逾時只是**表層**，真瓶頸是**回應不可解析**。

- 排隊取得車道後實測：`model=heuristic`（**非** `heuristic_fallback`）配 **98.594s** ⇒ 依 code 路徑，`use_llm=True` 而 model 為 `heuristic` 只有一種可能：**LLM 沒逾時、它答了，但 `_parse_llm_json` 解不開、整個答案被丟掉**。故 90s 只是差一點不夠（98.6s），**9000s 遠超所需、逾時不是真瓶頸**。
- **三件疊在一起**：① `"think": False` **沒有真的關掉思考**——qwen3:4b 照樣把推理當**正文**吐（實測開頭＝「首先，理解任務：我是入庫預審助理…」），只是不包 `<think>` 標籤；② `num_predict=220` 把它截斷（507 字元用完，斷在「這表示」，**還沒輪到輸出 JSON**）；③ `_parse_llm_json` 抓到的 `{...}` 是模型**複述的 schema**（`{"score":0.0到1.0,...}`＝非合法 JSON）⇒ 回 None。
- **解法＝ollama `"format": "json"`**（強制 JSON、連前言都不產生）＋`num_predict`→400。實測 **98.6s→62.7s（反而快）、model=qwen3:4b、llm_ok=1、可解析 True**。**本地 AI 首次真正答成。**
- **判斷正確性已親核**：模型答「license_regime 空值，需確認授權狀態」，實查 DB `aozora_books.license_regime = None` ⇒ **判讀正確**。⇒ hugo「本地 AI 對原文語意本來就具備基本理解」成立；先前看不到是因為**它從未被允許把答案交出來**。
- ⚠ 殘留：system prompt「score 高＝較值得人優先審」語意含混，模型在前言中誤讀為「高分＝較安全可放行」，把兩者對調 ⇒ 分數語意可能反轉，未擅改（影響排序判準、待裁）。
- ⚠ 另記：`heuristic_only` 欄混淆「未用 LLM」與「答了但不可解析」——07-30 早 05:00 那次 40 筆中 **24 fallback／16 不可解析**，後者訊號在帳本中消失。

**（史料）原判＝逾時，非治權結果**：`assist_admission_review.py` 之 `model=heuristic_fallback:qwen3:4b` 只在例外分支產生；實測 `_ask_ollama` **90.3s TimeoutError** ⇒ 啟發式 fallback ⇒ 無法判斷 ⇒ `hold_for_human=True`。**本地 AI 從未答成過**。90s 對 CPU-only 本機（見 [[machine-pc002-s1800-hardware]]）不足，qwen3 預設 thinking 更慢。今日 05:00 timer 跑 58 分鐘、exit 0、零產出，全程持 `flock /tmp/augur_llm.lock`。
- ⚠ **假訊號**：**沒有 `ollama.service` 這個 systemd unit**（ollama 非 systemd 起），故 `systemctl is-active ollama` 回 `inactive` **不代表 ollama 掛了**——`/api/tags` 有回三模型才是真。我曾據此誤判並撤回。
- **來源層人簽不是過時條款**：`chk_ks_active_needs_approval` 仍在；v1.48.0 一律准入僅解除 **item 層**；**P8「甲成立」正繫於此代償介入點——動它會重啟 P8**。惟措辭不精確：機器批 `auto_rules_v1` 48 列 vs `admin` 3 列，**機器批才是主路徑**，應改「待放行（機器批七謂詞／或人簽）」。

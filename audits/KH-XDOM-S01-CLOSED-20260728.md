# KH-XDOM-S01 CLOSED（2026-07-28）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/KH-XDOM-PLAN-APPROVED-20260728.md`（Steward `KH-XDOM-PLAN`＋`KH-XDOM-S01`＋`PME-XDOM-NO`＋`FZ-keep`）  
> **計畫**：`reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`（S0＋S1＋S1b）  
> **不含**：S2 評測集／S3 品質／ATA 外部放量／來源 approve／異域進化閉環／FinMind／FRED

## 一、做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **拍板登錄** | ✅ | `KH-XDOM-PLAN-APPROVED-20260728.md`；計畫書 Steward 欄已更新 |
| **S0 診斷帳** | ✅ | D3 呼叫點：repo 無 advisor 路徑傳 `domain=`；`retrieve_all` 本來就不傳。PG 分桶重跑；孫子 works＝`孫子兵法`／`孫臏兵法`；item「The Art of War」@`business_mgmt` 無全文（缺終態≠分域閘） |
| **S1 去作答分域閘** | ✅ | `retrieve_items(domain=)` 標為策展 opt-in；`retrieve_all`／`advise` 預設鎖定不傳；`corpus.clean_item_sql` 文件化 RBAC≠策展；selftest 鎖呼叫 |
| **S1b ATA 骨架** | ✅ | 新 `scripts/advance_knowledge_terminal.py`（dry-run／有界 apply；四段既有 CLI）；`system+approve→PermissionError`；執行路徑禁 `transition` |
| **重啟 advisor** | ✅ | `systemctl --user restart augur-advisor`（#7）；`:8399` active |
| **FZ-keep／PME-XDOM-NO** | ✅ | 零市場 API；未開異域進化閉環 |

## 二、S0 數字（真兆）

### 分桶（`report_knowledge_fulltext_buckets.py`）

| 指標 | 值 |
|---|---|
| gaps | `ft_no_sent=0`／`sent_no_emb=13241`（腳本 headline；ATA dry-run 池見下） |
| erp_tiptop | items 141,873／ans 100% |
| medicine 等 pending 域 | 仍大量 pending（覆蓋問題；非本輪放量） |

### ATA dry-run 池量

`pending=107601`／`ft_no_sent=0`／`sent_no_emb=430`（唯讀；零執行）

### 作答曾傳 `domain=` 呼叫點

| 路徑 | 結論 |
|---|---|
| `retrieve_all` → `retrieve_items` | **不傳** `domain=`（S1 鎖＋selftest） |
| `advise` 預設 | 改為 `retrieve_all`（原誤預設 works-only `retrieve`） |
| `serve_advisor_openai` | 已顯式 `retrieve_fn=retrieve_all` |
| 顯式 `domain=` | 僅 `retrieve_items` 可選參數；對比測：`domain=chemistry`→0；`business_mgmt`→8 |

## 三、S1 探針「孫子兵法在企業管理上的運用」

**scope＝Steward／super**；`retrieve_all`＋`relevant_citations`＋`advise(mock-llm)`：

| 項 | 結果 |
|---|---|
| raw／relevant | 8 → 5 |
| domains／thinkers | `孫武`、`王陽明`、`erp_tiptop`、`solar_rd`（**多標籤／works＋items**；非 domain= 空） |
| guard（mock） | pass |
| 對照 | 強制 `domain=chemistry`→0＝證「單域閘會死」；預設路徑無此閘 |

> 噪音（solar_rd／erp 管理字面）屬 S3 相關度調參範圍；S01 驗收＝**非因分域閘空**，非答案品質滿分。

HTTP `chat/completions` 全鏈（qwen3:8b）本輪曾因逾時／BrokenPipe 未取完整 JSON；**檢索＋相關度＋advise 編排**已 mock-LLM 親驗。advisor 服務已重啟載入新碼。

## 四、硬邊界核對

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不做異域進化灌因子 | ✅（`PME-XDOM-NO`） |
| 不自動 approve／activate | ✅（ATA selftest＋骨架禁 transition） |
| 不改 [N]／不搬 CJK glossary 入憲 | ✅（暫留 hardcode；NHC 另案） |
| 素養不進預測 | ✅（未碰 predict） |

## 五、變更檔

- `src/augur/philosophy/retrieval.py` — domain 策展 opt-in 文件＋selftest  
- `src/augur/advisor/advise.py` — 預設 `retrieve_all`  
- `src/augur/knowledge/corpus.py` — RBAC≠策展註解  
- `scripts/advance_knowledge_terminal.py` — **新** ATA 骨架  
- `audits/KH-XDOM-PLAN-APPROVED-20260728.md`／本 CLOSED  
- `reports/augur_knowhow_cross_domain_advisor_plan_20260728.md` — 拍板欄  

## 六、下一步建議碼（決策層）

1. **`KH-XDOM-EVAL`** — S2 跨域評測集＋跑分（含標註缺終態）  
2. **`KH-XDOM-QUAL`** — S3 相關度／噪音↓（本探針 solar_rd／erp 假命中）  
3. **`KH-ATA-EXEC`** — ATA 對準評測缺口之有界 OA（≠解凍市場 API）  
4. **NHC** — CJK glossary hardcode→DB 入憲（另計畫；勿與 S01 混）  
5. 市場 API：**仍凍**（`FZ-keep`）

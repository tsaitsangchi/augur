# JOB4-SENT-EMBED CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward「**job4→sent+embed — 75 新 item 進可檢索**」  
> **拍板**：`audits/JOB4-SENT-EMBED-APPROVED-20260730.md`  
> **範圍**：job_id∈{3,4} ∧ `ingest_status='inserted'` → **75 unique items**

## 一、做了什麼

| 步驟 | 結果 |
|---|---|
| `build_sentences --scope items` | ✅ 段 0／切句 0（75 項**已有句**：234 sent） |
| `embed_knowledge … zh --scope items --gap-fill` | ✅ 處理 31、**新嵌 0**、junk 31 |
| `embed_knowledge … en --scope items --gap-fill` | ✅ 處理 9,228、**新嵌 88**、junk 9,140 |
| Qdrant（`--url http://127.0.0.1:6333`） | ✅ en：missing→補 **321**、差=0；zh：synced **887**、差=0 |
| FZ-keep | ✅ |

**備註**：首跑未加 `--url` 時落到 `~/qdrant_local` embedded 卡住（Dl/jbd2）；已停、改 server URL（與 FT-COV WAVE3 同路徑）。

## 二、75 item 覆蓋（真兆 DB）

| 指標 | 值 |
|---|---:|
| unique items | 75 |
| 有全文 | 75 |
| 有句 | 75（234 sent） |
| **有 ≥1 嵌入 → 可檢索** | **65** |
| 零嵌入 | **10**（全 en） |
| 句嵌覆蓋 | 182／234 sent |

### 按語言

| lang | items | 有嵌 | 零嵌 | sent | emb |
|---|---:|---:|---:|---:|---:|
| en | 72 | 62 | 10 | 142 | 90 |
| zh | 3 | 3 | 0 | 92 | 92 |

### 零嵌 10 項原因（誠實）

`is_junk(en)`：**len(sentence) > 1000**（切句過粗／單句過長）。樣本 min_len 1346–8000。  
→ **非漏跑**；要納入須另令「重切長句」再 embed（本輪不做）。

## 三、硬邊界

| 項 | |
|---|---|
| ≠ 解凍 API | ✅ |
| ≠ 強嵌 junk／>1000 en | ✅ |
| ≠ 宣稱 75/75 全進向量 | ✅ **65/75** 可向量檢索；10 項僅 DB 全文 |

## 四、下一步（待另令）

1. 可選：對 10 長句 item 重切（`build_sentences` 參數／修切）→ 再 gap-fill  
2. advisor smoke：用 job4 標題／關鍵詞問一句驗命中

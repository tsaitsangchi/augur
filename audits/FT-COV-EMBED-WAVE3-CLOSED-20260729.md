# FT-COV-EMBED-WAVE3 CLOSED [I]（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **前序**：`audits/FT-COV-DASH-EMBED-CLOSED-20260728.md`（P0 DASH＋P1 EMBED CLOSED；en junk 排除；ft_no_sent=0）  
> **Steward 指令**：`FT-COV-embed`＋`FZ-keep`（NET8 §三）  
> **不含**：en junk 重嵌／市場 API 解凍／他域進化閉環

## 一、做了什麼

| 階段 | 狀態 | 摘要 |
|---|---|---|
| **build_sentences（items 側）** | ✅ | 13 段待切→60 句新建（`--scope items`；0.7s） |
| **embed gap-fill（zh items）** | ✅ | 73 句處理、**42 新嵌**、31 junk 排除（已入 ledger）；model=`intfloat/multilingual-e5-small`；耗時 8.5 分 |
| **Qdrant push** | ✅ | `export_qdrant_index.py --side items --language zh`：upsert 887（含新 42）；orphan=0；私有擋下 148,087（`local_private` 不匯外部） |

## 二、數字（DB 親驗 2026-07-29 ≈17:00 +08）

| 指標 | Wave2（07-28） | Wave3（07-29） | Δ |
|---|---:|---:|---:|
| `knowledge_sentence` 總句 | 1,789,622 | **1,789,682** | +60 |
| `knowledge_sentence_embedding` 總嵌 | 1,721,515 | **1,721,557** | **+42** |
| zh gap（未嵌句） | 31 | **36**（含新 5 junk） | +5 junk |
| en gap（未嵌句） | 68,071 | **68,089**（全 junk/CLEAN 排除） | +18 junk |
| Qdrant `kn_sent_it_ime5s30b1cd_tn1` | 78,419 前 | **78,419 後**（887 CLEAN upsert 含既存） | sync 齊 |

### zh 殘餘 36 gap 全為 junk

抽樣：`。`（1 char）、`□□□□……`（6 char）、`……`（2 char）、`= ''）`（5 char）、`|]`（2 char）、`...`（3 char）——**正確不嵌**，非漏嵌。

### en 68,089 gap＝延續 P1 判定

P1 已確認 en gap 全為 junk／CLEAN 排除（`knowledge_embed_ledger` ledger_id=86）；本輪未重跑 en（無新 en 非 junk 句）。

## 三、Qdrant 影子索引狀態

| collection | points | indexed_vectors | 備註 |
|---|---:|---:|---|
| `kn_sent_it_ime5s30b1cd_tn1` | 78,419 | 77,452 | items 側 CLEAN；私有 148,087 僅 pgvector |

## 四、硬邊界核對

| 碼 | 本輪 |
|---|---|
| `FZ-keep` | ✅ 零 FinMind／FRED |
| 不假重嵌全庫 | ✅ gap-fill only |
| 不把 junk 強嵌 | ✅ junk 31＋新 5＝36 正確排除 |
| 不解凍／不降閘 | ✅ |
| 素養層不進預測管線 | ✅ |
| #1／#8／全文三軌 | ✅ |

## 五、下一步

- **en gap 68,089 全 junk**——不需動作；若未來有新 en CLEAN 句，再跑 `--language en --gap-fill`。  
- **Qdrant works 側**（`kn_sent_wk_*`）本輪未動（哲學側無新句）。  
- **P2+／HAR-ext 續批**——需另碼、FZ-keep。

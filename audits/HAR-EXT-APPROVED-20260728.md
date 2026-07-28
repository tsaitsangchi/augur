# HAR-ext（＋可選 FT-COV-BATCH）拍板登錄（2026-07-28）

> **性質**：拍板登錄（[I]；不創設 [N]）。  
> **計畫**：`reports/augur_knowledge_fulltext_coverage_plan_20260728.md`（P2／P3）  
> **hugo／Steward 對話拍板原文（要旨）**：`HAR-ext`（建議先各域 `--limit 3`）＋可選 `FT-COV-BATCH`  
> **簽名誠實註記**：本檔由 agent 依 Steward 拍板繕寫登錄；決策者＝hugo、繕寫者＝agent，二者分立。

## 一、近程採納範圍（本輪）

| 碼 | 含義 | 本輪 |
|---|---|---|
| **`HAR-ext`** | 知識域 OA fetch **窄窗 P2**——下列 8 域各 `python scripts/fetch_oa_fulltext.py --domain <d> --limit 3` | ✅ 核准並執行 |
| **`FT-COV-BATCH`（可選）** | P2 煙測通過後，同批域有界 `--limit 50`（或計畫書 P3 上限）；**禁止**無 limit 全域放量 | ✅ 本輪一併授權有界續跑（條件＝P2 健康） |
| **`FZ-keep`** | FinMind／FRED 維持凍結；本 HAR-ext ≠ 解凍市場 API | ✅ 預設仍成立 |
| **清 pending 無界／全域放量** | 無 `--limit` 全庫猛抓 | ❌ **禁止** |
| **他域進化閉環／素養進預測** | — | ❌ 不含 |

### 核准域清單（8）

`medicine` · `social_sciences` · `engineering` · `physics` · `arts_and_humanities` · `electronics` · `biochemistry_genetics_and_molecular_biology` · `agricultural_and_biological_sciences`

## 二、效力邊界

1. **P2（必做）**：每域 `--limit 3`；記錄 `fetched`／`skip_*`／`error`；#25 最小單位精神。  
2. **FT-COV-BATCH（條件）**：僅當 P2 健康（無系統性 403／429／連續熔斷、腳本可正常寫 text 或 skip 終態）才得對同批域跑 `--limit ≤50`。  
3. **熔斷**：見 403／429／連續熔斷 → **當日停、不重試風暴**。  
4. **全文三軌／license 閘**：`blocked`（`skip_*`）＝合法終態，**勿灌假全文**。  
5. **後續鏈（有界）**：對**新取得全文**接 `build_sentences`／`embed_knowledge`（本地）；重跑 `report_knowledge_fulltext_buckets.py` 對照前後。  
6. **前置**：`UNPAYWALL_EMAIL` 須在環境／`.env`（勿印出）；缺則停手。

## 三、硬邊界核對（開工前）

| 項 | 本輪 |
|---|---|
| 零 FinMind／FRED；不解凍 | ✅ |
| 不把 blocked 洗成全文 | ✅ |
| 禁止無 limit 全域放量 | ✅ |
| #1／#8／全文三軌 | ✅ |
| `UNPAYWALL_EMAIL` 已載入（值不入 audit） | ✅（開工核對） |

## 四、執行落點（後填 CLOSED）

- 執行／數字：`audits/HAR-EXT-CLOSED-20260728.md`
- HANDOFF 一句更新（FT-COV 近程列）
- 封存：`bash scripts/archive_push.sh --slug har-ext-p2-batch`（若可）

# Augur

> 只用真實資料、誠實預測台股。

Augur 從 FinMind / FRED 抓進可溯源的日級資料，算成 source-pure 特徵，選出資料乾淨的核心股，
訓練模型預測未來 H 日的**相對強弱**（橫斷面排序 → top-N），並以 walk-forward 誠實驗證、附可信度。

它給的是**機率 + 可信度，不是命令**——系統建議、人決策；augur **不下單、不動錢**。

**augur** = 古羅馬觀兆者，讀真實徵兆來預言。**只讀真兆，不造假兆——只信真兆。**

它的每一條紀律都在防三個敵人：**① 假資料 · ② 偷看未來 · ③ 自我欺騙**。

> 🚧 **狀態**：開發中。治權已立（靈魂 v1.5.0・原則精華 v1.9.0〔20 條法律〕・憲章 v1.43.0・CLAUDE v1.25——歷次入憲演進之明細見憲章「修訂歷程」，不在此複列防漂移）；`core / ingestion / audit / features / universe` 已建並實跑，特徵層三鏡頭 8 特徵＋康波毛利循環相位入生產、剪共線 volatility_20d（27→35）、經濟回測基礎(`evaluation/portfolio.py`)已建；raw 全市場全史 sync 已完成至 as-of 2026-05-31（84/84 逐表完整性定案）；**FREEZE 已於 2026-07-12 解除、轉 live 增量維運（原則精華 v1.9.0 解凍子條；live 准入依 unfreeze gate 紀律）**；`models`（F3）未建（規劃中）；知識素養層三部曲（registry 窮舉 → harvest 常規批 → text 逐字理解）已上線、`knowledge / philosophy / advisor` 橫切已建（三粒度向量檢索嵌入已建；「誠實博學的我」顧問角色層續建中，詳 `reports/augur_knowledge_text_understanding_plan_20260702.md`）。

---

## 先讀這幾份（治權檔）

| 文件 | 角色 |
|---|---|
| [`docs/系統核心思想_v1.8.0.md`](docs/系統核心思想_v1.8.0.md) | **靈魂**：系統是什麼、為什麼、什麼絕不能違反 |
| [`docs/原則精華_v1.9.0.md`](docs/原則精華_v1.9.0.md) | **20 條不可違反原則**（三條基石：#1 / #8 / #15）＋ 資料完整性判準（as-of · FREEZE） |
| [`docs/系統架構大憲章_v1.45.0.md`](docs/系統架構大憲章_v1.45.0.md) | **憲法**：三個敵人 × 管線 + 12-PHASE 維運 + 升版規則；歷次架構/判準演進明細＝檔內「修訂歷程」（單一權威家 #12，此處不複列） |
| [`CLAUDE.md`](CLAUDE.md) | AI 協作工具規則 |

## 管線

```
raw (FinMind/FRED) → feature (source-pure) → universe (核心股) → model (樹/transformer) → validate (multi-cycle)
```

## 目錄

```
src/augur/   ingestion / features / universe / models(F3 未建) / evaluation / audit / catalog（預測管線 7 pkg）
             core（兩側共用 infra 橫切）；knowledge / philosophy / advisor（素養橫切，AST 強制隔離、預測管線零 import）
scripts/     薄 CLI entrypoints（呼叫 src，不放邏輯；個別可執行 + 資料驅動不 hardcode，CLAUDE #29；
             知識擷取=DB 三層管線 knowledge_source→acquire→staging→promote，新增領域=INSERT 來源列零 code）
docs/        治權三件套 + datasets_zh.md(資料源逐欄 catalog) + finmind-references(FinMind 官方 dataset 抓法權威源) + archive(考古索引)
reports/     研究報告產出
tests/       單元測試
```

## 環境

```bash
python -m venv venv && source venv/bin/activate
pip install -e .
cp .env.example .env   # 填 DB / FINMIND_TOKEN / FRED_API_KEY
```

## 授權

MIT — 見 [`LICENSE`](LICENSE)。

---

最高紀律：**零 AI 幻像（#1）** — 每個值都能 trace 回真實 API；用假資料跑模型沒有意義。**只信真兆。**

# Augur

> 只用真實資料、誠實預測台股。

Augur 從 FinMind / FRED 抓進可溯源的日級資料，算成 source-pure 特徵，選出資料乾淨的核心股，
訓練模型預測未來 H 日的**相對強弱**（橫斷面排序 → top-N），並以 walk-forward 誠實驗證、附可信度。

它給的是**機率 + 可信度，不是命令**——系統建議、人決策；augur **不下單、不動錢**。

**augur** = 古羅馬觀兆者，讀真實徵兆來預言。**只讀真兆，不造假兆——只信真兆。**

它的每一條紀律都在防三個敵人：**① 假資料 · ② 偷看未來 · ③ 自我欺騙**。

> 🚧 **狀態**：開發中。治權已立（原則精華 v1.7.1・20 條法律；憲章 v1.12.0・catalog 橫切元資料登錄 + 官方 datasets.md 入憲 + 特徵發現方法論入憲 + 配額感知暫停/續跑）；`core / ingestion / audit / features / universe` 已建並實跑，raw 全市場全史 sync 暫停、轉 catalog-driven 規劃（已產 `docs/datasets_zh.md` 全 83 表逐欄 catalog + 抓取最佳化計畫/token 預算）；`models / evaluation`（F3）未建。

---

## 先讀這幾份（治權檔）

| 文件 | 角色 |
|---|---|
| [`docs/系統核心思想_v1.2.0.md`](docs/系統核心思想_v1.2.0.md) | **靈魂**：系統是什麼、為什麼、什麼絕不能違反 |
| [`docs/原則精華_v1.7.1.md`](docs/原則精華_v1.7.1.md) | **20 條不可違反原則**（三條基石：#1 / #8 / #15） |
| [`docs/系統架構大憲章_v1.12.0.md`](docs/系統架構大憲章_v1.12.0.md) | **憲法**：三個敵人 × 管線 + 12-PHASE 維運 + 升版規則（+ 橫切 catalog 元資料登錄 + 官方 datasets.md 入憲 + 特徵發現方法論入憲 + 配額感知暫停/續跑）|
| [`CLAUDE.md`](CLAUDE.md) | AI 協作工具規則 |

## 管線

```
raw (FinMind/FRED) → feature (source-pure) → universe (核心股) → model (樹/transformer) → validate (multi-cycle)
```

## 目錄

```
src/augur/   core / ingestion / features / universe / models / evaluation / audit / catalog
scripts/     薄 CLI entrypoints（呼叫 src，不放邏輯）
docs/        治權三件套 + datasets_zh.md(資料源逐欄 catalog) + archive(考古索引)
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

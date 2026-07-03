# Augur

> 只用真實資料、誠實預測台股。

Augur 從 FinMind / FRED 抓進可溯源的日級資料，算成 source-pure 特徵，選出資料乾淨的核心股，
訓練模型預測未來 H 日的**相對強弱**（橫斷面排序 → top-N），並以 walk-forward 誠實驗證、附可信度。

它給的是**機率 + 可信度，不是命令**——系統建議、人決策；augur **不下單、不動錢**。

**augur** = 古羅馬觀兆者，讀真實徵兆來預言。**只讀真兆，不造假兆——只信真兆。**

它的每一條紀律都在防三個敵人：**① 假資料 · ② 偷看未來 · ③ 自我欺騙**。

> 🚧 **狀態**：開發中。治權已立（靈魂 v1.4.0；原則精華 v1.7.1・20 條法律；憲章 v1.20.0——修訂歷程見該檔修訂表）；全管線 `raw→feature→universe→model→validate` 已打通——raw 全市場全史 sync 完成、as-of 2026-05-31 完整性逐表驗證定案（84/84）；特徵層 35 特徵入生產（三層飽和定論）；F3 as-of Ridge 於 `evaluation` walk-forward 實證 alpha、經濟價值驗證成立（#14、`evaluation/portfolio.py`；`models` package 為待建空殼，F3 驗證走 evaluation 雙軌）；philosophy / knowledge 素養層落地（素養庫＋lexicon 逐字定義＋concordance＋三粒度嵌入＋harvest 知識管線——零量化價值、不進預測管線）。

---

## 先讀這幾份（治權檔）

| 文件 | 角色 |
|---|---|
| [`docs/系統核心思想_v1.4.0.md`](docs/系統核心思想_v1.4.0.md) | **靈魂**：系統是什麼、為什麼、什麼絕不能違反 |
| [`docs/原則精華_v1.7.1.md`](docs/原則精華_v1.7.1.md) | **20 條不可違反原則**（三條基石：#1 / #8 / #15） |
| [`docs/系統架構大憲章_v1.20.0.md`](docs/系統架構大憲章_v1.20.0.md) | **憲法**：三個敵人 × 管線 + 12-PHASE 維運 + 升版規則（現行 v1.20.0；逐版特性見該檔修訂歷程） |
| [`CLAUDE.md`](CLAUDE.md) | AI 協作工具規則 |

## 管線

```
raw (FinMind/FRED) → feature (source-pure) → universe (核心股) → model (樹/transformer) → validate (multi-cycle)
```

## 目錄

```
src/augur/   core / ingestion / features / universe / models / evaluation / audit / catalog / philosophy / knowledge / advisor
scripts/     薄 CLI entrypoints（呼叫 src，不放邏輯；個別可執行 + 資料驅動不 hardcode，CLAUDE #29；
             知識擷取=DB 三層管線 knowledge_source→acquire→staging→promote，新增領域=INSERT 來源列零 code）
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

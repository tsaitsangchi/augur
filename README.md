# Augur

> 只用真實資料、誠實預測台股。

Augur 從 FinMind / FRED 抓進可溯源的日級資料，算成 source-pure 特徵，選出資料乾淨的核心股，
訓練模型預測未來一段期間的相對表現，並以 walk-forward 誠實驗證。

**augur** = 古羅馬觀兆者，讀真實徵兆來預言。只讀真兆，不造假兆。

---

## 先讀這三份（治權三件套）

| 文件 | 角色 |
|---|---|
| [`docs/系統核心思想_v1.0.md`](docs/系統核心思想_v1.0.md) | **靈魂**：系統是什麼、為什麼、什麼絕不能違反 |
| [`docs/原則精華_v1.0.md`](docs/原則精華_v1.0.md) | **15 條不可違反原則**（憲章骨幹） |
| `docs/系統架構大憲章_v1.0.0.md` | **憲法**：架構分層 + 維運矩陣 + 升版規則（撰寫中） |
| [`CLAUDE.md`](CLAUDE.md) | AI 協作工具規則 |

## 管線

```
raw (FinMind/FRED) → feature (source-pure) → universe (核心股) → model (樹/transformer) → validate (multi-cycle)
```

## 目錄

```
src/augur/   core / ingestion / features / universe / models / evaluation / audit
scripts/     薄 CLI entrypoints（呼叫 src，不放邏輯）
docs/        治權三件套 + archive(舊版考古索引)
reports/     研究報告產出
tests/       單元測試
```

## 環境

```bash
python -m venv venv && source venv/bin/activate
pip install -e .
cp .env.example .env   # 填 DB / FINMIND_TOKEN / FRED_API_KEY
```

---

最高紀律：**零 AI 幻像** — 每個值都能 trace 回真實 API；用假資料跑模型沒有意義。

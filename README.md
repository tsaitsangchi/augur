# Augur

> 只用真實資料、誠實預測台股。

Augur 從 FinMind / FRED 抓進可溯源的日級資料，算成 source-pure 特徵，選出資料乾淨的核心股，
訓練模型預測未來 H 日的**相對強弱**（橫斷面排序 → top-N），並以 walk-forward 誠實驗證、附可信度。

它給的是**機率 + 可信度，不是命令**——系統建議、人決策；augur **不下單、不動錢**。

**augur** = 古羅馬觀兆者，讀真實徵兆來預言。**只讀真兆，不造假兆——只信真兆。**

它的每一條紀律都在防三個敵人：**① 假資料 · ② 偷看未來 · ③ 自我欺騙**。

> 🚧 **狀態**：開發中。治權已立（原則精華 v1.7.1・20 條法律；憲章 v1.19.0・catalog 橫切元資料登錄 + 官方 datasets.md 入憲 + 特徵發現方法論入憲 + 配額感知暫停/續跑 + 特徵提拔關卡入憲 + 經濟價值驗證收尾關卡入憲 + 執行省 usage × 理解 ultracode 窮盡二分 + 投資哲學框架層入憲 + v1.17.0 哲學素養框架擴博學〔博學投資大師 AI〕 + v1.18.0 版權著作核心精神合規路入憲〔真實文獻 principle→因子→#14、禁 AI 整理〕 + v1.19.0 知識層多域擴充準則入憲〔通用知識管線、多域素養零量化價值、domain 隔離因子鏈〕）；`core / ingestion / audit / features / universe` 已建並實跑，特徵層三鏡頭 8 特徵入生產（27→34）、經濟回測基礎(`evaluation/portfolio.py`)已建；raw 全市場全史 sync 暫停、轉 catalog-driven 規劃；`models`（F3）續建中。

---

## 先讀這幾份（治權檔）

| 文件 | 角色 |
|---|---|
| [`docs/系統核心思想_v1.4.0.md`](docs/系統核心思想_v1.4.0.md) | **靈魂**：系統是什麼、為什麼、什麼絕不能違反 |
| [`docs/原則精華_v1.7.1.md`](docs/原則精華_v1.7.1.md) | **20 條不可違反原則**（三條基石：#1 / #8 / #15） |
| [`docs/系統架構大憲章_v1.19.0.md`](docs/系統架構大憲章_v1.19.0.md) | **憲法**：三個敵人 × 管線 + 12-PHASE 維運 + 升版規則（+ 橫切 catalog 元資料登錄 + 官方 datasets.md 入憲 + 特徵發現方法論入憲 + 配額感知暫停/續跑 + 特徵提拔關卡 + 經濟價值驗證收尾關卡 + 執行省 usage × 理解 ultracode 窮盡二分 + 投資哲學框架層入憲 + v1.17.0 哲學素養框架擴博學〔博學投資大師 AI〕 + v1.18.0 版權著作核心精神合規路入憲〔真實文獻 principle→因子→#14、禁 AI 整理〕 + v1.19.0 知識層多域擴充準則入憲〔通用知識管線、多域素養零量化價值、domain 隔離因子鏈〕）|
| [`CLAUDE.md`](CLAUDE.md) | AI 協作工具規則 |

## 管線

```
raw (FinMind/FRED) → feature (source-pure) → universe (核心股) → model (樹/transformer) → validate (multi-cycle)
```

## 目錄

```
src/augur/   core / ingestion / features / universe / models / evaluation / audit / catalog
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

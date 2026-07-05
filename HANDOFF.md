# HANDOFF — augur 跨機接續指南

> **這份文件是什麼**：augur 專案會在**另一台電腦接續開發**。這份是「新機 clone 後第一份該讀的文件」——
> 告訴你**從哪接、怎麼跑起來、哪些不在 git、進度到哪、紅線是什麼**。
> 快照時點：**2026-07-06**（`main` 當時在 tag `prediction-sop-stage-a-20260706` / commit `3069c72`；HEAD 之後會前進，以 `git log` 為準）。

---

## 0. 一句話

源碼在 GitHub（clone 即得全部，含預測層）；**DB 不在 git、靠 D 碟 dump 搬**；`.env` 與 build 產物不在 git、**須手動重建**；治權與計劃都在 repo 內（讀 §1）。

## 1. 先讀這些（治權 SSOT + 路線圖，勿憑記憶）

| 檔 | 是什麼 |
|---|---|
| `docs/系統核心思想_v1.5.0.md` | **靈魂**：為誰、預測什麼、成功定義=經濟價值非 IC、系統建議人決策 |
| `docs/原則精華_v1.7.1.md` | **20 條不可違反法律**（三敵、anti-leakage #8、經濟 #14、誠實 #15…） |
| `docs/系統架構大憲章_v1.35.0.md` | **憲法**：三敵×管線、12-PHASE 維運、升版規則、修訂歷程（歷次判準演進看這） |
| `CLAUDE.md` | AI 協作工具規則（Read-before-Edit、clean-room、plan-first、一支一支檢視…） |
| `README.md` | 專案狀態 + 標準 setup |
| `reports/augur_prediction_sop_plan_20260705.md` | **股市預測 SOP 主計劃**：端到端管線、階段 A-D、8 拍板點紀錄（§16）、對抗審查發現表 |
| `reports/*_plan_*.md` | 各子系統計劃（顧問精準度、RBAC、知識 v3.0 text…） |

> **紀律**：clean-room（零 stock_backend 參考）、plan-first（規劃類先產計劃報告→人拍板→才實作）、
> 一支一支檢視、改常駐服務後 `systemctl restart` 再實測（見 CLAUDE.md）。

## 2. 新機 setup 序

```bash
git clone https://github.com/tsaitsangchi/augur.git
cd augur
# OS 依賴：PostgreSQL(含 headers)、OpenMP(libgomp,lightgbm/xgboost 需)
python -m venv venv && source venv/bin/activate
pip install -e .                       # README 標準；scripts 個別可執行(不依賴 PYTHONPATH,#29 _bootstrap)
# 還原 DB(不在 git,見 §3)
createdb augur   # 或建 augur 角色/庫
pg_restore -j4 -h 127.0.0.1 -U augur -d augur /path/to/augur_YYYYMMDD_HHMM.dump
# 重建 .env(見 §3)——setup 才會過
python -c "import augur; from augur.core import db; print('smoke ok', db.ping())"   # import + DB smoke
# 常駐服務(WSL2 systemd,可選):augur-chat:8090 / advisor:8399 / admin:8500 / ollama:11434
```

工作目錄隨機器變（WSL2 `/home/<user>/project/augur`、Mac `/Users/<user>/project/augur`；程式一律寫真實工作目錄，CLAUDE #13）。

## 3. 不在 git、新機須重建（皆 gitignored）

- **DB**：靠 dump 搬（#30）。最新 = `D:\database\augur_20260705_2327.dump`（`-Fc` 單檔、164 表含預測層 `model_registry`/`prediction_values`）。**dump 不進 git**（46GB 級）；跨機用外接碟/雲端搬 dump 檔。
- **`.env`**：**手動重建**，須有這些鍵（**值不在此、不入 git**）：
  `DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD`、`FINMIND_TOKEN`、`FRED_API_KEY`、
  `GITHUB_TOKEN`、`AUGUR_ADMIN_PASSWORD`、`AUGUR_INTERNAL_SECRET`、`UNPAYWALL_EMAIL`、`GEMINI_API_KEY`，
  以及 `git config --global user.name` / `user.email` 兩行（commit 身分）。
- **build 產物**（可重生，勿 commit）：`models_artifacts/`（.joblib，`scripts/train_ranker.py` 重生）、`data/`、`models/`。
  > 注意：`.gitignore` 的模型輸出規則已錨定為 `/models/`（根目錄限定）——**勿改回未錨定的 `models/`**，否則會遞迴誤傷 `src/augur/models/` 套件源、致預測骨幹靜默漏 commit。

## 4. 進度快照（2026-07-06 接手當下）

**已完成並 committed**：
- **市場資料層**：raw 全市場全史 sync 至 as-of 2026-05-31（84/84 表、~46GB PostgreSQL SSOT）；features 35 特徵入 `feature_values`（發布日 gate 已落地）；universe `core_universe_asof`；evaluation 六模組（label/walkforward/portfolio/metrics/cross_section/baseline）。
- **知識/哲學/顧問層**：知識三部曲上線；「誠實博學的我」顧問 v1.35.0（精準度：題型自適應 + 空檢索誠實保守白名單 + guard 出處斷言閘 + B-1 相關度收尾；guard 四閘 + 誠實固定句閉集）。
- **股市預測 SOP 階段 A 骨幹**（`prediction-sop-stage-a-20260706`）：`src/augur/models/`（RankRidge 與 baseline B2 逐值等同 + RankGBDT + registry + artifact）、`scripts/train_ranker.py` / `predict_asof.py`、`model_registry` / `prediction_values` 兩表。端到端跑通（as-of 2026-05-31 top1=2330、prediction_values 344 列）。

**⚠️ 尚未做（下一棒）**：
- **預測 SOP 階段 A'**：隔離 AST 稽核（`audit/import_isolation.py`）+ DB GRANT 雙閘、embargo 改保證下界（H=252 禁入 gate）。
- **階段 B**：HAC-t gate **綁死**（禁裸用 iid effective_t）、五鏡 audit、sanity 負對照、as-of IC ≤ pan-hist ——**這是「預測到底有沒有價值」的第一道真檢驗**。
- **階段 C**：扣成本經濟終判（強制 cost≥0.585%、size/beta 中性化揭 exposure 偽裝、逐空頭子期）——**靈魂成功判準**。
- **階段 D**：容量/衝擊成本模型、monitor、point-in-time roster 真消 survivorship、chip 同日含 probe。
- **其他排隊**：知識 v3.0 text W2.7（en 檢索命門 textnorm）+ W8（讀端 kNN API）；admin 控制台 +資料夾多格式抽取器。

## 5. 誠實紅線（不可逾）

- **三敵零容忍、非試錯對象**：①假資料 ②偷看未來（as-of/anti-leakage）③自我欺騙（out-of-sample）。
- **「骨幹跑通 ≠ 預測有價值」**：階段 A 只證管線機械可跑；目前的 top-N 排序**尚未驗證有預測力**。台股橫斷面 alpha 本質微弱，**很可能過不了經濟終關、須誠實判停項**。
- **三處未閉環須誠實標債、不當既成 alpha**（見 SOP 計劃 §0/§13）：(a) headline +0.132 當前 DB 不可重現；(b) `core_universe_asof` 未真消 survivorship（現為倖存名單）；(c) 隔離 AST 稽核尚未建。
- 決策層人拍板、執行層 AI 主動（§26）；碰治權判準變更/破壞性/API 放量/commit-push 即停下問。

---

**續建入口**：讀 §1 治權 + SOP 計劃 → 接階段 A'/B（或用戶指定）→ 一支一支實作、實測、誠實記錄。

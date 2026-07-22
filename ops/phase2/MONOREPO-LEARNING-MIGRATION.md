# 學習用 public monorepo 遷移清單 [I]

* **性質**：資訊性營運計畫，不創設 [N] 義務。
* **前提**：學習 AI 專案；**`https://github.com/tsaitsangchi/augur` 維持 public**；願意公開治權／規格文件；密鑰與 dump **永不進 git**。
* **本機終態（已定）**：**只留一個工作樹** → **`/home/giga/augur`**，追蹤 public `augur`（整包 monorepo）。

---

## 1. 終態 vs 現況

| | 現況（過渡） | 終態（目標） |
|---|---|---|
| 本機工作樹 | `/home/giga/augur`（constitution）＋ `/home/giga/augur-code-work`（app） | **僅 `/home/giga/augur`** |
| GitHub | `augur-constitution`（private）＋ `augur`（public） | **僅 public `augur`** |
| 治權／MCP | 在 constitution 倉 | 在 monorepo 的 `governance/`（或等價目錄） |
| 應用 | 在 `augur-code-work` | 在同一 `/home/giga/augur` 的 `src/`／`scripts/` 等 |

**過渡期允許雙目錄；遷完後 `augur-code-work` 改名 `_archived_*` 再刪，避免雙寫。**

---

## 2. 目標目錄樹（在 `/home/giga/augur`＝public `augur`）

```text
/home/giga/augur/                 # 唯一本機工作樹 ↔ github.com/tsaitsangchi/augur
├── README.md
├── .gitignore                    # 合併兩邊；.env、venv、.project_memory、*.dump、augur-data/
├── .cursor/mcp.json
├── governance/                   # ← 今日 constitution 倉主體（名稱可改 constitution/）
│   ├── constitution/
│   ├── specs/
│   ├── audits/
│   ├── ops/                      # machines、phase2、packs…
│   └── tools/                    # constitution_* / local_llm_* / project_memory_* / lint
├── src/                          # ← 今日 augur-code-work 應用
├── scripts/
├── docs/
├── tests/
├── pyproject.toml
├── import_database.sh
└── install_services.sh           # 去掉 hugo 硬編碼；PROJECT_ROOT=/home/giga/augur
```

MCP 仍在 **repo 根** 以 `python3 -m tools…` 啟動時：遷目錄後須改套件路徑，或把 `tools/` 留在根、`governance/` 只放文書——**實作遷移時二選一寫死**（建議：**tools 留根**，文書進 `governance/`，少改 MCP）。

**較少摩擦的變體（推薦實作時採用）：**

```text
/home/giga/augur/
├── constitution/ specs/ audits/ ops/ tools/ reports/   # 治權（現狀可幾乎不動）
├── src/ scripts/ docs/ tests/ pyproject.toml          # 應用自 code-work 併入
└── .cursor/mcp.json
```

即：**不必強行多一層 `governance/`**，只要單一 remote、單一本機根。

---

## 3. 遷移順序（先合、後刪）

| 步 | 動作 | 完成標準 |
|---|---|---|
| **0** | 兩倉各 `git tag`／`git bundle` 備份 | 可還原再建議刪倉 |
| **1** | 公開掃描：密鑰、dump、不當語料 | 無敏感物進 public 歷史 |
| **2** | 在 `augur` 上開遷移分支：併入治權樹＋保留應用樹 | 單一分支目錄齊 |
| **3** | 改路徑：`.env.example`／`install_services`／packs／probe；`PROJECT_ROOT=/home/giga/augur` | selftest／setup_check／路徑契約正確（✅ 2026-07-22 @ `migrate/monorepo-learning`） |
| **4** | **本機收斂**：以 `/home/giga/augur` 為唯一工作樹 `git remote` → `augur`；停用對 `augur-code-work` 的寫入 | 只在一個根開發（✅ 2026-07-22：`augur-code-work`→`/home/giga/augur`；舊 constitution 樹→`_archived_augur-constitution_20260722`） |
| **5** | 觀察期：`augur-constitution` 改名 archived／read-only | 無他機死鏈（✅ 2026-07-22：rename→`augur-constitution-archived`＋GitHub archive 唯讀；舊 URL redirect；正典＝public `augur`） |
| **6** | 刪 GitHub `augur-constitution`（可選再清本機 `_archived_augur-code-work`） | 確認無依賴（✅ 2026-07-22：遠端已不存在；DESKTOP=`PC002-S1800` 已改指） |

**禁止：** 先刪 remote 再搬內容。

---

## 4. 本機收斂操作（示意，遷完再跑）

```bash
# 遷完且 public augur 已含治權+應用之後：
cd /home/giga/augur
git remote -v          # 應只有 origin → github.com/tsaitsangchi/augur.git
git fetch origin && git checkout main && git pull --ff-only

# 舊應用樹停寫
mv /home/giga/augur-code-work /home/giga/_archived_augur-code-work_$(date +%Y%m%d)

# 驗證
./ops/machines/packs/aitopatom-b96e/setup_check.sh
python3 -m tools.local_llm_mcp selftest
```

`.env` 仍只在本機：`/home/giga/augur/.env`（gitignore），從舊 `augur-code-work/.env` 複製並改 `PROJECT_ROOT`。

---

## 5. 與 T1 的關係

- **現在：** 雙目錄可繼續 T1（PG／qdrant／dump）；應用暫用 `augur-code-work`。  
- **之後：** monorepo 收斂到 `/home/giga/augur` 後，T1 的 `PROJECT_ROOT`／systemd 工作目錄改指同一根。  
- 合倉 **不替代** 資料還原。

---

## 6. 一句話定案

> 學習＋public 前提下：唯一遠端＝`tsaitsangchi/augur`；**唯一本機工作樹＝`/home/giga/augur`**；廢止獨立 `augur-constitution` remote（備份與觀察期後）；密鑰／dump 永不進 git。

---

*文件：`ops/phase2/MONOREPO-LEARNING-MIGRATION.md`｜2026-07-22*


---

## 7. 步 5 觀察期紀錄（2026-07-22）

* GitHub：`tsaitsangchi/augur-constitution` → **`augur-constitution-archived`**（**archived／唯讀**）。
* 說明欄已指向 public monorepo：`https://github.com/tsaitsangchi/augur`（PR #3）。
* 本機舊樹：`/home/giga/_archived_augur-constitution_20260722/`（見同目錄 `OBSERVATION-STEP5.md`）。
* **他機**：若仍追蹤舊 remote，改 clone／改 `origin` 至 public `augur`；勿再向 archived 倉 push。清單：[`../machines/packs/DESKTOP-8MQPFS8/RETARGET-TO-PUBLIC-AUGUR.md`](../machines/packs/DESKTOP-8MQPFS8/RETARGET-TO-PUBLIC-AUGUR.md)（須在 DESKTOP 本機執行；GB10 無直連代跑）。
* **步 6**：DESKTOP 驗收貼回（見該檔 §C）後再刪遠端（本步不刪）。


---

## 8. 步 6 刪遠端紀錄（2026-07-22）

* GitHub 已無 `tsaitsangchi/augur-constitution`／`augur-constitution-archived`（API 404；刪倉完成）。
* 正典唯一遠端：`https://github.com/tsaitsangchi/augur`（`main` monorepo）。
* 他機驗收：`PC002-S1800`（文件舊名 DESKTOP-8MQPFS8）`/home/hugo/project/augur` → `MONOREPO_OK`。
* 本機可選清檔（**未自動刪**）：`/home/giga/_archived_augur-constitution_20260722`、`/home/giga/augur-constitution`、`/home/giga/augur-archive/augur-constitution-*`。

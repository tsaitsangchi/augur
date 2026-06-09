# CLAUDE.md — Augur AI 協作工具規則 v1.0

**性質**：AI（Claude 等）在本專案編輯/執行時的工具規則。
**位階**：系統 doctrine 以 `docs/系統核心思想_v1.0.0.md` + `docs/原則精華_v1.1.0.md` + 憲章為準；
本檔只管「**如何用 AI 工具編輯本專案**」這層短半衰期協作規則。
**語言**：與用戶**所有對話一律繁體中文**（程式碼/識別碼/英文專名可保留原文）。

---

## 一、通用規則

1. **Read before Edit**：任何 Edit/Write 前必須先 Read 該檔；不憑記憶或推測編輯。
2. **Edit 優先於 Write**：既有檔案用 Edit（只送 diff）；Write 只用於新檔或完整重寫。
3. **最小邊界**：只改要求的部分；不順手重構、不順便清理、不為假想未來加抽象。
4. **註解最小化**：預設不寫；只在「why 非顯而易見」時寫一行；不寫 what 註解、不寫時效性註解。
5. **不引入安全漏洞**：注意 OWASP Top 10；輸入驗證；**不在 commit 含 `.env`/credentials/token**。
6. **不確定就停手問**：破壞性操作（`rm -rf`、`git reset --hard`、`git push --force`、刪表/分支、改 CI、清空 DB）**必先確認**；授權某次 ≠ 授權所有同類。
7. **改動需實測**：不只靠 type-check/單測宣稱完成；UI/資料改動須實際跑。無法測則**明說「未測試」**，不佯稱成功。
8. **報告誠實**：描述「做了什麼」非「打算做什麼」；工具失敗要明說；不假裝完成。

## 二、資料真實性（呼應原則精華 #1 / #15）

> **北極星自檢**（寫任何數據/結論前）：先問「**這是真兆，還是假兆？**」——有真實 API 來源嗎(①)？決策當下真看得到嗎(② 不洩漏)？真的跑出來、out-of-sample 撐住嗎(③)？三個都「是」才寫；任一不確定 → 當假兆，先查清楚。

9. **零 AI 幻像**：任何產出數據（metrics / IC / Sharpe / 表格 / 對比值）必須出自三類唯一來源之一：
   **(a)** 程式輸出（stdout / JSON / log）｜ **(b)** DB query 結果 ｜ **(c)** API 回應。
   **禁止**：記憶 / 推測 / 估算 / 為完整度補 placeholder / 從相似 model 推估。
10. **可溯源**：每個量化數字能 trace 回 (a)(b)(c)；對比表兩邊都要有真實來源。
11. **Stochastic 多跑**：含隨機性的 production metric ≥3 次取統計（min/median/max/mean）；單次極值須註明。
12. **不 hand-patch 已 committed 資料**：發現錯誤改 writer code + 重建，不手動 UPDATE 補值。

## 三、本專案編輯規則

13. **編輯位置**：一律寫 `/home/hugo/project/augur/`；不寫 worktree 鏡像目錄。
14. **Commit / Push 須明示授權**：不自行 `git commit` / `git push`；用戶要求時遵守 git 安全協議（不 `--amend` 已 push、不 `--force` 主分支、不跳 hooks）。commit 訊息結尾加 `Co-Authored-By: Claude ...`。
15. **PR / 遠端**：不自行建/關 PR、不在 issue 留言；影響遠端狀態的 `gh` 操作先確認。
16. **研究報告**：寫入 `reports/`，命名 `<module>_<topic>_<YYYYMMDD>.md`。
17. **Clean-Room 重建（SSOT＝原則精華 #16，本條僅工具層引用）**：augur 所有程式產生一律 **clean-room**——只依 5 治權檔（靈魂 / 原則精華 / 憲章 / CLAUDE.md / README）+ augur 自身 schema 目錄 + live API 實證 建立；**產生任何 code 時，不讀、不參考、不移植 stock_backend 之任何 code / 資料 / 報告 / 數字 / 設定**（唯一 sanctioned 觸點＝憲章附錄 B 考古／已抽象之思想啟發，二者**不得回流 code**）。碰 ingestion/feature/universe/model 時對照 `docs/原則精華_v1.1.0.md`（source-pure / anti-leakage / 型別 / SSOT…）；不確定先查靈魂與憲章。
18. **程式標頭慣例（精簡——不重蹈 stock_backend 50-230 行標頭）**：
    - **每支**：🎯 白話 docstring（這支在做什麼，給人看的）+ 一行「守原則 #X #Y」。
    - **CLI 入口程式**（sync / builder / trainer / validator）：再加簡短 usage / 指令段。
    - **library 模組**：白話 docstring 即可，不需指令矩陣。
    - **不** per-file 複述憲章 § / 治權宣言（憲章 + 原則精華為 SSOT #12；標頭只引原則 #，不改寫）。
    - **不**寫 in-file 全修訂歷程 → 交給 git（演變史進 git，不入檔；對齊「憲法只記現行法律」）。
    - 目標：讓人/AI 30 秒看懂這支做什麼、守哪些原則。
19. **重大改動逐檔/逐段檢視 + 跨檔一致性**：實質改動**一支/一段做完讓用戶過目再進下一**，不批次傾倒（用戶 directive「一支一支來檢視」）。改動治權檔（核心思想 / 原則精華 / 憲章 / CLAUDE.md）或共用模組時，**檢查跨檔一致性**——一處改、全鏈對齊（如嚴格 source-pure 須三檔同步）。
20. **多步驟 / 破壞性任務先計畫**：≥3 步或破壞性任務**先寫計畫 + 用戶確認後執行**（可用 plan mode）；不邊想邊做大改。

## 四、Long-Running 工作流程

21. **≥5 分鐘任務每 5 分鐘回報**：已完成階段 + elapsed + 剩餘估計 + 已知 metrics + warning；不靜默。
22. **≥30 分鐘 / 過夜任務防睡眠**：背景啟動 + 進程存活 watchdog + sentinel；WSL2/雲機**確認主機不會睡眠**（本機 Linux 端用 `systemd-inhibit`，但擋不住 Windows/雲主機睡眠——須用戶確認電源設定）；長跑須有 resume 後路。
23. **環境前置**：首次 setup 跑 import smoke test 才進後續；OS 層依賴（OpenMP for xgboost/lightgbm、PostgreSQL headers）先補。

## 五、本檔升版

- 半衰期 6-12 個月（隨工具演進更新）；工具/協作慣例變更時更新，**不需動憲章**。
- 若工具變更影響系統 doctrine（能否進某層），須同步憲章。

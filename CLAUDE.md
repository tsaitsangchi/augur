# CLAUDE.md — Augur AI 協作工具規則 v1.0

**性質**：AI（Claude 等）在本專案編輯/執行時的工具規則。
**位階**：系統 doctrine 以 `docs/系統核心思想_v1.0.md` + `docs/原則精華_v1.0.md` + 憲章為準；
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
17. **新程式對齊原則精華**：碰 ingestion/feature/universe/model 時，對照 `docs/原則精華_v1.0.md`（source-pure / anti-leakage / 型別 / SSOT…）；不確定先查靈魂與憲章。

## 四、Long-Running 工作流程

18. **≥5 分鐘任務每 5 分鐘回報**：已完成階段 + elapsed + 剩餘估計 + 已知 metrics + warning；不靜默。
19. **≥30 分鐘 / 過夜任務防睡眠**：背景啟動 + 進程存活 watchdog + sentinel；WSL2/雲機**確認主機不會睡眠**（本機 Linux 端用 `systemd-inhibit`，但擋不住 Windows/雲主機睡眠——須用戶確認電源設定）；長跑須有 resume 後路。
20. **環境前置**：首次 setup 跑 import smoke test 才進後續；OS 層依賴（OpenMP for xgboost/lightgbm、PostgreSQL headers）先補。

## 五、本檔升版

- 半衰期 6-12 個月（隨工具演進更新）；工具/協作慣例變更時更新，**不需動憲章**。
- 若工具變更影響系統 doctrine（能否進某層），須同步憲章。

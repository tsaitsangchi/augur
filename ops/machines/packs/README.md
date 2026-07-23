# 機器設定包（ops/machines/packs/）

各機一份**營運設定包**——與自動產生的 `ops/machines/<hostname>.md`（硬體快照）互補：

| 產物 | 誰寫 | 內容 |
|---|---|---|
| `ops/machines/<hostname>.md` | `collect_machine_info.sh` | 軟硬體實測數字 |
| `ops/machines/packs/<hostname>/` | 人／Agent 維護 | **此機專用**檢查清單、建議 env、一鍵驗證 |

## 鐵律

1. **錯誤主機拒絕執行**：`setup_check.sh` 必須核對 `hostname`，非本包主機即 exit ≠ 0。
2. **無密鑰**：包內不得放 `.env`、token、DB 密碼（那些仍本機 gitignore）。
3. **共享碼仍共享**：設定包只收「此機差異」；憲章／MCP 程式本體仍走 GitHub 主線。

## 現有包

| 主機 | 角色 | 路徑 |
|---|---|---|
| `aitopatom-b96e` | 治理 + 本地推論／語意記憶（GB10） | [aitopatom-b96e/](aitopatom-b96e/) |
| `DESKTOP-8MQPFS8` | 開發／驗證 + 資料層（WSL2 · GTX 1650） | [DESKTOP-8MQPFS8/](DESKTOP-8MQPFS8/)（精簡 stub） |
| `PC002-S1800` | 開發／驗證 + 資料層（WSL2 · i5-10500 · 無獨顯） | [PC002-S1800/](PC002-S1800/) |

---
name: guard-mechanisms-that-silently-fail
description: "防呆機制自己壞掉且不出聲的四種型態(欄名錯被 except 吞、測試靜默 skip、斷言掃到自己、字面斷言驗不到真行為);判斷句「這個機制若壞了,會不會安靜地變成綠燈?」"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-27T12:49:45.896Z
---

**augur 反覆出現的一類 bug:不是功能沒寫,而是「防止 X 的機制」自己失效且不出聲**——外觀全綠,實際沒在看。2026-07-27 一天內撞到四次。

**四種型態(皆實犯,非假想):**

1. **欄名錯 + 寬 except 吞掉** — `heavy_slot.defer()` 寫 `(axis,task,reason,payload)`,實表欄是 `(axis,step_key,reason,detail)`;`UndefinedColumn` 被 `except Exception` 接成一行 stderr → **「不 silent skip」的機制本身 silent skip**,實測落地 0 列。
2. **測試靜默 skip** — 以 `PGDATABASE`/`PGHOST` 環境變數名當「有沒有 DB」旗標,但連線參數住 `augur.core.config` → 有庫時 live 層照樣 skip,等於白寫。**改成真的連連看再決定 skip。**
3. **斷言掃到自己** — 稽核器把自己寫的判準文字也掃進去而假紅(A12 讀整檔含自身斷言字串、heavy_slot 掃到自測合法的 `db.connect`、A7 因 `ver-if-y` 內含 `if` 使 `(if|elif|while)` 自我命中)。修法是**縮到正確射程**(排除自身檔案/只掃取鎖路徑),不是放寬判準。
4. **字面斷言驗不到真行為** — 「原始碼裡有 `evolution_deferred_work` 字樣」通過了,但那列根本插不進去。**會寫的東西就要真寫一次再刪**;會判的東西就餵一次真資料。

**判斷句(寫任何 guard/assert/test 時自問):「這個機制如果壞了,會不會安靜地變成綠燈?」** 會 → 就得有一條讓它**大聲失敗**的路:真插一列、真連一次、rc≠0、或把「零筆」明白印成「零筆 ≠ 全過」。

**相關**:[[eval-boilerplate-floor]](分數高≠有能力,同一家族的自我欺騙)、[[audit-attestation-falsegreen]](audit 曾假綠:死表空視窗靜默 PASS)、[[augur-mechanical-gate-gaps]](機械閘缺口盤點)、[[cross-claim-contradiction-check]]。

**另一半是好習慣救的**:`install_cron.sh` 的無參數唯讀比對擋下了我寫進 cron 註解的反引號被 heredoc 命令替換;而同一天上午 crontab 被清空,正是因為沒先看輸出就 `sed | crontab -`。**先唯讀比對、再 apply**。

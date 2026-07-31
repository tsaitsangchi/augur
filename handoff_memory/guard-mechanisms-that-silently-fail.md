---
name: guard-mechanisms-that-silently-fail
description: "防呆機制自己壞掉且不出聲的型態(欄名錯被 except 吞、測試靜默 skip、斷言掃到自己、字面斷言驗不到真行為、庫級放行冒充逐item、機器覆寫人裁);判斷句「這個機制若壞了,會不會安靜地變成綠燈?」＋「這個綠燈量的是不是它宣稱在量的東西?」"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-31T10:27:26.570Z
---

**augur 反覆出現的一類 bug:不是功能沒寫,而是「防止 X 的機制」自己失效且不出聲**——外觀全綠,實際沒在看。2026-07-27 一天內撞到四次。

**四種型態(皆實犯,非假想):**

1. **欄名錯 + 寬 except 吞掉** — `heavy_slot.defer()` 寫 `(axis,task,reason,payload)`,實表欄是 `(axis,step_key,reason,detail)`;`UndefinedColumn` 被 `except Exception` 接成一行 stderr → **「不 silent skip」的機制本身 silent skip**,實測落地 0 列。
2. **測試靜默 skip** — 以 `PGDATABASE`/`PGHOST` 環境變數名當「有沒有 DB」旗標,但連線參數住 `augur.core.config` → 有庫時 live 層照樣 skip,等於白寫。**改成真的連連看再決定 skip。**
3. **斷言掃到自己** — 稽核器把自己寫的判準文字也掃進去而假紅(A12 讀整檔含自身斷言字串、heavy_slot 掃到自測合法的 `db.connect`、A7 因 `ver-if-y` 內含 `if` 使 `(if|elif|while)` 自我命中)。修法是**縮到正確射程**(排除自身檔案/只掃取鎖路徑),不是放寬判準。
4. **字面斷言驗不到真行為** — 「原始碼裡有 `evolution_deferred_work` 字樣」通過了,但那列根本插不進去。**會寫的東西就要真寫一次再刪**;會判的東西就餵一次真資料。

**判斷句(寫任何 guard/assert/test 時自問):「這個機制如果壞了,會不會安靜地變成綠燈?」** 會 → 就得有一條讓它**大聲失敗**的路:真插一列、真連一次、rc≠0、或把「零筆」明白印成「零筆 ≠ 全過」。

---

## 2026-07-31 續:同一個病的第二種問法——**「這個綠燈量的是不是它宣稱在量的東西?」**

該日四路平行稽核＋主 session 逐項親驗,抓到 **7 個實例**,不是七個獨立 bug:

| 綠燈 | 實際量的東西 |
|---|---|
| KH depth 7(145,948 件) | 只是 `has_text ∧ KH4 eligible`——KH2/5/6/7 皆**庫級恆 pass** |
| `constitution_lint report` 7/7 PASS、缺口 0 | 「下層文件有沒有**引到**這個條號」,不是義務有沒有做到(同時 `audit` 自陳 P3/P4 骨架未實作) |
| `run_evolution_iteration --selftest` 全綠 | 「例外被接住了嗎」,不是「這筆紀錄落得了帳嗎」 |
| `validation_evidence` 19/19 綠 | 不會紅的斷言(5 條 manual 對紅燈永久免疫) |
| LAIEVO robot 臂過地板 | 零知識格式機贏過受測臂 |
| 「人簽唯人」 | 一支 CLI 的 `isatty()`;`governance_proposal` 對 `decided_by` **零 CHECK** |
| OCV 單向棘輪 | 全 repo `.py` 僅 1 處提及,**零機械實作**;表由被評估者手寫 |

**三個新型態(補 1-4):**

5. **庫級放行冒充逐 item** — `KH6` 只要 `knowhow_interaction_probe_run` 有任一列即放行全庫 28 萬件,而該表**無任何 item 級欄位**;`KH5` 後路 `if snap["domain"]` 而 domain 零 NULL。**判法:讀該判準的 SQL,看 WHERE 有沒有綁到被判的那個個體。**
6. **機器覆寫人裁且無痕** — `verify_validation_evidence.py` 之 `nn = note or "斷言為假"` 使 `COALESCE(%s,status_note)` 成死碼,每跑必覆寫;該表 trigger=0、無 pre-image ⇒ hugo 的拍板逐字理由被抹掉。**修法是分欄(machine_note vs status_note),不是改 COALESCE**——兩者本是不同種類的東西,同欄則任一方的正確行為都毀掉另一方。
7. **凍結了判準文字,沒凍結判準的實作** — `V2-SUNSET` 之 (a) 凍結原文寫「方向門**有可讀數**」,判定程式 `report_triple_evolution_week.py` 要求 `evaluated_pass>0`(門**通過**)。`prereg_gate_no_goalpost` trigger 守 DELETE/終態/`criteria_sha`,**守不到解釋 criteria 的那支程式**。往嚴改也是挪門柱,且本專案有明文程序(升嚴走 GATE-raise 開新列)未走。**§8.1 解釋權專屬 Steward,AI 不得代判。**

**回歸鎖唯一有效驗法(該日確立)**:寫完後**把修正退回壞版,確認斷言真的變紅**。只跑綠燈不算數——那正是它上次騙過我的方式。實作:自測之假例外須帶**真實型別的 payload**(`TimeoutExpired.stdout` 即使 `text=True` 仍是 **bytes**),斷言須驗**終態可用性**(`json.dumps` 不拋 ＝ 真的落得了帳),而非「例外被接住」。

**相關**:[[eval-boilerplate-floor]](分數高≠有能力,同一家族的自我欺騙)、[[audit-attestation-falsegreen]](audit 曾假綠:死表空視窗靜默 PASS)、[[augur-mechanical-gate-gaps]](機械閘缺口盤點)、[[cross-claim-contradiction-check]]、[[kh0-coverage-vs-quality]](KH 覆蓋≠品質)、[[never-type-human-signature]](人簽不代打——本則型態 6 是其鏡像面:不是我去寫人簽,是程式把人寫的抹掉)。

**另一半是好習慣救的**:`install_cron.sh` 的無參數唯讀比對擋下了我寫進 cron 註解的反引號被 heredoc 命令替換;而同一天上午 crontab 被清空,正是因為沒先看輸出就 `sed | crontab -`。**先唯讀比對、再 apply**。

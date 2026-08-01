# [DRAFT 呈案] B3｜drain 補跑器 stale-hold 護欄＋timer 修好再重啟（未經拍板不得施作）

> **狀態**：DRAFT 呈案——W2 批（登錄冊 2026-08-01 §3 B3）；**未經 Steward 拍板不得施作**。
> **L6.18(c) 自我利益揭露**：本案由 AI 修改 AI 自建之自動化機制（drain 是全 repo 唯一會自動 spawn 重活補跑的排程之一）並提請重啟 hugo 已停用之 timer。變更方向為**收縮**自主行動射程（rerun 加 stale-hold 閘）非擴張；L6.16 四項對照：人類介入點數**增**（stale→人裁新增一介入點）、否決可達性不變（timer 隨時可 stop）、揭露比例不變（--check／journal 全印）、最大自動鏈長不增（timer→drain→單筆補跑，未加鏈節）——**單向棘輪未弱化**。重啟動作本身＝hugo 親跑 systemctl（人類授權落點）。
> **撰寫**：2026-08-01 15:21（六）；施作前置＝**B2 已 COMMIT 驗收＋B1-apply 已跑**（登錄冊 CR4 固定序 B2→B1→B3）。

---

## §1 問題與授權鏈

**問題**：drain timer（`augur-drain-deferred.timer`，每 30 分）已被 hugo 於 07-31 停用。病因不在機制——「餓死三日之修」的補跑腿是對的——而在**內容**：`decide()` 對無佐證積壓一律判 rerun、無論多舊，導致 07-31 17:21 最後一次發車撿起 3 天前的 #4 補跑，**燒道 13.3 小時（17:21→翌日 06:47）並把 07-31 23:00 夜輪餓死 3 小時（產生 #11）**。裁決建議單 B3 條：**修好再重啟（非停用）**——前置 B2 清帳、`decide()` 加 stale-hold（>72h ⇒ hold，判準=Steward 輕裁），然後 `systemctl --user start`。

**授權鏈**：
- 呈案＝登錄冊 §3 B3（分派 W3-b，「判準 Steward 輕裁＋AI」）＋裁決建議單 B3 條。
- 施作授權＝Steward 圈選「**B3-同意**」（含門檻值批註，§4）；code diff 由 AI 施作（執行層）＋selftest 實證（#7）；**timer 重啟由 hugo 親跑**（翻轉 hugo 本人之停用態，不由 AI systemctl）。
- 固定序（登錄冊 CR4）：B2（帳本歸零）→ B1-apply（run 11–19 殭屍回填）→ **B3**。

---

## §2 現況親驗（2026-08-01 15:21；全部唯讀）

### 2.1 timer 現況：runtime 停、install 態仍 enabled（⚠ 重開機自動復活）

- stamp 檔 `~/.local/share/systemd/timers/stamp-augur-drain-deferred.timer` mtime＝**Jul 31 17:21**＝最後一次發車；同目錄其他 augur timer 08-01 皆有新 stamp（audit-watchdog 14:52、l2 06:15、embed 03:30…）⇒ drain runtime 確已停。
- **enable symlink 仍在**：`~/.config/systemd/user/timers.target.wants/augur-drain-deferred.timer` 存在＋unit `Persistent=true` ⇒ **重開機（或 default.target 重掛）即自動復活**。在 B2 施作前復活＝立即對 7 筆全 rerun（B2 呈案 §2.4）。
- unit 內容（親讀）：service＝oneshot 跑 `drain_deferred_work.py --apply --limit 1`；timer＝`OnBootSec=10min / OnUnitActiveSec=30min / Persistent=true`；drop-in `augur-drain-deferred.service.d/onfailure.conf`＝`OnFailure=augur-alert@%n.service`（C4′ sink 已掛，失敗會落 `~/logs/alerts.log`）。
- 註：登錄冊 CR2 已否決 `install_services.sh` 路（該腳本無條件 `enable --now` drain timer＋restart 六常駐服務）；本案重啟僅用單一 `systemctl --user start`。

### 2.2 `decide()` 現行簽名與判準（`scripts/drain_deferred_work.py:61-72` 親讀）

```python
def decide(axis: str, step_key: str, superseded_ref: str | None) -> tuple[str, str]:
    """純函式判準（可自測）：這筆積壓該怎麼處置。

    superseded 佐證存在 → 清帳（附佐證）；無佐證且在 rerun 白名單 → 補跑；
    其餘 → hold（誠實留帳、印明需人工，**不得為了清而清**）。
    """
    if superseded_ref:
        return "superseded", f"已被積壓時點後之成功輪涵蓋：{superseded_ref}"
    if (axis, step_key) in RERUN_CMDS:
        return "rerun", "無涵蓋佐證 → 補跑（rc=0 才清）"
    return "hold", (...)
```
**無任何時齡概念**——3 天前的積壓與 30 分鐘前的一視同仁判 rerun。`--check` 親驗（08-01 15:2x）：現存 7 筆未清**全判 rerun**（含 4 筆測試探針）。呼叫端恰兩處（:115 check、:130 apply）＋selftest 五處（:181-190）；全 repo 無其他 import 者（grep 親驗）。selftest 現行 **GREEN（12 checks, rc=0）**＝改動前基線。

### 2.3 白燒之實證鏈（為何 72h stale-hold 是對的修法）

07-31 17:21 timer 發車 → 撿 #4（當時已 66h 舊）→ spawn `run_evolution_iteration --run --slot-wait 600` → 續跑 open 之 r01：I3 跑 18:19→08-01 04:11（10h）→ 佔道使 07-31 23:00 夜輪等滿 10800s 落 #11（`twevo.log` 親驗）→ r01 08-01 06:47 閉帳 failed。**舊積壓補跑（低價值）餓死當夜新輪（高價值）**＝stale 積壓不該自動重跑之直接證據。
另注意：stale-hold **不能取代 B2**——以此刻時齡計：#4≈88h（>72 會擋）但 #5≈64h、#7-10≈42h、#11≈37h（<72 **不會**擋）⇒ 探針與近期積壓仍會被 rerun。**B2 清帳是硬前置，stale-hold 是防未來復發的縱深**。

---

## §3 方案

### §3.1 code diff（`scripts/drain_deferred_work.py`；逐 hunk，行號＝現行檔）

**Hunk 1｜:45 後加 import**
```python
 import subprocess
 import sys
+from datetime import datetime, timezone
 from pathlib import Path
```

**Hunk 2｜:51 後加判準常數**（`DRAIN_LOCK = "/tmp/augur_drain.lock"` 之後）
```python
+# stale-hold 判準（B3 呈案 2026-08-01;值=Steward 輕裁）：無佐證且積壓逾此時齡者不自動補跑。
+# 實證：07-31 撿 66h 舊積壓補跑,燒道 13.3h 並餓死當夜 23:00 新輪（twevo.log/#11）。
+STALE_HOLD_HOURS = 72.0
```

**Hunk 3｜:61-72 `decide()` 全文替換**（簽名收緊＝必帶 age_hours，漏改呼叫端即 TypeError fail-loud）
```python
def decide(axis: str, step_key: str, superseded_ref: str | None,
           age_hours: float) -> tuple[str, str]:
    """純函式判準（可自測）：這筆積壓該怎麼處置。

    superseded 佐證存在 → 清帳（附佐證；不受 stale 限制——有證據的清帳永遠誠實）；
    無佐證且積壓逾 STALE_HOLD_HOURS → hold（過期補跑恐非原語境,留帳待人裁）；
    無佐證且在 rerun 白名單 → 補跑；其餘 → hold（**不得為了清而清**）。
    """
    if superseded_ref:
        return "superseded", f"已被積壓時點後之成功輪涵蓋：{superseded_ref}"
    if age_hours > STALE_HOLD_HOURS:
        return "hold", (f"積壓已 {age_hours:.0f}h（>{STALE_HOLD_HOURS:.0f}h stale 判準）"
                        "→ 過期補跑恐非原語境,留帳待人裁,不自動重跑")
    if (axis, step_key) in RERUN_CMDS:
        return "rerun", "無涵蓋佐證 → 補跑（rc=0 才清）"
    return "hold", ("不在 rerun 白名單（lai 臂重跑需全參數＋eval_code_hash 身分，"
                    "擅代跑＝未預註冊實驗）→ 留帳待 (a) 佐證出現或人工處置")
```

**Hunk 4｜:113-115 `check()` 呼叫端**
```python
-    for did, ax, sk, at, reason, detail in rows:
-        ref = find_superseded_ref(cur, ax, at, detail or {})
-        action, why = decide(ax, sk, ref)
+    now = datetime.now(timezone.utc)
+    for did, ax, sk, at, reason, detail in rows:
+        ref = find_superseded_ref(cur, ax, at, detail or {})
+        action, why = decide(ax, sk, ref, (now - at).total_seconds() / 3600.0)
```

**Hunk 5｜:129-130 `apply()` 呼叫端**
```python
-        ref = find_superseded_ref(cur, ax, at, detail or {})
-        action, why = decide(ax, sk, ref)
+        ref = find_superseded_ref(cur, ax, at, detail or {})
+        age_h = (datetime.now(timezone.utc) - at).total_seconds() / 3600.0
+        action, why = decide(ax, sk, ref, age_h)
```
（`requested_at` 為 timestamptz、psycopg2 回 tz-aware datetime，與 `datetime.now(timezone.utc)` 相減安全；hold 在 apply() 既有行為＝`continue`——stale 列不阻擋其後新鮮列。）

**Hunk 6｜:181-190 selftest 既有五呼叫補 age（新鮮值 1.0，語意不變）**
```python
-    a, w = decide("tw", "run_evolution_iteration", "ledger.uid=X")
+    a, w = decide("tw", "run_evolution_iteration", "ledger.uid=X", 1.0)
     ...（:183/:185/:187/:189 同型，各補第 4 參數 1.0）
```

**Hunk 7｜:190 後新增三 case（回歸鎖須驗紅）**
```python
+    a, w = decide("tw", "run_evolution_iteration", None, 100.0)
+    chk("**stale(>72h) 無佐證 → hold 不補跑**（舊邏輯回 rerun;本 case 在舊碼必紅）",
+        a == "hold" and "stale" in w)
+    a, _ = decide("tw", "run_evolution_iteration", "ledger.uid=X", 100.0)
+    chk("stale 但有佐證 → 仍 superseded（證據清帳不受 stale 限制）", a == "superseded")
+    a, _ = decide("tw", "run_evolution_iteration", None, STALE_HOLD_HOURS)
+    chk("恰等於門檻 → 仍 rerun（嚴格大於才 stale,邊界不誤殺）", a == "rerun")
```

**Hunk 8｜module docstring「清帳之兩條合法路」段補一行**（(b) rerun 之後）
```
+  **rerun 限新鮮積壓**：無佐證且逾 STALE_HOLD_HOURS(72h)者退 hold 待人裁——
+  過期補跑恐非原語境(07-31 實證:66h 舊積壓補跑燒道 13.3h、餓死當夜新輪)。
```

**驗紅程序**（「回歸鎖須驗紅」）：新 selftest 貼回舊碼＝簽名不符 **TypeError 必紅**（fail-loud）；語意紅由 Hunk 7 第一 case 鎖住（舊邏輯對 age=100h 回 rerun≠hold）。施作時以 `git stash`（舊碼）跑新測驗紅、`git stash pop` 後跑 GREEN，兩段輸出貼施作記錄。

### §3.2 重啟程序（前置=B2＋B1-apply；hugo 親跑）

1. **前置確認（機械）**：
   a. B2 驗收全過（B2 呈案 §6；`--check` 印「未清積壓：0 筆」）。
   b. B1-apply 已跑：`SELECT count(*) FROM evolution_run WHERE run_id BETWEEN 11 AND 19 AND status='running'` ＝ **0**。
   c. 本 diff 已落地：`--selftest` GREEN（15 checks）＋驗紅記錄在。
   d. heavy slot 空閒非必要（drain 自己會誠實空轉），但確認無異常行程：`ps aux | grep -E "drain_deferred|run_evolution_iteration"` 無列。
2. **hugo 親跑**：
   ```bash
   systemctl --user daemon-reload            # unit 檔未改,保險步
   systemctl --user start augur-drain-deferred.timer
   ```
   （**不跑 `install_services.sh`**——CR2 否決：會 enable --now＋restart 六常駐服務。unit 本已 enabled，只需 start。）
3. **即時驗證**：`systemctl --user list-timers | grep drain` NEXT 有值；40 分內 stamp 檔 mtime 前進；首發後 `journalctl --user -u augur-drain-deferred.service -n 20` 印「未清積壓：0 筆」、無 traceback。

---

## §4 選項與建議案

| 決點 | 選項 | 建議 |
|---|---|---|
| stale 門檻 | 48h / **72h** / 96h | **72h**（裁決單原值）。48h 在週末停機情境會把週五夜 defer 於週一誤 hold；96h 對「舊積壓餓死新輪」防護太鬆。已知邊界：週末全程關機時週五夜 defer 於週一 boot 補跑時齡 56–80h，**可能**跨 72h 被 hold——後果無害（週一 23:00 cron 自開新輪，hold 列印明待人裁），誠實留帳優於誤補 |
| stale 行為 | hold（留帳印明）/ 自動標 superseded | **hold**。無佐證自清＝「為了清而清」，違本支 docstring 鐵律 |
| rerun 白名單 | 保留 tw 一項 / 清空（drain 退化為純佐證清帳器） | **保留**。清空＝機制自宮，違裁決單「病在內容不在機制」 |
| timer | 修好再重啟 / 續停 / 停用（disable） | **修好再重啟**（裁決單原案）。另注意：現況 enabled＋Persistent＝重開機自動復活，「續停」實際上不是穩定狀態——若 Steward 改裁續停，須改為明示 `disable` 才真停 |

**證偽條件**（裁決單原文）：重啟後一週內再現「每 30 分白燒車道」樣態 ⇒ 回頭停用（機械檢法見 §6-5）。

---

## §5 風險與回滾

- **code 風險低**：純函式改動＋兩呼叫端；簽名收緊 fail-loud（漏改必 TypeError，不會靜默走舊判準）；無 DB schema 變更、無新依賴。回滾＝`git revert` 單 commit。
- **timer 風險受控**：隨時 `systemctl --user stop augur-drain-deferred.timer` 收回；OnFailure sink 已掛（onfailure.conf 親驗），服務失敗會落 `~/logs/alerts.log`＋週報近 7 日 alerts 段可見。
- **順序風險**：若跳過 B2 先重啟＝每 30 分對 7 筆積壓（含 4 探針）判 rerun、單筆潛在燒道 10h+ 並與 08-03 起的夜輪 cron 搶道——**固定序 B2→B1→B3 不可倒置**；本呈案施作段以 §3.2-1a/1b 機械前置擋住。
- **已知無害邊界**：週末停機致週五夜 defer 被 stale-hold（§4）；hold 列會在每次 --check／journal 印明，不靜默。

---

## §6 驗收判準（機械可判）

1. `venv/bin/python scripts/drain_deferred_work.py --selftest` → **GREEN、15 checks、rc=0**（原 12＋新 3）。
2. 驗紅記錄：舊碼＋新測＝RED（TypeError 或 stale case 紅）之輸出留檔於施作記錄。
3. `--check` 於積壓 0 時印「未清積壓：0 筆」rc=0；對人造 stale 情境（僅文件推演，不造假列入庫）判準函式回 hold。
4. timer 重啟後：`list-timers` NEXT 非空；40 分內 stamp mtime 前進；首發 journal 無 traceback。
5. **一週觀察窗**（至 08-08）：`journalctl --user -u augur-drain-deferred.service --since <重啟時點> | grep -c "補跑："` ＝ **0**（積壓 0 ＋ 週間新 defer 若生、超 72h 前應已被 rerun 清掉或被佐證清掉；出現對 #4–#11 任何補跑＝B2 證偽、出現每 30 分連續補跑樣態＝B3 證偽 → 回頭停用）。
6. `~/logs/alerts.log` 無 augur-drain-deferred 失敗列（有則依 sink 內容處置）。

---

## §7 Steward 決定欄

（留白——圈選格式：`B3-同意`（默認 72h）/ `B3-同意-門檻__h` / `B3-改採____`；timer 重啟時點請一併批註）

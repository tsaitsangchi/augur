# OPT-SIM-EVO P0 第一刀｜觀測＋零 DB selftest [I]

> **時點**：2026-08-04 ≈08:12+08  
> **授權**：`OPT-SIM-EVO-20260804-go` 伴隨裁——run22 running 期間僅 **觀測＋儀器設計＋零 DB selftest**  
> **範圍**：P0-A 監看＋Lane-SIM-DOC selftest；**未** Lane-SIM-APPLY／未搶 `heavy_slot`／未改 evolution driver／未 commit  
> **FZ**：keep · **GATE**：keep · **M-T5**：watch  
> **#32a**：self-reported 觀測敘事；數字皆出自 stdout／`ps`／埠探測（DB 拒連處明說）

## 1. 指令與 rc

| 指令 | rc | 備註 |
|---|---|---|
| `python3 scripts/decide_sim_verdict.py --selftest` | **0** | 零 DB；全通過 |
| `python3 scripts/check_sim_clock.py --selftest` | **0** | 零 DB；含「不 acquire heavy_slot」 |
| `python3 scripts/check_parallel_capacity.py --selftest` | **0** | 零外依；含不呼叫 acquire |
| `python3 scripts/evaluate_sim_calibration.py --selftest` | **0** | 零 DB；SELFTEST PASS |
| `python3 scripts/settle_sim_outcomes.py --selftest` | **0** | 零 DB |
| `python3 scripts/propose_sim_candidate.py --selftest` | **0** | 零 DB＋FakeCursor |
| `python3 scripts/run_sim_calibration_cell.py --selftest` | **0** | 零 DB；格點／防衛／ledger SQL |
| `python3 scripts/migrate_sim_evolution_ddl.py --selftest` | **0** | 免 DB；GREEN |
| `python3 scripts/observe_twevo_run22.py --selftest` | **0** | 零 DB 純函式；**未**跑 `--morning` |
| `pg_isready -h 127.0.0.1 -p 5432` | 無回應 | Connection refused |
| `augur.core.heavy_slot.holder_status()` | 例外 | `OperationalError`：5432 refused |
| `observe_twevo_run22.py --morning` | **未跑** | 需 DB＋結輪語意；本刀禁假綠 |
| 任何 `--run`／`--allow-apply`／sim cell apply | **未跑** | 伴隨裁禁 |

總耗時 selftest 串跑 ≈5.6s（低負載、不與 I3 搶滿核）。

## 2. 唯讀觀測（≈08:12+08）

### 2.1 run22／進程

| 項 | 值 |
|---|---|
| 父 | `pid=254493` `run_evolution_iteration.py --run --slot-wait 10800`；ELAPSED≈**09:12** |
| 子（I3） | `pid=254552` `run_philosophy_evolution.py --local-gates`；ELAPSED≈**09:12**；**%CPU≈60.3** |
| cron 殼 | `pid=254492` |
| 判斷 | **仍 running**（預期量級 I3 7–10h；**未**殺輪、**未**縮逾時） |
| sim／`--allow-apply` 活進程 | **無**（pgrep 無真正 sim apply 作業） |

### 2.2 twevo.log（尾）

- 開輪紀錄：`✓ 開輪 tw-20260803-r01(trigger=TWEVO-S2-go;apply_allowed=false)`
- 史料：舊輪 `TimeoutExpired … 7200 seconds`（07-28 軸）；**不得**與現行 I3 混讀成「本輪已炸」
- 開輪後無進一步 flush 之步結（與計畫 §2.1 一致）

### 2.3 DB／slot／sim 表

| 項 | 結果 |
|---|---|
| PostgreSQL `:5432` | **拒連**（TCP／`pg_isready`） |
| `heavy_slot` 鎖態 | **不可讀**（CLI 需 PG）——引用 step r2 01:04 史料：`owner=tw_iteration`；**本視點不宣稱現鎖列** |
| `evolution_run` 22 列 | **未查**（B2） |
| `mc_simulation_run`／`sim_run_link`／時鐘水位 | **未查**（B2／B4 仍「未知」） |

## 3. 發現（對 P0）

| ID | 狀態 |
|---|---|
| **B1** run22 佔槽 | **仍成立** → Lane-S／SIM-APPLY／LAIEVO 重活禁 |
| **B2** PG 拒連 | **仍成立** → 儀表／morning／P0-D 數字帳卡死 |
| **P0-A** | **部分完成**——ps／log 誠實；DB 儀表降級為「拒連」 |
| **零 DB selftest** | **9/9 rc=0**——sim 工具鏈純函式鎖綠 |
| **P0-C／P0-D** | **不可驗收**——缺終態＋缺 DB |
| **P0 整階段綠燈** | **未達**（須結輪誠實 audit＋首格狀態非未知＋零搶槽） |

## 4. 是否可進 P0 下一項？

| 下一項 | 可否現在開 | 條件 |
|---|---|---|
| **P0-B** PG 復通哨 | 僅持續偵測 | 起停屬運維／人；AI 不假稱已通 |
| **P0-C** 結輪 OBS | **否** | 待 run22 終態＋DB |
| **P0-D** 首格盤點 | **否** | 待 DB；且禁 `--apply` |
| **P1 儀器設計（文件）** | **是**（伴隨裁允許） | 零寫庫／零搶槽；勿滿載 CPU |
| **Lane-D**（N7／043 起草） | **是**（計畫 §5） | 與本專項無關衝突；仍 FZ-keep |
| **Lane-SIM-APPLY／首格** | **否** | 須 slot 空＋DB＋Steward 另裁 |

**結論**：第一刀（觀測＋零 DB selftest）**已收口**；P0 未整綠。可並行推進 **P1 儀表設計（文件）** 或 **Lane-D 起草**；DB／結輪相關 P0 子項須等。

## 5. 下一步建議（AskQuestion）

1. **繼續儀器設計**——開 P1-1 共槽儀表／P1-4 模型檔位卡草稿（零寫庫、可與 run22 並行）  
2. **等結輪**——維持 P0-A 監看；DB 復通後立刻 heavy_slot＋`observe … --morning`  
3. **Lane-D**——轉一般 step 之 N7／043 起草（錯開 sim APPLY）

## 6. 本波未做（明示）

- 不改 `run_evolution_iteration`／I3 driver  
- 不 `--allow-apply`／不 sim cell apply  
- 不搶／不釋放 `heavy_slot`  
- 不殺 run22  
- **不 commit／push**（拍板檔由另一 agent 推）

---

*完。self-reported（#32a）。*

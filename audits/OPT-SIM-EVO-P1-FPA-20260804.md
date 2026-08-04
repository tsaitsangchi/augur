# OPT-SIM-EVO P1｜FP-A 假兆詞探針骨架 [I]

> **時點**：2026-08-04  
> **授權**：Steward 選「實作最小探針 FP-A 骨架＋`--selftest`」  
> **設計**：`reports/augur_sim_evo_p1_instruments_design_20260804.md` §4.2 FP-A  
> **硬紀律**：零 DB · 不搶 `heavy_slot` · 不 `--apply` · 不改 evolution · FZ-keep · **不 commit**  
> **#32a**：self-reported；數字皆 stdout／本檔突變實測

## 1. 交付

| 項 | 路徑／結果 |
|---|---|
| 腳本 | `scripts/probe_sim_false_signal_lexicon.py` |
| 純函式 | `find_bare_claims(text)` —— 裸「可交易／確立級」；否定位白名單見 `NEGATION_PREFIXES` |
| 指令矩陣 | 無參數印矩陣（rc=0）；`--selftest`／`--check`／`--text` |

## 2. 實測 rc

| 指令 | rc | 備註 |
|---|---|---|
| `python3 scripts/probe_sim_false_signal_lexicon.py` | **0** | graceful 印矩陣 |
| `python3 scripts/probe_sim_false_signal_lexicon.py --selftest` | **0** | 零 DB；13 斷言全綠 |
| `… --text 'sim 校準通過故可交易'` | **1** | 探針判紅（1 hit＝可交易）|
| `… --text 'sim 校準≠可交易≠確立級'` | **0** | 否定位綠 |
| `python3 scripts/check_cmd_matrix.py` | **0** | NEED=0；受檢含本檔 |
| `python3 scripts/check_false_assertions.py --scan --path scripts/probe_sim_false_signal_lexicon.py` | **0** | ERROR 0／WARN 0 |

## 3. 先驗紅證（#35）

### 3.1 設計指定壞句（偵測臂必紅）

| fixture | 結果 |
|---|---|
| `sim 校準通過故可交易` | hits=`['可交易']` @start=9；`--text` → rc=1 |
| `本輪已過確立級，可交易進場` | hits=`['可交易','確立級']` |

### 3.2 突變弄壞本尊 → selftest 必紅

手續：臨時將 `find_bare_claims` 改為開頭 `return []`（MUTANT），跑 `--selftest`：

| | |
|---|---|
| mutant `--selftest` | **rc=1**；紅向 5 條 ✗（壞句無 hit；本尊＝壞臂）|
| 還原後 `--selftest` | **rc=0** |

**結論**：鎖壞了不會安靜綠——先驗紅成立（本 audit 留證；本任務不 commit）。

## 4. 明確未做

- 未 `HeavySlot.acquire`／未寫任何 sim 生產表  
- 未開 FP-B／C／D／E；未實作 P1-1 dashboard  
- 未對預設 glob 全庫 `--check` 當「文件已潔淨」驗收（設計／計畫 meta 句本身會列詞；升嚴／清稿另裁）  
- 未 commit／push  

## 5. AskQuestion（請 Steward 裁）

1. **接 FP-B**（混尺詞／`gain_basis`）骨架？  
2. **commit** 設計＋P0 OBS＋本 FP-A（脚本＋本 audit）？  
3. **等結輪**（維持僅 DOC／selftest，待 run22＋DB）？

---
status: executed
series: s3_macro_stock
go: audits/S3-MACRO-STOCK-BUILD-GO-20260805.md
contract: audits/S3-MACRO-STOCK-CONTRACT-20260805.md
self_reported: true
---

# EXECUTED｜S3-MACRO-STOCK-BUILD · 2026-08-05

> **GO**：`S3-MACRO-STOCK-BUILD-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **碼**：`src/augur/features/macro_stock.py` · `scripts/build_macro_stock_candidates.py`  
> **self-reported（#32a）**；數字＝stdout `/tmp/macro_stock_build.log`

---

## 1. 材料化（`feature_candidate_values`）

| feature | n | panel 窗 | distinct stocks |
|---|---:|---|---:|
| `stock_beta60_x_vix` | **36,804** | 2014-12-31→**2026-08-04** | 760 |
| `stock_ret20_x_t10y2y_chg` | **36,104** | 2015-12-31→2026-08-04 | 684 |
| `mkt_vix_broadcast` | **36,805** | 2014-12-31→2026-08-04 | 760 |
| **合計寫入/更新** | **109,713** | | |

- selftest：`python -m augur.features.macro_stock --selftest` **PASS**  
- **未**寫 `feature_values`／**未** prodset／**未** `#11`／**未** Tier-B  

---

## 2. 單因子 IC

### pan-hist

| feature | H20 IC／HAC-t／勝率／n | H60 IC／HAC-t／勝率／n |
|---|---|---|
| `stock_beta60_x_vix` | −0.0049／−0.24／0.54／106 | +0.0073／+0.22／0.50／104 |
| `stock_ret20_x_t10y2y_chg` | −0.0061／−0.42／0.45／103 | −0.0029／−0.26／0.48／101 |
| `mkt_vix_broadcast` | **n/a**（截面無變異——對照臂預期） | **n/a** |

### as-of

| feature | H20 IC／HAC-t／勝率／n | H60 IC／HAC-t／勝率／n |
|---|---|---|
| `stock_beta60_x_vix` | −0.0107／−0.52／0.54／106 | −0.0008／−0.02／0.48／104 |
| `stock_ret20_x_t10y2y_chg` | −0.0058／−0.40／0.50／103 | −0.0082／−0.75／0.49／101 |
| `mkt_vix_broadcast` | n/a | n/a |

---

## 3. 判定（對 CONTRACT §6）

| 尺 | 結果 |
|---|---|
| 材料化＋PIT 門 | ✅ 三名落地；broadcast 誠實無截面 IC |
| 異質名 HAC \|t\|≥2 | **❌ 皆未過**（|t|≪2） |
| 建議 `S3-MACRO-STOCK-VERIFY-go` | **不建議**本窗——無過門異質名 |
| 股級 macro SKIP「無契約／無 builder」根因 | **契約＋builder 已閉**；**預測力未立**＝另假說或維持候選 |

---

## 4. #3 狀態回寫

| 子項 | 狀態 |
|---|---|
| M0 雙軌 plan | ready |
| M1 CONTRACT | accepted |
| M2 BUILD | **EXECUTED**（本帳） |
| M3 VERIFY | **defer**（未過門） |
| 軌 X β5 | **仍停** |

*完。*

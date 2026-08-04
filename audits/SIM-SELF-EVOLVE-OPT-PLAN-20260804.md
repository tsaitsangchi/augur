# SIM-SELF-EVOLVE-OPT-PLAN 登錄 [I]（2026-08-04）

> **位階**：[I] 計畫登錄／接續留痕（非 META-CONSTITUTION [N]）。  
> **時點**：約 **2026-08-04 11:48+08**（GO）／**11:52+08**（初版 enrichment）／**11:56+08**（latest 重覆驗証 enrichment）  
> **狀態**：**GO-EXECUTED**——計畫＝**approved SSOT**；後續 **acceptance enrichment**（**不撤 GO**）  
> **拍板帳**：`audits/SIM-SELF-EVOLVE-OPT-PLAN-GO-20260804.md`  
> **self-reported（#32a）**：繕寫＝agent；決策者＝Steward（hugo）。

## 標的檔

| 角色 | 路徑 |
|---|---|
| **計畫 SSOT（已拍＋驗收補強）** | `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` |
| **GO-EXECUTED** | `audits/SIM-SELF-EVOLVE-OPT-PLAN-GO-20260804.md` |
| sim 校準專項（已拍） | `reports/augur_local_ai_sim_evolution_plan_20260804.md`（`OPT-SIM-EVO-20260804-go`） |
| 一般優化 step | `reports/augur_optimization_step_plan_r3_20260804.md` |
| 地基 | `reports/augur_project_optimization_plan_20260804.md` |
| 預測⊥API | `audits/PREDICT-ORTHOGONAL-API-RULING-20260724.md`；`.cursor/rules/predict-vs-market-api.mdc` |
| API-THAW-bounded | `audits/API-THAW-20260804.md` |

## Steward 主軸（強制）

Steward 管線原文映射為計畫 **唯一主軸階段地圖**：

| 階段 | Steward 句（latest） | 一句 |
|---|---|---|
| S0 | （計畫） | 定錨／拍板／Discovery；零寫庫零 API |
| S1 | 抓取 FinMind 及 FRED（**資料完整**） | 取數 API 門；⊥預測熱路徑 |
| S2 | raw 交互產生 KH | 概念／關係；非整庫 raw 入靈魂 |
| S3 | 產生股票特徵值（**最佳化特徵完整＋多種特徵重覆驗証**） | 庫內 as-of features／panel＋#11／提拔閘 |
| S4 | 產生模型（**最佳化多種模型重覆驗証**） | 多模型／horizon／多 seed＋八閘→prodset |
| S5 | 產生預測股價（**最佳化準確率的漲跌比率重覆驗証**；＋sim） | OOS／多 seed 漲跌比＋#14；sim 旁軸 |

## 生效碼（§7.1）—**仍生效、不撤**

```text
SIM-SELF-EVOLVE-OPT-PLAN-20260804-go + GATE-keep + NHC-keep + API-THAW-bounded
```

Steward shorthand：`親打計畫內 GO`。  
**不含**（除非另授）：sim `--apply`、`P1-DRIFT: C-go`、放量 sync、Dividend rebuild、Registry COMMIT、kill A1、predict 寫庫。

## 驗收 enrichment（2026-08-04；不撤 GO）

### Latest（supersede prior parentheses where richer）

Steward 原文（逐字）→ 計畫 §0.5：

```
本地AI股市預測模擬自進化計畫
→抓取finmind及fred資料(資料完整)
→raw data交互產生KH
→產生股票特徵值(最佳化特徵完整，最佳化多種特徵值重覆驗証)
→產生模型(最佳化多種模型重覆驗証)
→產生預測股價(最佳化準確率的漲跌比率重覆驗証)
```

階段驗收一語：

| 階段 | 括號（latest） | 驗收一語 |
|---|---|---|
| S0 | （計畫） | GO 仍生效＋Discovery 五項證據；零寫庫零 API |
| S1 | **資料完整** | THAW-bounded 熱路徑 as-of 完整（**≠**全 339 表）；缺席誠實記帳；**doctrine 不變** |
| S2 | （doctrine） | raw 交互→可核 KH 概念／關係；非整庫 raw 入靈魂；**doctrine 不變** |
| S3 | **特徵完整＋多種特徵重覆驗証** | 多特徵＋提拔閘（as-of＋HAC-t）＋#11 ≥3／多 seed＋prodset **誠實**覆蓋 |
| S4 | **多種模型重覆驗証** | 多模型／horizon＋多 seed＋八閘→人 APPLY→prodset／artifact；#14 可溯 |
| S5 | **漲跌比率重覆驗証** | OOS folds／多 seed direction accuracy／漲跌比＋#14；**禁假確立級**；sim 分尺 |

詳見計畫 §0.5／各階段「驗收」列；§8 自檢項 6–8。  
本登錄＝薄指針；**零碼／零 API／零 sim-apply**。

## 正文強制邊界（已入計畫散文）

1. **Predict／train／sim ⊥ live API**——DB as-of；S1 sync 分離；`--skip-sync`。  
2. **KH＝raw interaction 概念／關係**——禁整庫 raw 入靈魂。  
3. **Anti-leakage**；**經濟終關 #14**；**禁假關確立級**（`evaluated_pass` 唯門二）。  
4. Schema＋python＋分波＋GO phrases 齊備（見計畫 §2–§7）。  
5. **括號驗收**＝可測終態定義（含 latest **重覆驗証**）；**≠**默授執行開工碼。

## 本質 enrichment（2026-08-04；不撤 GO）

> **一句**：本計畫＝**S1→S5 自我進化閉環計畫書**（非線性 checklist）。留痕＝`audits/SIM-SELF-EVOLVE-ESSENCE-S1S5-LOOP-20260804.md`；計畫 §0.0。

## 閉環 enrichment（2026-08-04；不撤 GO）

C0／C1／C2＝**同一閉環**之弧段別名（非三套平行 SSOT）。

| 代號 | 範圍 | 詳細 | 登錄 |
|---|---|---|---|
| **C1** | S3→S2→擴大 S1→重驗 S2／S3（Arc A／B／C） | `reports/augur_s1_s2_s3_closed_loop_plan_20260804.md`（Arc A＝`augur_s2_kh_optimize_after_s3_plan_20260804.md`） | `audits/SIM-S1-S2-S3-CLOSED-LOOP-20260804.md` |
| **C2** | S4↔S5 | `reports/augur_s4_s5_closed_loop_plan_20260804.md` | `audits/SIM-S4-S5-CLOSED-LOOP-20260804.md` |
| **C0** | 全鏈總圖（＝本質） | parent §0.8 | `audits/SIM-SELF-EVOLVE-ESSENCE-S1S5-LOOP-20260804.md` |

GO：C1＝`LOOP-S3-TO-S2-go`／`LOOP-S2-TO-S1-EXPAND-go`／`LOOP-CYCLE-N-go`（狀態見該弧 audit）；**C2／C0 已授**（2026-08-04）＝`LOOP-S4-TO-S5-go`／`LOOP-S5-TO-S4-OPT-go`／`LOOP-FULL-CHAIN-go` → `audits/LOOP-S4-S5-FULL-GO-20260804.md`（≠一鍵全鏈重建／≠predict 寫／≠sim apply）。

## 下一步（機械提醒）

1. **S0 Discovery（§2.7）**——**DONE**（`audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md`）；本登錄不重寫該帳。  
2. 預測主刀另待 `P1-DRIFT: C-go | FZ/GATE-keep | no-SIM-apply | skip-sync`。  
3. C1 另待 `LOOP-S3-TO-S2-go`／`LOOP-S2-TO-S1-EXPAND-go`／`LOOP-CYCLE-N-go`（零 sync／零 build／不殺 A1 直至明示）。  
4. C2 另待 `LOOP-S4-TO-S5-go`／`LOOP-S5-TO-S4-OPT-go`（零 train／零 predict 寫直至明示）。  
5. sim apply／首格另待 §7.3 明示碼。  
6. 各階段開工時對照計畫 §0.5 **latest** 括號驗收（含重覆驗証），不以 enrichment 倒推已執行。

---

*完。[I] 登錄 → GO-EXECUTED＋acceptance enrichment（latest＝重覆驗証）＋本質＝S1→S5 閉環＋C1／C2／C0＝弧段別名。*

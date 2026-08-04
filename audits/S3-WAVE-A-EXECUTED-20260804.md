# EXECUTED｜S3-WAVE-A · 2026-08-04

> **位階**：[I] 執行帳  
> **GO**：`audits/S3-WAVE-A-GO-20260804.md`（Steward 原文 `S3-WAVE-A-go | FZ/GATE-keep | skip-sync | no-SIM-apply`）  
> **SSOT**：`reports/augur_s3_features_for_market_model_families_20260804.md` §3 **S3-A**＝組 1–7  
> **前置**：`audits/S3-FEATURES-PLAN-GO-20260804.md`  
> **self-reported（#32a）**：判讀為呈案；數字＝(a) stdout／(b) DB

---

## 1. 做了什麼

| 步 | 結果 |
|---|---|
| 登錄 GO | `audits/S3-WAVE-A-GO-20260804.md` |
| 庫內覆蓋盤點 | **38** distinct `feature`；**113** panel（2007-12-31…**2026-06-30**） |
| 組 1–7 對映 | 計畫列名 **全 HAVE**（缺列＝source-pure，不假填） |
| prodset 契約 | active＝**3**：`cycle_position_252d`／`inst_cumflow_position_120d`／`lending_fee_rate_mean_30d`（`resolve_prodset_feats`） |
| 有界 rebuild | `build_feature_panel.py --panels 2026-06-30 --asof` → **893** 股、**32,811** 值、**RC=0**（roster 895；2 股無價量跳過） |
| sync／sim／predict 寫 | **未做**（skip-sync／no-SIM-apply） |
| 全史×全 roster 重算 | **未做**（錯峰 A1；Wave-A 驗收＝誠實覆蓋＋契約，非一夜重灌 113×全表） |

log：`/tmp/s3-wave-a-20260804/rebuild-latest-asof.log`

---

## 2. 組 1–7 覆蓋（摘要）

| 組 | 狀態 | 註 |
|---|---|---|
| 1 價量／動能 | **have** | return／momentum_5…252d |
| 2 波動／循環位 | **have** | vol／range／cycle／phase 位 |
| 3 流動性／八二量能 | **have** | dollar_volume／turnover／gini／max_share |
| 4 技術形狀（扁） | **have**（與 2–3 重疊） | 序列張量契約＝**Wave-D／partial**，本波不開 |
| 5 估值 | **have** | pe／pb／div／mcap／price_to_10yr；pe 離群 winsorize＝**已知債** |
| 6 基本面／毛利循環 | **have** | roe／debt／gross_margin_pctile／monthly_revenue_yoy |
| 7 籌碼／借券 | **have** | 法人／融資／外資／lending_fee_30d 等；名實窗＝**已知債** |

**extra（非 G1–7 主列）**：`lending_fee_rate_mean_20d`（prodset **removed**）仍存表。

**本波不做（另波／gated）**：組 8–9 截面＋股級 macro＝`S3-WAVE-B`；10–11＝C；12–13＝D；14–16＝E／gated／N/A。

---

## 3. 提拔／#11（重覆驗証）— 引用既有真 stdout（不重挖飽和集）

| 尺 | 證據 | 結論 |
|---|---|---|
| prodset 熱路徑 | P1-C／LOOP-S5 OOS 用 `feature-source=prodset`（n_feats=3） | 契約可解析、非空 |
| #11 多 seed | `audits/S5-OOS-20260804.md` M1_gbdt H60×seed{1,2,42} | min／med／max Sharpe 已陳；hit＝bench→**不升格** GBDT |
| 多 horizon 重覆 | 同檔 H20／40／60／120 RankRidge OOS | H60／H20 主尺；H40 方向警示；H120 n=8 勿終局 |
| 新候選提拔本窗 | **未**再跑 `verify_candidate_promotion` 挖新特徵 | 對齊歷史飽和定論：Wave-A＝覆蓋／契約，**≠**再開特徵漏斗 |

---

## 4. 驗收對照（S3 報告 §5）

| # | 判準 | 本帳 |
|---|---|---|
| 1 | 多種特徵組 | ✅ 組 1–7 皆有落地列 |
| 2 | 提拔閘路徑 | ✅ prodset promote 史＋active∩覆蓋；本窗不新晉升 |
| 3 | #11 重覆 | ✅ 引 S5-OOS／P1-C 多 H／多 seed |
| 4 | 誠實覆蓋 | ✅ rebuild 缺價量跳過；不 median-fill |
| 5 | ≠可交易 | ✅；dgate pass=0 仍在 |
| 6 | 族可追溯 | ✅ 本檔 §2；N/A／gated 留給 B–E |

---

## 5. 硬邊界守則（本窗）

skip-sync · no-SIM-apply · FZ/GATE-keep · 不殺 A1 · 不 FinMind 放量 · 不臆造 LOB／NLP · 不假確立級

---

## 6. 下一刀（**另句**；本 GO 不默授）

```text
S2-KH-OPT-AFTER-S3-go + GATE-keep + NHC-keep + API-THAW-bounded
```

（≡／可連）

```text
LOOP-S3-TO-S2-go + GATE-keep + NHC-keep + API-THAW-bounded
```

可選後續：`S3-WAVE-B-go`（截面＋股級 macro）；全史 panel 重建（錯峰＋明示時窗）。

---

*完。EXECUTED（scoped asof rebuild＋覆蓋盤點＋prodset／#11 引用）。self-reported（#32a）。*

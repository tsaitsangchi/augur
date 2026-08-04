# EXECUTED｜S3-WAVE-B · 2026-08-04

> **位階**：[I] 執行帳  
> **GO**：`audits/S3-WAVE-B-GO-20260804.md`（Steward 原文 `S3-WAVE-B-go | FZ/GATE-keep | skip-sync | no-SIM-apply`）  
> **SSOT**：`reports/augur_s3_features_for_market_model_families_20260804.md` §3 **S3-B**＝組 **8–9**  
> **前置**：`audits/S3-WAVE-A-EXECUTED-20260804.md`  
> **self-reported（#32a）**：判讀為呈案；數字＝(a) stdout／(b) DB

---

## 1. 做了什麼

| 步 | 結果 |
|---|---|
| 登錄 GO | `audits/S3-WAVE-B-GO-20260804.md` |
| 庫內盤點 | `feature_values` **零** macro 名特徵；`fred_series` 有列至 2026-08-03；`market_direction_feature` 旁路表可消費 VIX／利差 PIT |
| **組 8** 截面相對化 | `validate_feature_candidates.py --since 2014-01-01 --h 20,60` → **RC=0**；寫入 `feature_candidate_values` **85,050** 列（4 名×核心宇宙） |
| 組 8 五鏡 IC | pan-hist rank IC 見 §2（stdout `/tmp/s3-wave-b-20260804/xsec.log`） |
| 組 8 #11 提拔複核 | `verify_candidate_promotion.py --features … --h 60 --seeds 3 --keep`＝**封帳時仍在跑**（見 §3；不擋 Wave-B 核心驗收） |
| **組 9** market PIT | `build_market_direction_features.py --run --since 2025-01-01 --until 2026-06-30` → **RC=0**、**7,174** 列（VIX＝`macro_vintage` PIT） |
| 組 9 股級 `feature_values` macro | **誠實 SKIP／partial**——無 builder 寫入股級 macro；本波**不**臆造欄、**不** FRED 放量（skip-sync／FZ） |
| prodset 晉升 | **未做**（GO 禁自動晉升） |
| sync／sim／predict 寫 | **未做**（skip-sync／no-SIM-apply） |

log 目錄：`/tmp/s3-wave-b-20260804/`（`xsec.log`／`mkt-dir.log`／`verify.log`／`post.log`／`inventory.log`）

---

## 2. 組 8｜截面相對化（候選材料化＋IC）

**命令**：`PYTHONPATH=src ./venv/bin/python scripts/validate_feature_candidates.py --since 2014-01-01 --h 20,60`

**候選列數（`feature_candidate_values`，DB 現查）**：

| feature | n | min panel | max panel |
|---|---:|---|---|
| `pb_xsec_rank` | 23,850 | 2014-12-31 | 2026-06-30 |
| `pb_industry_demean` | 23,850 | 2014-12-31 | 2026-06-30 |
| `pb_self_pctile_252d` | 23,850 | 2014-12-31 | 2026-06-30 |
| `inst_govbank_divergence` | 13,500 | 2021-07-31 | 2026-06-30 |
| **合計** | **85,050** | | |

**橫斷面 rank IC（pan-hist；五鏡①⑤；stdout 節錄）**：

| feature | H=20 IC／Eff-t／勝率／n | H=60 IC／Eff-t／勝率／n |
|---|---|---|
| `pb_ratio`（raw 對照） | −0.0259／−1.79／0.42／106 | −0.0378／−2.55／0.42／104 |
| `pb_xsec_rank` | −0.0259／−1.79／0.42／106 | −0.0378／−2.55／0.42／104 |
| `pb_industry_demean` | −0.0135／−1.40／0.39／106 | −0.0270／−2.69／0.34／104 |
| `pb_self_pctile_252d` | +0.0050／0.37／0.52／106 | **+0.0430／3.45／0.67／104** |
| `inst_govbank_divergence` | −0.0059／−0.43／0.43／60 | +0.0133／0.87／0.55／58 |

**判讀（self-reported）**：`pb_xsec_rank` ≈ raw `pb_ratio`（相對化未強化）；`pb_self_pctile_252d` H60 Eff-t≈3.45 為本窗最強單因子訊號；**≠** 可交易／prodset 晉升（dgate pass=0 仍在；本 GO 禁自動 promote）。

---

## 3. 組 8｜#11 提拔複核（多 seed）— 封帳狀態

| 項 | 值 |
|---|---|
| 命令 | `verify_candidate_promotion.py --features pb_xsec_rank,pb_industry_demean,pb_self_pctile_252d,inst_govbank_divergence --h 60 --seeds 3 --keep` |
| 啟動 | ≈2026-08-04 14:32+08；封帳時 elapsed≈**35+** min、仍在 GBDT 折／seed |
| `--keep` | 僅保留 staged 候選表、**不清**；**不**＝prodset 晉升 |
| 正式多 seed 表 | **待補**——進程結束後以 `/tmp/s3-wave-b-20260804/verify.log` 末段＋`RC_VER` 回填本節（或另開 `S3-WAVE-B-VERIFY-APPEND*`） |

Wave-B **核心驗收不繫於**本窗多 seed 終表：五鏡 IC＋候選材料化＋macro 誠實 SKIP 已滿足 GO 組 8／9 邊界。

---

## 4. 組 9｜Macro／FRED PIT

| 路徑 | 結果 |
|---|---|
| `market_direction_feature` PIT 刷新 | **DONE**：since 2025-01-01 → until 2026-06-30；**7,174** 列；表總約 **82,665** 列／**20** features／max date **2026-06-30** |
| 股級 `feature_values` macro | **0** 列（`feature ~* macro\|vix\|fred\|t10y`）→ **誠實 SKIP** |
| FRED 放量／`sync_macro` 本波 | **未開**（skip-sync／FZ；THAW 白名單不因本 GO 擴） |
| 新股級 macro builder | **未寫**（需另 plan／GO；禁臆造欄） |

**一句**：組 9 本波＝**旁路市場表 PIT 可消費**＋**股級 panel 缺口誠實記帳**——不解凍、不假完整。

---

## 5. 驗收對照（S3-B）

| # | 判準 | 本帳 |
|---|---|---|
| 1 | 組 8 候選相對化可測路徑 | ✅ 4 候選入 `feature_candidate_values`＋IC |
| 2 | 提拔／#11 路徑 | ✅ 五鏡 IC 已跑；多 seed verify **in-flight**（§3） |
| 3 | 組 9 macro PIT | ✅ 市場方向表刷新；股級 FV **SKIP** |
| 4 | 誠實覆蓋／不假填 | ✅；零 median-fill；零幻造 macro |
| 5 | ≠可交易／≠自動晉升 | ✅；prodset 未動 |
| 6 | skip-sync／no-SIM／FZ | ✅ |

---

## 6. 硬邊界守則（本窗）

skip-sync · no-SIM-apply · FZ/GATE-keep · 不 FinMind／FRED 放量 · 不臆造股級 macro · 不自動 prodset 晉升 · 不假確立級

---

## 7. 下一刀（**另句**；本 GO 不默授）

```text
S3-WAVE-C-go | FZ/GATE-keep | skip-sync | no-SIM-apply
```

（方向表↔ranker 契約／meta）

並行可選（與本波正交）：

```text
S4-WAVE-A-EXECUTED   # 待 direction 臂收口後正式封
```

---

*完。EXECUTED（組 8 候選材料化＋IC；組 9 市場 PIT＋股級 SKIP；#11 多 seed 封帳時 in-flight）。self-reported（#32a）。*

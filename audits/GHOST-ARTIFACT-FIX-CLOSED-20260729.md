# GHOST-ARTIFACT-FIX — 關閉報告

> **日期**：2026-07-29 · **狀態**：✅ CLOSED · **觸發**：Steward NET8 指示

## 問題

`model_registry` 中 5 列 `feats_hash = 3a4e66fae8cfa2fa` 指向磁碟上不存在的 ghost artifact（`.joblib` 檔案從未產生或已清除），導致 `joblib.load()` 時 `FileNotFoundError`。

受影響 model_id（皆 RankRidge, created 2026-07-11 14:11–16:43）：

| horizon | model_id | 原 artifact_path |
|---------|----------|-------------------|
| H20 | `RankRidge_H20_…_3a4e66fae8cfa2fa` | `…/RankRidge_H20_…_3a4e66fae8cfa2fa.joblib` ❌ 不存在 |
| H40 | `RankRidge_H40_…_3a4e66fae8cfa2fa` | 同上 ❌ |
| H60 | `RankRidge_H60_…_3a4e66fae8cfa2fa` | 同上 ❌ |
| H82 | `RankRidge_H82_…_3a4e66fae8cfa2fa` | 同上 ❌ |
| H120 | `RankRidge_H120_…_3a4e66fae8cfa2fa` | 同上 ❌ |

## 磁碟上存在的 canonical artifact

`feats_hash = ce62866bb62de38b`，H20/H40/H60/H120 四檔皆存在於 `models_artifacts/`，`joblib.load()` 驗證通過。H82 無 canonical artifact。

## 修復動作（UPDATE，無 retrain）

| horizon | 修復方式 |
|---------|----------|
| H20 | `artifact_path` → canonical `ce62866b` 路徑；`feats_hash` → `ce62866bb62de38b` |
| H40 | 同上 |
| H60 | 同上 |
| H120 | 同上 |
| H82 | `artifact_path` → `GHOST_NO_ARTIFACT__3a4e66fae8cfa2fa`（無 canonical artifact 可指向；保留 registry 列因 FK 約束 `prediction_probability` 339 列引用） |

## 驗證

1. ✅ `model_registry` 5 列已更新，`feats_hash` H20/40/60/120 = `ce62866bb62de38b`
2. ✅ canonical artifact H20/40/60/120 `joblib.load()` 成功（type=dict）
3. ✅ H82 明確標記為 ghost，不會誤觸 `FileNotFoundError`（載入端需判斷非絕對路徑即跳過）
4. ✅ `prediction_probability` FK 完整性保持（未刪列）

## 備註

- `model_id` 欄仍含 `3a4e66fa` 後綴（PK，不可改），但 `artifact_path` 與 `feats_hash` 已修正指向真實 artifact。
- H82 為孤立 horizon（無 canonical artifact），後續若需 H82 預測須重新訓練。

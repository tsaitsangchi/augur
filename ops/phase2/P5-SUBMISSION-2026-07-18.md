# Phase 2 生產施作 P5 呈核單 [I]——一次拍板（RULING-2026-015 主文四）

* **日期**：2026-07-18｜**前提**：補件分支 `remediation/phase2-retire-backfill`（b5b19f1）對抗審查雙鏡 GO（8 代理、164 指令；本單即審查三 major 所命之 runbook 載體）
* **涵蓋**：(A) 補件分支准併 main；(B) 生產三步施作全順序（裁③：retire→鑄造→屬性）

## 一、核准數字錨（2026-07-16 同步態；審查官獨立重算吻合）

| 項 | 核准數 |
|---|---|
| 下市紀錄／預鑄 retired 身 | **342**（0 重複 0 NULL） |
| 名冊：Security／Index／FredSeries | 3,086／32／31（殘差 0） |
| 預期紅旗（重用碼 provisional） | **235** |
| **終態**：registry／alias／retire 事件／屬性版本 | **3,491／3,491／342／9,258**（⚠ 勿比對沙盒 3,492——彼含測試探針） |
| 名實不符人裁佇列 | **37 例**（裁決文 ~35 為估算，以實跑 37 為準——CSV 已入庫） |

**漂移停止條件（審查 major②）**：每步 `--apply` 前先於生產跑該腳本 `--check`（唯讀），逐項比對上表；**任何偏離＝停止、回報 Steward 重錨**（生產為活庫，拍板與實跑間有例行同步）。

## 二、Runbook（幕僚執行；單實例；環境釘死）

```bash
# 步 0 備份錨點（回退定義之 (b) 錨）——記錄時間戳
export RESTIC_REPOSITORY=/mnt/d/augur_restic RESTIC_PASSWORD_FILE=/home/giga/augur/backups/restic.pass
pg_dump -h 127.0.0.1 -U postgres -d augur -Fc -Z 3 -f /home/giga/augur/backups/augur_pre_phase2_$(date +%Y%m%d_%H%M).dump && restic backup 該檔

# 步 1 retire backfill（前置閘：registry=0 ∧ alias=0；環境=生產故不設 DB_NAME）
venv/bin/python scripts/backfill_lifecycle_retire.py --check     # 比對：下市 342/預鑄 342/名實不符 37
venv/bin/python scripts/backfill_lifecycle_retire.py --apply     # 單交易+advisory lock 單實例
# 驗收閘：retire 事件=342 ∧ registry=342（全 adopted）

# 步 2 存量鑄造（前置閘：retire 事件=342 ∧ registry=342）
venv/bin/python scripts/backfill_entity_registry.py --check      # 比對：3,086+32+31/殘差 0
venv/bin/python scripts/backfill_entity_registry.py --apply
# 驗收閘：registry=3,491 ∧ provisional=235 ∧ 紅旗計數=235

# 步 3 屬性同步（前置閘：registry=3,491）
venv/bin/python scripts/sync_attribute_versions.py --check       # 比對：已繫 3,086/null_date 0
venv/bin/python scripts/sync_attribute_versions.py --apply
# 驗收閘：entity_attribute_version=9,258；重跑 --check append=0（冪等證）
```

**步序閘（審查 major③）**：前置閘 SQL 為驗收閘之對偶——**錯序執行（鑄造先於 retire）產生語義相反且 append-only 下不可重來的拓撲**，前置閘不綠一律停止。

## 三、回退之誠實定義（審查 minor）

append-only 體制下無原地撤銷：(a) **前向補償**＝registry status→tombstoned＋lifecycle `correct` 事件（EVIDENCE_REQUIRED）；或 (b) **整庫還原**至步 0 備份錨點（影響全庫、非僅 identity 表）。簽核即知悉此定義。

## 四、known-notes（審查四 minor，簽核即知悉）

1. **軸割**：預鑄 retired 身之 `registry.status='active'`／alias 時界 NULL——退役真相在 **lifecycle 事件軸**（本包教義、selftest 鎖住）；Phase 2 後段消費切換須列檢核項。
2. 冪等鍵含 stock_name：來源改述名字→重跑 `already≠342` 時**先查來源改述**、非逕視異常。
3. C2 並發測試判別力首跑後衰減（C1 承擔回歸防護）；沙盒留恰一枚探針（有界）。
4. test_release_lag 間歇 flake 屬 diff 外未根治（本審兩輪全綠）。

## 五、簽核

> **請 Steward 核示**：(A) 准併補件分支；(B) 准依本 runbook 施作生產全順序。
> - [ ] **准（A＋B）**（簽：＿＿＿ 日期：＿＿＿）
> - [ ] 修改意見：＿＿＿
>
> 效果：**~3,491 個世界實體獲得憲章身份、235 個重用碼歷史正確分離、37 例入人裁佇列**——P3「Identity before Knowledge」自條文成為資料列。

# Phase 1(d) owner 分離施工包 [I]——沙盒已實測，呈請 P5 核准生產施作

* **日期**：2026-07-18｜**依據**：CODE-MIGRATION-PLAN Phase 1(d)（經對抗審查修訂版——審查官 major#3 之完整 GRANT＋角色切換＋沙盒權限鏈實測，全數在此落實）
* **目的**：關閉「守衛 trigger 擋不住 owner」之最後缺口（審計 AUD-02 殘餘風險：強制機制與其可解除者同屬一權限主體時，該不變式於憲章意義上不成立——L7.16 同旨）
* **性質**：[I] 施工包。**生產施作須：生產備份（經還原確認）＋ P5 書面核准 ＋ 本包驗收閘全綠**；沙盒實測 ≠ 生產核准。

## 一、設計

| 角色 | 屬性 | 職責 |
|---|---|---|
| `augur_owner` | NOLOGIN | 十張憲章表＋2 個 SECURITY DEFINER 函式之 owner；無人可登入，唯 superuser 可 SET ROLE |
| `augur_app` | LOGIN | 應用連線角色；廣域 DML（零回歸）＋憲章十表**僅 SELECT/INSERT**（＋serving 之 `superseded_by` 欄 UPDATE 例外）＋schema CREATE（generic_schema 動態建 raw 表） |
| `augur`（現行） | 保留 | 過渡橋：.env 切換前 heal/mint 不斷線（SELECT/INSERT 十表）；**UPDATE/DELETE 一併收回**（原 owner 旁路關閉） |

雙層強制：**ACL（42501）＋守衛 trigger（19 支）**——任一層被繞過仍有另一層。

## 二、沙盒實測證據（2026-07-18，augur_sandbox＝55GB 生產同構複本）

| # | 測試 | 結果 |
|---|---|---|
| 1 | 十表 ACL 探測（`SET ROLE augur_app` 逐表 INSERT；權限錯 42501=FAIL、約束錯 23xxx=ACL 通過） | **10/10 通過** |
| 2 | 真實寫入（交易內回滾）：heal 鏈 `raw_supersede_log` 全欄寫入＋讀回；mint 鏈 `entity_type_catalog`→`entity_registry` FK 全通 | **✅** |
| 3 | `augur_app` UPDATE 十表 | 42501 拒 ✅ |
| 4 | `augur_app` DELETE 十表 | 42501 拒 ✅ |
| 5 | `augur_app` ALTER TABLE | 拒（非 owner）✅ |
| 6 | **`augur`（原 owner）DELETE 十表** | **42501 拒 ✅——旁路關閉** |
| 7 | **`augur` DISABLE TRIGGER ALL** | **拒（owner 已分離）✅——守衛不可被解除** |

附註：`CREATE ROLE` 為叢集級，沙盒實測時已建立 `augur_owner`／`augur_app` 二角色；**其對生產資料庫惰性**（未 GRANT 前於 augur 資料庫無任何權限），生產腳本之角色段冪等跳過。

## 三、生產施工步驟（依序；步 3 起需 P5 核准在案）

1. **備份**：`pg_dump` 全庫＋還原至臨時庫確認可用（未經實測之備份推定不存在）。
2. **P5 書面核准**（見 §五呈核單）。
3. **SQL 施作**：`psql -U postgres -d augur -f phase1_owner_separation.sql`（冪等、可重跑）。
4. **密碼 provisioning**（TTY 人工）：`ALTER ROLE augur_app PASSWORD '<新>';` 不入版控。
5. **驗收閘 A**（連線切換前）：腳本 §6 之 (a)(b)(c) 三驗——owner=augur_owner、augur_app 可寫、augur 之 DELETE 被拒。
6. **應用切換**：`.env` 之 `DB_USER=augur→augur_app`＋`DB_PASSWORD` 更新 → **systemd 服務全部重啟**（CLAUDE #7：改 code/組態必重啟常駐服務；單位清單以 `systemctl list-units | grep -i augur` 現況為準）。
7. **驗收閘 B**（切換後）：一輪唯讀健檢綠＋下次 heal 遇 value_mismatch 後 `SELECT count(*) FROM raw_supersede_log` > 0（計畫 Phase 1 閘）。
8. 任一閘不綠：`phase1_rollback.sql` ＋ `.env` 改回 ＋ 重啟——全程可逆。

## 四、與計畫其餘子項之關係

本包僅 Phase 1(d)。Phase 1(a) 分支併 main（Steward #19 檢視）、1(b) 生產 code 切換（heal 快照 gate 生效）、1(c) `setup_predict_role --apply`（TTY 人工）各依計畫另行辦理；本包之過渡橋設計使 (d) 可先行而不斷 (b) 之接線。

## 五、P5 呈核單

> **請 Steward 核示**：准依本包§三施作生產 owner 分離（步 3–7），完成後留痕於 AL 與 HANDOFF。
> - [ ] **准**（簽：＿＿＿＿ 日期：＿＿＿＿）
> - [ ] 駁回／修改意見：＿＿＿＿
>
> 已備事項：沙盒實測 7/7 ✅｜施工/回退 SQL 在庫｜驗收閘機器可判｜全程可逆

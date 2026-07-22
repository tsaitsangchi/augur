# Phase 1(a) 分支 #19 檢視卷宗 [I]——remediation/impl-2026-07-17（7fcc267）併 main 前審

* **日期**：2026-07-18｜**審查**：三鏡對抗工作流（正確性／憲章合規／部署風險，7 代理、267 指令、全 sandbox 實測、零觸生產）＋雙反駁覆核
* **範圍**：merge-base 493fd73..7fcc267 真實 code 變更＝**22 檔、+2000／−16**（−16 逐行核＝全機械式簽名擴充，零既有行為變更——「新增式」宣稱實證成立）

## 一、判定：三鏡全數 GO

| 鏡 | go | 一句話 |
|---|---|---|
| 正確性 | ✅ | supersede 快照 15/15＋identity 六表行為逐一實證；比對口徑單一權威（共用 `_norm`）；同交易回滾實測成立 |
| 憲章合規 | ✅ | P4.E3／P4.E5／P3.E2 忠實落地；六個亮點不可動區零觸動（檔清單×機制位置對照）；snapshot_reason 三呼叫端透傳完整 |
| 部署風險 | ✅ | 上線首日運行路徑全 SELECT/INSERT（augur_app 端到端通過）；merge-tree 零衝突；回退＝純 git |

**測試證據**：18/18 全綠（含 7 個 DB 行為測試以 `augur_app` 身分在 owner 分離後之 sandbox 通過＝生產部署形狀）。

## 二、存活 major（兩鏡獨立撞見同一件）——**已當場修復**

> **augur_app 持有兩枚法規抹除函式（`raw_supersede_tombstone`／`identity_de_identify`）之 EXECUTE 權**——應用角色可單呼叫抹除證據內容，刺穿 P4.E3／ID.42「受控唯一例外」。根因＝Phase 1(d) 手術之 `GRANT EXECUTE ON ALL FUNCTIONS` 過寬（施工者自認）。
> **修復（2026-07-18，本卷宗作成前）**：沙盒＋生產同步 `REVOKE EXECUTE … FROM augur_app, augur, PUBLIC`，`has_function_privilege` 驗證雙庫全 false——抹除唯 owner／superuser 路徑（人工、留痕）可達。

## 三、部署鏡五問之關鍵事實（更正我方前提）

1. **origin/main 實已前進 15 commits（含 alpha feat code），非 3 個文件 commit**——merge-tree 實測零衝突、檔案零交集，可安全併；惟部署 scope 含 main 側 alpha code，Steward 應知。
2. **無須重啟服務**：四支常駐服務不 import 任何被改模組；heal／attest 每輪 fresh process 自動載新碼。
3. **heal 快照上線首日即生效**（呼叫端恆傳 reason，非旗標關閉）：首個 value_mismatch heal 即開始對 `raw_supersede_log` 留痕——**這正是排程 #5「首筆憲章數據」之觸發器**。
4. 硬化未 apply 之庫會 fail-loud 拒快照（生產已硬化，不觸發）。
5. 回退＝`git revert`，零 DB 步驟。

## 四、minors（12 項，不阻併；已排處置）

| 類 | 項 | 處置 |
|---|---|---|
| 接線潛伏 | `link_observed_effect`／serving `superseded_by`／alias 轉換之 UPDATE 在 augur_app 下無權（今日零呼叫端） | **Phase 3/4 接線時**補 column-level GRANT 或 definer 收尾函式（已記入計畫） |
| 運維摩擦 | `seed_entity_type_catalog` 之 ON CONFLICT DO UPDATE 須 owner 跑 | Phase 2 施工卷宗載明 |
| 體例 | `migrate_raw_supersede --selftest` 頂層 import db（違 #29(a)；姊妹腳本皆延遲） | 併後小修 |
| 測試誠實 | fixture superuser 分支永久套 DDL 與「零殘留」檔頭矛盾（未 apply 之庫情境）；建議改 `pytest.skip` | 併後小修 |
| 文字 | `daily_maintenance:122` 註解與決策 B 矛盾；`lifecycle` 錯誤訊息僅列 4/9 型別 | 併後一行修 |
| 效能 | pre-image 無上限 WHERE-IN（最壞 ~14 萬字面值，loud 失敗非靜默） | 比照 upsert 分頁，Phase 2 前 |

## 五、建請 Steward

- [ ] **准併 main**（merge 零衝突；併後我依 #14 執行 merge＋push＋留痕）
- [ ] 知悉：部署（排程 #5）將一併帶上 main 側 15 commits 之 alpha code
- [ ] 知悉：併＋部署後，heal 首個 value_mismatch 即產生第一筆憲章表數據

# Phase 2 分支 #19 檢視卷宗 [I]——remediation/phase2-identity（22468bb）

* **日期**：2026-07-18｜**審查**：三鏡對抗工作流（正確性／憲章合規／資料完整性，9 代理、255 指令、全沙盒、零觸生產）＋雙反駁覆核
* **範圍**：main..22468bb＝四新檔（resolve.py／backfill／sync_attribute_versions／test_phase2_identity）＋`identity/__init__.py` 一行；**亮點不可動區與 ingest.py 零觸動親驗**

## 一、三鏡判定：全數 GO，機械面自陳全數親證

| 鏡 | go | 關鍵親驗 |
|---|---|---|
| 正確性 | ✅ | 五動作判準逐路徑無誤；名冊判準與 core_gate 逐字同；交易原子（零孤兒）；SCD-2 邊界穩健；12 測真測到宣稱行為 |
| 憲章合規 | ✅ | ID.43／P3.E1／P3.E2 機制忠實；evidence 抽驗回源全吻合；命名空間方向正確（Index 出 security 空間＝AUD-04 正名） |
| 資料完整性 | ✅ | **3,149＝3,086＋32＋31 以獨立 SQL 直查來源表重算完全吻合**；三表 0 重複 0 孤兒 0 錯配；9,258＝3,086×3 精確；catalog 未被越權 seed |

## 二、三項存活 major＝三個待你裁的決策點（皆非阻併缺陷）

### 裁① 並發防護（正確性 major）
`resolve_or_mint` 無並發防護——雙連線同碼**親測雙鑄**（entity_alias 無唯一約束；UNIQUE 不可行——ID.43 合法同碼二列）。
**建議處置**：不阻併；**「advisory lock 防護」列為 Phase 2 後段攝取接線之前置條件**；生產 backfill runbook 明列**單實例執行**。

### 裁② 新鑄 alias 生而 'adopted'（憲章 major——本包唯一逾越機械登錄之處）
三型別（T.1 `^[0-9]`／T.2 來源自標／FredSeries）之同一性判準**皆無 ID.20 採認紀錄**，而新鑄 alias 直標 adopted——預清了 provisional 旗標，使 ID.51 未解析存量盤點失真（憲章上 3,149 待採認、機械上 0）。
**兩路處置**：
- **(a) 建議採**：你於准併裁示中**順勢追認 T.1／T.2／FredSeries 三判準之操作化採認**（補齊 ID.20 具名紀錄）——審查鏡評估證據堅實（32 檔指數全攜價格序列＝Instance 非分類節點；判別謂詞為來源自標非幕僚自創），追認後 adopted 合法。
- (b) 改鑄 provisional：3,149 全掛 provisional 待逐批人裁採認——憲章最嚴格但實務上將長期停留（採認亦需你逐判準裁）。

### 裁③ 存量鑄造 vs 下市事件之先後序（憲章 major——「紅旗 0」的真相）
「紅旗 0」係 **lifecycle 表空之結構必然、非實質檢出**：沙盒同庫 TaiwanStockDelisting **342 筆**未被消費（retire backfill 屬 Phase 2(d)、不在本包）；其中 **235 碼在今日名冊**（下市後再現＝疑似重用/relist）、**35 碼名實不符**（含 2301 光寶合併案）。先鑄後補 retire → 歷史縫合固化風險。
**建議處置（生產 apply 順序）**：(1) seed 型別 → (2) **retire backfill 先行**（342 筆→lifecycle 事件；小腳本待補、我可即刻發包）→ (3) 存量鑄造（此時紅旗機制有接地證據——235 例將正確走 provisional 不縫合）→ (4) 屬性同步。**效果**：生產 minted 預期 ~3,149 但含 ~235 枚 provisional（與沙盒演練之全 adopted 不同——此為憲章正確之樣貌）；35 例名實不符入人裁佇列。

## 三、minors（7 項，已排處置）

名冊分割前瞻縫隙加殘差計數｜resolve docstring 言明「退役=lifecycle 事件軸」＋ambiguous tie-break｜valid_from today() 兜底改誠實跳過｜生產 runbook 明列 seed 先行｜套件間歇 flake（diff 外 test_release_lag，6 跑 4 綠、單獨跑恆綠）——併後小修批。

## 四、簽核單

- [ ] **准併 main**（code 三鏡全 GO；併後我執行 merge＋push＋minors 小修）
- [ ] 裁①：advisory lock 為接線前置＋backfill 單實例（建議如上）
- [ ] 裁②：(a) 追認三判準（建議）或 (b) 改鑄 provisional
- [ ] 裁③：生產順序 retire 先行（建議）——准即發包 retire-backfill 腳本補件，**P5 生產拍板延至該補件審畢後一次裁**

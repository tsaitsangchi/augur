# augur 跨機接續 handoff — 執行階段快照(2026-06-12 夜版)

> 接續者(人/AI)**先讀這份**,再讀治權 SSOT。對話一律**繁體中文**。
> 前序:`..._20260612.md`(晨版,治權版本已過時)+ `..._20260611.md`(setup)。本份為**當日全量更新**。

---

## ⚠️ 0. 最關鍵警告(先看)

1. **本機(WSL2 PC002-S1800)sync 正在跑** —— run2 PID 81095、nohup detach、resume-safe。
   **強烈建議:本機續跑、新機只做開發**。DB 不隨 git:本機已落 **31.1M 列**,新機從零=浪費數天;
   resume 只在本機 DB 有效。若本機必須停:`kill <pid>` 安全(冪等+DB resume),但進度留在本機。
   **本機 Windows 須設不睡眠**(主機睡=進程死,需手動重啟續傳)。
2. **FINMIND_TOKEN `2026-06-24` 到期**(sponsor 6000/hr)——剩 ~12 天,全史 sync 必須在此前完成。
3. **`.env` 不進 git** —— 新機須重建(DB 五件套 + FINMIND_TOKEN + FRED_API_KEY)。
4. **新機=新 IP=額度/節流全新**;但 token 共用 → 兩機同時抓會共耗 6000/hr 配額(quota gate 看的是 token 錶)。
5. **rate 為用戶決策:`MIN_INTERVAL=0.8` / `PER_STOCK_WORKERS=8`,勿自行改回**;0.8s/8w 每小時 ~30-35 分
   就觸額度頂 → **週期性 gate 暫停屬預期行為**(log 出現 `[finmind] 額度…主動暫停/續抓`),非故障。

## 1. 接機(新機 setup)

```bash
git clone https://github.com/tsaitsangchi/augur && cd augur   # HEAD 796bdf6
# 建 .env(永不進 git);python -m venv venv && pip install -e .;OS 依賴見 README/前序 handoff
PYTHONPATH=src venv/bin/python -c "import psycopg2,pandas,numpy,requests; print('ok')"
```
- **治權 SSOT(版本已升)**:靈魂 v1.2.0 / **原則精華 v1.6.0(20 條,新增 #20 自驅動×實證決策)** /
  憲章 v1.6.0 / CLAUDE v1.3 / README。
- 今日 8 tag:`treaty-v1.6.0` → `finmind-quota-cooldown` → `quota-gate-f2-roadmap` →
  `feature-design-trilogy` → `f3-model-plan` → `f3-theory-enhancements` → `f3-self-critique`(各-20260612)。

## 2. 執行階段現況(2026-06-12 17:0x 實查)

- **sync run2**:15:44 起跑,`[2/82]` 完成(GovBank #7 PASS / BalanceSheet #7 PASS),
  ShortSaleBalances resume 中;**0 異常**。log `/tmp/augur_fullsync.log`(run1 在 `_run1.log`)。
- **本機 DB(不隨 git)**:31,122,412 列 / 7 表(GovBank 13.7M、BalanceSheet 8.37M、ShortSale 7.67M、
  FinSt 1.28M、FRED 84.7k、Info 4.1k+audit)。
- **額度錶**:4435/6000(rolling)——gate 首次實戰暫停可能隨時發生(預期)。
- 監看:`tail -f /tmp/augur_fullsync.log`;進度行含 `N/3101 股`;對帳行 `✅ #7 對帳 PASS`;
  問題檔 `reports/augur_fullsync_issues_20260610.md`(run2 重置,目前 0 筆)。
- ⚠️ Claude session 的兩個 Monitor(心跳/關鍵事件)**不隨機器/句柄走**,新 session 須重掛(或直接 tail)。

## 3. 今日(6/12)成果總覽(全部已 commit+push)

### A. 治權:#20 入憲 + 二輪優化(treaty-v1.6.0)
**#20 自驅動 × 實證決策**(D 類):AI 自己 prompt 自己朝靈魂目標推進、執行層方法 AI 主導、自我糾錯試錯;
**凡判斷/做法先實證(probe/API/code/DB),嚴禁憑「我以為」**;決策層人拍板/執行層 AI 自駕。
5 檔同步升版;另:分類導讀(條號非連續說明)、時效性移歷程、#17/#24 三層防護入治權。

### B. 限流實戰與 code(最重要工程教訓)
- **403 惡性循環實證**:0.8s/8w ~30 分撞 6000/hr;舊 backoff 重試風暴 → 錶永遠滿、不自癒(15:04 #25 止血)。
- **額度=rolling 視窗**(零 call 期間錶連續退,**非整點清零**;恢復點 12:37/13:52 非整點)。
- **兩種 403**:額度型(gate 可防)vs IP sustained 型(只能保守+休養)。
- **三層防護已落地**:`_pace`(0.8s)→ **`_quota_gate`**(閉環輪詢 `/user_info` 權威錶;≥limit−200 先停、
  ≤一半續;403 期間可讀、讀錶不自計)→ `QUOTA_COOLDOWN`(403 固定 1800s,不重試風暴)。
- `/translation` 實證:**僅 12 dataset、翻科目值(type 值域)非欄名** → 留作科目字典工具。
- `scripts/annotate_schema_comments.py`:表/欄中文入 PG COMMENT(8 表 55 欄已落;**全 sync 完重跑→82 表**);
  欄中文=catalog 文檔對照、表中文=augur 釋義、來源標記於 table comment。

### C. 設計鏈(F2→F3 完整藍圖,5 份報告)
1. `augur_f2_feature_expansion_roadmap_20260612.md`:82 表四分類 **P22/E12/X36/R12** + 分期 F2b-g。
2-4. 特徵三部曲:`first_principles`(七軸)/ `pareto_thought`(六軸,無切點泛函)/ `cycle_thought`(六軸,相位共振)。
5. `augur_f3_model_plan_three_thoughts_20260612.md` **v1.2**:可行性(正名=橫斷面排序)+ 基準階梯
   B0→B2.5(經典因子對照)→GBDT→ensemble + 三族消融 + §七理論定位 + §八六強化 + **§九自我批判(5 弱點 5 修正:
   H=20/60 主戰場、共同樣本窗鐵則、conviction 降級、成本入 #14 核心)——修正後=現行計畫**。

### D. anti-leakage 金礦(F2d/F2f 落地第一件事)
`Dividend.AnnouncementDate/Time`(API 自帶公告時點)· `MonthRevenue.create_time`(**疑 PIT 時戳,待實證**)·
`Shareholding.RecentlyDeclareDate`;財報三表無公告欄→法定期限 lag;`BusinessIndicator` 次月下旬發布→lag 必須。

## 4. 接續 TODO(順序)

- [ ] **看顧 sync 到 82/82**(本機;預期數天、跨日;gate 暫停=正常;`FinMind error`/`FAIL` 才要處理)
- [ ] 完成後:重跑 `annotate_schema_comments.py`(82 表)+ 全表 #7 對帳總驗
- [ ] F2b 起步(籌碼特徵;依 roadmap;前置=該表 sync 完+#7 PASS+發布時點記錄)
- [ ] F3 M-0(label/panel/metric SSOT helpers + core_universe as-of 快照)
- [ ] 待實證清單:`MonthRevenue.create_time` 語意 / 財報公告欄 probe / catalog 未取樣 1 表
- [ ] commit/push 一律用戶明示授權;clean-room #16;**新機記憶不隨 git→本檔即記憶替身**

## 5. 關鍵檔案

driver `scripts/full_market_sync.py` · 引擎 `src/augur/ingestion/sync.py` ·
`finmind.py`(`_pace`/`_quota_gate`/`QUOTA_COOLDOWN`/`translation`)· 對帳 `audit/reconcile.py` ·
註解 `scripts/annotate_schema_comments.py` · 設計 5 報告(§3C)· 治權 5 檔(§1)。

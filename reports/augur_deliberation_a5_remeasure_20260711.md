# 審議引擎 A5 七片複量報告(2026-07-11;GATE 結果照實寫回)

> **這份是什麼**:補完計畫(reports/augur_deliberation_completion_plan_20260711.md)P3 收尾之 A5 複量——
> 對「A5 自審 not_yet」裁定的七片量測維度逐片複查落帳,並照實寫回 GATE 結果(過與不過皆留)。
> **性質=F2 開閘前置復審文件**(前台檔位計畫 §5:翻旗標前置=GATE+A5+用戶拍板)。
> 全數字出自 DB 實查(#9;查詢時點 2026-07-11 晚間,git HEAD 163caf0+工作樹 v2 改動)。

## 1. GATE 誠實史(三批全列、不消音)

| 批 | 結果 | 說明 |
|---|---|---|
| `gate_663fecd41783`(07-11 10:45 預註冊) | **FAIL** | 增量 +46.7pp ✓、McNemar p=5.53e-10 ✓、**假確認逐輪條款 ✗**(engine=1)→ 依「不挪門柱」判死留檔 |
| `gate_97ece3e0a2bd`(15:47) | 作廢 | 凍到素材修正前題庫(`core_universe` bug——題庫假設它不存在、實存在);由 v3 取代,留檔 |
| `gate_43044a574c0d`(15:48 預註冊;跑程被停電切斷於 7/9、以 run/task 帳本 resume 完跑) | **PASS** | median acc:engine **100.0%** vs 最佳非引擎 53.3% → **+46.7pp**(門檻 +15pp)✓;**假確認 engine=0** vs 各臂 min=7 ✓;McNemar 合併 **p=3.64e-12**、逐輪(seed 41/42/43)0.000/0.001/0.000 全顯著 ✓ |

**判定:引擎效力預註冊成立**(`--report-gate` 機械輸出;門檻讀自凍結快照非 code 常數)。
效力域=GATE 題型所及(schema 存在/量比較/檔內容/隔離不變式等 5-oracle 可裁域);undecidable 誠實 escalate 不變;LLM 意見零證據力不變;治權觸線強制人裁不變。

## 2. 七片複量(帳=SQL 實查;不落帳=未量測)

| 片 | 驗收 | 現值 | 判 |
|---|---|---|---|
| D1 模型速率 probe | 18/18 有 tok_per_s | 18/18(qwen3:8b 6.7、4b 17.1 tok/s) | ✅ |
| D2 題集 seed | ≥3 seeds | 3(41/42/43,凍於 batch 快照) | ✅ |
| D3 長跑 session | (裁定後)completed run 之 wall-clock ≥1800s ≥1 | GATE run 11:07→15:47(>4.5h)+跨停電 resume 完跑 | ✅(措辭修正案,hugo 裁 2026-07-12) |
| D4 kill-resume 帳跡 | (裁定後)run 曾經 resume_reset 重置 ≥1 次且終態 completed | dlrun_fc1bc20f3472:真實停電 kill→resume_reset→completed | ✅(措辭修正案,hugo 裁 2026-07-12) |
| D5 人裁閉環 | resolved ≥10 | **88/94 resolved**(6 未決=今日 red-line 演練新單,by design 等 hugo) | ✅ |
| D6 red-line 觸線 | live 帳 red_line_category ≥1 | **6 筆**(今日 live 演練:AnnouncementDate 健檢宣稱全數被強制轉 human_claude ✓機制實證) | ✅ |
| D7 模型一致性 | ≥5 topics | 5 topics | ✅ |

**模式面**:模式 4 判官團=12 分落帳(今日首跑,proposal 59-62 三 lens 評分);模式 9 iterate=14 proposal;模式 10 run/task=GATE 承載+真實停電 resume 實證。十模式全數有帳或有實跑。
引擎規模帳:54 sessions、243 claims、benchmark 102+ 列。

## 3. 兩個字面未達項的誠實處置(**已裁:hugo 2026-07-12 採措辭修正案**——§2 表已依裁定更新)

- **D3(≥1800s session)**:GATE 長跑實際由 **run/task 帳本**承載(首跑 11:07→15:47 逾 4.5h、第二跑跨停電 resume)——session 本身 by design 短(單場審議數十秒)。字面驗收寫錯了載體。**提案**:驗收句改「completed run 之 wall-clock ≥1800s ≥1」(現已滿足),或維持原句+標註不適用。=驗收措辭變更,**須 hugo 裁**。
- **D4(attempt≥2)**:真實 kill-resume 已發生(停電殺進程→`resume_reset` running→pending attempt+1→完跑),但 attempt 終值=1(第二次 reset 走 failed 路徑不加 attempt)。**帳跡存在、計數器語意不同**。提案:同上,句改「run 曾經 resume_reset 重置 ≥1 次且終態 completed」(已滿足),或補一場人為 kill-resume 演練湊 attempt=2。**須 hugo 裁**。

## 4. F1 前後台對接現況(「本地 ultracode 接前後台」)

- **code 鏈 100% 已接**(commit d86444b):chat UI 雙選單(模型×力度,ultra 檔顯示「ultracode(審議·分鐘級)」)→ `window.TIER` → advisor `resolve_tier` → `effort.run_ultracode` → **`engine.deliberate` 真呼叫**(oai_compat.py:263→effort.py:134)→ 裁決以零-LLM 機械模板附回覆尾(宣稱原文標明非系統背書)。
- **旗標=關**(`deliberation_engine_config.frontend_tiers.enabled=false`)→ live 前台現在看不到選單。
- **L2 每日自審**:入口 script+題庫 3 題就緒,cron 未掛(前置=GATE+A5)。

## 5. 開閘 checklist(全部剩決策層動作)

| # | 動作 | 狀態 |
|---|---|---|
| 1 | GATE 過 | ✅(gate_4304) |
| 2 | A5 複量報告 | ✅(本檔;§3 兩項措辭裁定隨附) |
| 3 | 人裁佇列 6 單 red-line 演練單處理 | ⏳ hugo(`scripts/resolve_escalation.py` 或 admin 後台) |
| 4 | **翻旗標**(用戶拍板)| ⏳ hugo:`UPDATE deliberation_engine_config SET config=jsonb_set(config,'{enabled}','true'), updated_at=now() WHERE config_key='frontend_tiers';`(fresh 讀、免重啟) |
| 5 | 掛 L2 cron | ⏳ hugo 拍板後:`15 6 * * * cd ~/project/augur && venv/bin/python scripts/run_daily_deliberation.py --run` |

翻開後 ultra 檔行為:eligibility 關鍵詞命中才進引擎(表/欄位/schema/列數/檔案/隔離/import)、單飛鎖 max_concurrent=1、不合格題誠實 fallback 走一般管線——「像 Claude 的 ultracode」=機械可驗宣稱之對抗驗證,不是萬能深思。

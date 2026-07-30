---
name: augur-project-map
description: augur 專案地圖(2026-07-30 全面重寫;舊版數字與版本已全過期作廢)——定義框架、治權現行版、三塊架構、兩軸現況指針
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T04:05:39.378Z
---

**定義與框架**：見 [[augur-world-construction-core]]（**必先讀**）——augur 是從零建構的世界（L0–L7），一條路×八行走者；台灣市場只是第一個登錄域。**不要再用「只用真實資料、誠實預測台股的系統」當定義**（該句仍在靈魂 v1.8.0 之「一句話」；其與 WM.7「世界模型不得優先適配資料來源」之疑義已呈裁，見 `reports/augur_treaty_core_alignment_plan_20260730.md` 乙-1）。

**治權現行版（2026-07-30 親驗檔名）**：上位 `constitution/META-CONSTITUTION.md`＝**AUGUR-MC v1.6**；七規格 `specs/{WORLD-MODEL,ONTOLOGY,IDENTITY,KNOWLEDGE-SYSTEM,COGNITIVE-KERNEL,AGENT-RUNTIME,INFRASTRUCTURE}-SPECIFICATION.md`；領域四件套＝靈魂 `docs/系統核心思想_v1.8.0.md`（登錄 L1）・法律 `docs/原則精華_v1.11.0.md`（登錄 L4；20 條，基石 #1／#8／#15）・架構 `docs/系統架構大憲章_v1.49.0.md`（登錄 L7）・工具規則 `CLAUDE.md v1.31`（登錄 L6）；入口＝`constitution/GOVERNANCE-MAP.md`；41 份 RULING＋`AMENDMENT-LOG.md` 在 `constitution/`。⚠ 版本會滾動——引用前跑 `python3 scripts/check_treaty_refs.py`（2026-07-30 新建；四類機械檢：死引用／連到已被取代版／現況宣告行落後／SUPERSEDED 指幽靈版）。

**技術底座**：見 [[augur-tech-baseline-20260730]]（294 表／18 package／425 scripts／63 migrate DDL／11 systemd unit 皆 user-level／ollama 三模型／套件實況含「無 peft」）。

**三塊架構**：①**預測管線**（core・ingestion・catalog・audit・features・universe・evaluation・models・arena・execution）②**素養橫切**（knowledge・philosophy・advisor——AST import-lint＋DB role 雙閘與預測管線隔離）③**治理與自進化**（evolution・deliberation・identity ＋ 人閘 `governance_proposal`／`governance_queue`）。「一條路」之實作層斷裂與統一設計見 [[augur-path-six-parallel-gap]]。

**兩軸現況（指針；細節在各專題記憶）**：市場軸＝相對強弱主線已證（扣成本淨 Sharpe ~1.2-1.5 vs 基準 0.83、21 個月切面），方向軸全家族兩次證偽已凍結、不開 v3，走勢需求由四鎖 MC 模擬承接；知識軸＝KH1–KH4 閉環、KH5–KH10 逐層點亮中。自反軸＝重演軌／程序重演／本地 AI 進化／模擬方法進化。

**關鍵 operational 約束（仍有效）**：as-of 治權參數＝解凍後 live 增量（arena 資料地基釘 `2026-06-30` G1-PIN）；`OUT_OF_UNIT`＝3 表物理排除（分點／權證／鉅額分點）；`finmind.py:_quota_gate` 預設啟用、黑箱錶機台以 env `FINMIND_QUOTA_GATE=off` 降為只 log（勿改 code）；sponsor-only 已落地資料＝最終資產不可 drop 重建；git push 用 `.env` 之 GITHUB_TOKEN（[[git_identity_in_env]]）；DB／`.env`／memory 皆 machine-local 不隨 git（[[db-cross-machine-independent]]）。

**Why**：舊版此檔累積多層補丁後自相矛盾（同時寫「models 已建」與「models 仍未建」；15 package／193 scripts／原則精華 v1.9.1／憲章 v1.46.0 皆已過期），在錯底座上規劃會排出跑不動的行程。

**How to apply**：接手本專案讀序＝本檔 → [[augur-world-construction-core]] → [[augur-tech-baseline-20260730]] → repo `HANDOFF.md`。**回答前重讀對應 SSOT 原文、勿憑本摘要**（#20 實證教訓）。

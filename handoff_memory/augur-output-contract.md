---
name: augur-output-contract
description: "2026-07-12 輸出契約入憲+三度堅持刪句(靈魂v1.8.0/憲章v1.44.0→v1.45.0,現行v1.46.0)——E[r]升格幅度級得逐股;⚠A3三門實為preregistered未簽(2026-08自動出手deadline)"
metadata: 
  node_type: memory
  type: project
  originSessionId: b066145f-886c-4e08-a8ce-952b36c108ab
---

2026-07-12 用戶英文規格拍板「以上入憲」→ 輸出契約立法完成:**靈魂 v1.6.0→v1.7.0、憲章 v1.43.0→v1.44.0**。

**三產物閉集**:①方向機率 P(up)%(個股+top3/5)②方向準確率=horizon 級 OOS 命中率%(**非單股保證**硬綁)③期望報酬率 E[r]=②之確定性經濟換算(horizon/組合級非逐股、唯導自經濟終關同一裁判、econ_verdict 同源硬綁、econ 判死不顯數字)。**永久除外不變**:逐日價格點位/路徑/目標價、單股準確率宣稱、100% 正確。

**Why(雙留痕)**:E[r] 撞靈魂「不是預測絕對漲跌幅」→ AI 勸阻(修靈魂不增可預測性、僅改敢說與否)→ 用戶二度堅持「修靈魂」→ 裁以**和解式增修**:不刪不可違反句、增列衍生產物+和解句「E[r] 係方向機率之經濟翻譯、非幅度預測」。Opus 4.8 三視角對抗審查 4 blocker 全吸收入憲文本(fail-closed 升格 DB 機械閘/增列不取代五項硬綁/跨家族多重性揭露/ECE=DB 讀值)。SSOT=`reports/augur_oracle_output_contract_plan_20260712.md` §9-§11。

**三度堅持刪句(同日,commit 1cdee99)**:用戶回「明確要修靈魂」=三度堅持 → **靈魂 v1.8.0/憲章 v1.45.0**:刪「不是預測絕對漲跌幅」句(治權檔規範零殘留、僅存刪除紀錄);E[r] 升格**幅度級產物、得逐股呈現**(E[r]ᵢ=horizon 級命中率×該股波幅−成本)。**不受影響之鎖完整清單住憲章 v1.45.0 輸出契約條**(逐日點位/路徑除外、no-v3、GATE 唯一路、五項硬綁含⑤禁單股準確率、三敵、guard 棘輪、100% 除外)。三視角執行審查:誤鬆檢查零發現。留痕=計畫 §12。

**How to apply**:O1 實作殘餘缺口(非憲法層)——produce 呈現「gate 所驗證 artifact 本身」非全資料重訓、market model 身分路由(FK 卡死)、econ_verdict 持久化(⚠原記「現無表」已過時:`econ_verdict_rule`/`direction_econ_verdict` 兩表已存在)、as-of 前瞻推論路徑(trainer 只出 OOS 歷史)、成本 COST_TW 落 DB(#29b)。

**三鏡頭候選(T0-T4 全完成 2026-07-12)**:`own_threelens_interact`——T1 月頻鏈 113 panels/222.9 萬值/44 特徵(builder=`build_threelens_monthly.py` **換 FEATURE_TABLE 零複製 generator**);T2 冒煙一次跑(hit .517/.521/.534 工程數字非宣稱);T3 adapter(REGISTRY 第 8)+凍結註冊;T4 **A3 獨立家族 3 門**:原三門 criteria_sha 為手刻配方 bug(12碼/無separators)→「挪門柱」假警報,舊配方重算證內容未變;修復=舊列 superseded 留檔+`_r2` 同判準重註冊(jsonb 等值✓)+寫入器改用 `_sha`。⚠️**更正(2026-07-17 live DB 實查,推翻本則原「已簽核」句)**:`_r2` 之重簽**只寫進 code(`preregister_direction_gate.py`)、從未對生產 DB 執行**——live `direction_gate` 查 `_r2` **0 列**;實際三門=`dgate_a3_threelens_{20,40,82}`、status=**preregistered**、approved_by=**NULL**(擱置未簽)。以 DB 為準(憲章 approve 唯決策層人 TTY 執行);note 自由文字寫「approve 併簽」但 status≠approved→**機器狀態是唯一權威、非 note**。fail-closed 仍成立(錯在保守側)但**有 deadline**:候選 `own_threelens_interact` status=active/track=H→**2026-08 首個交易日自動出手=首手早於 approve**。K 計畫同日六件全執行(橋 59,706 係數/items 軌 119,764/三閘負向測試過/週更 timer/R6 合格 0.87/O1 fail-closed 生產器);**Wave 1 已 R4+activate(hugo)**:FRASER key 有效(僅收 X-API-Key header、adapter_config.auth_header 機制)、首輪最小 harvest 落 knowledge_item(fraser 2/oapen 61/sec 2)、全文層需源專屬抓取待 plan-first;audit 自癒跑者住 `~/augur_audit_selfheal.sh`(持久)。**開賽前置人工關卡全清,唯等 audit 綠→E1→strict→evaluate→開賽(零人工)**。關聯 [[augur-oracle-direction-verdict]] [[augur-three-lens-research]]。

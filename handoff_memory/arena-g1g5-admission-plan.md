---
name: arena-g1g5-admission-plan
description: arena 開賽前置=G1-G5 實質驗證機制(取代已退史料的 unfreeze gate);⚠2026-07-17更正:Phase 0 全7顆已拍板(非僅D-1~D-5)、gate arena_adm_5305655ad1cd evaluated_pass、arena 已開賽(親驗 direction_arena_prediction 4,128 列/8 隊/已結算 0)
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

**2026-07-16 hugo 拍板轉向**:evaluate(unfreeze gate) 實測=純唯讀診斷(只機械測守門1-4、不改 status、G1-G5 標「本計畫內不可達」=**從未實作**)→ 接受解凍已由入憲 07-12 完成、gate `unfreeze_06dcb178267d` **status→superseded 史料留檔**、**arena 開賽前置改以 master plan §4 G1-G5 實質驗證機制為準**。(我先前誤稱 evaluate「燒 gate 不可逆」是照搬 criteria g5 設計文字、非 code 事實——#15 教訓:治權物件行為以 code 為準。)

**計畫書 SSOT** = `reports/arena_g1g5_admission_gate_plan_20260716.md`(ultracode workflow 12-agent 盤點+三面對抗審查;含 §5 表 schema/§6 python 程式規畫/§9 開賽驗收/§10 逐條處置)。

**對抗審查揪出的 blocker(實證確認)=軸別誤植**:要開賽的「arena」是**方向/預言機軸**(`direction_gate` 6 列 `dgate_arena%` approved:chronos/timesfm/own_stack;特徵 `daily_direction_feature_values` 19.2M 列;日管線 `run_arena_daily_pipeline.py::_gate_approved` 只檢這個;ledger `direction_arena_prediction` 0 列),但 master plan §4 G2/G3/G4 全是**相對強度軸**產物(feature_values/RankRidge/econ_verdict_rule)。硬接=跨軸誤植+違 #12 雙校準棧。

**核心解法=兩層切分**:(A) 開賽硬前置(今日可判)=G1(reconcile)+G2(anti-leakage 迴歸);(B) 開賽後持續 verdict=G3+G4(綁實際產 live 輸出的軸)。方向 arena 開賽即入 `review_observation_only` tier、永不宣稱確立級;確立升格走方向軸自己門二 `evaluate_direction_gate`(≥60 clusters)。

**G1-G5 機制化現狀**:G1(reconcile)partial(近期真綠但 missing_in_db=5369 抽樣吸收、窗滾動非全史)、G2 gap(方向特徵無洩漏鎖)、G3 gap(無 live 視窗碼)、G4 partial(升級判定器未實作)、G5 partial(原子 evaluator 只方向 gate 有)。

**Phase 0 決策(2026-07-16 hugo 逐項拍板)**:
- **D-2 軸別=Reading A**(方向走門二;G3/G4/D-7/D-8/D-9/consecutive_k 移出 arena 關鍵路徑、歸相對強度部署)
- **D-5 對帳=全真名冊 3,114 真股**(排除權證;`reconcile_per_stock(roster_only=True)`+`daily_maintenance --full-universe`+`scripts/full_universe_attest.py` 已實作;過夜放量進行中 driver=full_universe)
- **D-1 G2 方向覆蓋=補做**(建 `daily_direction_feature_values` anti-leakage 迴歸鎖;實作首步查 `build_daily_direction_features.py` as-of 紀律)
- **D-4 MIS=補明確揭露**(全宇宙跑完 MIS=真實數非抽樣吸收)
- **D-3 gate 表=新專表 `arena_admission_gate`**(帶 axis 消歧+supersedes_gate_id 鏈+白名單 trigger;subsumes D-10)
- **D-6 hash 正規化=復用 `reconcile._norm` 口徑**(#12 單一住所;定點舍入+確定性排序+NULL sentinel;normalization_ref 版本化)
- **D-11 U6 放鬆語意=白名單枚舉+fail-closed**(floor↓/ceiling↑/count↓/alpha↑=放鬆;未列/新鍵當疑放鬆要簽核)
- **→ arena 開賽關卡 Phase 0 全 7 顆已拍板**(D-1~D-6、D-11;D-10 subsumed);降級=D-7/D-8/D-9/consecutive_k(相對強度部署、非開賽關卡)

**G1-PIN(07-16 午後 hugo 拍板;supersede G1 滾動框架)**:「資料就定在 2026-06-30、不要再去追資料完整」——live 世界 byte 對帳=移動標靶(每日新資料+修訂),滾動真綠明天即過期=「凍一條河」概念錯誤(hugo 點破);且追 byte-equal-to-current-API 與 as-of vintage #8 有張力。**G1 重定義:≤05-31 凍結期快照認證(既有)+06 月段一次到綠→凍 G1 參照,不再滾動追**;與 feature_values 凍結後 panel(06-30)對齊。滾動全宇宙放量中止於 32/84(checkpoint 留檔;工具 `full_universe_attest.py` 支援 --audit-until 可復用於 pinned 窗);TaiwanFuturesDealerTradingVolumeDaily EX2990 未鑑識(滾動窗產物)。06 月段驗證方式(全名冊/抽樣揭露/接受日常 sync 證據)=gate criteria 組裝時小裁決待 hugo。

**Phase 1 全 7 元件完成(2026-07-16)**:①`migrate_arena_admission_gate_ddl.py`(表+挪門柱 trigger;selftest 4/4)②`preregister_arena_admission_gate.py`(繼承 990ddea 逐鍵複製+sha 等值斷言;draft `arena_adm_3f1cfdc9aded`)③`freeze_feature_panel_hash.py`(兩軸洩漏鎖:36+2,830 panel/19.2M 列 verify PASS;防改 trigger;踩雷=named cursor 跨 commit 須 withhold=True、背景命令勿包 tail pipe 吃 exit code)④`evaluate_arena_admission.py`(核心裁判:守門鏈+G1/G2 fail-closed+原子單筆終態;**--check=唯讀預演必先跑**)⑤`verify_score_repro.py`(**校正:oos_sample.score=walk-forward 逐折 refit 產物、非 4 artifact 輸出**;正解=artifact 重打分決定性,4 模型×28 panel=112 組凍結+verify 100% 復現至 5 位;正典家族=990ddea scope.model_ids 已答 ce62866,D-7 免議)⑥`report_restatement_diff.py`(U5 人裁佇列;pending 擋綠→簽核放行,evaluator 聯動實證)⑦雙閘接線(daily_pipeline+arena_round:閘一 dgate approved ∧ 閘二 admission evaluated_pass;fail-closed 實證兩 chokepoint 皆拒 rc=1)。

**終局(2026-07-16 晚):gate `arena_adm_5305655ad1cd` evaluated_pass、雙閘全開、arena 可開賽**。hugo 拍板鏈:06 月段=sampled_disclosed+凍結授權代跑(聊天留痕)→06 月窗對帳第一輪 FAIL(EX6826/gap1)→根因四治:SplitPrice→cadence、TaiwanStockInfo→snapshot(台灣本尊漏標,同型 4 張先例)、Dealer→restating(上游整批撤 dealer 申報 6776 列實證)、BuySell/Wide EX36=**API 整日撤列**(2443/4144 實證)→**撤列容忍第三層(hugo 拍 A;FRED Tier A 同構:sync 決定性→DB-only 必=API 曾回=合法 restatement;by-date 抓失敗仍保守留 EX)**→第二輪 PASS(#4:VM0/EX0/容忍36揭露)→freeze(approved_by=hugo)→check 綠→evaluate=evaluated_pass→990ddea 雙向鏈回填。**踩雷:`run_at::date` 別名遮蔽——cast 輸出欄名仍=run_at,ORDER BY 綁到 date 型輸出欄→同日兩列排序退化未定序→evaluator 抓到舊 FAIL 列**(修=AS run_date;check 曾假紅、--check 唯讀預演救了不白燒)。開賽剩=cron 掛+首日陪跑(A2 排程已核)。

**執行邊界(hugo directive)**:皆計畫層方向決策;實作(建表/evaluator/hash/接線)與治權修訂**一律待 hugo 後續拍板才動工**(#26),不因決方向就動手。

**A4 波次入賽(2026-07-17)**:Chronos-2+Moirai-2.0 兩隊入賽(8 隊全員)——依台股 TSFM benchmark(reports/tsfm_taiwan_benchmark_20260717.md:20 個 DM 檢定零顯著勝 RW、Chronos-2 最不退化)。A4 家族 K=2/α=0.025/21 門全序列揭露;license 白名單擴 cc-by-nc-4.0(hugo 拍 A;**Moirai=NC、商業化前須清算**);dgate approve=hugo TTY 親核(憲章 v1.42.0 TTY 閘實證擋 AI 代跑,admission gate 可代跑之對比)。踩雷:Chronos-2 predict_quantiles 回 list[(1,H,9)] 非 v1 stacked;uni2ts 裝機降級 numpy/torch(四關驗綠無傷,score repro 洩漏鎖首次實戰)。**alpha 提升計畫**=reports/taiwan_alpha_improvement_plan_20260717.md(三軸 D/P/M、51 項對抗審查、11 拍板點、DSR 雙基線對帳=P0 交付;待 hugo 拍)。

**治權修訂批次完成(2026-07-17 hugo「全批照案」)**:原則精華 v1.9.1(解凍子條 live 准入=G1-G5 機制+G1-PIN+門二確立)/憲章 v1.46.0(L130 加註+L131④ 精確化+修訂歷程)/CLAUDE v1.29(§2 blockquote)/README/HANDOFF 全鏈級聯;判準值零變動。**發現平行 meta-治理體系**:hugo 另一會話建 `augur-constitution` repo(AUGUR-MC v1.3 Layer 0 lex superior/Steward 裁決/AUD 審計),5 治權檔已加「憲章從屬聲明」檔頭(Layer 登錄;#7 vs P4.E5 緊張揭露、補正期 2026-10-14)——rebase 整合乾淨(雙方改動共存);日後治權工作須認知此上位體系存在。

見 [[augur-unfreeze-20260712]](gate 退史料+解凍入憲)、[[augur-validation-master-plan]](G1-G5 SSOT=master plan §4)、[[audit-attestation-falsegreen]](G1 對帳誠實化史)、[[augur-oracle-direction-verdict]](方向軸六門判死史、arena=解凍後重測)。

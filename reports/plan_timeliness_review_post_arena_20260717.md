# 兩計畫開賽後時效性複核(2026-07-17)

**建議存檔名**:`reports/plan_timeliness_review_post_arena_20260717.md`(#16 命名)
**性質**:複核報告,呈 hugo 拍板;本報告只給判定+選項+建議,**不代拍**。
**複核方法**:2026-07-17 逐節實查——live DB query(經 `augur.core.db`)、Read/Grep live code、治權檔現行版次(靈魂 v1.8.0/憲章 v1.46.0/原則精華 v1.9.1/CLAUDE v1.29)、git log/tag;**零記憶引證**,每一判定附可溯源實證。

**判定字彙**:
- **已被實現**=該節交付物已由後續工作真實落地(code/DB/服務可證),照案再做=重工;
- **仍有效**=該節主張至今為真且仍在承重;
- **需改寫**=結論核心仍立但前提/措辭已過時,引用須改寫;
- **已被超越**=該節已被更新機制/裁決取代,引用即引已廢法。

---

## 一、背景(hugo 07-12 預裁、觸發條件 07-16 開賽已滿足)

- hugo 於 2026-07-12 預裁:「開賽後 AI 先做兩份 07-09 計畫的時效性複核再拍」(HANDOFF §4.5 待辦第 2 項)。arena 已於 **2026-07-16 開賽**(cron 三行掛載實查:22:30 pipeline/23:10 settle/月初 scoreboard;首手 1,376 列;tag `archive-20260716-arena-live`、commit `e23a102`)——觸發條件滿足,本複核即該預裁之執行。
- 兩計畫誕生於 2026-07-09,其後八日發生系統性巨變(節錄,全數實證):**07-10** 全知 e2e 主計畫 v3 定稿——其檔頭「合併取代」**明文列名吸收本次待複核之兩案**(`reports/augur_omniscient_e2e_master_plan_20260710.md` 第 3 行);**07-11** 驗證總綱 V0-V2+antileakage 修 4 洩漏+計畫②結案釐清報告(commit `a7a2c0c`);**07-12** 解凍入憲(憲章 v1.43.0/原則精華 v1.9.0)+方向軸 v2 全家族判死 no-v3+輸出契約入憲(E[r] 三產物,憲章 v1.44/45);**07-14** Qdrant serving 上線+audit 誠實化;**07-16** unfreeze gate 退史料+arena 前置 G1-G5+G1-PIN+開賽;**07-17** 治權批次(原則精華 v1.9.1/憲章 v1.46.0)。
- 故本複核重點為「**v3 合併取代後,兩案是否尚有殘漏工項與登記債**」,同時逐節留判定紀錄供溯源。

---

## 二、計畫①全能顧問(`reports/augur_omniscient_advisor_plan_20260709.md`)

### 逐節判定表(13 節:已被實現 8/仍有效 1/需改寫 1/已被超越 3)

| 節 | 判定 | 關鍵實證(2026-07-17 實查) |
|---|---|---|
| §0 三十秒+主作者親查 | **已被實現** | v3 檔頭第 3 行明文「合併取代」本檔;P1-P8 落地:G3 缺口已焊(`src/augur/advisor/ollama.py:33` `_assert_local_host` 建構時斷言+`:109`/`:161` 焊點註記,selftest `:223` 拒 `http://evil`);import_isolation 本日實跑 exit 0;散裝鏈由 `scripts/refresh_knowledge_pipeline.py` 顯式 DAG(`:50-68`,harvest→…→vector_export)完成 |
| §1 治權張力 T1-T3 | **需改寫** | T1 仍有效(isolation exit 0、`guard.py:60` 數字白名單健在);T2 過時——`payload.py:30-32` 已有 probs 欄+prob_note(v1.40.0)、`prediction_probability` live(5 horizon×339 列)、07-12 輸出契約入憲;T3 前提已死——FREEZE 07-12 解凍入憲、07-16 unfreeze gate 退史料(`unfreeze_06dcb178267d`=superseded,live query),live 准入改 arena G1-G5 |
| §2 十個 stage S1-S10 | **已被實現** | 十段全存活、「須補」全補齊:S8 works/en 積壓已清(`knowledge_build_meta` cursor=1,785,693 @07-12;殘餘僅 59,852 句債,憲章 v1.40.0 已列冊);S9 Qdrant 上線(`knowledge_vectorstore_config` sentence_items=qdrant_server;curl 6333 回 collection);S10 服務 live(curl 8399/8090 HTTP 200) |
| §2.1 思想相關性推導 | **仍有效** | 承重牆仍立且長大:`knowledge_term_affinity`=3,076,918(philosophy 2,957,154 未變+items 119,764 新增)、group_affinity=6,968、lexicon=154,875;紅線③守恆(`vectorindex.py` search 只回 `(pg_pk,distance)`、PAYLOAD_FIELDS 窄封閉集)。唯「擴 domain 零改碼」一句被 K 計畫升級取代(K1 語意橋 59,706 列 live) |
| §2.2 W-fix-1/2/3 | **已被實現** | W-fix-2:refresh 具 `--domain/--stage/--from-stage/--until/--stage-limit`+flock 單例;W-fix-3:`vectorindex.py` make_index+config 表;W-fix-1 目標已達但機制被 v3 D7 取代(鏈尾住 orchestrator DAG 非 harvest 內),終態由憲章 v1.40.0 暢通不變式+`verify_knowledge_e2e_smoke.py` 機械判定 |
| §3 可換接縫表 | **已被實現** | config 表 live 且已實戰切換(四 scope,比計畫多 sentence_works 拆分)+shadow_eval 表+embedspec fail-loud 斷言;設計細節被 v3 A-34 超越:無 PgvectorIndex adapter——pgvector=SSOT 直讀(`philosophy/retrieval.py:81/:88`)、qdrant 才走 make_index(`:316-321`)+故障自動降級(`:339`) |
| §4 對話設計(三通道+五閘) | **已被實現** | 五閘全焊(G1 isolation+BRIDGE_LITERALS 字面閘 `import_isolation.py:175`;G2 PAYLOAD_FIELDS 封閉;G3 建構時 assert;G4 items affinity 同走 registry;G5 憲章 v1.23.0 CLEAN fail-closed);三通道 live 且升級(通道1 H60 picks+P6 機率附欄 `payload.py:196/:211-225`;通道2 concept_graph `advise.py:60`+K1 橋;通道3 兩宇宙 deflated 地板 `payload.py:136-148`)。**注意:本節 G1-G5 與 07-16 `arena_admission_gate` 之 G1-G5 同名異物,日後引用須標明** |
| §5 最小 token 紀律 | **已被實現** | 已從計畫慣例升格為憲章不變式:v1.46.0 `:185` 暢通不變式(零 Claude/雲端 LLM usage)+v1.37.0 本機 LLM 隱私上限條文健在(`:181`) |
| §6 分階段 W1-W8 | **已被實現** | W1-W6 全 ✅(逐項實證見判定 JSON;W6 works/en cursor 1,785,693);W8「不做 Qdrant」被 07-14 serving 上線**反向推翻**;唯一殘項=**W7 逐字證據句進 prompt**(`advise.py:58` 明文「屬 W7 後續」) |
| §7 拍板決策清單 | **已被超越** | 決策1 被計畫②執行+判死+機率層取代;決策2(W8 不啟)被 Qdrant 上線推翻;決策4 已放量執行;決策5 由 G6 收窄定案;決策3(換模重嵌)仍活但住所已移 v3 §4 SOP-A |
| §8 入憲項 | **已被超越** | 實際入憲走 v3 §8 路線=憲章 v1.40.0(非本檔擬的 CLAUDE #29 增補,grep 現行版零 vectorstore 字樣);唯一可補=v1.37.0 條加一句「G3 已焊為建構時機械 assert」留痕,可選微修 |
| 附:實查證據錨(07-09) | **已被超越** | 全部數字已位移(sentence 1,756,836、term_affinity 3,076,918、item 254,176…);僅 isolation exit 0 與 G3 兩親查結論至今仍真 |
| §9 schema+程式規畫 | **已被實現** | `knowledge_vectorstore_config` 建成且升級(4 scope+CHECK 含 qdrant_server)、migrate 腳本同名存在;vectorstore.py 改名 `vectorindex.py` 落地;改碼1/2/3/5 ✅、改碼4 被 DAG 取代;payload 新讀三表(probability/calibrator/revalidation_baseline)均超出計畫視野 |

### 總評

本計畫已被 v3 檔頭明文「合併取代」,且 v3 隨後**真的實作了本計畫幾乎全部交付物**;W8 更被反向推翻。照案續行已無對象;後續譜系(K 計畫 07-12→三通道 master 07-14)已是現行前進藍圖。

**殘留工項(僅 2 件,均微小)**:
1. W7 共現逐字句進 prompt(`advise.py:58`)——建議移交 K 計畫/三通道 master 譜系追蹤;
2. 憲章 v1.37.0 條補「G3 建構時機械 assert」留痕一句——可選、單獨小修即可。

**登記債(本次複核唯一新發現)**:HANDOFF §1 第 22 行仍標本檔「活躍計畫①:未執行、待拍板」,與 v3 合併取代聲明及落地事實矛盾,須修。

**取代譜系**:v3 主計畫(07-10)→K 計畫(07-12)→三通道 master(07-14);另 07-12 解凍+輸出契約廢 T3/通道1 前提、07-14 Qdrant 推翻 W8、憲章 v1.40.0 承載入憲項。

---

## 三、計畫②短 horizon 模型(`reports/augur_prediction_short_horizon_model_plan_20260709.md`)

### 逐節判定表(10 節:已被實現 7/已被超越 3)

| 節 | 判定 | 關鍵實證(2026-07-17 實查) |
|---|---|---|
| §0 三十秒+誠實預期 | **已被實現** | 拍板當日即執行完畢(commit `001095b`):verdict 報告 H20 判死(淨 Sharpe +0.27<+0.30、DSR 0.001)、H40/H60/H120 thin(DSR 0.308/0.407/0.771);live 實查 `prediction_probability` 5 horizon×339 列 econ_verdict(H20=dead、餘 thin_unestablished);07-11 結案報告確認「完成而非失敗」 |
| §1 單位釐清(命門) | **已被實現** | 日曆日對映已定案並固化:`payload.py:228-229`「P30←H20 ≈29 日曆日·dead;P60←H40 ≈58 日曆日·thin」;horizon 矩陣全跑(外加 H120/H82);`walkforward.py:21-22` 交易日單位+`_H_FORBIDDEN=252` 原封 |
| §2 治權框定 | **已被超越** | 核心綁定 FREEZE 已於 07-12 解除(原則精華 v1.9.1 `:79`:解凍+live 准入依 arena G1-G5+G1-PIN 2026-06-30);其餘框定(軸別/#8 雙閘/#14)仍為治權常項,但那是**憲章之法、非本計畫存續之功** |
| §3 誠實四關管線 | **已被實現** | live 實查:`revalidation_ledger` H20/H40 各 B=3、D=48;`trial_ledger` H20/H40 各 8 列(`trial_ledger_uq` 七欄鍵原封,pg_constraint 實查);`revalidate.py:48-49` 即計畫指定之唯一改碼處;且已被升級覆蓋——stage R 五軸各 89 列、stage_chk 擴為 {B,C,D,R},**比原四關更嚴** |
| §4 分階段 W1-W5 | **已被實現** | 07-11 結案報告逐項對照全數完成或升級取代,本次 live 複核仍成立(W2 model_registry RankRidge 各 horizon 落地;W5 由機率層升級取代);誠實殘留 3 項(RankGBDT 未入 registry/H82 無 B/D/trial 列/W5 live e2e 未複測)**本次實查仍未清,但均已移交鄰接軌** |
| §5 誠實裁決預判 | **已被實現** | 預判全中:H20 判死、H40 薄、H120 仍最強(0.771,「越長越強」序保持);「不會變成可靠 30 天漲跌預言」更被方向軸十門判死+no-v3 入憲(憲章 v1.46.0 `:140`)以更強形式定案 |
| §6 拍板+入憲 | **已被超越** | 拍板①②已被落地吸收;入憲路徑被取代:`_DEPLOY_HORIZON` 從未落地(grep 零命中)、FREEZE 留痕失效;部署/升級生命週期現歸 **G4 相對強度部署軌**(G1-G5 計畫 D-2 裁決),且 H20 復活有硬規:`preregister_unfreeze_gate.py:85` `h20_dead_no_shortcut`+G4-W5 升級迴圈排除 dead |
| §7.1 schema:無新表 | **已被實現** | 四表全數如計畫承載寫入;`trial_ledger_uq` 與計畫一字不差;兩處演化屬升級非違約(stage_chk 加 R;in_portfolio 改標 top decile=33) |
| §7.2 程式規畫 | **已被實現** | 六支全存在如規畫(`train_ranker.py`/`predict_asof.py`/`deflate_headline_verdict.py`/`report_short_horizon_verdict.py`/`revalidate.py:48-49` 行內註解即引本計畫);唯一未竟=RankGBDT 無 registry artifact(結案報告已列殘留、不擋結案) |
| 附:實查錨(07-09) | **已被超越** | registry 已由 {H60,H120} 變 {20,40,60,82,120}(RankRidge 9 列,最新 07-11 canonical 29 重訓);H120 DSR 0.936→0.771;引用數字一律以 ledger/verdict 現值為準 |

### 總評

本計畫已**三重處置完畢**:(1) 07-09 當日全數執行(commit `001095b`);(2) 07-10 v3 檔頭明文合併取代;(3) 07-11 結案釐清報告 W1-W5 逐項對照建議結案(commit `a7a2c0c`)。本次複核確認結案判定**全部仍成立、無新翻案**。

**對導讀三問的裁定**:
- **軸別**:本計畫=相對強度軸(§2 明文),與方向軸 no-v3 **零衝突**(no-v3 只鎖方向假說);
- **h20_dead**:零衝突且反被其保護——07-09 重跑發生在 `h20_dead_no_shortcut` 預註冊之前、屬誠實再驗證;今後 H20 復活須重走 B 提拔三審+G4 升級迴圈(排除 dead);
- **日曆日**:待釐清項已定案為日曆日對映並固化 payload 固定用語。

**警示兩則**:(a) 日後任何人引本計畫 §2/§6 做 H20/H40 部署依據=**引已廢法**,一律走 G4 軌(DSR≥0.95 硬條件+consecutive_k+h20_dead_no_shortcut);(b) 結案報告 3 項誠實殘留不因廢止而遺失——已移交 gbdt 部署時/H82 軌/顧問例行 e2e。

**取代譜系**:v3 主計畫(07-10)、verdict 報告(07-09)、結案報告(07-11)、驗證總綱 V0-V2、機率層、原則精華 v1.9.0/1.9.1 解凍條、G1-G5 計畫 G4 部署軌。

---

## 四、總建議(選項+理由;最終 hugo 拍)

### 計畫①全能顧問——四選項評估

| 選項 | 評估 |
|---|---|
| 照案續行 | **無對象**——v3 明文合併取代且交付物幾乎全部落地,續行=重做已完成之事 |
| 小修後續行 | 可修者僅 §1 措辭與 §8 微留痕,修完後計畫仍無未執行主體,無收益 |
| 大改 | 後續譜系(K 計畫/三通道 master)已是現行藍圖,大改=重複造藍圖 |
| **廢止併入他案(AI 建議)** | 正式裁定=已結案史料、併入 v3/K/三通道譜系 |

**若採建議,配套三件**:
1. 修 HANDOFF §1 第 22 行(去除「活躍計畫①待拍板」標記)——本次複核唯一登記債;
2. W7 共現逐字句進 prompt 移交 K/三通道譜系追蹤;
3. (可選)憲章 v1.37.0 條補 G3-assert 留痕一句,單獨小修。

### 計畫②短 horizon——四選項評估

| 選項 | 評估 |
|---|---|
| 照案續行 | 已於 07-09 當日全數執行完畢,無可續工項 |
| 小修後續行 | §2 FREEZE/§6 入憲路徑已廢,無活體可修 |
| 大改 | 部署/升級已歸 G4 軌,另立計畫=與 G1-G5 計畫重複 |
| **廢止併入他案(AI 建議)** | 對 07-11 結案報告正式**追認「已結案(由後續工作完成+取代)」**即可,零新工作量 |

**若採建議,配套一件**:3 項誠實殘留(RankGBDT registry/H82 B-D-trial/W5 live e2e)於追認時明文記「已移交鄰接軌」,防遺失。

### 共通登記債(不論選項皆建議處理)

1. HANDOFF §4 STATE 落後 07-17 治權批次+AUD-02 共四個 commit;
2. HANDOFF「chronos/timesfm 套件缺待補裝」已被 07-16 晚間入賽事實推翻(live 實查 `direction_arena_prediction` 07-16=6 隊×344=2,064 列);
3. 本複核完成後,HANDOFF §4.5 待辦第 2 項可勾銷(待 hugo 拍板後)。

---

## 五、無法判定項(誠實列)

本次逐節判定 23 節均得出明確判定、無「無法判定」節;以下為**未重驗/未歸因**之誠實保留:

1. **顧問 live e2e 對話級行為未重測**:本次僅以服務存活(curl 8399/8090 HTTP 200)+讀碼佐證,未逐字重測 P30/P60 對答輸出——即計畫②結案殘留 #3(W5 live e2e)至今仍未複測,建議併入顧問例行 e2e 時清償。
2. **H120 DSR 0.936→0.771 位移未歸因**:僅確認現值(verdict 報告重驗值),未分解係 canonical 29 重訓抑或資料窗變動所致;不影響「越長越強」序之判定。
3. **嵌入殘債 ≈59,852 句對檢索品質之實際影響未量測**:債已列冊(憲章 v1.40.0 管線債,sentence 1,756,836 vs embedding 1,696,984),但檢索品質降幅本次未測。
4. **範圍外觀察(非判定)**:arena 尚無已結算列(settle_mode 全 NULL,開賽次日屬正常)、9 候選中 own_stack_rolling/own_threelens_interact/own_v2_frozen 尚未出手、A3 三門 dgate 仍 preregistered——均屬 arena 軌現況、非兩計畫範圍,本複核不作判定。

---

*複核依據:兩案逐節判定 JSON(2026-07-17 live 實查)+07-09 後大事錨點清單(git/HANDOFF/docs/DB 實查)。本報告為呈核文件,兩案處置最終由 hugo 拍板。*
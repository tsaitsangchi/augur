# 終版圈選單（2026-08-01 晚）——20 項裁決、一次會話圈完

> **性質**：`augur_steward_adjudication_sheet_20260801.md`（建議案）＋`reports/w2_20260801/`（17 份呈案）之**圈選介面終版**。
> 呈案起草後同日又落地 A1 符號尺／D1／F3／cron apply／drain-timer disable——本單經 **12 路唯讀鮮度驗證**
> （wf_5e997a41-98f，250 次工具親驗，08-01 16:14 前後現查），過期處已就地修正、每項附證據級 final line。
> **裁決仍專屬 Steward（§8.1／L6.18(a)）**；本單為 AI 起草之建議，多項涉及對 AI 自身產出之閘——證偽條件住呈案單，不重複。
>
> **圈選格式**：整批＝回覆「照終版單圈：全部同意（含三個內嵌子裁）」；逐項＝「<ID>-同意」／「<ID>-改採…」。

## 先講三個內嵌子裁（圈「全部同意」時預設採建議案）

| 子裁 | 選項 | 建議 |
|---|---|---|
| S-i（附 TWEVO-APPLY-go） | 開閘方式：**A 逐顆人裁**（hugo 親跑 `--allow-apply --gate-ref TWEVO-APPLY-go`）vs B cron 常開（`--allow-apply` 進 TWEVO 行） | **A**——晉升是治權動作，driver 明文不代簽；B 失去逐顆人裁語意 |
| S-ii（附 E2） | headline 錨定名歧異（HANDOFF 稱 1.1302「新錨」vs 登錄冊「1.1321=治權錨」） | **三列版並記**：1.1321=P0 治權重定錨／1.1302=P2 量尺 headline 兼本機快照／1.1972=historical_reference 家譜首節點——`scale_note` 分欄各記其義，不擇一抹史 |
| S-iii（附 F3-apply） | 「--check 常備」無機械載體（無 cron、無儀表掛載） | **掛入週日儀表一行**（唯讀 `--check`，下批 cron 合批進 SSOT）——名實相符，免季度演練另立制度 |

---

## 批次一｜殭屍帳本三件（圈後 AI 立即執行，一小時內清完）

| # | 終版建議行 | 執行 |
|---|---|---|
| 1 | **B1-apply-同意**——親驗 running 恰 9 列＝run 11-19、run 20 succeeded 無新增；`--check` 實跑 9 筆全擬回填、無活引擎（pgrep＋/proc comm）；`--apply` 帶 `AND status='running'` 冪等＋活引擎/1h 雙閘 | AI（apply 前重跑 --check 防 01:30 cron 新輪混入） |
| 2 | **B2-同意**——甲案全 7 筆全標不刪：#7–#10 標 `test-artifact-20260731`、#4/#5/#11 標 `ruling:superseded` 各附理由。7 筆微秒時戳逐筆吻合呈案 WHERE 釘值；表零 trigger；**timer 已 disable（08-01 16:00，含 wants symlink 移除）＝重開機復活風險已解、無時間壓力**；斷言已釘 `defer_id<=11` 不誤傷 08-03 後新列 | AI（cleared_by 為處置標記非人簽欄） |
| 3 | **B3-同意**——修好再重啟（非停用）：前置 B1+B2 清帳、`decide()` 加 stale-hold（>72h⇒hold），再 `systemctl --user enable --now augur-drain-deferred.timer`（**注意：現連 symlink 都已移除，重啟須 enable 非 start**） | AI |

## 批次二｜晉升鏈（本週末窗口：A3 於週一 08-03 23:00 TWEVO cron 前落地）

| # | 終版建議行 | 執行 |
|---|---|---|
| 4 | **A3-同意**——四件套＋UNJUDGEABLE⇒FAIL＋77 筆乙案（重評＋遷移）。08-01 晚全數親驗仍準：pending_auto=77 逐字吻合、sign 表 4 列口徑相容、全部 diff 錨在 HEAD f268f14 原樣可套。落地時機用三查（pgrep∧slot∧ledger）；前置批次一（殭屍 9 列使第三查不空） | AI（A3-5 遷移之 decided_by 為機器標記；欲親跑請圈明） |
| 5 | **TWEVO-APPLY-go-同意**——三條件齊才開＋一次一顆（機械載體＝R2 單輪上限 1）；條件②明確讀為「該候選之 G-SIGN=PASS（run 21 產出）」。註：A3 乙案遷移使 pending 歸零⇒開閘時點自然後移至 run 21 後 | AI＋hugo-TTY（開閘本體依 S-i） |
| 6 | **A2/A4-同意**——**S1 已跑、14 口徑全未中**⇒依呈案原文分支**直接甲案**：mean_20d demote 除役、存量 17,072 列留史料。符號 PASS（h20 −0.0755/h60 −0.0831、5 bootstrap 全同號）誠實下修權重，但殘餘兩腳親驗仍立：run 20 G-PROM FAIL＋**零產生器不可續建**；且驗證另掘出呈案未列之 **G-ECON FAIL（port_sharpe 0.906≤bench 0.943）**增強甲案。乙案 _v2 新名立案不互斥、可另行 | AI＋hugo-TTY（demote 屬人裁：decided_by 類欄 hugo 親跑；⚠audits S1 檔的「符號證據 0 筆」一腳已被 13:57 PASS 推翻，以呈案單 14:55 補註為準） |

## 批次三｜時效項（E1 於週一 08-03 20:00 arena cron 首發前施作）

| # | 終版建議行 | 執行 |
|---|---|---|
| 7 | **E1-同意**——A 案 supersede 三門＋retire 候選。**理由採修正版**：月頻×min_clusters=36⇒判決時程約 2029 Q4、supersede 不封路（呈案單原「B′ 增每日 API 面」經親驗不成立，勿引）。**驗收數字修正**：呈案「閘一現 8 列」實為 6（起草筆誤）、施作後餘 approved=3 列即閘一仍開。逾期未施作⇒own_stack 自動首發 ≈1,035 列永久無門觀察列（僅帳面噪音、非違規） | AI |

## 批次四｜可全批次圈（無互斥、無時效）

| # | 終版建議行 | 執行 |
|---|---|---|
| 8 | **B4-同意**——甲案 3 升級＋1 新掛＋9 檔 10 點通行證先行。親驗零漂移（delonly 23表46支/真裸22/fsc 零 trigger、唯一寫入者 --record 純 INSERT 不受閘）。DDL 入 3c 統一窗、禁與週六 07:30 備份 cron 同窗（#30）；F3 若日後啟用封存另閉 4 表 UPDATE 面，P2 分批時重算清單 | AI＋hugo-TTY |
| 9 | **prodset_delta-同意**——dual_green_n 已 run-scoped（07-31 97de39b）但 `prodset_active_n` 仍全域（:183）＝**仍需施作**；併加 snapshot 版本鍵防新舊口徑跨尺直比 | AI |
| 10 | **C1-同意**——90 天＋降轉＋CHECK 三旋鈕照甲案；**排程段已 live 免執行**（你 apply 的 crontab 已含兩行、首跑 08-02 07:10）；到期日現算 10-09/10-10 全在 10-14 復審前。manual 重簽 UPDATE 屬人裁級=hugo 親跑；施作以字串錨非行號錨（§3.2 微漂 1-2 行） | AI＋hugo-TTY |
| 11 | **C2-同意**——watchdog 改 DB 三態機＋6h 牆鐘＋COOLOFF_H=24＋throttle 0.7 沿用。假綠仍每 30 分重演至 15:54、diff context 完全可套。歧義裁定：以呈案 §7 旋鈕為準（撞 403⇒COOLOFF 加大至 48，非裁決單筆誤的「改 12h」） | AI |
| 12 | **D2-同意**——MIN_MINORITY_MASS=0.05。現查全同呈案（band 非眾數質量 0.0027、閘現 ok=True、三選項皆轉 False）、錨點未漂 diff 原樣可套 | AI |
| 13 | **D3-同意（附施作批註）**——甲案本身仍正確（恆 ready 100%、mapped 12.016% 皆現查一致），**但 §3.1 全文替換須先重繫今日 D1**：保留 `f.status<>'unattempted'` 兩行＋註解，僅加二 kwarg＋_axis_parts＋axis_domain_mapped 一行；§3.2-3.5 可套（行號 +2）。逐字照抄呈案＝靜默回退 D1（121,389 件重誤判 terminal_blocked） | AI |
| 14 | **D4-同意**——乙案 token 通行證＋trigger 留帳＋R1 回收 4 筆。**施作序不可倒：先引擎 clamp 後 DDL**——驗證新發現週日 04:30 `augur-knowhow-refresh.timer` 之 KIP 路為自動批次寫入者（現射程 0，參數一改即含曾降級 145,945 件），clamp 在共用 progressive_item 內同時護住此路；與 B4 零物件重疊 | AI＋hugo-TTY |
| 15 | **E2-同意**——建 `alpha_headline_anchor`＋hugo TTY 親簽；採 S-ii 三列版、定名歧異依 S-ii 併記不擇一；DDL 入 3c 窗 | AI＋hugo-TTY（INSERT 親簽） |
| 16 | **F1-同意**——RULING-2026-042＋L7.16 適用性註記＋AL-2026-046＋同 commit 條件式紅燈。042/AL-046 親驗仍空缺、L7.16(e) 引文逐字一致；施作前重確認編號未被並行 session 搶號；裁決檔簽核欄 hugo 親為 | AI＋hugo-TTY |
| 17 | **F5-同意**——CLAUDE.md 新增 #35（三規則、限向前生效）＋§3.3 選配殘句一併准。與已落地之 pre-commit 假斷言閘不重複：閘機械強制型1/2、條文課先驗紅/下游絆線/純函式真輸入並為 --no-verify 之規範錨。基線親驗 ERROR 20/WARN 46/基線 22 行；施作以內容錨（「條號導讀」實在 :14 非 :16） | AI |
| 18 | **F3-apply-同意**——不啟用只 --check 常備；**親驗現況已即此狀態**（已 commit、--check 綠、封存 0/4）＝圈選＝追認現狀零施作；常備載體依 S-iii 掛週日儀表 | AI |
| 19 | **G2-同意**——A 外接碟為主＋C DESKTOP 為輔、B 不採。三前提 16:14 全親驗成立（零外接裝置、11G 週備份已落但同一實體碟、私有通道先例在）。⚠DESKTOP 今日 8 次探測全不可達（比呈案 6 次更多）坐實 C 僅可為輔；**生效日≠圈選日**：仍需你購碟＋插碟 | AI＋hugo-TTY |
| 20 | **G3-同意**——沙盒演練→新 P5 一次拍板→生產 apply＋最小接線＋零消費者誠實條款。六表 to_regclass 全 NULL、沙盒前提乾淨、演練材料在位。⚠演練 dump 錨=augur_20260801_weekly_Fd，輪替僅留 3 份——拍板延逾三週須換最新檔名 | AI＋hugo-TTY |
| 21 | **H1-同意**——R-CELL′ 判讀層修（不換尺）＋S-8 robot=量尺哨兵。現行尺錨 b6e5208ef821 未動（ef142e… 係 07-28 中繼尺已退役）；施作前以當刻帳本重凍 wins 集再比對 | AI＋hugo-TTY |
| 22 | **H2-同意**——三件套＋D-1 甲「首件逐件」＋method key 正名 `iid_bootstrap`。FK 三鎖/540 列 20 法皆親驗如呈案；步 4/步 6 人簽欄 hugo 親跑。⚠入冊僅解物理死鎖，sim 軸合法評估仍待 D-2 另案 | AI＋hugo-TTY |

## 已無題可裁（劃出）

- **G4**——你已親跑 `install_cron.sh --apply`；`--check` 現驗「✓ 一致」rc=0（live≡SSOT），E4/C1/G1 合批條目皆在 live crontab（52 行快照存 scratchpad）。呈案之時點建議已如期履行完畢。

## 圈選後執行分工（一覽）

- **AI 立即施作**（圈後即動、無需你在場）：B1→B2→B3→A3→E1→C2→D2→D3（重繫版）→F5→prodset_delta→F3（零施作）。
- **AI 施作＋你 TTY 親簽收尾**（我備妥指令、你逐一親跑）：A2/A4 demote（decided_by）、E2 錨 INSERT、F1 簽核欄、C1 manual 重簽、D4/B4/H2 之 DDL 窗確認與人簽欄、H1 判讀修後之裁讀、G3 沙盒拍板。
- **純你側**：G2 購碟插碟（硬體）。

## 驗證方法備考

12 路唯讀 agent 各對 live DB／repo／systemd／crontab 現查（合計 250 次工具呼叫）；judgment 準則＝「照呈案原文圈選是否仍正確」，凡數字現查不信文件。過期二項（D3/G4）與筆誤三處（E1 之 8→6 列、C2 之 id 8→9、F5 之 :16→:14）已就地修正並溯源。

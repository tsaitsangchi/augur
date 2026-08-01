# TTY 親簽包（2026-08-01 晚）——一次 session 簽完，20 項裁決全結案

> **用法**：由上往下逐格跑。標 **〔你親跑〕** 的格＝人簽／人閘動作（AI 不代打）；
> 標 **〔授權句〕** 的格＝回一句話我立即代跑（機械步、無人簽欄）。
> 前置皆已備妥並經 selftest＋突變驗紅；每格附「這是在簽什麼」。
> 缺席項（誠實）：A3 遷移與 C1 DDL 因 18:10 限額重置後才落碼，**不在本包**、落碼後小補丁另遞。

---

## 0〔你親跑・30 秒〕F1 簽核欄——RULING-2026-042 生效

**簽什麼**：L7.16 與單一角色部署之衝突登錄＋適用性註記（spec 零改、殘餘風險明載「superuser 可 DISABLE TRIGGER」不粉飾）。三件套已入庫（`57eb275`）、紅→綠驗訖；簽核欄勾選後裁決生效。

```bash
cd /home/hugo/project/augur && sed -i 's/- \[ \] \*\*准：L7.16 衝突登錄/- [x] **准：L7.16 衝突登錄/; s/（簽：＿＿＿＿，日期：＿＿＿＿）/（簽：hugo，日期：2026-08-01）/' constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md && grep -n "\[x\]" constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md
```

跑完說一聲，我 commit（生效 commit 依 #14 明示授權）。

## 1〔授權句〕統一 DDL 窗——B4＋D4＋E2＋H2 四案一次上閘

**授什麼**：四支冪等 migrate `--apply`（全部 `lock_timeout='5s'` 快敗不排隊、避 dump #30、皆經沙盒/selftest 驗證）：
B4＝3 升級＋1 新掛 UPDATE-GUC 閘（把「機器覆寫人裁」的裸 UPDATE 面關掉）；D4＝再晉升鎖 trigger（升 depth 須通行證＋自動留帳）；E2＝`alpha_headline_anchor` 建表；H2＝sim 三 CHECK＋煞車列＋kill_switch 五值。窗後我自跑行為探針（BEGIN…ROLLBACK 負測）＋同變更集 code diff（KILL_SCOPES 加 sim）。

**回「窗-跑」＝我代跑**；想親跑則依序：

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && flock -n /tmp/augur_pgdump.lock true && venv/bin/python scripts/migrate_honesty_guards_ddl.py --apply && venv/bin/python scripts/migrate_admit_state_guard_ddl.py --apply && venv/bin/python scripts/migrate_alpha_headline_anchor_ddl.py --apply && venv/bin/python scripts/migrate_sim_constraints_ddl.py --apply
```

## 2〔你親跑〕E2 簽錨三列（S-ii 三列版；**窗後**才有表）

**簽什麼**：headline 宣稱帳首三列。定名歧異照 S-ii **並記不擇一**（scale_note 各記其量尺；1.1321＝P0 量尺重定錨、1.1302＝P2 turnover 半和量尺 headline 兼本機快照、1.1972＝家譜首節點）。`recorded_at` 由 DB 生成、`claimed_at` 不可考＝NULL 不補造。**metric_value／定名若與你認定不同，以你改的為準。**

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-127.0.0.1}" -p "${DB_PORT:-5432}" -U "${DB_USER:-augur}" -d "${DB_NAME:-augur}" <<'SQL'
BEGIN;
SET LOCAL lock_timeout='5s';
INSERT INTO alpha_headline_anchor (anchor_label, claim_kind, metric_name, metric_value, recipe, scale_note, n_basis, claim_asof, claimed_at, source_ref, signed_by, machine, note) VALUES
('headline_govern_20260717','governance_signed','net_sharpe',1.1321,
 'ridge_H60_LO/asof_incumbent/canonical34/since2014/cost0.585%',
 'P0 量尺(2026-07-17 PriceAdj 修復後重定錨當日)',
 'T=25;DSR=34.5%@N=32(alpha_p0_diagnostics §5 實跑;HANDOFF 之 47.9% 查無來源不採)',
 DATE '2026-07-17', NULL,
 'reports/alpha_p0_diagnostics_20260718.md:24,44;memory:alpha-phase1-anchor-repair(簽核=另一機器,repo 無獨立簽核文件——誠實揭露)',
 'hugo','DESKTOP(簽核機;本機 DB 無此帳)',
 '本機不可再現(07-16 快照 dry-run=1.1302,Δ0.0019=PriceAdj 快照漂);定名歧異見 E2 呈案 §2.2'),
('headline_local_20260717','local_snapshot','net_sharpe',1.1302,
 'ridge_H60_LO/asof_incumbent/canonical34/since2014/cost0.585%',
 '雙出處並存:P2 turnover 半和量尺 headline(維持不動)/本機 07-16 快照 dry-run(S-ii 並記)',
 'T=25;本機 dry-run DSR=34.3%(N=32 口徑)',
 DATE '2026-07-17', NULL,
 'reports/alpha_phase1_tail_verdict_20260717.md:111;reports/alpha_p1_buffer_verdict_20260717.md:4;HANDOFF.md:207,209;memory:alpha-phase1-anchor-repair',
 'hugo','PC002-S1800',
 'HANDOFF.md:209 稱本值「新錨」——與「1.1321=治權錨」定名並記(S-ii);本機 revalidation_baseline 現值仍 1.1972 世代(07-09 凍結)'),
('headline_hist_20260709','historical_reference','net_sharpe',1.1972,
 'ridge_H60_LO/asof_incumbent(07-09 凍結世代)',
 '舊世代量尺(PriceAdj 修復前);07-17 起不可再現、僅家譜首節點',
 'T=25(revalidation_baseline 07-09 凍結:1.197184709380887)',
 DATE '2026-07-09', NULL,
 'DB:revalidation_baseline(cell=ridge_H60_LO,universe=asof_incumbent,frozen_at=2026-07-09);trial_ledger(max run_at 2026-07-13)',
 NULL,'PC002-S1800','變體a 家譜首節點;被 1.1321/1.1302 世代取代');
COMMIT;
SELECT anchor_id, anchor_label, claim_kind, metric_value, claim_asof, recorded_at FROM alpha_headline_anchor;
BEGIN; DELETE FROM alpha_headline_anchor WHERE anchor_id=1; ROLLBACK;
SQL
```

（最後兩行＝負向探針：DELETE 應被 guard RAISE、屬預期紅。）

## 3〔你親跑〕A2/A4 demote——mean_20d 除役（decided_by＝你）

**簽什麼**：`lending_fee_rate_mean_20d` 自 prodset 除役（甲案；三腳依據＝G-PROM FAIL＋G-ECON FAIL＋零產生器不可續建；符號 PASS 已誠實下修權重仍不翻案）。存量 17,072 列留史料不動。queue 487 記你裁決。

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-127.0.0.1}" -p "${DB_PORT:-5432}" -U "${DB_USER:-augur}" -d "${DB_NAME:-augur}" <<'SQL'
BEGIN;
SET LOCAL lock_timeout='5s';
SET LOCAL augur.honesty_write='on';   -- B4 窗後 prodset UPDATE 須通行證
UPDATE evolution_production_feature_set
   SET set_status='removed', last_action='demote', updated_at=now(), source_queue_id=487
 WHERE feature='lending_fee_rate_mean_20d' AND set_status='active';
UPDATE promotion_queue
   SET queue_status='applied', decided_by='hugo', decided_at=now()
 WHERE queue_id=487 AND queue_status='rejected_gate';
COMMIT;
SELECT feature, set_status, last_action FROM evolution_production_feature_set ORDER BY feature;
SQL
```

（預期：兩 UPDATE 各 1 列；跑完 active 僅剩 `inst_cumflow_position_120d`。）

## 4〔你親跑〕D4 R1 回收 4 筆（KH8 尾巴解閘之再膨脹回收）

**簽什麼**：item 277948–277951 回 depth 7＋通行證帳留痕（`change_actor='hugo'`）。腳本有 isatty 人閘＋`R1-GO` 確認＋帳冪等。**窗後**執行。

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/migrate_admit_state_guard_ddl.py --apply-r1
```

## 5〔你親跑〕H1 判準核可——R-CELL′＋S-8（提案已凍結）

**簽什麼**：R-CELL′ 逐格判讀判準全文＋S-8「robot＝量尺哨兵非受測臂」條款（碼已落 `57eb275`、wins 恰等預凍集；此步＝判準補登錄入人閘帳本）。

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a && venv/bin/python scripts/governance_queue.py --approve gp_ec112c0b24a8
```

（approve 後我跑 `--enact` 收尾。）

## 6〔你人審→授權句〕H2 mc_baseline 入冊（正名 iid_bootstrap）

**審什麼**（5 分鐘）：`reports/w2_20260801/H2_iid_bootstrap_registration_draft.md`＋`H2_iid_bootstrap_param_schema_draft.json`——人審點＝required 三欄是否過嚴、x-unclassified 兩鍵形知悉。⚠三處已明標：**入冊僅解物理死鎖，sim 軸合法評估仍待 D-2 另案**。
**回「H2-照案」**＝我 submit（凍結）→ 你 `governance_queue.py --approve <gp_id>`（屆時給 id）→ 我 enact → 你依草案 §四親跑 registry INSERT（`approved_by='hugo'`）。

## 7〔你親跑〕G3 拍板——沙盒演練已實證、生產 apply 候簽

**簽什麼**：identity 六表生產化（甲案＋W-a 唯讀哨兵＋零消費者誠實條款）。沙盒證據：`augur_sandbox` 現存供檢視（registry 3,505 含探針 2／retire 344／mismatch 37 人裁佇列）；演練記錄在 scratchpad `G3_sandbox_drill_record.md`。
**動作**：親自編輯 `reports/w2_20260801/G3_identity_sandbox.md` §7 勾甲案＋W-a、簽名日期——或回「G3-簽（甲+W-a）」我把勾選文字備好、你只跑一條 sed 親簽。簽後我跑生產 runbook P0-P5（含 mismatch CSV 落 reports/ 供你裁 37 例）。

## 8〔一句話〕B4 收尾兩件

- §7 決定欄＋「翻 C5 一部」之 **RULING 編號指配**（下一號＝2026-043；回「B4-043」即定）。
- P2 殘餘 19 表分批授權時點（可回「P2-下批」擇日）。

---

## 附：本包之外、AI 側自動續跑

18:10 限額重置後：A3 四件套＋C1 落碼（含突變驗紅）→ A3 遷移 77 筆（三查已滿足）→ C1 DDL 小窗＋既有 5 列 manual 回填 SQL 呈你過目 → 登錄冊全冊收斂＋封存點。B2 證偽觀察窗至 08-08、C2 閉環 48h 窗、明早 09:00 T7 週報自測照走。

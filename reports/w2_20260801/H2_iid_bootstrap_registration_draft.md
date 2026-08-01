# [DRAFT] H2 件二｜sim 首 method 入冊草案——`iid_bootstrap`（呈案單所稱 mc_baseline 之正名）

> **草案（步 1 產物）；未經 hugo 人審（步 2）不生效、未經步 3-6 全鏈不入冊。**
>
> **⚠ 邊界明標（Steward 鮮度警告照錄）**：入冊**僅解 B-1 物理死鎖**（registry 0 列 ⇒ 候選 FK 寫不進）；
> **sim 軸合法評估仍待 D-2 另案**（`evolution_prereg_gate` `axis='sim'` 現 0 列，2026-08-01 親驗）——
> **不得據本入冊宣稱 sim 可開跑**。
>
> 裁決依據：Steward 圈選 H2「同意（照建議案）」＝三件套照案＋D-1 甲（首件逐件）＋method key 甲
> （**正名 `iid_bootstrap`**）＋丙 甲（kill_switch sim 列 set_by=腳本名）。
> 呈案 SSOT＝`reports/w2_20260801/H2_sim_first_method.md`；本檔＝其 §3.2 步 1 之落地產物。

## 一、正名宣告（method key）

呈案單 H2 建議句所稱 **`mc_baseline`** 為「MC 基線法」之**描述語**——全 repo＋DB 查無此鍵
（20 個史料 method、`mc_simulation_run_method_check` 值域、任何 code 皆無）。裁決正名＝
**`iid_bootstrap`**（261 列史料直接對應、D-5 回填可用、零額外 DDL）；registry `note` 將註記
「呈案單 H2 所稱 mc_baseline 之正名＝iid_bootstrap」。

## 二、param_schema 草案（步 1 derive 產物；待步 2 人審）

- 產出工具：`venv/bin/python scripts/derive_sim_param_schema.py --method iid_bootstrap`（唯讀、確定性——
  連跑兩次 byte-identical 已驗）。
- 草案全文：**`reports/w2_20260801/H2_iid_bootstrap_param_schema_draft.json`**
  （x-provenance：mc_simulation_run 261 列、asof 資料側 2026-07-27、git_sha b6ceaa8）。
- 摘要：properties＝`horizon_td`{21,30,42,60,63,126}／`n_paths`{10000}／`seed`{42}（三者全列非 NULL
  ⇒ required）；`block_len_td` 史料全 NULL ⇒ x-excluded；summary 兩種鍵形（260 列 7 鍵＋1 列 16 鍵）
  全列 x-unclassified、逐鍵分類屬人審。

**步 2 人審點（hugo）**：
1. values 合理否（seed 單值 42、n_paths 單值 10000——required 是否過嚴？若未來輪需異 seed，
   schema 現形仍容任意 integer，僅 x-observed 記史料觀測值，**不構成值域鎖**）。
2. `required=[horizon_td,n_paths,seed]` 是否過嚴。
3. x-unclassified 兩鍵形逐鍵知悉（其中 1 列 16 鍵形＝maxdd 混入列，人審決定是否註記）。

## 三、入冊全步序（呈案 §3.2；★＝hugo TTY 親簽點，AI 機械上不可代）

| 步 | 執行者 | 動作 | 狀態 |
|---|---|---|---|
| 0 | Steward | 拍板（三件套照案＋D-1 甲＋正名甲） | ✅ 已圈選 |
| 1 | AI | derive 產草案 JSON | ✅ 本檔＋草案 JSON |
| 2 | **hugo（人審）** | 過目 §二草案：照案或修訂指示 | ⏳ 待 hugo |
| 3 | AI | `venv/bin/python scripts/governance_queue.py --submit --kind other --title "sim 首法註冊：iid_bootstrap" --diff-file reports/w2_20260801/H2_registration_payload_draft.md`（submit 即凍結；人審若修訂草案，先同步 payload 再 submit） | ⏳ 待步 2 後 |
| 4 | **★hugo TTY** | `venv/bin/python scripts/governance_queue.py --approve <gp_XXXX>`（TTY 閘＋親手打簽名） | ⏳ |
| 5 | AI | `venv/bin/python scripts/governance_queue.py --enact <gp_XXXX>` | ⏳ |
| 6 | **★hugo TTY（psql 親跑）** | §四 INSERT（registry 首列；approved_by='hugo' 唯親跑） | ⏳ |
| 7 | AI | B-1 解除探針（呈案 §6-2：交易內 INSERT 候選→ROLLBACK；rc=0＋零殘留） | ⏳ |
| 8 | AI | audits/ 登錄＋登錄冊 §1 H2 勾（驗收過才勾） | ⏳ |

前置相依：**步 6 之前波3統一 DDL 窗須已跑 `migrate_sim_constraints_ddl.py --apply` 嗎？——不須**
（registry INSERT 不受該 DDL 影響）；但步 7 探針只證 FK 通過，候選之 llm_local CHECK 等機械閘
仍待統一窗落地後才在位。

## 四、步 6 INSERT 全文（hugo psql 親跑；`<gp_XXXX>` 以步 3 實值替換）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -v schema="$(cat reports/w2_20260801/H2_iid_bootstrap_param_schema_draft.json)" \
  -v gpid="<gp_XXXX>" -v gitsha="$(git rev-parse --short HEAD)" <<'SQL'
INSERT INTO simulation_method_registry
  (method, family, purpose, param_schema, tilt_free, status,
   gate_ref, approved_by, approved_at, git_sha, note)
VALUES
  ('iid_bootstrap', 'bootstrap',
   '歷史日報酬 iid 重抽之分位錐基線（模擬非預測；純歷史重抽零 tilt；史料 261 列對應）',
   :'schema'::jsonb,
   true, 'registered',
   :'gpid', 'hugo', now(), :'gitsha',
   '呈案單 H2 所稱 mc_baseline 之正名＝iid_bootstrap；首法入冊（D-1 逐件）；入冊僅解 B-1 物理死鎖，sim 合法評估仍待 D-2');
SQL
```

（若步 2 人審修訂了草案 JSON，本 INSERT 之 `-v schema` 自動取修訂後檔案內容——單一住所。）

## 五、驗收（呈案 §6-1/6-2）

入冊後 `SELECT method, family, status, approved_by IS NOT NULL AND approved_at IS NOT NULL AND
gate_ref IS NOT NULL AS signed FROM simulation_method_registry` ＝恰 1 列
`iid_bootstrap | bootstrap | registered | t`；探針 INSERT→ROLLBACK rc=0、候選表 count 仍 0。
錯列回滾＝`status='retired'`（`smr_no_delete`/`smr_no_truncate` 在位、判死留檔）——故人審在 INSERT 前。

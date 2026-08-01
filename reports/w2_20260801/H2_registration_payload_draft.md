# sim 首法註冊 payload：iid_bootstrap（governance submit 之 --diff-file 全文）

> 本檔＝`governance_queue.py --submit` 之 diff-file（submit 即凍結不可改；proposal_id＝
> gp_+sha256(title+diff)[:12]）。**若步 2 人審修訂 param_schema 草案，先同步本檔再 submit。**
> 依據：Steward 圈選 H2 同意（三件套照案＋D-1 甲首件逐件＋method key 正名 iid_bootstrap）；
> 呈案＝reports/w2_20260801/H2_sim_first_method.md §3.2；草案＝同目錄 H2_iid_bootstrap_registration_draft.md。

## 註冊內容

- method：`iid_bootstrap`（呈案單 H2 所稱 mc_baseline 之正名；261 列史料直接對應）
- family：`bootstrap`
- purpose：歷史日報酬 iid 重抽之分位錐基線（模擬非預測；純歷史重抽零 tilt；史料 261 列對應）
- tilt_free：`true`——論證：iid bootstrap 對歷史日報酬**等機率重抽**，無任何方向性傾斜參數；
  param_schema 三參數（horizon_td／n_paths／seed）皆無 tilt 自由度；產出以 `is_simulation=true`
  硬綁「模擬非預測」口徑（mc_simulation_run 同名欄 NOT NULL 先例）。
- param_schema：`reports/w2_20260801/H2_iid_bootstrap_param_schema_draft.json` 之人審後版本
  （derive 草案：properties＝horizon_td{21..126 六值}/n_paths{10000}/seed{42}、required 三欄、
  additionalProperties=false、block_len_td 史料全 NULL 列 x-excluded、summary 兩鍵形列 x-unclassified）。
- status：`registered`；gate_ref＝本提案 enacted 後之 proposal_id；approved_by/approved_at＝
  hugo TTY 親簽（步 4）＋psql 親跑（步 6），AI 不代填。

## 邊界聲明（照 Steward 鮮度警告）

本入冊**僅解 B-1 物理死鎖**（simulation_method_registry 0 列 ⇒ sim_evolution_candidate FK 寫不進）。
**sim 軸合法評估仍待 D-2 另案**（evolution_prereg_gate axis='sim' 現 0 列）——不得據此宣稱 sim 可開跑。
餘 19 史料法不隨本案入冊（D-1 甲：首件逐件；餘者待首輪跑通後另以包裹提案收）。

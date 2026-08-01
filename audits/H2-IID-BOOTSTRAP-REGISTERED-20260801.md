# H2 sim 首 method 入冊完成記錄（2026-08-01 晚）

- **鏈**：derive schema（sha256 黃金鎖）→ hugo 人審「H2-照案」→ submit 凍結 `gp_df544cbb1b94`
  → hugo TTY approve（人簽）→ enact → hugo psql 親跑 registry INSERT（`INSERT 0 1`，approved_by='hugo'）。
- **入冊列**：`iid_bootstrap|bootstrap|registered|hugo`（param_schema=人審後 JSON；gitsha 937014b）。
- **B-1 解除探針（步 7）**：交易內候選 INSERT 過＋ROLLBACK 零殘留；雙負向＝
  `llm_local∧非synthetic` 被 `chk_sce_llm_is_synthetic` 拒、未入冊 method 被 FK 拒（入冊=唯一門）。
- **探針途中親驗之草案偏差（誠實留檔）**：live CHECK 白名單與草案 B-1 例示不符——
  `origin` 合法集=`llm_local/grid/human/carryover`（無 engine）、`status` 起始=`candidate`（無 proposed）、
  `trust_rank` 恆 `'TR-C'`（非整數）。探針已按 live 白名單改寫；候選寫入端（W5 driver）實作時以本記錄為準。
- **不得宣稱**：sim 軸合法評估仍待 D-2（prereg gate axis='sim' 現 0 列）；煞車列初期零消費者。

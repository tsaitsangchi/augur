# Augur Steward 裁決第 2026-026 號

**Agent 協作產物之個別可驗證性——「執行指令矩陣」升格為 Layer 6／§8.3 解釋落點**

* **依據**：`AUGUR-MC v1.4 §8.1`（Steward 解釋權）、`§8.3`（ENFORCE／機器可稽核）、`§0.5`（Layer 對照表）、`§8.6`（Layer 表 editorial／minor）；領域細則 `CLAUDE.md` #18／#29
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 用戶（Steward）明示「檢查所有 python 程式是否都有執行指令矩陣，請補全部，並入元憲章」
* **登錄**：Amendment Log AL-2026-029
* **性質**：§8.1 解釋（效力自本裁決；**不改 §8／構成性依據之 [N] 本文**）＋ §0.5 Layer 6 列 editorial（不升 MC 版本號）

## 一、§8.1 解釋（一項）

| 項 | 系爭 | 解釋 |
|---|---|---|
| **執行指令矩陣** | Layer 6 Agent 編寫／維護之 Python 可否僅憑「有程式」即充作合規／可驗證？ | `§8.3`「機器可稽核／ENFORCE」於 **Layer 6 Agent Runtime** 之落點，涵蓋 Agent 所編寫或維護之**可執行 Python 入口**——凡 `scripts/` CLI，或具 `if __name__ == "__main__"` 之 library／tools／ops 模組，其模組 docstring **必須**載明 canonical 標題「**執行指令矩陣**」（至少含無參數之安全預設／用途說明，以及該模組所宣告之 `--selftest` 或等價零外部依賴自測路徑）。無參數執行不得裸 traceback。細則、豁免（如純 path-bootstrap 輔助模組之最小矩陣）與實測分級由 `CLAUDE.md` #18／#29 定之。**缺矩陣之入口不得充作「已個別驗證／合規稽核通過」之依據。**本義務**及於裁決後嗣後新增**之可執行 Python 入口——新增即負矩陣義務（首次提交當下即須具備），不以裁決當時之一次性盤點為限（2026-07-23 editorial 補述，見執行層落地）。本解釋不新增 §8.3 [N] 條文、不擴張 102 母集。 |

## 二、MC 本文變更（僅 §0.5 editorial；版本維持 v1.4）

* §0.5 Layer 6「所轄規格」列：於 CLAUDE.md 括註補「可執行 Python 入口須載執行指令矩陣」並引用本裁決——屬 Layer 對照表之 editorial／minor 範圍（§8.6），**不升 v1.4 版號**（無原則級變更、PA／五原則／§8 [N] 零改）。

## 三、執行層落地（同案）

* 盤點並補齊 repo 內缺 canonical「執行指令矩陣」之可執行入口 docstring（library／tools／scripts／ops／proxy 等）。
* `CLAUDE.md` 憲章從屬改引 **AUGUR-MC v1.4**，並標本裁決為 #18／#29 之上層依據。
* **2026-07-23 全量盤點補齊完成**：新增稽核腳本 `scripts/check_cmd_matrix.py` 掃全 repo，實測結果 = 受檢入口 320 支（`scripts/` 202、`src/augur` 80、`tools/` 26、`augur_proxy` 8、`ops/` 3、`tests/`（具 `__main__` 者）1）／缺漏 0。本輪實補 25 支——原僅套件級 `selftest.py` 覆蓋、模組自身未具 `--selftest` 之 `augur_proxy/{cache,classifier,claude_cli,local_llm,logger,router}.py`（6）、`ops/gpu-verify/{cuda_native_test,gpu_test}.py`（2）、`tools/constitution_lint/{model,mcp_client,audit_lint,mc_clauses,report,compliance_lint}.py`（6）、`tools/constitution_mcp/{server,tools}.py`（2）、`tools/local_llm_mcp/{server,tools}.py`（2）、`tools/project_memory_mcp/{chunk,govern,embed,store,index,recall,server}.py`（7）。`tests/*.py` 之 pytest 測試檔以 `pytest tests/x.py -v` 為既定個別執行協定，非本裁決「可執行入口」範疇，不強加 `__main__`（見 `scripts/check_cmd_matrix.py` 稽核腳本注記）。稽核用法：`python3 scripts/check_cmd_matrix.py`（供隨時自跑，見 `CLAUDE.md` #29(d)）。

## 四、明示不為

* 不改 §8.3 [N] 條列本文（self-entrenchment；改 [N] 須原則級程序）。
* 不因本裁決擴張 WM.44／§8.3 之 102 條母集計數。
* 不以靜默 skip／降 severity 替代矩陣義務。

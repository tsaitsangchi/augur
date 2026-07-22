# constitution-mcp

Augur 憲章**條款級查詢** MCP server —— 讓模型以數百字元的工具呼叫，取代動輒
30–150 KB 的整檔讀取。**唯讀、純 stdlib、無外部相依。**

實測八場景平均節省 **97.2%** context（`python3 -m tools.constitution_mcp.measure`）。

## 為何不用官方 `mcp` SDK

1. 本 repo 治權工具鏈以「純 stdlib、無外部相依」為紀律（見 `tools/constitution_lint/README.md`）——
   合憲判定之工具不應繫於會漂移的外部套件。
2. `.mcp.json` 因此無須綁定 venv 路徑，換機即可用。
3. MCP stdio 即 line-delimited JSON-RPC 2.0，協定層約 60 行。

> **歷史註**：本 repo 原有之 `mcp/` 目錄（Multi-**C**hannel **P**roxy，提示詞路由器）
> 與 Model **C**ontext **P**rotocol 同名異物，且會**劫持** `import mcp`（本地套件優先於
> site-packages）。已於 2026-07-21 改名 `augur_proxy/`。

## 使用

已由 repo 根之 `.mcp.json` 註冊，進入本專案即自動載入、離開即卸載（專案作用域）。
手動起服務或自測：

```bash
python3 -m tools.constitution_mcp             # stdio server
python3 -m tools.constitution_mcp selftest    # 自測（含突變鎖）
python3 -m tools.constitution_mcp.measure     # 實測 context 節省
```

## 七支工具（全部唯讀）

| 工具 | 用途 | 典型節省 |
|---|---|---|
| `get_clause` | 取憲章條款原文＋自有括號名＋行號（`P4.E1`／`§2.5`／`F4`／`EV.9`） | 98.8% |
| `get_spec_clause` | 取下層生效規格條款原文（`WM.44`／`KS.42`／`L7.21`） | 97.6–99.3% |
| `search_clauses` | 關鍵詞檢索，回代號＋標籤＋摘句（不回全文） | 99.0% |
| `lint_compliance` | 實跑 §8.3 compliance lint，回結構化結果 | 99.0% |
| `layer_status` | 八層現況（front-matter 實地解析，非硬編碼） | 95.5% |
| `get_ruling` | 取裁決主文（長文截斷；短裁決無節省，屬正常） | 視長度 |
| `list_amendments` | 修訂登錄簿最近 N 筆摘要 | 91.7% |

先以 `search_clauses` 定位，再以 `get_clause`／`get_spec_clause` 取全文——
這是最省的用法。

## 四項設計紀律（皆有可執行斷言）

承接本專案治理教訓，`selftest` 逐項鎖住：

1. **唯讀** —— 不提供任何寫入工具。修規格為 Steward `§8.5`／`§8.6` 之權，
   不得因本工具而生一條經 MCP 之旁路。
   *鎖法*：工具名動詞前綴檢查 ＋ **AST 掃描實作層**（`open(mode=w/a/x/+)`、
   `os.remove`／`shutil.rmtree` 等模組限定呼叫）。後者為權威判準——名稱不足為憑。
   *突變驗證*：注入 `os.remove()` 即紅，還原即綠（已實跑）。

2. **合規檢查永不快取** —— `lint_compliance` 每次實跑。本專案已三度實證
   「陳舊綠燈」之害（linter 三輪 `error 0` 而實質錯誤並存）；於合規判定前置
   TTL 快取即自造第四輪。
   *鎖法*：以 spy 包裹 `lint_spec`，斷言同檔連呼二次確實實跑二次。

3. **回傳附出處** —— 每筆附 `file:line`，俾模型引用時可回溯。
   *鎖法*：斷言 `get_clause`／`get_spec_clause` 之輸出含 `.md:` 行號。

4. **失敗發聲** —— 解析失敗回明確錯誤，不靜默退回近似答案（承接 gate 硬化
   B9「靜默降級」教訓）。
   *鎖法*：不存在之條款代號／規格檔／裁決號一律須拋 `ToolError`；經協定層者
   須帶 `isError: true`，不得偽裝成正常結果。

另設 **B3 迴歸鎖**：`§2.5 Evidence`／`§2.6 Knowledge`／`§2.7 Intelligence`／
`§2.10 Confidence` 四條核心定義須可取——此四條曾因 list-item 體例而未進入
條款宇宙，致 linter 之「85 條全數涵蓋」為假陽性。

## selftest 涵蓋

協定層（initialize／tools/list／通知不回應／壞 JSON 不崩）、四項紀律、
B3 迴歸、各工具功能面與錯誤面。**凡 README 所宣稱之性質，皆有對應斷言** ——
本專案曾發生 README 宣稱一個不存在的測試，此為該教訓之遵行。

## 已知限制

* `search_clauses` 為子字串計分檢索，非語義檢索；同義詞須自行嘗試。
* `get_ruling` 對 4 KB 以下之短裁決無節省效果（回傳近乎全文），屬正常。
* 條款原文之抽取沿用 `mc_clauses` 之範圍判定；該模組已知 `§9` 正文範圍
  溢收附錄（見 gate 硬化報告），本工具承其限制。
* 需要**全文**工作（如逐列重建整張矩陣）時，讀全檔仍為正解，本工具不取代之。

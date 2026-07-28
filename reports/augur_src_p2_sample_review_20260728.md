# SRC-AUTO P2 抽核——首批「可自動」32 源之人工覆核清單（含端點重複發現＋P7 提案）

> **性質**：[I] P2 關卡交付（SRC-AUTO 計畫 §五：抽核通過才開 `--run`）。2026-07-28。
> **鏈**：REGIME-MAP-v1（核可）→ P4P5-go Q1/Q2（probe 波＋雙 verb 假陰性修復 `72d7bd7`＋pacing 落值 42 倉）→ dry 重分桶「✅ 可自動 32」首次非空 → 本件。

## 一、Q2 落地數字（全 (a)(b) 真源）

- 步①證據波（修復後累計）：119 倉探畢——**格式實證過 59**／真失敗 13（406/SSL/timeout 類）／首波污染 47 已全數重探。
- 步②落值：合格 60 倉 → **可落值 42**（有倉自報 completeListSize）／18 誠實跳過（無自報數，留人工桶 #9）。
- dry 重分桶：`✅ 可自動 32`｜路乙判入 505｜P4 桶 446（enrich 未收槍前之未探倉）｜P5 桶 28（10 超 5 萬煞車＋18 無自報數）。

## 二、抽核時自查發現：端點重複（P7 提案，待簽）

32 源 → **唯一 OAI 端點僅 16**：`borealisdata.ca ×13`、`heidata ×3`、`dataverse.nl ×2`、`dataverse.no ×2`。成因＝re3data 按機構登錄（各機構 Dataverse 各一列），但 OAI 端點同指 umbrella 主機；我方存證（est_scale 同值）證明它們在本系統中不可區分——**全批＝重複來源 16 列**（若日後接 harvest＝同端點 N 倍打＋重複入庫）。

**P7 提案（機械謂詞，tighten-only）**：auto-approve 以 **normalized OAI base 唯一**為前提——每端點唯一代表列（`min(source_key)` 確定性擇取）可自動；其餘同端點列**留 proposed＋記 duplicate-endpoint note**（非拒絕；日後若要按機構 set-scoped harvest 再另案啟用）。一字簽：`P7-go`。

## 三、16 代表列核可表（每端點一列；license 證據逐列附原文連結）

| # | source_key | 倉名 | regime | est | license 證據（re3data dataLicense 原文） |
|---|---|---|---|---|---|
| 1 | r3d100010897 | Agri-environmental Research Data（Borealis 代表列） | cc_whitelist | 25336 | CC BY 4.0＋CC0（deed 連結齊） |
| 2 | r3d100012676 | CSISA Data Repository | public_domain | 1153 | **⚠** name=「Public Domain」但佐證連結為專案網頁非法律文本（R1 名中、證據弱——此列請個別裁） |
| 3 | r3d100012769 | Banque de données du CDSP（SciencesPo） | cc_whitelist | 557 | CC BY-SA 4.0 deed.fr |
| 4 | r3d100012333 | DATADOI（Tartu） | cc_whitelist | 454 | CC BY 4.0 |
| 5 | r3d100013468 | ASU Research Data Repository | cc_whitelist | 102 | CC BY 4.0＋CC0 |
| 6 | r3d100013134 | DataSuds（IRD） | cc_whitelist | 467 | CC BY 4.0 deed.fr |
| 7 | r3d100012162 | LibraData（UVirginia） | public_domain | 529 | CC0 1.0 legalcode（名標 CC、URL 為 CC0 法律文本） |
| 8 | r3d100011201 | DataverseNL | cc_whitelist | 11297 | CC BY 4.0 |
| 9 | r3d100011623 | TROLLing（dataverse.no 代表列） | public_domain | 2298 | CC0 |
| 10 | r3d100013550 | Riga Stradins University dataverse | public_domain | 165 | CC0 1.0 |
| 11 | r3d100012673 | Data INRAE（recherche.data.gouv） | cc_whitelist | 5107 | CC BY 2.0 FR＋「OGL」——**⚠ 此 OGL＝法國 Etalab Licence Ouverte（名稱撞 R3 之英國 OGL）**；實質同為署名開放授權，且單靠 CC BY 已足 cc_whitelist——regime 不受影響，名稱碰撞誠實揭露 |
| 12 | r3d100011108 | heiDATA（Heidelberg） | cc_whitelist | 1410 | CC BY-SA 3.0＋ODC-BY |
| 13 | r3d100012929 | Oxford Brookes RADAR | cc_whitelist | 38768 | CC BY 4.0 |
| 14 | r3d100013637 | Addis Ababa University RDR | cc_whitelist | 528 | CC BY 4.0＋CC0 |
| 15 | r3d100012394 | ISTA Research Explorer | cc_whitelist | 6582 | CC BY-SA＋CC BY＋CC0 |
| 16 | r3d100010139 | Hamburg ZFS Korpus Repositorium | cc_whitelist | 5285 | CC BY 4.0 legalcode |

抽樣法＝確定性 `md5(source_key‖'20260728')`；因唯一端點僅 16 ＜ 20，本表為**全查**（普查嚴於抽核）。

## 四、觀察一則（未來收緊選項，不阻本批）

R2 之 url pattern `/licenses/by/` 為 domain-agnostic——本批撞上 `opendatacommons.org/licenses/by/`（＝ODC-BY，恰為 R4 同 regime，無害）；理論上可能匹配非 CC 網域之同構路徑。**收緊選項**：R2 pattern 錨定 `creativecommons.org/licenses/by/`（tighten-only，符 L-V 精神）。要收緊請帶一句：`R2-錨定-go`。

## 五、回覆格式

- `P2-16-核可`＝16 代表列全過（#2 CSISA 弱證據列若要剔除：`P2-15-核可-剔2`）；
- `P7-go`＝端點唯一謂詞入 run()（建議，防重複來源）；
- 可另附 `R2-錨定-go`。
- 之後我執行：（P7 實作＋selftest）→ `--run --limit 16`（週上限 50 內）→ 留痕 review_log actor=auto_rules_v1 → R6 digest 呈現；enrich 收槍後波第二遍＋重分桶，後續批次照既定管線走。

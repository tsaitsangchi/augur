# TTAI/Tiptop ERP 全庫嵌入 — 跨語檢索品質驗收裁決

**日期**:2026-07-06 ｜ **性質**:唯讀驗收(未寫入、未 commit)｜ 全數字 trace 自 `retrieve_items(...)` 實跑 + psql
**守**:#15(誠實揭露真兆假兆、e5-small 高分≠相關)· #1(owned_local 治理)· #28(本地)

## 一、落地與治理(通過)
- `domain='erp_tiptop'`:item **141,825**、句 **151,961**、已嵌 **151,849**(e5-small multilingual-384;112 未嵌)。
- **治理正確**:item_text 全 `license='owned_local'` + `access_scope='local_private'` + `owner_user_id=1`(無 NULL-owner 漏網)。語言 zh 147,222 / en 4,739(zh 佔 97%)。CLEAN_ITEM 閘可過。
- **內容本質**=Tiptop schema/metadata 標籤(「檔名·欄位 xxNN:業務中文 label(Oracle 型別)」),**非自然語散文**。

## 二、檢索品質(逐題實測,rank@8=首個真相關名次、FP=離題筆數)
- **zh→erp**:10 題 **6 題 rank@1、0 FP**(料件主檔/生產工單/庫存盤點/供應商主檔/帳款科目代碼/應收帳款沖銷);4 題失敗塌陷。
- **en→erp**:11 題 **僅 3 題可用**(vendor master/material master rank@1、account voucher #1);8 題失敗。
- **跨語(zh↔en)**:24 題**幾乎全垮**,多塌到 zh 權限設定檔 boilerplate 或破碎 SQL 殘句(rank@8 常為「無」)。

## 三、誠實裁決:**局部可用,整體不足以支撐 advisor 穩定答 ERP**
1. **同語 zh + 「檔名式術語」query → 好用**(rank@1、0 FP);因語料本身即「XX資料主檔·欄位」格式、與 query 表面同構。
2. **跨語幾乎全垮**(與 memory 舊經驗哲學 en→zh rank 3-4 顯著相反):ERP 的 zh 內容是**電報式 schema 標籤非句子**,e5-small 對「英文自然語概念 ↔ 中文欄位標籤」對齊很弱;**英文問 ERP 基本不可用**。
3. **e5-small 誠實崩壞為真**(呼應 MBB #15):`應收帳款`→**0.89 高分卻全是「應付帳款」**(收/付語意反了分數還最高);`會計科目`/`採購單`/`折舊`→ 塌 boilerplate 也 0.83-0.86。**高分 ≠ 相關,絕不可靠 top-k「有回」判通過;若 advisor 裸吃 top-k,會自信拿應付帳款回答應收帳款**。

## 四、根因與建議(依 CP 值排序,皆為後續改進、本驗收不動)
1. **清權限設定檔 boilerplate(29,121 句、19.2% 全庫、頭號污染源)**:retrieval 對 ERP 加 `sentence NOT LIKE '權限設定檔%'` 過濾或標 low-value 降權/不嵌——立刻救回採購單/會計科目/折舊/receivable/depreciation 等塌陷題。**最高 CP。**
2. **句切階段濾破碎 SQL 殘句**(`="M"）`、`='MISC'）`、`—·SQL:INSERT`),避免污染 en query。
3. **建 ERP concordance 或加 cross-encoder rerank**:ERP 在 `knowledge_concordance` 為 **0 列** → exact 快路徑永遠 miss、全押 ANN;失敗題 FP 達 8/8,不能裸用。
4. **跨語需雙語擴展或 bge-m3**:zh↔en 業務術語對照(receivable→應收…)先擴 query,或 language='zh' 收窄 + 英譯中 ERP 術語;純向量跨語在此語料不成立。bge-m3 對多語/長標籤對齊優於 e5-small,但 boilerplate + 破碎句仍須語料層清理(換模型救不了 near-dup 塌陷)。

## 五、對 advisor 整合的直接意涵
- ERP 走 `retrieve_all` 之 local_private 半路合併 → **advisor Tier-1 相關度閘對 ERP 同樣是必要防線**(擋「應付當應收」自信誤答);但閘的內容詞重疊對電報式 schema 標籤行為需另測。
- **結論**:TTAI 嵌入與治理已竣工,但**檢索品質尚不足以讓 advisor 安全答 ERP 問題**;最小修法=清 boilerplate + 建 concordance/rerank,跨語需雙語擴展或 bge-m3。屬後續改進、待用戶排序。

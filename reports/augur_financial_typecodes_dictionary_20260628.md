# 財報 type 碼完整字典 — 全 224 碼 in-data 中文解碼(2026-06-28)

> **性質**:三大財報表 `type` 欄全部 224 個碼(損益 62 / 資產負債 128 / 現金流 34)之權威中文對照。
> **來源(source-pure #1)**:**資料自身 `origin_name` 欄**(各表皆有、每碼眾數中文)——**非 FinMind 外部文件、非杜撰、非 stock_backend**;100% 可解碼(62/62、128/128、34/34)。
> **意涵**:先前 ledger 列「224 罕見碼待外部文件」之 ⏳ **已解除**——欄位層所有 type 碼皆有 in-data 定義。

## 關鍵解碼(先前不明者,已由 origin_name 釐清)
- **`-`** = 「合併前非屬共同控制股權損益」(及綜合損益/前手權益變體)——FinMind 無對應英文碼之科目,`type` 落 `-` 但 origin_name 仍載真義。
- **`OTHNOE`** = 「其他收益及費損淨額」(縮寫,非標準碼)。
- **`HedgingAinancialAssets`** = 「避險之金融資產」(FinMind 拼字錯 Ainancial→Financial)。
- **中文 type 碼**(保險其他營業成本/少數股權淨利（損失）/所得稅利益（費用）…)= 舊期資料 type 直接落中文(混語編碼),origin_name 同值。
- **`_per` 後綴** = 該科目「佔資產總額%」(BalanceSheet 專有,每科目皆有金額+`_per` 兩碼)。

---

## 一、損益表 TaiwanStockFinancialStatements(62 碼)

| type | 中文(origin_name) |
|---|---|
| Revenue | 營業收入 |
| CostOfGoodsSold | 營業成本 |
| GrossProfit | 營業毛利（毛損）|
| OperatingExpenses | 營業費用 |
| OperatingIncome | 營業利益（損失）|
| TotalNonbusinessIncome | 營業外收入及利益 |
| TotalnonbusinessExpenditure | 營業外費用及損失 |
| TotalNonoperatingIncomeAndExpense | 營業外收入及支出 |
| TotalNonbusinessIncome / OTHNOE | 其他收益及費損淨額(OTHNOE)|
| PreTaxIncome / IncomeBeforeIncomeTax | 稅前淨利（淨損）|
| IncomeBeforeTaxFromContinuingOperations | 繼續營業單位稅前淨利(淨損)|
| TAX | 所得稅費用（利益）|
| IncomeAfterTax / IncomeAfterTaxes | 稅後純益 / 本期淨利（淨損）|
| IncomeAfterTaxFromContinuingOperations | 繼續營業單位稅後合併淨利(淨損)|
| IncomeFromContinuingOperations | 繼續營業單位本期淨利（淨損）|
| IncomeLossFromDiscontinuedOperation | 停業單位損益 |
| IncomeLossAfterTaxFromDiscontinuedOperation | 停業單位損益(稅後)|
| NetIncome | 本期淨利(淨損)|
| EPS | 基本每股盈餘 |
| EquityAttributableToOwnersOfParent | 淨利歸屬於母公司業主 |
| NoncontrollingInterests | 淨利歸屬於非控制權益 |
| ConsolidatedNetIncome | 合併總損益 |
| ConsolidatedNetIncomeAttributed2NoncontrollingInterest | 合併總損益歸屬予少數股權 |
| TotalConsolidatedProfitForThePeriod | 本期綜合損益總額 |
| TotalConsolidatedProfitForThePeriodAfterTax | 本期綜合損益總額(稅後)|
| TotalConsolidatedProfitForThePeriodBelongsParentCompany | 合併總損益歸屬予母公司股東 |
| OtherComprehensiveIncome | 其他綜合損益（淨額）|
| OtherComprehensiveIncomeAfterTax(ThePeriod) | 本期其他綜合損益(稅後淨額)|
| ComprehensiveIncomeConsolidatedNetIncomeAttributedNonControllingInterest | 綜合損益總額歸屬於非控制權益 |
| Income / Expense | 收益 / 支出及費用 |
| AdjustmentItem | 調整項目 |
| **`-`** | **合併前非屬共同控制股權損益** |
| **ExtraordinaryItems(AfterTax)** | 非常損益(稅後)(舊 ROC-GAAP,IFRS 前)|
| **CumulativeEffectOfChanges(InAccountingPrinciple)(AfterTax)** | 會計原則變動累積影響數(舊 GAAP)|
| RealizedGain / UnrealizedGain | 已/未實現銷貨（損）益 |
| RealizedGainFromInterAffiliateAccounts / UnrealizedGain… | 聯屬公司間已/未實現利益(舊合併)|
| **金融業**:NetInterestIncome / NetNonInterestIncome / ServiceFeeRevenueCommissionNet | 利息淨收益 / 利息以外淨收益 / 手續費淨收益 |
| BadDebts / BadDebtExpenseGuaranteeLiabilityProvisions | 呆帳費用及保證責任準備提存 |
| **保險業**:NetChangeInProvisionsForInsuranceLiabilities / 保險服務結果 / 保險其他營業成本 / 財務結果 / 其他營業結果 | IFRS17 保險分部 |
| **農業(IAS41)**:GainsOnChangesInFairValueLessCosts2SellOfBiologicalAssets… / GainsOnInitialRecognitionOfBiologicalAssets… | 生物資產公允價值/原始認列損益 |
| (舊期中文碼)少數股權淨利（損失）/ 所得稅利益（費用）/ 繼續營業部門稅前(後)淨利（淨損）/ 呆帳費用及保證責任準備提存（各項提存）| 同名 |

## 二、資產負債表 TaiwanStockBalanceSheet(128 碼 = 64 科目 × 金額/`_per`)

> `_per`=佔資產總額%。以下列科目(金額碼;`_per` 同義略)。

**資產**:CashAndCashEquivalents 現金及約當現金、CurrentAssets 流動資產合計、NoncurrentAssets 非流動資產合計、AccountsReceivableNet 應收帳款淨額、BillsReceivableNet 應收票據淨額、OtherReceivable 其他應收款淨額、AccountsReceivableDuefromRelatedPartiesNet 應收帳款-關係人淨額、OtherReceivablesDueFromRelatedParties 其他應收款-關係人淨額、Inventories 存貨、Prepayments 預付款項、PropertyPlantAndEquipment 不動產廠房及設備、IntangibleAssets 無形資產、RightOfUseAsset 使用權資產(IFRS16)、InvestmentAccountedForUsingEquityMethod 採權益法之投資、DeferredTaxAssets 遞延所得稅資產、CurrentIncomeTaxAssets 本期所得稅資產、ConstructionContractReceivable 應收建造合約款、OtherCurrentAssets 其他流動資產、OtherNoncurrentAssets 其他非流動資產、TotalAssets 資產總額。

**金融資產(IFRS9 + 舊 IAS39)**:CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss 透過損益按公允價值-流動(FVTPL)、NonCurrent… 非流動、FinancialAssetsAtFairvalueThroughOtherComprehensiveIncome(NonCurrent) 透過其他綜合損益(FVOCI)、FinancialAssetsAtAmortizedCost(NonCurrent) 按攤銷後成本(AC)、(舊)CurrentAvailableForSaleFinancialAssets 備供出售-流動、NonCurrent… 非流動、CurrentHeldToMaturityFinancialAssets 持有至到期-流動、HedgingAinancialAssets(NonCurrent) 避險之金融資產(拼字錯)。

**負債**:CurrentLiabilities 流動負債合計、NoncurrentLiabilities 非流動負債合計、AccountsPayable 應付帳款、AccountsPayableToRelatedParties 應付帳款-關係人、OtherPayables 其他應付款、ShorttermBorrowings 短期借款、LongtermBorrowings 長期借款、BondsPayable 應付公司債、CurrentContractLiabilities 合約負債(IFRS15)、CurrentTaxLiabilities 本期所得稅負債、CurrentProvisions 負債準備-流動、CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss 透過損益按公允價值之金融負債-流動、CurrentDerivativeFinancialLiabilitiesForHedging 避險之金融負債-流動、OtherCurrentLiabilities 其他流動負債、OtherNoncurrentLiabilities 其他非流動負債、Liabilities 負債總額。

**權益**:Equity 權益總額、EquityAttributableToOwnersOfParent 歸屬母公司業主權益合計、NoncontrollingInterests 非控制權益、CapitalStock 股本合計、OrdinaryShare 普通股股本、CapitalSurplus 資本公積合計、CapitalSurplusAdditionalPaidInCapital 發行溢價、CapitalSurplusChangesInEquityOfAssociatesAndJointVentures… 採權益法認列關聯企業股權淨值變動、CapitalSurplusChangesInOwnershipInterestsInSubsidiaries 取得/處分子公司股權價格與帳面差額、CapitalSurplusDonatedAssetsReceived 受贈資產、CapitalSurplusNetAssetsFromMerger 合併溢額、RetainedEarnings 保留盈餘合計、LegalReserve 法定盈餘公積、UnappropriatedRetainedEarningsAaccumulatedDeficit 未分配盈餘、OtherEquityInterest 其他權益合計、EquivalentIssueSharesOfAdvanceReceiptsForOrdinaryShare 預收股款之約當發行股數、NumberOfSharesInEntityHeldByEntityAndByItsSubsidiaries 母子公司持有之母公司庫藏股股數。

**合計**:TotalLiabilitiesEquity 負債及權益總計。

## 三、現金流量表 TaiwanStockCashFlowsStatement(34 碼)

| type | 中文 |
|---|---|
| NetIncomeBeforeTax | 本期稅前淨利（淨損）|
| IncomeBeforeIncomeTaxFromContinuingOperations | 繼續營業單位稅前淨利（淨損）|
| TotalIncomeLossItems | 收益費損項目合計 |
| Depreciation / AmortizationExpense | 折舊費用 / 攤銷費用 |
| InterestIncome / InterestExpense / PayTheInterest | 利息收入 / 利息費用 / 支付之利息 |
| ReceivableIncrease | 應收帳款（增加）減少 |
| InventoryIncrease | 存貨（增加）減少 |
| AccountsPayable / AmountDueToRelatedParties | 應付帳款(關係人)增加(減少) |
| CashReceivedThroughOperations | 營運產生之現金流入（流出）|
| CashFlowsFromOperatingActivities / NetCashInflowFromOperatingActivities | 營業活動之淨現金流入（流出）|
| CashProvidedByInvestingActivities | 投資活動之淨現金流入（流出）|
| CashFlowsProvidedFromFinancingActivities | 籌資活動之淨現金流入（流出）|
| PropertyAndPlantAndEquipment | 取得不動產、廠房及設備(capex)|
| OtherInvestingActivities | 其他投資活動 |
| ProceedsFromLongTermDebt / RepaymentOfLongTermDebt | 舉借 / 償還長期借款 |
| DecreaseInShortTermLoans | 短期借款減少 |
| RedemptionOfBonds | 償還公司債 |
| RentalPrincipalRepayments | 租賃本金償還(IFRS16)|
| DecreaseInDepositDeposit | 存出保證金減少 |
| OtherNonCurrentLiabilitiesIncrease / Decrease | 其他非流動負債增加 / 減少 |
| DeferredCredit | 遞延貸項 |
| HedgingFinancialLiabilities | 除列避險之金融負債 |
| RealizedGain / UnrealizedGain | 已/未實現銷貨損益 |
| CashBalancesBeginningOfPeriod / EndOfPeriod | 期初 / 期末現金及約當現金餘額(水位、非流量)|
| CashBalancesIncrease | 本期現金及約當現金增加（減少）數 |

> **註**:現金流主體為**累計YTD**(§ledger §一-b 驗:capex |Q4|/|Q1|≈4.8);CashBalancesBegin/End 為**時點水位**(ratio≈1)。少數 origin_name 與英文碼略不一致(如 OtherNonCurrentLiabilitiesIncrease 落「其他流動資產(增加)減少」)= FinMind 標籤瑕疵、值仍以 type 為準。

## 可追溯
全表 `SELECT type, mode(origin_name)`(三表各 100% 解碼);量級/覆蓋見 ledger §一;單位=元(§ledger 單位交叉驗)。

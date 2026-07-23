# Augur Steward 裁決第 2026-033 號

**L3（AUGUR-ID v1.0）單層 ultracode findings 處置——AO.2／T-ID-3 部分解消同步＋ID.50 已解析定義對齊、lifecycle 判準擴覆、§0.1／TR 矩陣機械修正（合併版 findings：2 medium＋5 minor，同案）**

* **依據**：`AUGUR-MC v1.4 §8.6`（minor／patch）、`§8.2`（較嚴格解讀之解消）、`§8.1`（解釋之界線，v1.5）；findings 冊 `audits/L3-ID-ULTRACODE-20260723.md`；RULING-2026-014（Security／Index／FredSeries 採認）；RULING-2026-030（T-ID-3／CSV-2 同體例）；RULING-2026-028（施作留痕＋獨立核驗）；先例＝RULING-2026-032（L2 同體例一攬子）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **登錄**：Amendment Log **AL-2026-037**
* **性質**：minor／patch 執行層施作（第一至七點）；**不動 parent 歸類、不觸 MC、PA／五原則 byte 級零改、ID 版本維持 v1.0**——所涉變更為 [N] 判準同步／定義對齊、CS.1-P2 判準揭示、ID.40 可判定判準擴覆、[I] 矩陣／§0.1 殘留機械修正
* **分級登錄（Steward 2026-07-23）**：**F-L3-1／2**＝ **medium**（處置採 patch／minor）；**F-L3-3–7**＝ **minor**。零 major；**不動搖 L3 蓋章**（findings 冊結論）

## 一、擬裁一〔AO.2／T-ID-3 與 RULING-2026-014 同步——F-L3-1，medium〕✅

同案 minor／editorial 同步（030 CSV-2／T-ID-3 同體例）：

1. **AO.2 增部分解消註記**：RULING-2026-014 已採認 T.1 Security／T.2 Index／FredSeries 操作化判準；改名／借殼殘留面續保守預設（RULING-2026-030／AL-2026-033）。
2. **Issuer（T.20）**：**不另採認**——本裁決明示 Issuer 判準**維持待採認**（與 RULING-2026-014 一致；AO.4 分軌不變）。
3. **可判定判準改 per-Type**：「無**該 Type** 採認紀錄時將涉該 Type 之引用視為已解析者違反」——Security 已採認面不再過保守；Issuer 面仍保守。
4. **CS.2 T-ID-3**：同步 Issuer 待採認敘事（與 AO.2 一致）。
5. RULING-2026-028 第 1 點自檢：本處置為**文件同步＋per-Type 判準精確化**——不課新類型義務、不解鎖、不除制衡；(a)(b)(c) 均不該當，得以 patch 為之。

## 二、擬裁二〔ID.50「已解析」合取式——F-L3-2，medium〕（**乙案**）✅

採 findings 冊**乙案**（**不採甲案**——不新增 ID.51(d) provisional 清除判準）：

1. **刪除 ID.50 合取式第二 conjunct**（原假引 ID.51(a)「旗標清除」）。
2. **明定「已解析」**：iff〔涉該 Type 之判準採認已生效（ID.20）**且** 該引用**非** ID.21 所定 provisional（未解析）態〕。
3. **同步 CS.1-P2 判準揭示**（`:727`）：與 ID.50 合取式一致——採認已生效且非 provisional 態。
4. **定級**：Steward 定級 **medium**（L3 核心閘可判定性缺陷之 patch；非採認機制骨架變更）。

## 三、擬裁三〔ID.40 lifecycle Evidence 判準擴覆——F-L3-3，minor〕✅

1. **ID.40 可判定判準**：由僅列 merge／split／retire／relist／redirect，擴為「任一 ID.40 所列 lifecycle 事件型別（`:235` 枚舉閉集）缺 Evidence 引用者違反本條」——mint／correct 等納入機械判域（de-identify 仍可由 ID.42 兜底，不衝突）。

## 四、擬裁四〔§0.1 ONT「草案」殘留——F-L3-4，minor〕✅

1. **§0.1 upper-specs**：刪 `AUGUR-ONT v1.0`（Layer 2，**草案**）之「草案」——與【地位】及 Annex CS `upper-specs` 一致（RULING-2026-009 真空同族 mechanical patch）。

## 五、擬裁五〔TR.Y §2.8 落點誤植——F-L3-5，minor〕✅

1. **TR.Y MC §2.8（Agent 定義）列**：改「P5.D／P5.E1、ID.11」→「**ID.11、CS.1-P5（Agent identifier）**」——P5.D 為 Action 定義，非 Agent。

## 六、擬裁六〔TR.B P5 理由欄位移——F-L3-6，minor〕✅

1. **P5.D–P5.Y 各列**：理由正文移入「模式」欄；「ID 落點／處置」欄改 CS.1-P5——與 TR.C 三欄慣例一致，機器抽取模式欄可獲完整理由。

## 七、擬裁七〔TR.C Annex D 主題列截斷——F-L3-7，minor〕✅

1. **D4／D6／D8 主題列**：補全括號與字串（對齊 `AUGUR-WM v1.0` Annex D 權威正文）——D4 含 WM.35 unmapped；D6 拍板後承接；D8 embargo、purged 口徑。

## 八、明示不為

* **Issuer T.20 不另採認**——本裁決不追認 Issuer 判準；僅 AO.2／T-ID-3 同步「部分解消」敘事。
* 不採 F-L3-2 **甲案**（新增 ID.51(d) provisional 清除判準）。
* 不動 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0` 任何條文；不動 MC；PA／五原則 byte 級零改。
* L4–L7 各層 ultracode 不併本案。

## 九、驗證

* `python3 -m tools.constitution_lint report`：PASS 不退轉。
* `ULTRACODE-SCHEDULE.md` L3 列更新＋Amendment Log 登錄 AL-2026-037 於簽核生效時一併辦理。

## 十、施作紀錄（2026-07-23）

| 檔案 | 施作摘要 |
|---|---|
| `specs/IDENTITY-SPECIFICATION.md` | AO.2 部分解消＋per-Type 判準；ID.50 乙案＋CS.1-P2；ID.40 判準擴覆；§0.1 刪草案；T-ID-3 同步；TR.Y §2.8；TR.B P5 理由欄；TR.C D4/D6/D8 補全 |
| `constitution/RULING-2026-033-…` | 本檔生效＋簽核 |
| `constitution/AMENDMENT-LOG.md` | AL-2026-037 |
| `ULTRACODE-SCHEDULE.md` | L3 列閉環 |
| `audits/L3-ID-ULTRACODE-20260723.md` | 呈核段更新 |

## 十一、待獨立核驗（RULING-2026-028 第 3 點 (b)）

> **誠實揭露**：下列項次為 commit 前**須經非施作者**確認之核驗清單。本輪施作者已完成**機械簡核**（原文 grep／diff 限域／lint 親跑）；**獨立對抗核驗另輪**。

| # | 核驗項 | 範圍 | 機械簡核 | 獨立核驗 |
|---|---|---|---|---|
| 1 | **AO.2 部分解消**：014 Security／Index／FredSeries 已註記；Issuer T.20 明示待採認；per-Type 判準 | AO.2、T-ID-3 | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 2 | **ID.50 乙案**：無 ID.51(a) 假引；已解析＝ID.20 且非 ID.21 provisional | ID.50、CS.1-P2 | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 3 | **ID.40 擴覆**：判準覆 `:235` 枚舉閉集 | ID.40 | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 4 | **§0.1 草案刪除**：`:55` 無「草案」 | §0.1 | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 5 | **TR.Y §2.8**：無 P5.D 誤植 | TR.Y | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 6 | **TR.B P5 理由欄**：模式欄含完整理由正文 | TR.B P5 | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 7 | **TR.C D4/D6/D8**：括號閉合、字串完整 | TR.C | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 8 | **[N] 零逾越**：diff 限本裁決核示之 patch；無義務擴張 | ID 全 diff | ✅ 簡核 PASS | ⏳ 待獨立 agent |
| 9 | **lint 基線**：`python3 -m tools.constitution_lint report` error 0／warning 0 | 全 corpus | ✅ 簡核 PASS（7／7） | ⏳ 待獨立 agent |
| 10 | **PA／五原則 byte 零改** | `constitution/` 五原則檔 | ✅ 簡核 PASS | ⏳ 待獨立 agent |

**Steward 2026-07-23：**接受 033**（定案）**

## 簽核

> - [x] **准各項擬裁照收（一攬子採納；F-L3-1 AO.2 同步、Issuer 不另採認；F-L3-2 採乙案；F-L3-3–7 同案機械施作）**（簽：tsaitsangchi，日期：2026-07-23）
> - [x] **分級登錄**：F-L3-1／2＝medium；F-L3-3–7＝minor；零 major
> - [x] **逐項改核**：全照收（無逐項改核）
> - [ ] 修改意見：（無）

*本裁決定案（2026-07-23；Steward **接受 033**）。L3 ultracode 處置閉環；蓋章不動搖。第十一節獨立對抗核驗**待另輪**（機械簡核已完成）。*

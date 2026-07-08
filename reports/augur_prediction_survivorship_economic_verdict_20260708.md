# 股市預測 — survivorship 經濟重跑裁決(SOP 債 b 經濟閉環)

**日期**:2026-07-08 ｜ **性質**:誠實裁決(deflation 地板 §4 續、SOP 債 b 經濟閉環)｜ **對抗驗證**:3 鏡全 CONFIRM(workflow `w4jj7dos1`)
**口徑**:H60 LO top10%、cost 0.585%、asof panels 2016-2025、A'-3 embargo(splits h+62td 逐折);數字全由作者親跑 `scripts/survivorship_economic_verdict.py`(ground truth,非 agent)
**守**:#8(清算 label 無 look-ahead、宇宙純 ≤t) · #12 · #14 · #15(兩效應拆乾淨、不誤歸、兩宇宙並存)

---

## 0. 三十秒結論

方案 B 之前只算了 survivorship 的 **IC**(0.152→0.139、−8.5%),**經濟 Sharpe 未算**。本裁決補上,並**拆開兩個常被混為一談的效應**:

| 效應 | 幅度 | 性質 |
|---|---|---|
| **① 經典下市 survivorship**(加回下市股清算損失) | **≈ 0**(邊際 +0.0023 Sharpe) | 16 clearing 事件、0 落 top-decile;**債 b 的「下市偏誤」實證解決** |
| **② 完整度閘 incumbency**(全史齊 → 當下可算) | **−16.5%**(1.20 → 1.00) | point-in-time 無洩漏,但偏向自樣本起點連續在世老股 |

**把整個 −16% 標「survivorship」= 誤歸(敵③)。** 真下市偏誤近零;headline 1.20 vs 廣宇宙 1.00 之差,全來自**宇宙定義**(incumbency),非下市。

---

## 1. 方法

- **SURVIVOR 基準** = production `core_universe_asof`(`build_universe_asof`:逐 as-of t 要求「[首panel, t] 每個 panel 都齊 canonical 特徵」=**全史齊**)+ 生產 `forward_returns`。淨 Sharpe **1.1972**(= deflation headline 精確吻合)。
- **PIT 宇宙** = 放寬全史齊為「**當下 t 可算即納入**」(全 feats@T 齊、非全史)+ 近窗有交易@≤T + 真股/非ETF/流動性 P25@T,**純 point-in-time**。納入後來下市股 + 連續性不足的在世股。
- **清算 label(#8 命門)** `forward_returns_pit`:下市股取 [entry, exit] 內**最後可得還原價**(≤exit、不用未來);下市中途 last_d<exit → clearing 捕捉部分窗損益;只有 entry → 歸零近似(不外推)。
- **隔離**:PIT 宇宙【排除】9 下市股重跑 → 下市股邊際貢獻。

## 2. #8 對抗驗證(3 鏡全 CONFIRM、workflow `w4jj7dos1`)

- **清算 label 無 look-ahead**:SQL `date<=exit` 硬約束 + `seq[-1]` 取區間內最後一筆,結構上不可能取到 exit 之後價;實測 clearing 事件全部 `last_d<exit`;`verify_label_equiv` 證清算 label 對 survivor 全窗股 **== 生產 forward_returns(0 diff)**。
- **PIT 宇宙純 ≤t**:recency `p.date>floor AND p.date<=T`、feature `panel_date=T`、流動性 percentile `panel_date=T`,無一引用 >T。
- **embargo 兩側同口徑**:SURVIVOR/PIT 皆 `walkforward.splits(pds,60,cal)`(下界 h+62=122td)。

## 3. 結果(拆解)

| 宇宙 | 每 panel ~股數 | 淨 Sharpe | vs SURVIVOR |
|---|---|---|---|
| **SURVIVOR**(全史齊、穩定核心) | ~440 | **1.1972** | — |
| PIT 全含(當下可算 + 下市清算) | ~970 | 1.0022 | −16.3% |
| **PIT 排除 9 下市股**(隔離) | ~970 | **1.0000** | **−16.5%** |

- **① 下市 survivorship 邊際** = 1.0022 − 1.0000 = **+0.0023 Sharpe ≈ 0**(16 clearing 事件、0 落 top-decile;最壞投組衝擊 −0.08%/期)。
- **② 完整度閘 incumbency** = 1.0000 − 1.1972 = **−16.5%**(PIT 每期平均報酬低 0.59%、離散更大 → ~490/panel 額外在世股的宇宙重組)。
- **佐證(非單調性)**:v2 積極版補**更多**下市股(95 vs 9)降幅反而**更小**(−13.2% < −16.3%)→ 降幅非下市股驅動。

## 4. 兩宇宙並存標註(用戶拍板 2026-07-08:不改判準、兩者並存)

headline 依交易哪個宇宙有兩個誠實值:

| headline | 宇宙 | 定位 |
|---|---|---|
| **淨 Sharpe 1.20** | 全史齊「穩定核心」(~440/期) | 現狀;若只交易自樣本起點連續在世乾淨股。**帶 incumbency 樂觀** |
| **淨 Sharpe 1.00** | 當下可算全宇宙(~970/期) | 標準可交易準則(「現在可算即納入」);**更誠實反映真實可部署**,但含更多較噪/低完整度股 |

**全史齊是 point-in-time(無 look-ahead),但要求「[首panel,t] 全齊」= 用了個股自樣本起點的連續存在性(與存活/品質相關)→ incumbency 味**;2018 才 IPO 的股即使 2020 完全可交易也被排除。兩者皆合法宇宙定義,差異須並存揭露、不可只報 1.20。

## 5. 對 deflation 地板的意義(§4 方向修正)

- **deflation 裁決 §4 原寫「survivorship 債未閉環 → 報酬序列偏高 → 真實 DSR 更低」——就經典下市 survivorship 而言方向錯**:下市偏誤 ≈0、**不**推低 DSR。
- 真正壓低 headline 的是**宇宙定義**(全史齊 1.20 vs 廣宇宙 1.00)。若以更誠實的廣宇宙 1.00 為 base 複算 deflation,DSR 會再低(per-period SR 0.72→~0.60、haircut 後更接近 SR_0)——**地板比 1.20 版更低**。
- **SOP 債 b 狀態**:下市 survivorship 經濟效應**實證 ≈0(閉環)**;「完整度即倖存篩」的 incumbency 效應**量化 −16.5%**、屬宇宙定義決策(兩者並存)。IC 側 −8.5% 同理主為宇宙定義、非下市。

## 6. 複現 + 誠實邊界

```bash
python scripts/survivorship_economic_verdict.py          # SURVIVOR/PIT/isolation 三段一次拆解
```
- **口徑微差(#15)**:對抗驗證鏡重跑得 17 clearing / n=27,作者 grounded 16 clearing / n=25,差來自 embargo 面板邊界過濾口徑;不影響量級與裁決(下市邊際 ≈0 兩版一致)。
- **v2 積極版**(放寬完整度 + impute)另混 impute 雜訊,降幅 −13.2% 為含噪上界、不單歸任一因。
- PIT/清算機拟前為 scratchpad(#10 缺口),本裁決已固化入 committed `scripts/survivorship_economic_verdict.py`。

# P4 vol targeting 判決(alpha 1-4;2026-07-17)

**預註冊單點**:target=全期已實現年化 vol(口徑內生 14.34%、零外生魔數)、lookback=4 期、max_scale=1.0
(long-only 只縮不放)、scale 嚴格 ≤t−1(#8);等權單基準(G3/G4 未拍板前)。

| 指標 | 基準(1.1302 錨) | vol_target | 判 |
|---|---|---|---|
| Sharpe | 1.1302 | 1.0919 | ↓ −0.038 |
| MaxDD | −0.1579 | −0.1499 | 微改善 +0.8pp |
| Calmar | 1.0143 | 0.9706 | ↓ |
| skew | −0.2007 | −0.2055 | ≈ |
| kurt | 1.8972 | 1.9417 | ≈(基準本就 <3=薄尾) |

**裁決:分母通道無靶**——季頻 25 期 net 序列 kurt 1.90(<常態 3)、skew −0.20(溫和):「壓 kurt/修 skew」
之動機假設在此配方不成立;overlay 代價=Sharpe −0.038,唯 MaxDD 微淺。**Cederburg et al. 2020 反證
(C-m1 引註:vol-managed 組合樣本外普遍無改善)在台股季頻配方上重現**。

**處置**:
- **G2(sop_master)vol-target 側=能力清償**:`portfolio.vol_target_series` 純函式+4 selftest 鎖
  (含 #8 無前視紅綠)落地;趨勢過濾側維持另列 backlog。
- **不掛 risk_policy 啟用政策**(計畫驗收原文「政策落 risk_policy」,實證分母無靶→依 #15 誠實優先:
  啟用無據、掛之=無益複雜度;本報告即「不落之依據」留痕。hugo 若要監測級落列可另示)。
- dormant 揭露:4/25 期(首 lookback 窗 scale=1);scale<1 者 10/25 期、min_scale 0.668。
- **不入 ledger**(誠實化籃、overlay 未啟用、未改變 headline 建構)。
- inverse-vol 加權側:鑑於分母無靶之同一理由,**降列 backlog**(動機=同一分母假設;避免為做而做付 N)。

# EXECUTED｜S2-KH-L3 · 2026-08-04

> **位階**：[I]  
> **GO**：`audits/S2-KH-L3-GO-20260804.md`  
> **Exact**：`S2-KH-L3-go + GATE-keep + NHC-keep + API-THAW-bounded`  
> **前置**：L2 六針 dry-run `no_corpus`  
> **self-reported（#32a）**：判讀為呈案；數字＝(a)(b)

## 1. 做了什麼

| 步 | 結果 |
|---|---|
| 登錄 GO | ✅ |
| `acquire_knowledge` OpenAlex ×6 查詢（`--limit 5`／domain=`finance`／paper） | ✅ staging 淨增約 **28** 列（去重後） |
| `promote_knowledge --entity-type paper --domain finance` | ✅ 掃 28 pending → **ok=19**／dup=9 |
| `fetch_oa_fulltext --domain finance --limit 19` | ✅ 掃 19 DOI → **全文落地 0**；**license／OA 阻擋 19**（終態帳已記，下輪不重問） |
| `build_sentences`／embed 新全文 | **跳過**（無新 `item_text`） |
| 六針 `--run`（post-promote） | ✅ 完成；`no_corpus` **已解除**；但命中多 **spurious／ungrounded**（見 §3） |
| FinMind／FRED 放量／PME 灌因子／sim-apply | **未做** |

## 2. Acquire 查詢（對齊六針）

| # | query（OpenAlex） | 對針 |
|---|---|---|
| 1 | cross-sectional stock returns industry relative value demean | XSEC |
| 2 | macroeconomic factors cross-section of stock returns | MACRO |
| 3 | stock momentum volatility clustering interaction | MOM-VOL |
| 4 | business cycle regimes equity returns | CYCLE |
| 5 | institutional ownership crowding short selling costs | CHIP |
| 6 | trading volume concentration liquidity premium equities | PARETO-TW |

## 3. 探針複跑（誠實）

| probe_id | gap | spurious | 註 |
|---|---|---|---|
| RKI-XSEC-RELVAL-TW | [] | low | 命中仍偏雜訊／非標的論文（索引污染） |
| RKI-MACRO-PIT-XSEC | [] | low | 同上 |
| RKI-CYCLE-RET-TW | [] | low | 同上 |
| RKI-CHIP-CROWD-TW | ungrounded_hits | **high** | 多源共現弱 |
| RKI-MOM-VOL-TW | ungrounded_hits | **high** | 同上 |
| RKI-PARETO-TW-VOLUME | ungrounded_hits | **high** | 同上 |

**一句**：L3 達「metadata 入庫＋全文阻擋誠實終態」；**未**達「高品質可引用市場 KH 語料」。探針有 hit ≠ 概念橋成立 ≠ G-PROM。

## 4. 全文終態

```
掃 19 筆 DOI → 全文落地 0／item_text +0
skip: no_oa 2／license(版權未明含 NC-ND) 15／…；阻擋 19＝收斂
```

＝計畫 L3 驗收「終態或誠實 `fulltext_blocked`」✅（阻擋路徑）。

## 5. 下一刀（可選）

| 選項 | GO／動作 |
|---|---|
| 語料品質 | 策展更準 query／來源；或公版／CC 全文；**勿**假綠 spurious |
| L4 PME | 另拍 map；禁 cite 率當過閘 |
| Arc B | 若標 raw 洞：`LOOP-S2-TO-S1-EXPAND-go`（THAW-bounded） |
| 截面特徵 | `S3-WAVE-B-go`（與 KH 正交） |

```text
S2-KH-L4-go + GATE-keep + NHC-keep + API-THAW-bounded
```

（僅當要人裁 PME 候選時；本窗**未**默授。）

## 6. 路徑

- acquire：`/tmp/s2-kh-l3-20260804/acquire.log`  
- promote：`/tmp/s2-kh-l3-20260804/promote.log`  
- fulltext：`/tmp/s2-kh-l3-20260804/fulltext.log`  
- probe-run：`/tmp/s2-kh-l3-20260804/probe-run.log`

---

*完。EXECUTED＝L3（metadata＋fulltext_blocked 誠實；探針品質仍 gap）。*

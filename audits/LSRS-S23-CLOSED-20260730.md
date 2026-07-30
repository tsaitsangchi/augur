# LSR-S23 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward `LSRS-S23 + FZ-keep`  
> **拍板**：`audits/LSRS-S23-APPROVED-20260730.md`  
> **前置**：`audits/LSRS-S01-CLOSED-20260730.md`  
> **不含**：KH10-ENABLE-S1／放寬 junk／假抬非語意 eligible

## 一、做了什麼

| 階段 | 結果 |
|---|---|
| **S2 embed en** | 處理 42,304／**新嵌 35,584**／junk 6,720；151.3 分 |
| **S2 embed zh** | 處理 2,001／**新嵌 1,970**／junk 31；15.2 分 |
| **S2 Qdrant**（`--url`） | en upsert **35,449**／差=0；zh upsert **614**／差=0 |
| **S3 KH4** | `refresh_kh4_after_resplit.py`（新）；affected **1004** |
| **S3 admit** | `--until-empty --apply-up-to 9`；**advanced=112** |
| **FZ-keep** | ✅ |

## 二、真兆對照

### KH4（resplit 影響 item）

| answer_status | 前 | 後 |
|---|---:|---:|
| eligible | 885 | **997**（+112） |
| provisional | 112 | **0** |
| ineligible | 7 | 7（未假抬） |

### admit_depth（全庫）

| depth | 前 | 後 |
|---|---:|---:|
| 3 | 508 | **396**（−112） |
| 9 | 145837 | **145949**（+112） |

殘留 depth=3＝**396**：對齊既有永久 `non_semantic_entity_type`（material／compound／book…）——**誠實不抬**。

## 三、新增／變更檔

- `scripts/refresh_kh4_after_resplit.py` — **新**
- logs：`/tmp/lsr_s23_embed_{en,zh}.log`、`qdrant_{en,zh}.log`、`kh4_refresh.log`、`admit.log`

## 四、硬邊界

| 項 | |
|---|---|
| 未開 KH10-S1／PME APPLY | ✅ |
| 未放寬 `is_junk` | ✅ |
| 未假抬 ineligible | ✅ |
| 自動天花板仍＝9（≠KH10） | ✅ |

## 五、下一步（待另令）

```text
KH10-ENABLE-S1 + FZ-keep
```

（collect＋governance CLI；人裁常鎖。）

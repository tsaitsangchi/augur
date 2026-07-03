# augur 跨機接續交接報告(2026-07-03)

**性質**:本機(WSL2 PC002-S1800)→ 另一台電腦接續開發之完整交接。**新機第一件事=讀本檔 + MEMORY 攜帶段(§六)**。

---

## 一、專案狀態總覽(截至 2026-07-03 傍晚)

| 層 | 狀態 |
|---|---|
| 治權 | 靈魂 v1.4.0 / 原則精華 v1.7.1 / **憲章 v1.20.0**(知識層多域+全文准入雙軌)/ **CLAUDE v1.16**(#29 資料驅動三層管線、#30 平行 dump 慣例)/ README |
| 計畫 | 知識三部曲:① expansion(已執行)② harvest v1.3(已實作+上線)③ **text v2.0**(重生版:八層金字塔/W1-W9 執行序/拍板 3 點已裁決) |
| 最新 tag | `treaty-v1.16-embed-engine-20260703`(commit e5d36dc 之後尚有本檔 commit) |

## 二、DB 現況(本機實測;**DB 不進 git,靠 dump 遷移**)

| 資產 | 量 |
|---|---|
| registry | knowledge_query 4,706 詞 / knowledge_source 3,592 列(enabled 69)/ taxonomy 4,798 節點 |
| knowledge_item | 14,602(harvest 首輪+常規批;lineage 100%) |
| philosophy_thinker | ~4,000(獎項/域源 source 欄 100%) |
| **knowledge_lexicon** | **154,875 條逐字定義**(說文 9,831/康熙 p0 26,730/Webster 113,425/Roget 1,043/王弼 405/論語孟子注疏 3,441) |
| knowledge_sentence | ~1.54M 句(reference 誤入 28,835 句已清) |
| **knowledge_concordance** | **49,106,830 列 / 4.8GB**(純原典;「道」5,072/「仁」2,471/'valu' 12,659 處) |
| corpus 治理 | 1,317 部全蓋章(provenance 523/audit 794;**有全文 NULL=0 常備不變式**)、corpus_class reference 7 部、151 部 flag 待人審 |
| 嵌入 | chunk 63,601 既有;**W5 進行中**(lexicon+zh 句,見 §四) |

## 三、DB 遷移(⚠️ 有 snapshot 時點陷阱)

**現有 dump**:`C:\temp_augur_export\augur_pg17_20260703.dump`(4.5GB,pg_restore 驗證 ✓)。
**陷阱**:此 dump 的 snapshot 時點在 **W1 蓋章/reference 清理/DDL 四欄/W5 嵌入之前**(pg_dump 起跑即定格)。兩條路:

- **路 A(推薦)**:本機等 W5 嵌入完成後,用 CLAUDE #30 平行配方**重新 dump**(15-20 分),攜帶新檔:
  ```bash
  pg_dump -Fd -j 4 -Z1 -h 127.0.0.1 -U augur -d augur -f /home/hugo/augur_dump_final
  cp -r /home/hugo/augur_dump_final /mnt/c/temp_augur_export/
  ```
- **路 B**:用現 dump 還原後,在新機重放(全部冪等 script 在 repo):
  1. reference 清理 SQL(見 git log dc7916e 描述,或重跑 `build_sentences` 統計後手動 DELETE)
  2. W1 蓋章+DDL:e5d36dc commit 訊息內之 SQL(或看本檔 git blame 前一 commit)
  3. `python scripts/embed_knowledge.py --layer lexicon` → `--layer sentence --language zh` → `--build-index`

**新機還原**:
```bash
createdb -U <su> -O augur augur    # 或先建 role augur
pg_restore -j 4 -h 127.0.0.1 -U augur -d augur <dump 檔/目錄>
```

## 四、進行中/未完(接續佇列)

1. **W5 嵌入**(本機背景 `b2df4bado`,估至 ~21:00):p0 lexicon 154,875(~5-6h)→ p1 zh 句 → HNSW。**中斷無妨**:`knowledge_build_meta` 游標 resume-safe,新機還原後直接續跑同指令。
2. W5 完成後:跨語驗收 rank@10(**先做 junk chunk 清理工單**:「_」「----」高分污染)。
3. v2.0 W6-W9:term_stats 統計層 → 衍生層(對齊/引文網/圖譜,合規骨架先)→ L5 answer.py/profile.py/coverage → en 句嵌入 C 子集(已拍板)。
4. 分期債:康熙 p1(餘 174 部首)、十三經餘十一經、151 部 flag 人審(`review_flagged_works.py` 規格在 v2.0 §三,**尚未實作**)、staging pending 審、`verify_text_integrity.py`(v2.0 W2,**尚未實作**)。
5. harvest 常規批:nightly `python scripts/harvest_knowledge.py --batch 300 --rounds 4 --max-minutes 120`(排程空間剩 ~25,000 組合;googlebooks/S2 熔斷自癒設計)。

## 五、新機環境 setup(README + 本檔補充)

```bash
git clone https://github.com/tsaitsangchi/augur && cd augur
python -m venv venv && source venv/bin/activate && pip install -e .   # 含 jieba
cp .env.example .env   # ⚠️ .env 不進 git:DB_* / FINMIND_TOKEN / FRED_API_KEY 須手動帶
export UNPAYWALL_EMAIL=<聯絡信箱>   # fetch_oa_fulltext 需要
# PostgreSQL 17 + pgvector 0.8+;還原 DB 見 §三
```
驗證:`python scripts/harvest_knowledge.py`(無參數統計)、`python scripts/embed_knowledge.py`(各層已嵌統計)、`python scripts/verify_hygiene.py`。

## 六、記憶攜帶(⚠️ memory 檔不隨 git)

本機 Claude 記憶在 `~/.claude/projects/-home-hugo-project-augur/memory/`——新機不會有。兩選:
(a) 手動複製該目錄到新機同路徑;(b) 新機開工第一句對 Claude 說:「讀 reports/augur_cross_machine_handoff_20260703.md 與 reports/augur_philosophy_erudition_handoff_20260702.md 接續」——本檔已含關鍵狀態,治權檔+計畫檔為完整 SSOT。

## 七、操作要訣(實證教訓精選,防新機重踩)

- dump 期間禁 DDL(鎖風暴;CLAUDE #30 有診斷處置)
- FinMind:token 2026-06-24 已過期降 free;抓取一律 #24/#25(最小探測、問錶不推算)
- 批量一律本地 script 背景(#28);replace 改檔必 assert 錨點命中(print 成功≠真成功)
- Porter 正規形查詢(value→'valu');分區母表 size 要 sum 子分區
- DB 實況以實查為準,勿信任何文件快照數字(#15)

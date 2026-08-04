# G13｜剩餘 106 列 `awaiting_hugo` triage 呈案（2026-08-04）

> **性質**：[I] Steward 圈選卡。**非**自動清庫。  
> **上游**：`audits/OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED-20260804.md`（年齡門 >30d → 54 superseded；**keep＝106**）。  
> **硬界**：**無本卡 go 句不得**批量 supersede／改 status；不碰 G16 ALWAYS；不代裁。

---

## 1. 現查（live · as_of 2026-08-04）

| 度量 | 值 |
|---|---|
| `awaiting_hugo` | **106** |
| 年齡 ≤30 日 | **106**（＝全數仍在門內） |
| 年齡 >30 日 | **0**（年齡門已清） |
| 最舊／最新 `asked_at` | **2026-07-06**／**2026-08-03** |
| 最舊懸置日數 | **29**（≤30 → 探針年齡門綠） |
| `resolved_by='hugo'` | **0** |

探針綠 ≠「無人裁積壓已消」——106 列真決策／雜訊混存仍待 triage。

---

## 2. 抽樣（唯讀；不代裁）

**最舊（≈29d）**

| asked | 片段 |
|---|---|
| 2026-07-06 | 股市預測計畫完成了嗎?…TTAI 計畫完美就執行 |
| 2026-07-06 | phases的error是否可以處理 |
| 2026-07-06 | 我可以現在就改bge-m3嗎? |
| 2026-07-06 | TTAI計畫規畫完美嗎? |
| 2026-07-07 | 選股路由…是否需要增加選股預測模型… |

**最新**

| asked | 片段 |
|---|---|
| 2026-08-03 | FinMind MCP 網頁可否做 MCP |
| 2026-08-01 | 依解決問題最佳做法可下排程嗎 |
| 2026-08-01 | 此專案所有問題處理的最佳下一步 |

判讀（self-reported）：多為計畫狀態／工具選擇／聊天延續——**可能**適合噪音擴規或 session 叢集，但**不得**無授權整批清。

---

## 3. 選項（圈一）

```text
G13-106: keep | sample-triage | noise-expand-ask | age-lower-ask | session-cluster-ask
```

| 碼 | 意涵 | 機器效力（須另句才寫） |
|---|---|---|
| **keep** | 維持 106；僅監看探針 | 零改列 |
| **sample-triage** | 先呈 N 題（建議 10／20）人裁，其餘 keep | 僅對圈中 qid 依人裁 resolve／supersede |
| **noise-expand-ask** | 開案擴噪音／片段規則（另計畫） | **本句不寫庫**；通過後才 `--sweep` |
| **age-lower-ask** | 擬降年齡門（如 >14d）——**治權口徑變更** | **本句不寫庫**；須明示天數＋go |
| **session-cluster-ask** | 同 session 重複題機械叢集呈裁 | **本句不寫庫**；通過後才批次 |

---

## 4. Paste-ready go（人選後貼）

**維持：**

```text
G13-106: keep
```

**抽樣人裁（N＝10 或 20）：**

```text
G13-106: sample-triage N=10
```

```text
G13-106: sample-triage N=20
```

**僅開案、不寫庫：**

```text
G13-106: noise-expand-ask
```

```text
G13-106: age-lower-ask max_age_days=14
```

```text
G13-106: session-cluster-ask
```

**批量 supersede 明示（預設拒；僅 Steward 要整批才貼）：**

```text
G13-106-MASS-SUPERSEDE: confirm + max_age_days=<n> + decided_by=hugo
```

（無本句＝**禁**對 106 做年齡門以外之批量 supersede。）

---

## 5. 不做

- 不因探針綠宣稱「積壓已解」  
- 不碰 G16 ALWAYS／M-G15 `auto_admit`  
- 不 FinMind 寬窗；不 git commit  

*呈案時點：2026-08-04 ≈11:34+08。*

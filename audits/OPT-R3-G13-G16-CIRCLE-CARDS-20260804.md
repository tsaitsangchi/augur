# G13／G16 Steward 呈裁卡（can-do2 · 2026-08-04）

> **位階**：[I]。**來源**：`audits/OPT-R3-W1B-G3-PROBE-EXECUTED-20260804.md`（live 紅＝探針有效）。  
> **硬界（呈裁時）**：不代裁；不改 trigger；不改 `awaiting_hugo` 列。  
> **已裁（2026-08-04）**：見下「圈選結果」→ 執行＝`audits/OPT-R3-G13-G16-ARMS-EXECUTED-20260804.md`。

---

## 圈選結果（Steward 親打）

```text
G13-Q22: machine-supersede-ok
G16-ALWAYS: enable-always-go   # 殘本升臂（原 enable-probe-only；Steward 2026-08-04 另句）
```

| 閘 | 臂 | 狀態 |
|---|---|---|
| G13-Q22 | `machine-supersede-ok` | ✅ 臂＋年齡門批次→`OPT-R3-G13-AGE-G16-ALWAYS-EXECUTED` |
| G16-ALWAYS | `enable-always-go` | ✅ 已升臂＋ ALWAYS 116 支（同 EXECUTED） |

---

## 卡 A｜M-G13／Q22（steward question backlog）

| 項 | 值 |
|---|---|
| 探針 | `check_steward_question_backlog.py --check` |
| selftest | ✓（含先驗紅臂） |
| live（裁前／裁後複核） | **rc=1 紅**：`awaiting_hugo=160`；最舊 2026-06-22（懸置 **≈43** 日）；`resolved_by='hugo'=0` |
| 判讀 | 探針有效；紅＝真實 backlog 債，非假綠；臂准≠自動清列 |

**原選單（史料）**：

```text
G13-Q22: machine-supersede-ok | keep-awaiting | triage-first
```

| 選項 | 意涵 |
|---|---|
| `machine-supersede-ok` | ✅ **已選**——允許機器路徑將逾齡／可機械判定項 supersede（細節另跑本） |
| `keep-awaiting` | （未選） |
| `triage-first` | （未選） |

---

## 卡 B｜M-G16（trigger ALWAYS mode）

| 項 | 值 |
|---|---|
| 探針 | `check_trigger_always_mode.py --check` |
| selftest | ✓（0 ALWAYS→紅） |
| live | **rc=1 紅**：非內部 116 全 `'O'`；**ALWAYS=0**（probe-only 下紅＝誠實） |
| 判讀 | 殘本已升 `enable-always-go`＋ALWAYS 116（見 AGE-G16-ALWAYS EXECUTED） |

**原選單（史料）**：

```text
G16-ALWAYS: enable-probe-only | enable-always-go | defer
```

| 選項 | 意涵 |
|---|---|
| `enable-probe-only` | （初裁；殘本已升） |
| `enable-always-go` | ✅ **殘本已選**——准 ENABLE ALWAYS（見 AGE-G16-ALWAYS EXECUTED） |
| `defer` | （未選） |

---

## 不做清單（仍有效）

- 不代勾未選臂；不碰 M-G15 `auto_admit`  
- 本卡階段不機器改列／不改 trigger——**執行另見 ARMS-EXECUTED**（寫入閘已接線；本輪 dry-run 零候選）

*呈裁時點：2026-08-04 ≈11:00+08；圈選落地 ≈11:10+08。*

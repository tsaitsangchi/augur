# AVI／影音 ASR 抽字入庫 · PLAN（REGISTER）

date: 2026-08-11  
kind: plan_register  
status: REGISTERED — **未落地**；需雙明示重開才可 CODE-GO  
paste: "AVI-ASR-plan-register | ffmpeg+local-whisper | owned_local | five-mitigations | cite-20260713-reject | ≠PDF-C-no-ASR-flip-silent"

## 現況（真）
- `fileparse` **不認** `.avi`／影音 → `unknown_ext` 略過；上傳大影音還可能 `Failed to fetch`（整批讀入記憶體）。
- PDF-C 明文 **禁 ASR／caption**（`fileparse`／OCR 計畫）。
- [`augur_ocr_asr_transcription_amendment_20260713.md`](../reports/augur_ocr_asr_transcription_amendment_20260713.md)：**對抗審查綜合裁決＝否決**（laundering／下游洗白／whisper 流利幻覺）。PDF-C **不翻案**只開 Tesseract。

## 用戶意向（2026-08-11）
明示希望「augur **可以**處理 `.avi` 抽文字入庫」；選邊＝**本地 whisper／等效 ASR＋ffmpeg 抽音**（設計 GO）。

## 提案邊界（若雙明示重開）
| 准 | 禁 |
|----|----|
| 本機 `ffmpeg` 抽音軌 → 本地 ASR（faster-whisper／whisper.cpp） | 雲端 ASR、caption、摘要改寫入 `item_text` |
| `source_type=asr_transcribe`＋S0／置信度標記 |  silently 當「原文逐字」進 guard 當權威 |
| `license=owned_local`＋`access_scope=local_private` 硬綁 | 公版／CC 公網媒體走 ASR 入庫 |
| 品質閘 fail-closed（過短／過低 conf／靜音幻覺熱句表） | 無原件 sha／無 conf 仍 eligible |
| 上傳：影音改單檔／串流；超限回**結構化錯誤**非 Failed to fetch | 影音塞爆 50MB 記憶體後靜默斷線 |

## 粗落地塊
1. `fileparse`：`.avi`／`.mp4`／`.mov`／`.mkv`／`.mp3`／`.wav`／`.m4a` → `_read_via_asr`  
2. 新 `knowledge/transcribe_asr.py`（領域名詞）：ffmpeg → wav → ASR → `(text, conf, meta)|skip`  
3. acquire／webupload：單檔上限策略分離（影音可較大但不一次 multipart 讀爆）；admin UI 明確略過原因  
4. kh4／citations：展示／guard 感知 `asr_transcribe`（防下游洗白）  
5. 治權：對 2026-07-13 **明示重開**窄切（僅 owned_local 影音），**不**改 PDF-C no-ASR 句

## 依賴
- OS：`ffmpeg`（本機已有）  
- pip：`faster-whisper` 或 whisper.cpp binding（尚未進 venv）  
- 模型權重本機落盤（下載需你准）

## 下一步門檻（須再選）
- **A**：雙明示「重開 ASR 窄切」→ 寫 ADOPTED＋CODE-GO 再動碼  
- **B**：維持否決 → 僅改善上傳（影音略過＋清楚錯誤）；`.avi` **不**入庫正文  
- **C**：plan 停此

## 誠實句
在 A 未通過前，對用戶／UI 仍應說：**目前不能對 .avi 抽字入庫**；上傳失敗屬前端／大小限制，非已具備 ASR。

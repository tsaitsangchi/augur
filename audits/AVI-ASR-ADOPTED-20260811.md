# AVI／影音 ASR 抽字入庫 · ADOPTED

date: 2026-08-11  
kind: plan_adopted  
status: ADOPTED → **CODE EXECUTED**（見 `AVI-ASR-CODE-EXECUTED-20260811.md`）  
supersedes_in_scope: 2026-07-13 全開 ASR 否決 **之影音 owned_local 窄切除外**；PDF-C **no-ASR 不動**  
paste: "AVI-ASR-ADOPTED | owned_local+local_private | ffmpeg+local-ASR | five-mitigations | PDF-C-no-ASR-keep | CODE-EXECUTED"

## 雙明示
- 用戶：希望 `.avi` 可抽字入庫；選 `whisper_local` 設計；選 **重開 ASR 窄切**。  
- 本帳：採納 **僅 owned_local／local_private 影音／音訊** 走本機 ASR；**不**翻 PDF-C；**不**開 caption。

## 硬邊界（CODE 必須守）
1. `license=owned_local` ∧ `access_scope=local_private` 否則拒絕 ASR 入庫。  
2. 引擎：本機 only（faster-whisper 或 whisper.cpp）；禁雲。  
3. `source_type=asr_transcribe`；正文前綴誠實標記（如 `<!-- via=asr_transcribe -->`）。  
4. 品質閘 fail-closed：無語音／過短／conf 低／黑名單熱句（感謝觀看等）→ skip，不假入庫。  
5. 保原件：path／sha 進 evidence 或并列欄（依現 schema 能做的最小集）。  
6. citations／guard：ASR 引文不得偽稱「庫內原文逐字公版」無標記（至少 meta／via 可辨）。  
7. 上傳：`.avi` 等改可察覺略過或單檔串流；禁整批 OOM 靜默 `Failed to fetch` 無訊息。

## 範圍副檔名（初版）
- 影音：`.avi` `.mp4` `.mov` `.mkv` `.webm`  
- 音訊：`.mp3` `.wav` `.m4a` `.flac` `.ogg`  
（皆經 ffmpeg 抽單聲道 wav 再 ASR）

## PDF-C
維持「禁 ASR／caption」——僅指 PDF 光柵軌；**不**與本影音窄切開混。

## 下一步
~~等 **CODE-GO**~~ → 已落地；真人影音入庫：Admin 選 owned_local＋local_private 上傳 `.avi`（≤200MB），或 CLI `--dir`＋同授權。

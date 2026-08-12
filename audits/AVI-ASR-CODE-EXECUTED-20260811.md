# AVI／影音 ASR 抽字入庫 · CODE EXECUTED

date: 2026-08-11  
kind: code_executed  
status: CODE-GO 落地  
plan: `AVI-ASR-ADOPTED-20260811.md`  
paste: "AVI-ASR-CODE | fileparse+asr | admission asr_transcribe | owned_local gate | upload 200MB | faster-whisper | PDF-C-no-ASR-keep"

## 做了什麼
1. `transcribe_asr.py`：ffmpeg→wav→faster-whisper；品質閘；S0 `<!-- via=asr_transcribe -->`；`--selftest`／`--file`。
2. `fileparse`：影音／音訊副檔名走 ASR；單檔上限影音 200MB／文件 50MB；SKIP＋`asr_quality`／`asr_requires_owned_local`。
3. `admission.SOURCE_TYPE_WHITELIST` += `asr_transcribe`（#19）。
4. `acquire_local_files.ingest_file`：reason=`asr` → 強制 owned_local＋local_private，否則 skip；覆寫 `source_type=asr_transcribe`＋S0 標記。
5. `webupload`／admin 上傳：影音用 200MB；影音 BATCH=1；錯誤提示不再靜默 Failed to fetch。
6. `pyproject.toml` admin extras += `faster-whisper>=1.0`；venv 已裝 1.2.1。

## 自測／冒煙
- `python -m augur.knowledge.fileparse --selftest` → 全通過  
- `python -m augur.knowledge.transcribe_asr --selftest` → 全通過  
- `python -m augur.knowledge.webupload --selftest` → 全通過  
- sine 假音 `.wav`：`extract_text` → `asr_quality`（無語 VAD 空段，fail-closed 正確）  
- ffmpeg 在 PATH；模型冒煙用 `AUGUR_ASR_MODEL=tiny`

## 硬邊界（仍守）
- PDF-C **禁 ASR／caption** 不動（僅 PDF 光柵軌）。  
- 非 `owned_local`＋`local_private` 的影音抽得出字也不入庫（`asr_requires_owned_local`）。  
- 禁雲端 ASR。

## 後續 hotfix（同日）
- ffmpeg `subprocess text=True` 遇中文／locale stderr → `UnicodeDecodeError` → 假 `parse_error`（job30 六支 avi）。已改 binary capture。
- job30 用 `public_domain/public`：即使 ASR 成功也會 `asr_requires_owned_local`；重入須 `owned_local`＋`local_private`。

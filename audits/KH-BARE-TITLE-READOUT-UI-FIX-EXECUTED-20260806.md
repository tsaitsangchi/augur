# KH bare-title readout UI fix — EXECUTED 2026-08-06

## Symptom (Chat UI :8090)

```
此題不屬機械可驗域,ultracode 檔改以一般誠實管線作答。
知識庫中無此內容。
```

Query was bare title: `國碩-ERP-GP_DR說明(20211007-4-rman)1` (no 「請讀出」).

## Root cause

1. **`is_readout_intent` false** for bare doc titles → no readout arm; ANN/relevance path brittle for filename paste.
2. **Advisor :8399 long-lived** without reload of readout/compact (user systemd since 11:33).
3. Compact `wrap_compact_llm` previously **rebuilt** `ollama.make_llm_fn()` (dropped serve `--model` / stubs).

Ultra note is expected for ultracode tier on non-mechanical Q; **NO_KNOWLEDGE was the false denial**.

## Fix

- `readout.is_readout_intent`: bare title-like query (≤160, looks-like-title, no ask-particles) → readout.
- `compact_answer.wrap_compact_llm`: polish-wrap **caller** `llm_fn` only.
- Restarted `augur-advisor` + `augur-chat` (systemctl --user).

## Verify

- `python -m augur.knowledge.readout --selftest` (bare title ✓)
- Admin stub/live advise bare title: `readout.item_ids=[277948]`, `compact` on, response ≠ `知識庫中無此內容`, guard pass.

## Steward

Login still required for `domain=local` RBAC; anonymous remains fail-closed empty → honest closed set.

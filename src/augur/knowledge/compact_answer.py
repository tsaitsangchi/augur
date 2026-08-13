"""知-how／讀出緊湊作答——凍結引文＋短答約束（對症：本機 LLM／prompt 體積，非 KH 入庫）。

🎯 這支在做什麼(白話):檢索／readout 能命中（如 277948）後，**自動**把引文裁到有界、
   強制短答人格（禁複述用戶問題、禁三姿態、禁想題長文），必要時可兩段：
   Phase1 只凍結引文 → Phase2 再短答。瓶頸在弱 GPU／超長 prompt，不在入庫。
守 readout ADOPTED· #1（禁幻造／禁把問句當引文）· FZ-keep· #15。

執行指令矩陣:
  python -m augur.knowledge.compact_answer --selftest
"""
from __future__ import annotations

import os
import re
from typing import Any, Sequence

from augur.llm.ollama import strip_quote_marks

# 凍結預算（經驗：全量 inline＋4b 易 900s 逾時；~2.4k 字＋短答可在可接受時間）
MAX_CITE_CHARS = int(os.environ.get("AUGUR_COMPACT_CITE_CHARS", "2000"))
MAX_CITE_N = int(os.environ.get("AUGUR_COMPACT_CITE_N", "3"))
# 產品預設 960（K7：8b 逐步口吻達標）；可 env 覆寫回 480 等
COMPACT_NUM_PREDICT = int(os.environ.get("AUGUR_COMPACT_NUM_PREDICT", "960"))

_META_HEAD = re.compile(
    r"^(?:首先[，,\s]*我需要|"
    r"首先[，,\s]*(?:我會先|讓我)|"
    r"根據(?:提供的)?檢索|"
    r"讓我(?:先)?(?:分析|理解|看看)|"
    r"用戶(?:的)?問題是|"
    r"使用者(?:的)?問題是|"
    r"我會先判斷問題類型)"
    r"[^\n]*\n+",
    re.MULTILINE,
)

_INSTR_ECHO = (
    "禁止開場想題", "不要套投資", "硬約束", "只依據下方", "不能打引號",
    "完全不要打引號", "關鍵點：", "檢索索引文有", "我需要根據使用者",
)

# 中段想題／自我提醒（live 實證：條列後突然「我需要從這些…」）
_MID_THINK = re.compile(
    r"(?m)^(?:"
    r"我需要|"
    r"關鍵是[：:]|"
    r"不能(?:照抄|添加)|"
    r"從引文提取|"
    r"讓我(?:先)?|"
    r"接下來我|"
    r"首先[，,\s]*我|"
    r"不要整篇|"
    r"必須基於引文"
    r").*$"
)
_STEP_LINE = re.compile(r"(?m)^\s*(?:\d+[\.、\)]\s+|[-•・]\s+\[[\d]+\])")


def should_compact(
    query: str,
    citations: Sequence[Any] | None = None,
    *,
    readout_meta: dict | None = None,
    answer_mode: str | None = None,
) -> bool:
    """answer_mode: None/auto | compact | full | two_phase(等同 compact 作答)。"""
    mode = (answer_mode or os.environ.get("AUGUR_ANSWER_MODE") or "auto").strip().lower()
    if mode in ("full", "off", "0", "false"):
        return False
    if mode in ("compact", "two_phase", "short", "1", "true", "on"):
        return True
    # auto
    if readout_meta:
        return True
    from augur.knowledge.readout import is_readout_intent
    if is_readout_intent(query or ""):
        return True
    # 有 item 引文且問句像本地作業／步驟／路徑
    has_item = any(getattr(c, "item_id", None) is not None for c in (citations or ()))
    if has_item and re.search(
        r"(還原|備份|路徑|步驟|怎麼做|如何|演練|SOP|設定|RMAN|r-man|Oracle|DR)",
        query or "",
        re.I,
    ):
        return True
    return False


def freeze_citations(
    citations: Sequence[Any],
    *,
    prefer_item_ids: Sequence[int] | None = None,
    prefer_terms: Sequence[str] | None = None,
    max_chars: int = MAX_CITE_CHARS,
    max_n: int = MAX_CITE_N,
) -> list:
    """凍結引文：prefer item 優先且可獨占；問句詞密高者優先；再裁字數／條數。"""
    cites = list(citations or [])
    prefer = {int(i) for i in (prefer_item_ids or []) if i is not None}
    if prefer:
        primary = [c for c in cites if getattr(c, "item_id", None) in prefer]
        if primary:
            cites = primary  # 丢掉 works／雜訊 item，對症「命中卻混進 271659」
    terms = [t for t in (prefer_terms or []) if t]

    def _dens(c) -> int:
        blob = (getattr(c, "text", "") or "").casefold()
        if not terms:
            return 0
        s = sum(1 for t in terms if t.casefold() in blob)
        if "fgl_ws" in blob:
            s += 3
        return s

    if terms:
        cites = sorted(cites, key=_dens, reverse=True)
    out, total = [], 0
    for c in cites:
        t = getattr(c, "text", "") or ""
        if not t.strip():
            continue
        if len(out) >= max_n:
            break
        if total + len(t) > max_chars:
            break  # 不截斷單則（保 verify_verbatim）；寧少勿破閘
        out.append(c)
        total += len(t)
    return out


def strip_meta_reasoning(text: str) -> str:
    """剝開場「想題」套話（模型常無 <think> 標籤直接洩）。"""
    out = (text or "").strip()
    for _ in range(8):
        nxt = _META_HEAD.sub("", out, count=1).lstrip()
        if nxt == out:
            break
        out = nxt
    return out


def _strip_instruction_echo(text: str) -> str:
    """若模型把短答指令複述進答案，從真正內容行起裁。"""
    if not any(m in (text or "") for m in _INSTR_ECHO):
        return text or ""
    lines = (text or "").splitlines()
    keep: list[str] = []
    started = False
    for ln in lines:
        if not started:
            if any(m in ln for m in _INSTR_ECHO):
                continue
            if ln.startswith(("首先", "使用者問題", "用戶問題", "檢索索引文", "我會", "關鍵點")):
                continue
            if (
                "從引文" in ln
                or ln.lstrip().startswith(("- [", "・", "•", "1.", "（1）"))
                or any(k in ln for k in ("國碩", "DR演練", "災難還原", "r-man", "RMAN", "/u5", "NBU"))
            ):
                started = True
                keep.append(ln)
            continue
        keep.append(ln)
    return "\n".join(keep).strip() if keep else (text or "").strip()


def _strip_mid_think(text: str) -> str:
    """從第一行中段想題起截斷；保留其前的實質／步驟行。"""
    lines = (text or "").splitlines()
    keep: list[str] = []
    for ln in lines:
        s = ln.strip()
        if s and _MID_THINK.match(s):
            break
        if any(m in ln for m in ("我需要從", "不能照抄原文", "只用白話", "必須基於引文")):
            break
        keep.append(ln)
    return "\n".join(keep).strip()


def _prefer_step_lines(text: str) -> str:
    """若已有編號／[N] 條列，丢掉條列後的散文想題殘段。"""
    lines = (text or "").splitlines()
    step_idxs = [i for i, ln in enumerate(lines) if _STEP_LINE.match(ln)]
    if not step_idxs:
        return text or ""
    # 從頭到最後一條「步驟樣」行；其後若接想題已由 _strip_mid_think 處理
    last = step_idxs[-1]
    # 允許步驟行後同一段的延續（縮排／接續），遇到空行+想題才停
    end = last
    for i in range(last + 1, len(lines)):
        ln = lines[i]
        if not ln.strip():
            # 空行後若下一非空是想題／非步驟 → 停在空行前
            nxt = next((lines[j] for j in range(i + 1, len(lines)) if lines[j].strip()), "")
            if nxt and (_MID_THINK.match(nxt) or (
                not _STEP_LINE.match(nxt) and any(k in nxt for k in ("我需要", "關鍵是", "不能"))
            )):
                break
            end = i
            continue
        if _STEP_LINE.match(ln):
            end = i
            continue
        # 步驟說明延續（非想題）
        if _MID_THINK.match(ln) or any(k in ln for k in ("我需要", "關鍵是：", "不能照抄")):
            break
        end = i
    return "\n".join(lines[: end + 1]).strip()


def _normalize_cite_bullets(text: str) -> str:
    """把 `- [N]：…`／`- [N] …` 收成 `N. …`（模型常用引文點列替代 1.2.3.）。"""
    def repl(m):
        return f"{m.group(1)}. {m.group(2)}"
    out = re.sub(r"(?m)^\s*[-•・]\s*\[(\d+)\]\s*[：:]\s*(.*)$", repl, text or "")
    out = re.sub(r"(?m)^\s*[-•・]\s*\[(\d+)\]\s+(.*)$", repl, out)
    return out


def polish_compact_response(text: str) -> str:
    """緊湊路徑出閘前機械抛光：去引號框＋去想題頭／中段＋去指令複述＋偏好步驟塊。"""
    out = strip_meta_reasoning(strip_quote_marks(text or "")).strip()
    out = _strip_instruction_echo(out)
    out = _strip_mid_think(out)
    out = _prefer_step_lines(out)
    out = _normalize_cite_bullets(out)
    return out.strip()


# 設定填值機器閘：弱 LLM 常只寫「改 wsj02」不給字串 → 從凍引文抽出欄位=值強制注入
_FILL_KV_LINE = re.compile(
    r"(?im)^\s*(wsj0[1-9]|wsj\d{2})\s*=\s*(\S+)"
)
_FILL_KV_INLINE = re.compile(
    r"(?i)\b(wsj0[1-9]|wsj\d{2})\s*=\s*([^\s`|，,；;]+)"
)
_FILL_TABLE_KV = re.compile(
    r"\*\*(wsj\d+)\*\*[^\n`|]*`([^`]+)`",
    re.I,
)
_FILL_QUERY_RE = re.compile(
    r"(?i)(wsj\d+|填寫|填什麼|要填|VARCHAR2?|站台\s*IP|SOAP|設定檔|欄位|具體內容)",
)
_RESP_HAS_KV = re.compile(r"(?i)\bwsj\d+\s*=\s*\S+")


def extract_fill_kvs_from_citations(citations: Sequence[Any] | None) -> list[tuple[str, str]]:
    """自凍引文抽出可照抄 `欄位=值`（程式塊列優先，其次表列 backtick）。"""
    seen: dict[str, str] = {}
    order: list[str] = []
    for c in citations or ():
        blob = getattr(c, "text", "") or ""
        for m in _FILL_KV_LINE.finditer(blob):
            k, v = m.group(1).lower(), m.group(2).strip().rstrip("`")
            if k not in seen:
                order.append(k)
            seen[k] = v
        for m in _FILL_TABLE_KV.finditer(blob):
            k, v = m.group(1).lower(), m.group(2).strip()
            if k not in seen:
                order.append(k)
                seen[k] = v
        for m in _FILL_KV_INLINE.finditer(blob):
            k, v = m.group(1).lower(), m.group(2).strip().rstrip("`")
            if k not in seen:
                order.append(k)
                seen[k] = v
    return [(k, seen[k]) for k in order]


def response_has_fill_kv(text: str) -> bool:
    return bool(_RESP_HAS_KV.search(text or ""))


def ensure_fill_kv_in_response(
    text: str,
    query: str,
    citations: Sequence[Any] | None = None,
) -> str:
    """設定／wsj 題：若引文有範例而答文無 `欄位=值`，前置注入（機器閘，不靠弱模型守約）。"""
    q = query or ""
    kvs = extract_fill_kvs_from_citations(citations)
    if not kvs:
        return (text or "").strip()
    want = bool(_FILL_QUERY_RE.search(q)) or any(
        "填寫範例" in (getattr(c, "item_title", "") or "")
        or "wsj_file" in (getattr(c, "item_title", "") or "")
        for c in (citations or ())
    )
    if not want:
        return (text or "").strip()
    body = (text or "").strip()
    # 弱模型有時在已有引文時仍吐誠實閉集句 → 整句換掉再注入
    from augur.advisor.guard import NO_KNOWLEDGE_RESPONSE
    if body == NO_KNOWLEDGE_RESPONSE or body.startswith(NO_KNOWLEDGE_RESPONSE + "\n"):
        body = ""
    if response_has_fill_kv(body):
        # 已有任一欄=值仍可能缺關鍵欄；問句點名 wsj02 卻無 wsj02= → 補齊
        asked = re.findall(r"(?i)wsj\d+", q)
        missing = [
            (k, v) for k, v in kvs
            if asked and k in {a.lower() for a in asked} and not re.search(
                rf"(?i)\b{re.escape(k)}\s*=", body
            )
        ]
        if not missing and asked:
            return body
        if not asked:
            return body
        # 問了特定欄但答缺該欄 → 仍注入全組對照（同列 wsj02+wsj04）
    block_lines = [
        "【填寫範例｜格式示範，非貴司實機值】",
        *[f"{k}={v}" for k, v in kvs],
        "（把 IP／庫名／URL 換成維運提供的實機值後再存檔；同一列須同時有 wsj02 與 wsj04。）",
        "",
    ]
    return "\n".join(block_lines) + body


def wrap_compact_llm(llm_fn, *, num_predict: int | None = None, timeout: float | None = None):
    """緊湊路徑：保留呼叫端 model；能 bind 則鎖 num_predict；一律外包抛光。

    - 若 llm_fn 有 `_augur_bind_options`（ollama.make_llm_fn）→ 合併 num_predict／temperature
    - 否則只抛光（stub／自訂 fn 不重建、不吃錯 model）
    """
    npred = COMPACT_NUM_PREDICT if num_predict is None else int(num_predict)
    inner = llm_fn
    bind = getattr(llm_fn, "_augur_bind_options", None)
    if callable(bind):
        try:
            kw = {}
            if timeout is not None:
                kw["timeout"] = timeout
            inner = bind({"num_predict": npred, "temperature": 0}, **kw)
        except Exception:
            inner = llm_fn

    def fn(prompt: str) -> str:
        return polish_compact_response(inner(prompt))

    return fn


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    from types import SimpleNamespace as S

    chk("readout→compact", should_compact("國碩：請讀出具體內容", readout_meta={"item_ids": [1]}))
    chk("full mode off", should_compact("x", answer_mode="full") is False)
    a = S(item_id=277948, text="a" * 1000)
    b = S(item_id=1, text="noise" * 200)
    fr = freeze_citations([b, a], prefer_item_ids=[277948], max_chars=1500, max_n=2)
    chk("freeze prefer only target", all(c.item_id == 277948 for c in fr) and len(fr) == 1)
    meta = "首先，我需要理解用戶的問題：某某\n真正答案在此。\n"
    chk("strip meta", strip_meta_reasoning(meta).startswith("真正答案"))
    echo = (
        "首先，我需要根據使用者問題來回答。禁止開場想題。\n"
        "從引文[1]：國碩科技 DR演練記錄重點在災難還原。\n"
    )
    chk("strip instruction echo", "國碩" in polish_compact_response(echo) and "禁止開場" not in polish_compact_response(echo))
    chk("polish strips quotes", "甲" in polish_compact_response("「甲」") and "「" not in polish_compact_response("「甲」"))
    calls = []

    def stub(p):
        calls.append(p)
        return "「步」驟"

    wrapped = wrap_compact_llm(stub)
    out = wrapped("prompt-x")
    chk("wrap 保留呼叫端 llm_fn", calls == ["prompt-x"] and out == "步驟")
    live_leak = (
        "- [1]：確認 R6 規格與網路。\n"
        "- [2]：AIX 以 SAS Tape 還原。\n"
        "\n"
        "我需要從這些內容中提取具體的操作步驟。\n"
        "關鍵是：只列引文裡有的東西。\n"
    )
    pol = polish_compact_response(live_leak)
    chk("polish 中段想題截斷", "我需要" not in pol and "關鍵是" not in pol)
    chk("polish 點列→編號", pol.startswith("1.") and "2." in pol)
    fill_cite = S(
        item_id=1956038,
        item_title="EasyFlow整合站台設定-填寫範例-wsj_file.md",
        text=(
            "wsj02=10.1.2.30\nwsj04=EFGP_PROD\n"
            "| **wsj03** | x | `http://10.1.2.30:8080/efgp/services/SOAP` |"
        ),
    )
    bad_ans = (
        "1. 打開 EasyFlow 整合站台設定檔\n"
        "2. 找到欄位 wsj02 並修改其值為目標 IP 位址\n"
        "3. 保存設定檔後重新啟動 EasyFlow 服務\n"
    )
    fixed = ensure_fill_kv_in_response(bad_ans, "wsj02如何填寫", [fill_cite])
    chk(
        "fill 機器閘注入",
        fixed.startswith("【填寫範例")
        and "wsj02=10.1.2.30" in fixed
        and "wsj04=EFGP_PROD" in fixed
        and "目標 IP" in fixed,
    )
    chk(
        "fill 已有 kv 不重複注入",
        ensure_fill_kv_in_response(
            "1. 設 wsj02=10.1.2.30\n", "wsj02如何填寫", [fill_cite],
        ).startswith("1."),
    )
    nok = ensure_fill_kv_in_response("知識庫中無此內容", "wsj02如何填寫?", [fill_cite])
    chk(
        "fill 誤吐無內容句→改注入",
        "wsj02=10.1.2.30" in nok and "知識庫中無此內容" not in nok,
    )
    kvs = extract_fill_kvs_from_citations([fill_cite])
    chk("fill 自引文抽 kv", ("wsj02", "10.1.2.30") in kvs and ("wsj04", "EFGP_PROD") in kvs)
    from augur.llm.ollama import make_llm_fn
    base_fn = make_llm_fn(model="qwen3:4b", think=False, options={"num_predict": 900})
    chk("ollama fn 可 bind", callable(getattr(base_fn, "_augur_bind_options", None)))
    bound = base_fn._augur_bind_options({"num_predict": 480})
    chk("bind 保留 model", getattr(bound, "_augur_model", None) == "qwen3:4b")
    # ensure_* / extract_* 已於上方 fill 閘測用（同模組）
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

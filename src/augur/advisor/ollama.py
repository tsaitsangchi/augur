"""N5 Ollama llm_fn adapter — 本地 Ollama HTTP → advise() 抽象 LLM 界面的薄接頭。

🎯 make_llm_fn() 回 prompt(str)->response(str),接 advise(llm_fn=...)(advise.py:13 既有界面)。
   model tag / base_url / timeout 皆為操作值(env 或參數覆蓋、不寫死於呼叫端;#27 印 log 不鑄 schema);
   qwen3 `<think>` 段機械剝除(strip_think)於過 guard 閘前執行、思考段永不呈現——
   治 guard 假陽性源;剝除規則屬 P8 閘鏈定義之一環(計畫 §3-S7 N5)。
   重試僅限連線層錯誤且次數有界(見訊號即停、不重試風暴,#24 精神);逾時屬預期
   (qwen3:8b 於 4GB GPU 必部分 CPU offload、單回合可達分鐘級,計畫定錨 #16)→ 錯得大聲不硬衝。
守 #1(只轉發 LLM 原輸出、零改寫——剝 <think> 為機械規則非潤飾)· #15(失敗明說不佯稱)·
   #18(ollama=領域名詞)· 計畫 §6 SOP-C(換 LLM=改設定一行,本檔可整支替換)。
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "http://localhost:11434"   # 操作值:OLLAMA_BASE_URL env 覆蓋
DEFAULT_MODEL = "qwen3:8b"                    # 操作值:OLLAMA_MODEL env / make_llm_fn(model=) 覆蓋,不寫死
DEFAULT_TIMEOUT = 300.0                       # 秒;操作值:OLLAMA_TIMEOUT env 覆蓋(弱 GPU 分鐘級屬預期)

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
_QUOTE_MARKS = str.maketrans({"「": "", "」": "", "『": "", "』": "", "“": "", "”": ""})


def strip_quote_marks(text):
    """R2 架構機械正規化(2026-07-04):剝除模型輸出的引號框(「」『』"")。

    設計依據=模型(qwen3:8b)對名典有強記憶、反射性引用自己背的版本,與公版原文有標點/字差
    → 逐字閘必攔、整段解讀被打掉(實測)。R2 定調:**模型不從事逐字引用**(它做不到精準照抄),
    逐字原文改由系統 citations 逐字提供(oai_compat._citations_block,本即檢索原文=零幻像)。
    剝框後模型文字=純白話評論、不再宣稱 verbatim → guard ①(引文逐字)無可攔;而 guard ②③④
    (數字白名單/未來洩漏/逆向翻轉)仍作用於評論文本 → 數字與行動安全不受影響。與 strip_think 同層。"""
    return (text or "").translate(_QUOTE_MARKS)


def strip_think(text):
    """qwen3 <think> 思考段機械剝除(P8 閘鏈一環):閉合段全刪;
    未閉合(輸出截斷)→ 自 <think> 起全刪(fail-closed,寧空勿漏思考段入閘/入眼)。"""
    out = _THINK.sub("", text or "")
    cut = out.find("<think>")
    if cut != -1:
        out = out[:cut]
    return out.strip()


def base_url():
    """Ollama 端點(操作值):OLLAMA_BASE_URL env,預設 localhost:11434。"""
    return os.environ.get("OLLAMA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def make_llm_fn(model=None, base=None, timeout=None, retries=1, options=None, think=None, strip_quotes=False):
    """組一個 prompt(str)->response(str) 的 llm_fn(advise() 唯一需要的界面)。

    model:   Ollama model tag(預設 OLLAMA_MODEL env → 'qwen3:8b';操作值不寫死)
    base:    端點(預設 base_url())
    timeout: 單次呼叫秒數(預設 OLLAMA_TIMEOUT env → 300)
    retries: 連線層錯誤(connection refused 等)之有界重試次數;HTTP 4xx/5xx 與逾時不重試(不風暴)
    options: dict,原樣傳 Ollama options(如 {'temperature': 0, 'num_predict': 800})
    think:   qwen3 thinking 模式(False=關,不生成 <think> 推理段→弱 GPU 上大幅提速;None=不指定用模型預設)
    strip_quotes: True=剝除輸出引號框(R2 架構:模型不逐字引用、引用由系統 citations 負責,見 strip_quote_marks)
    回傳之 llm_fn 已含 <think> 機械剝除;失敗 raise RuntimeError(錯得大聲,#15)。
    """
    tag = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    url = (base or base_url()) + "/api/generate"
    limit = float(timeout if timeout is not None else os.environ.get("OLLAMA_TIMEOUT", DEFAULT_TIMEOUT))

    def llm_fn(prompt):
        body = {"model": tag, "prompt": prompt, "stream": False}
        if think is not None:
            body["think"] = think
        if options:
            body["options"] = dict(options)
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        last_err = None
        for attempt in range(retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=limit) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                out = strip_think(data.get("response", ""))
                return strip_quote_marks(out) if strip_quotes else out
            except urllib.error.HTTPError as e:            # 服務端有回應 → 不重試(非連線層)
                raise RuntimeError(f"Ollama HTTP {e.code} @ {url} model={tag}: {e.read()[:200]!r}") from e
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                if isinstance(getattr(e, "reason", None), TimeoutError) or isinstance(e, TimeoutError):
                    raise RuntimeError(
                        f"Ollama 逾時(>{limit:.0f}s)@ {url} model={tag};弱 GPU 分鐘級屬預期,"
                        f"調 OLLAMA_TIMEOUT 或換更小 model(SOP-C)") from e
                last_err = e
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))        # 有界短退避,僅連線層
        raise RuntimeError(f"Ollama 連線失敗 @ {url} model={tag}: {last_err}") from last_err

    return llm_fn

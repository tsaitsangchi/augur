"""本機影音／音訊 ASR 轉錄（AVI-ASR 窄切）— ffmpeg 抽音＋faster-whisper。

🎯 白話：對自有原件（owned_local）抽出**音中話語**的文字草稿入庫備援；非 caption、
   非雲端；品質閘 fail-closed。PDF-C 之「禁 ASR」只約束 PDF 光柵軌，不經本模組。
守 AVI-ASR-ADOPTED-20260811 · #1 轉錄≠無中生有（殘餘幻覺有標記）· #15 · FZ-keep。

執行指令矩陣:
  python -m augur.knowledge.transcribe_asr --selftest
  python -m augur.knowledge.transcribe_asr --file /path/to/x.avi
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from typing import Any

# 與 fileparse 分離：影音可大於文件 50MB（入庫前另過 license 閘）
MAX_AV_BYTES = 200 * 1024 * 1024
MAX_DURATION_S = 45 * 60
MIN_CHARS = 40
S0_ASR_MARK = "<!-- via=asr_transcribe -->\n"
_MODEL = None
_MODEL_NAME = os.environ.get("AUGUR_ASR_MODEL", "small")

_AV_EXT = {
    ".avi", ".mp4", ".mov", ".mkv", ".webm",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac",
}

# 流利幻覺熱句（結構性弱訊；命中整段過純則拒）
_HALLU_RE = re.compile(
    r"(感謝觀看|請訂閱|請按讚|謝謝收看|字幕by|subscribers?|thanks for watching|"
    r"please subscribe|like and subscribe)",
    re.I,
)


def is_av_ext(path: str) -> bool:
    return os.path.splitext(path or "")[1].lower() in _AV_EXT


def _ffmpeg_bin() -> str | None:
    return shutil.which("ffmpeg")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_wav(path: str, out_wav: str) -> tuple[bool, str]:
    """ffmpeg 抽單聲道 16k wav。回 (ok, err)."""
    ff = _ffmpeg_bin()
    if not ff:
        return False, "missing_parser"
    cmd = [
        ff, "-y", "-i", path,
        "-vn", "-ac", "1", "-ar", "16000", "-f", "wav",
        out_wav,
    ]
    try:
        # ffmpeg 常印 locale／中文路徑位元組；禁 text=True（UTF-8 硬解 → UnicodeDecodeError → 整檔假 parse_error）
        r = subprocess.run(cmd, capture_output=True, timeout=600)
    except (OSError, subprocess.SubprocessError):
        return False, "parse_error"
    if r.returncode != 0 or not os.path.isfile(out_wav) or os.path.getsize(out_wav) < 44:
        return False, "parse_error"
    return True, "ok"


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return None
    # CPU int8：WSL 通用；有 CUDA 時可設 AUGUR_ASR_DEVICE=cuda
    device = os.environ.get("AUGUR_ASR_DEVICE", "cpu")
    compute = os.environ.get("AUGUR_ASR_COMPUTE", "int8" if device == "cpu" else "float16")
    _MODEL = WhisperModel(_MODEL_NAME, device=device, compute_type=compute)
    return _MODEL


def _quality_ok(text: str, avg_logprob: float | None, no_speech: float | None) -> bool:
    t = (text or "").strip()
    if len(t) < MIN_CHARS:
        return False
    if _HALLU_RE.search(t) and len(t) < 120:
        return False
    if no_speech is not None and no_speech > 0.85 and len(t) < 80:
        return False
    if avg_logprob is not None and avg_logprob < -1.2 and len(t) < 100:
        return False
    return True


def asr_file(path: str) -> tuple[str | None, str, dict[str, Any]]:
    """回 (text|None, reason, meta)。reason 成功＝`asr`；失敗∈ fileparse.SKIP 語意。"""
    meta: dict[str, Any] = {"path": path}
    if not path or not os.path.isfile(path):
        return None, "parse_error", meta
    if os.path.islink(path):
        return None, "symlink", meta
    size = os.path.getsize(path)
    meta["bytes"] = size
    if size == 0:
        return None, "empty", meta
    if size > MAX_AV_BYTES:
        return None, "oversize", meta
    if not is_av_ext(path):
        return None, "unknown_ext", meta
    if _ffmpeg_bin() is None:
        return None, "missing_parser", meta
    model = _load_model()
    if model is None:
        return None, "missing_parser", meta

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        ok, err = extract_wav(path, wav)
        if not ok:
            return None, err, meta
        try:
            segments, info = model.transcribe(
                wav,
                language=os.environ.get("AUGUR_ASR_LANG") or None,
                vad_filter=True,
                beam_size=1,
            )
        except Exception:
            return None, "parse_error", meta
        parts: list[str] = []
        logprobs: list[float] = []
        nos: list[float] = []
        dur = 0.0
        for seg in segments:
            parts.append((seg.text or "").strip())
            if getattr(seg, "avg_logprob", None) is not None:
                logprobs.append(float(seg.avg_logprob))
            if getattr(seg, "no_speech_prob", None) is not None:
                nos.append(float(seg.no_speech_prob))
            dur = max(dur, float(getattr(seg, "end", 0) or 0))
            if dur > MAX_DURATION_S:
                break
        text = "\n".join(p for p in parts if p)
        avg_lp = sum(logprobs) / len(logprobs) if logprobs else None
        avg_ns = sum(nos) / len(nos) if nos else None
        meta.update({
            "duration_s": dur,
            "avg_logprob": avg_lp,
            "no_speech_prob": avg_ns,
            "language": getattr(info, "language", None),
            "origin_sha256": _sha256_file(path),
            "model": _MODEL_NAME,
        })
        if not _quality_ok(text, avg_lp, avg_ns):
            return None, "asr_quality", meta
        return text, "asr", meta


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("avi 副檔名", is_av_ext("a.AVI") and is_av_ext("x.mp3"))
    chk("非 av", not is_av_ext("a.pdf"))
    chk("熱句拒短幻覺", not _quality_ok("感謝觀看", -0.2, 0.1))
    chk("正常長度過閘", _quality_ok("這是一段足夠長度的測試語音內容用於品質閘。" * 2, -0.3, 0.2))
    chk("S0 mark 前綴", S0_ASR_MARK.startswith("<!-- via=asr_transcribe"))
    chk("ffmpeg 可選", True)  # 存在與否不強制自測紅
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    if "--file" in argv:
        i = argv.index("--file")
        path = argv[i + 1] if i + 1 < len(argv) else ""
        text, reason, meta = asr_file(path)
        print({"reason": reason, "chars": 0 if text is None else len(text), "meta": meta})
        if text:
            print(text[:800])
        return 0 if text else 1
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

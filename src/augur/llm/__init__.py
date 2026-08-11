"""跨包 LLM 適配（Ollama）— 供 advisor／deliberation／knowledge 共用，不含諮詢編排。"""

__all__ = ["ollama"]


def __getattr__(name: str):
    if name == "ollama":
        from augur.llm import ollama as _m

        return _m
    raise AttributeError(name)

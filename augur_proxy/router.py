"""FastAPI router — cache-first, then auto-switch local vs Claude."""
from __future__ import annotations

from typing import Literal, Optional

from . import cache, classifier, claude_cli, local_llm, logger

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - optional until deps installed
    raise ImportError(
        "MCP router requires fastapi and pydantic. "
        "Install with: pip install -r requirements-mcp.txt"
    ) from exc

app = FastAPI(title="Augur MCP Router", version="0.1.0")


class InvokeRequest(BaseModel):
    prompt: str = Field(min_length=1)
    type: Optional[Literal["quick", "static", "compliance", "audit"]] = None


class InvokeResponse(BaseModel):
    response: str
    backend: str
    tokens: int
    cache_hit: bool
    type: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/invoke", response_model=InvokeResponse)
def invoke(body: InvokeRequest) -> InvokeResponse:
    req_type = body.type or classifier.classify(body.prompt)

    if req_type == "static":
        cached = cache.get(body.prompt, req_type)
        if cached is not None:
            logger.log_request(
                req_type=req_type,
                prompt=body.prompt,
                backend="cache",
                tokens=0,
                cache_hit=True,
            )
            return InvokeResponse(
                response=cached,
                backend="cache",
                tokens=0,
                cache_hit=True,
                type=req_type,
            )
        response = f"(static miss) No cached entry for: {body.prompt[:80]}"
        cache.set(body.prompt, req_type, response)
        logger.log_request(
            req_type=req_type,
            prompt=body.prompt,
            backend="cache",
            tokens=0,
            cache_hit=False,
        )
        return InvokeResponse(
            response=response,
            backend="cache",
            tokens=0,
            cache_hit=False,
            type=req_type,
        )

    cached = cache.get(body.prompt, req_type)
    if cached is not None:
        logger.log_request(
            req_type=req_type,
            prompt=body.prompt,
            backend="cache",
            tokens=0,
            cache_hit=True,
        )
        return InvokeResponse(
            response=cached,
            backend="cache",
            tokens=0,
            cache_hit=True,
            type=req_type,
        )

    backend = classifier.backend_for(req_type)
    if backend == "local":
        response, tokens = local_llm.ask(body.prompt)
    else:
        response, tokens = claude_cli.ask(body.prompt)

    cache.set(body.prompt, req_type, response)
    logger.log_request(
        req_type=req_type,
        prompt=body.prompt,
        backend=backend,
        tokens=tokens,
        cache_hit=False,
    )
    return InvokeResponse(
        response=response,
        backend=backend,
        tokens=tokens,
        cache_hit=False,
        type=req_type,
    )


@app.post("/cache/flush")
def flush_cache() -> dict:
    removed = cache.flush()
    return {"flushed": removed}

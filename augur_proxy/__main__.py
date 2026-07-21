"""Run MCP router: python -m augur_proxy [--port PORT]"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Augur MCP Router")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "uvicorn required. Install with: pip install -r requirements-mcp.txt"
        ) from exc

    uvicorn.run("mcp.router:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()

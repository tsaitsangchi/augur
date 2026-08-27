#!/usr/bin/env python3
"""🎯 把報告 PDF 發到 Cursor Cloud 可下載面（/opt/cursor/artifacts）。

白話：git 的 reports/*.pdf 在 Cursor 網頁沒有下載鈕。本支把 PDF（及同名 HTML）
複製到 Cloud artifacts，可選渲 PNG 預覽與 zip，並印出路徑給 PR／回覆使用。
守原則 #16 #18 #29 #35。零外部 API。

執行指令矩陣：
  python3 scripts/publish_downloadable_pdf.py
      # 掃 reports/**/*.pdf → 能發布就發布；無 artifacts 目錄則說明後備
  python3 scripts/publish_downloadable_pdf.py --path reports/foo.pdf
  python3 scripts/publish_downloadable_pdf.py --path foo.pdf --dest /tmp/out --no-preview
  python3 scripts/publish_downloadable_pdf.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
CLOUD_ARTIFACTS = Path("/opt/cursor/artifacts")
MINIMAL_PDF = (
    b"%PDF-1.1\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 72 72]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def default_dest() -> Path | None:
    if CLOUD_ARTIFACTS.is_dir():
        return CLOUD_ARTIFACTS
    return None


def discover_report_pdfs(root: Path) -> list[Path]:
    reports = root / "reports"
    if not reports.is_dir():
        return []
    return sorted(p for p in reports.rglob("*.pdf") if p.is_file())


def assert_published(src: Path, dest_dir: Path) -> None:
    """下游絆線：發布若沒發生，這條必炸（不拆複製步驟去測）。"""
    dest = dest_dir / src.name
    if not dest.is_file():
        raise FileNotFoundError(f"未發布：{dest}")
    if sha256_file(src) != sha256_file(dest):
        raise ValueError(f"發布後內容不一致：{src} vs {dest}")


def _render_pngs(src: Path, dest_dir: Path, stem: str) -> list[Path]:
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return []
    out: list[Path] = []
    pdf = pdfium.PdfDocument(str(src))
    try:
        n = len(pdf)
        for i in range(n):
            pil = pdf[i].render(scale=1.4).to_pil()
            p = dest_dir / f"{stem}_p{i + 1:02d}.png"
            pil.save(p)
            out.append(p)
    finally:
        pdf.close()
    return out


def publish_one(
    src: Path,
    dest_dir: Path,
    *,
    make_zip: bool = True,
    preview: bool = True,
) -> dict:
    if not src.is_file():
        raise FileNotFoundError(src)
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"不是 PDF：{src}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_pdf = dest_dir / src.name
    shutil.copy2(src, dest_pdf)
    html_src = src.with_suffix(".html")
    dest_html = None
    if html_src.is_file():
        dest_html = dest_dir / html_src.name
        shutil.copy2(html_src, dest_html)
    pngs: list[Path] = []
    if preview:
        pngs = _render_pngs(src, dest_dir, src.stem)
    zip_path = None
    if make_zip:
        zip_path = dest_dir / f"{src.stem}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(dest_pdf, dest_pdf.name)
            if dest_html is not None:
                zf.write(dest_html, dest_html.name)
    assert_published(src, dest_dir)
    return {
        "src": str(src),
        "pdf": str(dest_pdf),
        "html": None if dest_html is None else str(dest_html),
        "zip": None if zip_path is None else str(zip_path),
        "pngs": [str(p) for p in pngs],
        "sha256": sha256_file(dest_pdf),
    }


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "sample.pdf"
        src.write_bytes(MINIMAL_PDF)
        dest = root / "artifacts"
        # 先驗紅：尚未複製時絆線必須炸
        red = False
        try:
            assert_published(src, dest)
        except FileNotFoundError:
            red = True
        chk("未發布時 assert_published 必紅（#35 先驗紅）", red)

        info = publish_one(src, dest, make_zip=True, preview=False)
        chk("發布後 PDF 存在", Path(info["pdf"]).is_file())
        chk("sha256 與來源相同", info["sha256"] == sha256_file(src))
        chk("zip 含 PDF", Path(info["zip"]).is_file() and zipfile.is_zipfile(info["zip"]))
        # 下游絆線在 publish_one 末已跑過；再餵被改壞的複本應紅
        Path(info["pdf"]).write_bytes(MINIMAL_PDF + b"\n%tamper\n")
        mismatch = False
        try:
            assert_published(src, dest)
        except ValueError:
            mismatch = True
        chk("內容被改後 assert_published 必紅", mismatch)

        dest2 = root / "out2"
        html = src.with_suffix(".html")
        html.write_text("<html>ok</html>", encoding="utf-8")
        info2 = publish_one(src, dest2, make_zip=True, preview=False)
        chk("旁路 HTML 一併複製", info2["html"] is not None and Path(info2["html"]).is_file())

        missing_ok = False
        try:
            publish_one(root / "nope.pdf", dest, preview=False)
        except FileNotFoundError:
            missing_ok = True
        chk("來源不存在則 FileNotFoundError", missing_ok)

        txt = root / "n.pdf.txt"
        txt.write_text("x", encoding="utf-8")
        bad_ext = False
        try:
            publish_one(txt, dest, preview=False)
        except ValueError:
            bad_ext = True
        chk("非 PDF 副檔名拒絕", bad_ext)

        chk("discover 只收 .pdf", discover_report_pdfs(root) == [])
        reports = root / "reports"
        reports.mkdir()
        (reports / "a.pdf").write_bytes(MINIMAL_PDF)
        (reports / "b.md").write_text("no", encoding="utf-8")
        found = discover_report_pdfs(root)
        chk("discover 找到 reports 下 pdf", [p.name for p in found] == ["a.pdf"])

    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="發布 PDF 到 Cloud artifacts 下載面")
    ap.add_argument("--path", action="append", default=[], help="指定 PDF（可重複）；省略則掃 reports/")
    ap.add_argument("--dest", default=None, help="覆蓋目的目錄（測試／本機）")
    ap.add_argument("--no-preview", action="store_true", help="不渲 PNG")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    dest = Path(args.dest).resolve() if args.dest else default_dest()
    paths = [Path(p).resolve() for p in args.path]
    if not paths:
        paths = discover_report_pdfs(REPO)
        if not paths:
            print("用途：把 reports/*.pdf 複製到 Cursor Cloud /opt/cursor/artifacts 供下載")
            print("執行指令矩陣見檔頭。目前 reports/ 沒有 PDF。")
            return 0

    if dest is None:
        print("本環境沒有 /opt/cursor/artifacts（非 Cloud Agent）。")
        print("後備：git 內檔案請用 GitHub raw URL 另存，例如")
        for p in paths:
            rel = p.relative_to(REPO) if REPO in p.parents or p.parent == REPO else p
            print(f"  https://github.com/<org>/<repo>/raw/<branch>/{rel}")
        return 0

    results = []
    for p in paths:
        info = publish_one(
            p, dest, make_zip=not args.no_zip, preview=not args.no_preview
        )
        results.append(info)
        if not args.json:
            print(f"published {info['pdf']}")
            if info["html"]:
                print(f"  html {info['html']}")
            if info["zip"]:
                print(f"  zip  {info['zip']}")
            for png in info["pngs"]:
                print(f"  png  {png}")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

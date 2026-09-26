#!/usr/bin/env python
"""网页转 Markdown 工具。"""

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import html2text
import requests
from readability import Document

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; web-to-markdown/1.0)"}


def fetch(url: str, timeout: int) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def to_markdown(html: str, url: str) -> tuple[str, str]:
    doc = Document(html)
    title = doc.short_title() or urlparse(url).netloc
    content_html = doc.summary(html_partial=True)

    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    md = h.handle(content_html)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, md


def safe_name(title: str) -> str:
    name = re.sub(r"[^\w\u4e00-\u9fa5-]+", "_", title).strip("_")
    return (name[:60] or "untitled") + ".md"


def convert(url: str, args, out_path: Path | None = None) -> bool:
    try:
        html = fetch(url, args.timeout)
        title, md = to_markdown(html, url)
    except Exception as exc:
        print(f"[失败] {url}: {exc}")
        return False

    body = f"# {title}\n\n> 来源: {url}\n\n{md}\n" if args.with_title else f"{md}\n"
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body, encoding="utf-8")
        print(f"[成功] {url} -> {out_path}")
    else:
        print(body)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="网页转 Markdown")
    parser.add_argument("url", nargs="?", help="网页 URL")
    parser.add_argument("-o", "--output", help="输出文件")
    parser.add_argument("--batch", help="URL 列表文件")
    parser.add_argument("--out-dir", help="批量输出目录")
    parser.add_argument("--with-title", action="store_true")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    if args.batch:
        urls = [u.strip() for u in Path(args.batch).read_text(encoding="utf-8").splitlines() if u.strip()]
        out_dir = Path(args.out_dir or "notes")
        ok = 0
        for i, url in enumerate(urls):
            if i:
                time.sleep(args.delay)
            try:
                html = fetch(url, args.timeout)
                title, md = to_markdown(html, url)
            except Exception as exc:
                print(f"[失败] {url}: {exc}")
                continue
            target = out_dir / safe_name(title)
            target.write_text(f"# {title}\n\n> 来源: {url}\n\n{md}\n", encoding="utf-8")
            print(f"[成功] {url} -> {target}")
            ok += 1
        print(f"\n完成 {ok}/{len(urls)}")
        return 0

    if not args.url:
        parser.print_help()
        return 1

    out = Path(args.output) if args.output else None
    return 0 if convert(args.url, args, out) else 1


if __name__ == "__main__":
    raise SystemExit(main())
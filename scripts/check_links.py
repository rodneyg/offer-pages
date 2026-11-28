#!/usr/bin/env python3
"""Fail when site anchors use placeholders or nonlocal, non-HTTPS targets."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href is not None:
                self.hrefs.append(href.strip())


def check_site(root: Path) -> list[str]:
    errors: list[str] = []
    files = sorted(root.rglob("*.html"))
    for page in files:
        parser = AnchorParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.hrefs:
            parsed = urlparse(href)
            if href.startswith("PAYLINK_"):
                errors.append(f"{page.relative_to(root)}: placeholder href {href}")
            elif parsed.scheme in {"mailto", "tel"}:
                continue
            elif parsed.scheme or parsed.netloc:
                if parsed.scheme != "https" or not parsed.netloc:
                    errors.append(f"{page.relative_to(root)}: href is not HTTPS: {href}")
            elif href.startswith(("#", "mailto:", "tel:")):
                continue
            else:
                target = (page.parent / parsed.path).resolve()
                if not target.is_relative_to(root.resolve()) or not target.exists():
                    errors.append(f"{page.relative_to(root)}: missing local href {href}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_site(args.root.resolve())
    if errors:
        print("Link check failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Link check passed for {len(list(args.root.rglob('*.html')))} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

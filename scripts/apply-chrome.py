#!/usr/bin/env python3
"""Stamp shared header/footer partials into every page.

Edit partials/header.html and partials/footer.html, then run:

    python3 scripts/apply-chrome.py

The stamped HTML is what GitHub Pages publishes from the repository root.
"""
from __future__ import annotations

from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
from root_urls import root_local_urls  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERVICE_PAGES = {
    "services.html",
    "consulting.html",
    "managed.html",
    "specialized.html",
    "verified.html",
}

HEADER_RE = re.compile(
    r"(?:<!-- include:header -->\s*)?"
    r"<a class=\"skip\".*?</header>"
    r"(?:\s*<!-- /include:header -->)?"
    r"\s*",
    re.S,
)
FOOTER_RE = re.compile(
    r"(?:<!-- include:footer -->\s*)?"
    r"<footer\b.*?</footer>"
    r"(?:\s*<!-- /include:footer -->)?"
    r"\s*",
    re.S,
)


def header_for(page: str, raw: str) -> str:
    # Normalize before matching so a relative partial cannot be stamped back
    # onto 404.html, where the browser URL is the missing path.
    html = root_local_urls(raw)
    if page == "index.html":
        html = html.replace(
            '<a href="/index.html">Home</a>',
            '<a href="/index.html" class="is-active">Home</a>',
            1,
        )
    elif page in SERVICE_PAGES:
        html = html.replace('<div class="has-sub">', '<div class="has-sub is-active">', 1)
        html = html.replace(
            f'<a href="/{page}">',
            f'<a href="/{page}" class="is-active">',
            1,
        )
    else:
        for slug, label in (
            ("careers.html", "Careers"),
            ("faq.html", "FAQ"),
            ("privacy.html", "Privacy"),
        ):
            if page == slug:
                html = html.replace(
                    f'<a href="/{slug}">{label}</a>',
                    f'<a href="/{slug}" class="is-active">{label}</a>',
                    1,
                )
                break
    return html.rstrip() + "\n"


def apply(page_path: Path, header: str, footer: str) -> None:
    text = page_path.read_text()
    h = header_for(page_path.name, header)
    text, n1 = HEADER_RE.subn(h, text, count=1)
    text, n2 = FOOTER_RE.subn(root_local_urls(footer).rstrip() + "\n", text, count=1)
    if n1 != 1 or n2 != 1:
        raise SystemExit(f"{page_path.name}: header={n1} footer={n2}")
    # 404.html is also returned for /old/service/, so its own recovery links
    # have to be root-absolute too, not only the shared chrome.
    page_path.write_text(root_local_urls(text))


def main() -> None:
    header = (ROOT / "partials/header.html").read_text()
    footer = (ROOT / "partials/footer.html").read_text()
    pages = sorted(p for p in ROOT.glob("*.html") if p.is_file())
    for page in pages:
        apply(page, header, footer)
        print("updated", page.name)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stamp canonical, share, and icon tags, and write sitemap.xml.

Titles and descriptions stay in each HTML file. This script copies them into
the Open Graph and Twitter tags so those cannot drift.

    python3 scripts/apply-meta.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_pages import INDEXABLE, PAGES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
META_RE = re.compile(r"\n*<!-- include:meta -->.*?<!-- /include:meta -->\n*", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)">', re.S)
OLD_ICONS = (
    '  <link rel="icon" href="images/logo-mark.png" type="image/png">\n',
    '  <link rel="apple-touch-icon" href="images/logo-mark.png">\n',
)
ANALYTICS = (
    '  <script src="js/analytics-config.js"></script>\n'
    '  <script src="js/analytics.js"></script>\n'
)


def attr(value: str) -> str:
    return html.escape(html.unescape(value.strip()), quote=True)


def block(page: str, title: str, description: str) -> str:
    url = PAGES[page]
    robots = "noindex" if page == "404.html" else "index,follow"
    title_attr = attr(title)
    desc_attr = attr(description)
    image = "https://ngxconsultants.com/images/og-image.png"
    lines = [
        "<!-- include:meta -->",
        f'  <link rel="canonical" href="{url}">',
        f'  <meta name="robots" content="{robots}">',
        '  <meta property="og:type" content="website">',
        '  <meta property="og:site_name" content="NGX Consultants">',
        f'  <meta property="og:title" content="{title_attr}">',
        f'  <meta property="og:description" content="{desc_attr}">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:image" content="{image}">',
        '  <meta property="og:image:type" content="image/png">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        '  <meta property="og:image:alt" content="NGX Consultants">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{title_attr}">',
        f'  <meta name="twitter:description" content="{desc_attr}">',
        f'  <meta name="twitter:image" content="{image}">',
        '  <meta name="twitter:image:alt" content="NGX Consultants">',
        '  <link rel="icon" href="favicon.ico" sizes="any">',
        '  <link rel="icon" href="favicon-32x32.png" type="image/png" sizes="32x32">',
        '  <link rel="icon" href="favicon-16x16.png" type="image/png" sizes="16x16">',
        '  <link rel="apple-touch-icon" href="apple-touch-icon.png" sizes="180x180">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <meta name="theme-color" content="#021946">',
        "<!-- /include:meta -->",
    ]
    return "\n".join(lines) + "\n"


def write_sitemap() -> None:
    urls = "\n".join(
        f"  <url><loc>{PAGES[name]}</loc></url>" for name in INDEXABLE
    )
    text = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(text)
    print("wrote sitemap.xml")


def apply(page: Path) -> None:
    text = page.read_text()
    title_match = TITLE_RE.search(text)
    desc_match = DESC_RE.search(text)
    if not title_match or not desc_match:
        raise SystemExit(f"{page.name}: missing title or description")
    text = META_RE.sub("\n", text)
    for old in OLD_ICONS:
        text = text.replace(old, "")
    stamped = block(page.name, title_match.group(1), desc_match.group(1))
    text, count = DESC_RE.subn(
        lambda match: match.group(0) + "\n" + stamped,
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"{page.name}: could not insert meta")
    text = re.sub(r"css/styles\.css\?v=\d+", "css/styles.css?v=8", text)
    text = text.replace(ANALYTICS, "")
    if "</body>" not in text:
        raise SystemExit(f"{page.name}: missing body close")
    text = text.replace("</body>", ANALYTICS + "</body>", 1)
    page.write_text(text)
    print("updated", page.name)


def main() -> None:
    pages = sorted(p for p in ROOT.glob("*.html") if p.is_file())
    names = {p.name for p in pages}
    if names != set(PAGES):
        raise SystemExit(f"HTML set {sorted(names)} != {sorted(PAGES)}")
    for page in pages:
        apply(page)
    write_sitemap()


if __name__ == "__main__":
    main()

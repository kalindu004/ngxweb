#!/usr/bin/env python3
"""Check the twelve site practices and the related markup.

    python3 scripts/check-site.py
"""

from __future__ import annotations

from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
import re
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preview  # noqa: E402
from site_pages import INDEXABLE, ORIGIN, PAGES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
BOOKING = (
    "https://bookings.cloud.microsoft/book/"
    "ConsultingIntroductionSession@ngxconsultants.com/s/-zpdRLckyk-PT0Z-2DEPkA2"
)
FAILURES: list[str] = []


def fail(message: str) -> None:
    FAILURES.append(message)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.images: list[tuple[dict[str, str], dict[str, str] | None]] = []
        self.links: list[dict[str, str]] = []
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean = {key: value or "" for key, value in attrs}
        if tag == "img":
            ancestor = next(
                (item for item in reversed(self.stack) if item[0] == "a"),
                None,
            )
            self.images.append((clean, None if ancestor is None else ancestor[1]))
        if tag == "a":
            self.links.append(clean)
        if tag in {"script", "img", "link"} and clean.get("src"):
            self.sources.append(clean["src"])
        if tag == "link" and clean.get("href"):
            self.sources.append(clean["href"])
        self.stack.append((tag, clean))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def read(name: str) -> str:
    return (ROOT / name).read_text()


def local_path(url: str) -> str | None:
    if url.startswith(("mailto:", "tel:", "http://", "https://", "//", "data:")):
        return None
    path = url.split("#", 1)[0].split("?", 1)[0]
    return path or None


def meta(text: str, name: str) -> str | None:
    match = re.search(
        rf'<meta name="{re.escape(name)}" content="(.*?)">',
        text,
        re.S,
    )
    return match.group(1) if match else None


def prop(text: str, name: str) -> str | None:
    match = re.search(
        rf'<meta property="{re.escape(name)}" content="(.*?)">',
        text,
        re.S,
    )
    return match.group(1) if match else None


def check_pages() -> tuple[dict[str, str], dict[str, str]]:
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    html_names = sorted(path.name for path in ROOT.glob("*.html"))
    if html_names != sorted(PAGES):
        fail(f"html files {html_names} do not match site_pages {sorted(PAGES)}")
    for name, canonical in PAGES.items():
        text = read(name)
        title_match = re.search(r"<title>(.*?)</title>", text, re.S)
        description = meta(text, "description")
        if not title_match or not title_match.group(1).strip():
            fail(f"{name}: missing title")
            continue
        if not description or not description.strip():
            fail(f"{name}: missing description")
            continue
        titles[name] = title_match.group(1).strip()
        descriptions[name] = description.strip()
        if f'<link rel="canonical" href="{canonical}">' not in text:
            fail(f"{name}: canonical is not {canonical}")
        if prop(text, "og:title") != titles[name]:
            fail(f"{name}: og:title does not match the title")
        if prop(text, "og:description") != description.strip():
            fail(f"{name}: og:description does not match the description")
        if prop(text, "og:url") != canonical:
            fail(f"{name}: og:url does not match the canonical")
        if prop(text, "og:image") != ORIGIN + "/images/og-image.png":
            fail(f"{name}: missing absolute og:image")
        if 'name="twitter:card" content="summary_large_image"' not in text:
            fail(f"{name}: missing large Twitter card")
        for href in (
            "favicon.ico",
            "favicon-32x32.png",
            "favicon-16x16.png",
            "apple-touch-icon.png",
            "site.webmanifest",
        ):
            if f'href="{href}"' not in text:
                fail(f"{name}: missing {href}")
        expected_robots = "noindex" if name == "404.html" else "index,follow"
        if meta(text, "robots") != expected_robots:
            fail(f"{name}: robots meta is not {expected_robots}")
        if 'class="mobile-cta"' not in text or BOOKING not in text:
            fail(f"{name}: missing the header call to action")
        if "js/analytics-config.js" not in text or "js/analytics.js" not in text:
            fail(f"{name}: analytics scripts are not referenced")
        if "googletagmanager" in text or "gtag(" in text:
            fail(f"{name}: analytics loader must stay in js/analytics.js")
        parser = PageParser()
        parser.feed(text)
        for attrs, anchor in parser.images:
            if "alt" not in attrs:
                fail(f"{name}: image {attrs.get('src')} has no alt attribute")
                continue
            if anchor is not None and not attrs["alt"] and not anchor.get("aria-label"):
                fail(f"{name}: linked image {attrs.get('src')} has an empty alt and no link name")
        for anchor in parser.links:
            href = anchor.get("href", "")
            if anchor.get("target") == "_blank" and "noopener" not in anchor.get("rel", ""):
                fail(f"{name}: {href} uses target=_blank without noopener")
            path = local_path(href)
            if path is not None and not (ROOT / path).exists():
                fail(f"{name}: broken link {href}")
        for source in parser.sources:
            path = local_path(source)
            if path is not None and not (ROOT / path).exists():
                fail(f"{name}: missing file {source}")
    if len(set(titles.values())) != len(titles):
        fail(f"titles are not unique: {titles}")
    if len(set(descriptions.values())) != len(descriptions):
        fail(f"descriptions are not unique: {descriptions}")
    home = read("index.html")
    hero = home.split('id="about"', 1)[0]
    hero_action = hero.split('class="hero-actions"', 1)
    if len(hero_action) < 2 or BOOKING not in hero_action[1][:700]:
        fail("home hero has no call to action above the about section")
    return titles, descriptions


def check_discovery() -> None:
    robots = read("robots.txt")
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        fail("robots.txt does not allow the site")
    if "Disallow: /" in robots:
        fail("robots.txt disallows the whole site")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
        fail("robots.txt sitemap URL is missing")
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [node.text for node in tree.findall("sm:url/sm:loc", NS)]
    expected = [PAGES[name] for name in INDEXABLE]
    if locs != expected:
        fail(f"sitemap locs {locs} != {expected}")
    if any("404" in (loc or "") for loc in locs):
        fail("sitemap includes the 404 page")
    if any(not (loc or "").startswith(ORIGIN + "/") and loc != ORIGIN + "/" for loc in locs):
        fail(f"sitemap has a non-canonical loc: {locs}")


def check_assets() -> None:
    expected = {
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
        "apple-touch-icon.png": (180, 180),
        "images/og-image.png": (1200, 630),
    }
    for name, size in expected.items():
        path = ROOT / name
        if not path.exists():
            fail(f"missing {name}")
            continue
        with Image.open(path) as image:
            if image.size != size:
                fail(f"{name} is {image.size}, expected {size}")
    ico = ROOT / "favicon.ico"
    if not ico.exists() or ico.stat().st_size < 100:
        fail("favicon.ico is missing")
    else:
        with Image.open(ico) as image:
            if image.format != "ICO":
                fail("favicon.ico is not an ICO")
    manifest = read("site.webmanifest")
    if "favicon-32x32.png" not in manifest or "apple-touch-icon.png" not in manifest:
        fail("manifest does not name the icons")


def check_privacy_and_analytics() -> None:
    privacy = read("privacy.html")
    for phrase in (
        "GitHub Pages",
        "Google Fonts",
        "Analytics is not running",
        "admin@ngxconsultants.com",
        "support.ngxconsultants.com",
        "No retention period is stated",
        "No street address is published",
    ):
        if phrase not in privacy:
            fail(f"privacy page is missing {phrase!r}")
    for phrase in (
        "PDPA",
        "Data Protection Officer",
        "100% secure",
        "Private Limited",
        "www.ngxconsultants.com",
    ):
        if phrase in privacy:
            fail(f"privacy page still claims {phrase!r}")
    config = read("js/analytics-config.js")
    if 'provider: ""' not in config or 'measurementId: ""' not in config:
        fail("analytics config is not empty")
    if re.search(r"G-[A-Z0-9]+|GTM-|UA-\d", config):
        fail("analytics config contains an identifier")
    loader = read("js/analytics.js")
    if "googletagmanager.com/gtag/js" not in loader or "if (!provider || !id) return;" not in loader:
        fail("analytics loader is not gated")
    readme = read("README.md")
    if "measurementId" not in readme or "collect nothing" not in readme.lower() and "does not contact" not in readme.lower():
        fail("README does not document the missing analytics setup")
    for path in (ROOT / "js").glob("*.js"):
        text = path.read_text()
        for banned in ("document.cookie", "localStorage", "sessionStorage", "fetch(", "XMLHttpRequest", "setTimeout"):
            if banned in text:
                fail(f"{path.name} contains {banned}")
    widget = read("js/whatsapp-widget.js")
    if 'aria-label", "Chat on WhatsApp"' not in widget and 'aria-label", "Chat on WhatsApp"' not in widget.replace("'", '"'):
        if "Chat on WhatsApp" not in widget or "aria-hidden" not in widget:
            fail("WhatsApp icon is missing an accessible name")
    if "spinner" in read("css/styles.css") or "aria-busy" in read("index.html"):
        fail("a loading spinner was added without an async operation")


def check_identity_files() -> None:
    cname = (ROOT / "CNAME").read_bytes()
    if cname != b"ngxconsultants.com":
        fail(f"CNAME bytes changed: {cname!r}")
    if not (ROOT / ".nojekyll").exists():
        fail(".nojekyll is missing")


def check_custom_404() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), preview.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/missing-page-check", timeout=5)
            fail("missing path returned 200")
        except urllib.error.HTTPError as error:
            body = error.read().decode()
            if error.code != 404:
                fail(f"missing path status is {error.code}")
            if "Page not found" not in body or 'content="noindex"' not in body:
                fail("custom 404 body is not served for an unknown path")
            if "GitHub Pages" in body and "Page not found · GitHub Pages" in body:
                fail("unknown path still uses the default GitHub 404")
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
            if response.status != 200 or b"mobile-cta" not in response.read():
                fail("home page did not serve the mobile call to action")
    finally:
        server.shutdown()


def main() -> None:
    check_pages()
    check_discovery()
    check_assets()
    check_privacy_and_analytics()
    check_identity_files()
    check_custom_404()
    completed = subprocess.run(
        ["node", "tests/analytics.test.mjs"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        fail(completed.stdout + completed.stderr)
    else:
        print(completed.stdout.strip())
    if FAILURES:
        print(f"{len(FAILURES)} failure(s):")
        for item in FAILURES:
            print(" -", item)
        raise SystemExit(1)
    print("checklist:")
    for line in (
        "1 custom 404: pass",
        "2 header and home CTAs: pass",
        "3 unique titles: pass",
        "4 unique descriptions: pass",
        "5 Open Graph image: pass",
        "6 favicon set: pass",
        "7 robots.txt: pass",
        "8 sitemap.xml: pass",
        "9 image alt attributes: pass",
        "10 no fake loading spinner: pass",
        "11 privacy page matches inspected behavior: pass",
        "12 analytics config empty and loader gated: pass",
    ):
        print(line)


if __name__ == "__main__":
    main()

"""Rewrite same-site href/src values to root-absolute paths.

GitHub Pages serves 404.html at the missing URL. A relative href such as
css/styles.css on /old/service/ is requested as /old/service/css/styles.css.
Root-absolute paths stay on the site root from any depth. Fragment, mail,
phone, and already-absolute URLs are left alone. Running this twice is safe.
"""

from __future__ import annotations

import re

ATTR_RE = re.compile(
    r"""(?P<attr>\b(?:href|src)=)(?P<q>["'])(?P<url>[^"']*)(?P=q)"""
)
PASSTHROUGH = ("/", "#", "mailto:", "tel:", "http://", "https://", "//", "data:")


def root_local_urls(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group("url")
        if url == "" or url.startswith(PASSTHROUGH):
            return match.group(0)
        return f"{match.group('attr')}{match.group('q')}/{url}{match.group('q')}"

    return ATTR_RE.sub(replace, text)

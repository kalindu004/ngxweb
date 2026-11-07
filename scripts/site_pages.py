"""Canonical public URLs for the static site. Import this; do not duplicate the list."""

ORIGIN = "https://ngxconsultants.com"

# 404.html is a real file with its own canonical URL, and it is not indexable.
PAGES = {
    "index.html": ORIGIN + "/",
    "services.html": ORIGIN + "/services.html",
    "consulting.html": ORIGIN + "/consulting.html",
    "managed.html": ORIGIN + "/managed.html",
    "specialized.html": ORIGIN + "/specialized.html",
    "verified.html": ORIGIN + "/verified.html",
    "careers.html": ORIGIN + "/careers.html",
    "faq.html": ORIGIN + "/faq.html",
    "privacy.html": ORIGIN + "/privacy.html",
    "404.html": ORIGIN + "/404.html",
}

INDEXABLE = [
    "index.html",
    "services.html",
    "consulting.html",
    "managed.html",
    "specialized.html",
    "verified.html",
    "careers.html",
    "faq.html",
    "privacy.html",
]

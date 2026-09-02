# ngxweb

Static replacement of the WordPress site at [ngxconsultants.com](https://www.ngxconsultants.com).

This tree is a multi-page HTML/CSS/JS site with local images and a WhatsApp widget. It is intended for preview/hosting under `test.ngxconsultants.com` (see `.cpanel.yml`).

**Hosting cutover of www is NOT done.** The live WordPress site remains at www until a separate cutover.

## Pages

- `index.html` — Home
- `services.html` — Services overview
- `consulting.html` — IT & Cybersecurity Consulting
- `managed.html` — NGX Managed IT Services
- `specialized.html` — Specialized Services
- `verified.html` — The NGX-Verified™ Program
- `faq.html` — FAQ
- `careers.html` — Job listings
- `privacy.html` — Privacy policy (PDPA Sri Lanka)

## Notes

- Talk to us / Book a Session open WhatsApp (`wa.me/94768355252`) because the live Book a Session URL is not usable from crawlers.
- Images are stored locally under `images/` (no WordPress hotlinks).
- Optional cPanel Git deployment copies `index.html`, the other HTML files, `css/`, `js/`, and `images/` to `$HOME/test.ngxconsultants.com`.

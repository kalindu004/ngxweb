# ngxweb

Static replacement of the WordPress site at [ngxconsultants.com](https://www.ngxconsultants.com).

Multi-page HTML/CSS/JS with local images and a WhatsApp widget.

**Hosting cutover of www is NOT done.** The live WordPress site remains at www until a separate cutover. This repo is not deployed via cPanel.

## Header and footer

Edit these once, then stamp them into every page:

- `partials/header.html`
- `partials/footer.html`

```bash
python3 scripts/apply-chrome.py
```

The HTML pages Hostinger serves already contain the header and footer (no JavaScript includes). The script also marks the current nav item.

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

- Talk to us / Book a Session open Microsoft Bookings (`bookings.cloud.microsoft` Consulting Introduction Session).
- Images are stored locally under `images/` (no WordPress hotlinks).

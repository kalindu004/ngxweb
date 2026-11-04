# ngxweb

Source of the NGX Consultants website, [ngxconsultants.com](https://ngxconsultants.com), served by GitHub Pages from the root of `main`.

Plain static HTML/CSS/JS; no build step on the host.

## Header and footer

Edit `partials/header.html` and `partials/footer.html`, then stamp them into every page:

```bash
python3 scripts/apply-chrome.py
```

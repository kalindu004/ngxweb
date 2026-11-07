# ngxweb

Source of the NGX Consultants website, [ngxconsultants.com](https://ngxconsultants.com), served by GitHub Pages from the root of `main`.

Plain static HTML/CSS/JS; no build step on the host.

## Header and footer

Edit `partials/header.html` and `partials/footer.html`, then stamp them into every page:

```bash
python3 scripts/apply-chrome.py
python3 scripts/apply-meta.py
```

`scripts/apply-meta.py` copies each page's title and description into the canonical and share tags, links the icon set, and rewrites `sitemap.xml`. Page titles and descriptions are edited in the HTML files.

## Icons and share image

`images/logo-mark.png` and `images/logo-dark-blue.png` are the masters. Rebuild the favicon files and `images/og-image.png` from those files with:

```bash
python3 scripts/build-brand-assets.py
```

## Analytics

No measurement ID was found in this repository or in the published homepage source (checked 7 November 2026: no analytics script and no `Set-Cookie` on `https://ngxconsultants.com/`). Collection stays off.

`js/analytics-config.js` ships with an empty provider and an empty `measurementId`. `js/analytics.js` returns immediately in that state. It does not contact Google and it does not set a cookie.

To turn collection on later, using a property this site already has:

1. Open the Google Analytics 4 property whose web stream is `https://ngxconsultants.com`.
2. Copy that stream's measurement ID. It has the shape `G-` followed by letters and numbers. Do not invent one, and do not reuse an ID from another site.
3. Set `provider` to `"ga4"` and `measurementId` to that exact ID in `js/analytics-config.js`.
4. Update `privacy.html` in the same change so it no longer says analytics is off.
5. Merge to `main`. GitHub Pages then publishes the loader, which requests `https://www.googletagmanager.com/gtag/js`.

No other analytics provider is wired. Nothing else needs to be created for the site to stay as it is.

## Checks

```bash
python3 scripts/check-site.py
```

`python3 scripts/preview.py` serves the site locally and returns `404.html` for unknown paths.

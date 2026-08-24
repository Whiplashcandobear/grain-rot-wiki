# GRAIN ROT Wiki

A fan-made SEO content site for the co-op horror extraction base-building game **GRAIN ROT**
(Steam App 4450620, by Beck & Branch Games / Neem Interactive, released 2026-08-07).

Built as the practical assignment for the *ShengCai YouShu* "AI Product (Overseas - Hot-Keyword Game Site)"
navigation manual — Levels 1–5.

## Structure

- `build.py` — generator that turns `grain_rot_site_info.json` + `keywords.json` + 关键词素材.md
  into the static site.
- `site/` — the generated static site (deploy root):
  - `index.html` — homepage (Hero / Start / About Game / Final CTA / Footer / sidebar codes)
  - `inner/*.html` — 19 long-tail keyword pages
  - `sitemap.xml`, `robots.txt`

## Regenerate

```bash
python3 build.py
```

## Deploy

Import this repo into Vercel; `vercel.json` points the output directory at `site/`.
Custom domain: grainrotgame.com (DNS via Cloudflare).
Analytics: GA4 `G-38E373YH0J`.

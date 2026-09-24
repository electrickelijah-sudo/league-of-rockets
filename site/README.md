# Astro Site — League of Rockets Splash Page

## What's here
- `site/` — Astro 4 project (marketing/landing splash page)
  - `src/pages/index.astro` — homepage: hero → concept gallery → car showcase → CTA
  - `src/components/` — Nav, Hero, ConceptGallery, CarShowcase, CTABanner, Footer, MotionInit
  - `src/styles/global.css` — design tokens: Syne (display) + Inter (body), cinematic dark palette, motion
  - `public/press/steam-description.txt` — Steam store copy + capsule specs
  - `public/favicon.svg` — L monogram favicon
  - `dist/` — build output (do NOT commit; generated)
- Repo root (`../`) — game at `League_of_Rockets.html`, splash copied to `index.html` + `_astro/` + `favicon.svg` + `press/`

## Design direction
- **Type:** Syne 700–800 (display/wordmark, bold cinematic sans) + Inter (body/UI)
- **Color:** deep `#07070d` base, `#22d3ee` cyan accent, `#fb923c` orange secondary, `#fbbf24` gold
- **Motion:** GSAP + ScrollTrigger (CDN, client-only) — reveal-on-scroll, hero parallax, stat count-up
- **Vibe:** premium dark product page (Linear/Vercel/Squarespace dark mode) with the game's cyan/orange identity

## Commands
```bash
cd site
npm install              # first time only
npm run dev              # dev server on :4321
npm run build            # outputs to site/dist/ (safe — never touches repo root)
npm run preview          # preview the built static site locally
```

## Deploy to repo root (then GitHub Pages)
```bash
cd site && npm run build
cd ..
cp site/dist/index.html ./index.html
cp -r site/dist/_astro ./_astro
cp site/dist/favicon.svg ./favicon.svg
cp -r site/dist/press ./press
```
Then push root `index.html` + `_astro/` + `favicon.svg` + `press/` to GitHub.
GitHub Pages → Source: `main` branch, `/ (root)`. Splash at `/`, game at `/League_of_Rockets.html`.

## Steam prep
See `site/public/press/steam-description.txt` — full store copy, feature bullets, capsule/banner specs (1920×620, 1920×1080, 1024²).

## Note
The splash references game images by absolute path (e.g. `/sunset_stadium_render.png`), so it only works when served from the repo root alongside the game assets.

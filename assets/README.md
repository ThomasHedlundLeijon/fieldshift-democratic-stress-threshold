# FieldShift Research Institute — Asset System

This directory contains all brand assets for FieldShift Research Institute.
See `/FieldShift_Brand_Book.md` for the complete brand guidelines.

## Quick Reference

### Which logo to use?

| Context | File |
|---------|------|
| Website masthead, dark background | `logo/fieldshift-logo-primary.svg` |
| Slide title, square context | `logo/fieldshift-logo-stacked.svg` |
| Print document, letterhead (B&W) | `logo/fieldshift-logo-mono-black.svg` |
| Dark colored background, embossing | `logo/fieldshift-logo-mono-white.svg` |
| App icon, favicon | `icon/fieldshift-favicon.svg` |
| Symbol-only (within established brand context) | `icon/fieldshift-icon.svg` |
| Social profile (GitHub, LinkedIn, Twitter) | `icon/fieldshift-social.svg` |
| Formal/ceremonial document | `seal/fieldshift-seal.svg` |

## Directory Contents

```
assets/
├── logo/       — Full wordmark logo in 4 color variants
├── icon/       — Symbol mark, favicon, social icon
├── seal/       — Academic circular seal
├── colors/     — CSS design tokens (fieldshift-tokens.css)
├── fonts/      — Self-hosted fonts (place here if not using CDN)
└── README.md   — This file
```

## Usage Rules

1. **Always use SVG** for web and digital — never PNG for logos when SVG is available.
2. **Do not recolor** marks outside the approved palette.
3. **Minimum clear space** = cap-height of "F" in "FieldShift" on all sides.
4. **Minimum size** (web): 180px wide for full logo; 24px for icon/favicon.
5. **Minimum size** (print): 50mm wide for full logo; 20mm for icon.
6. **The seal** is for formal use only — not a general logo replacement.
7. **The social icon** (400×400) must always have the navy background — export as PNG for social platforms.

## Color Tokens

Import `/assets/colors/fieldshift-tokens.css` before any component styles.
All brand colors, typography, and spacing values are defined there as CSS custom properties.

```css
@import '/assets/colors/fieldshift-tokens.css';
```

## Font Loading

Include in `<head>`:
```html
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@300;400;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

For self-hosted fonts (no CDN dependency), place `.woff2` files in `assets/fonts/` and use `@font-face` declarations.

## Questions?

Consult the Brand Book at `/FieldShift_Brand_Book.md`.

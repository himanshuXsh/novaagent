# 02_BRAND_GUIDELINES.md — NovaAgent Brand Guidelines

## Project Name
NovaAgent

## Tagline
"Your Intelligent Multi-Agent AI Workspace"

## Brand Personality
- **Intelligent** — precise, capable, never gimmicky
- **Modern** — dark, technical, SaaS-native aesthetic
- **Trustworthy** — clean data presentation, transparent citations/sources
- **Efficient** — no visual clutter, information-dense but not overwhelming

## Mission Statement (brand-facing)
"NovaAgent brings every AI capability a professional needs into one intelligent workspace — so you stop switching tools and start getting work done."

## Voice & Tone
- Direct, confident, technical-but-approachable — like a senior engineer explaining something clearly, not a marketing brochure.
- Avoid hype words ("revolutionary", "game-changing"). Let the product speak through clarity.
- UI copy is short and functional ("Choose an Agent", "Ask anything...") — not cutesy.

## Logo Usage
- Primary logo (see `04_LOGO_BRANDING.md`): hexagonal circuit-node "N" mark + "NovaAgent" wordmark, "Nova" in white, "Agent" in blue-purple gradient.
- Minimum clear space around the logo: equal to the height of the "N" mark on all sides.
- Never stretch, recolor outside the defined palette, or place on a busy/light background without the dark-mode-safe variant.

## Typography
- **Primary font**: Inter (free, Google Fonts) — used for all UI text.
- **Wordmark font**: the logo's custom lettering (from the brand image) is used only in the logo itself, not as a UI font.
- Hierarchy: H1 28px/700, H2 20px/600, H3 16px/600, Body 14px/400, Caption 12px/400 (same scale as `03_UI_UX_DESIGN_SYSTEM.md`).

## Brand Colors

| Token | Hex | Usage |
|---|---|---|
| Background Primary | `#0B0F19` | App background |
| Background Secondary | `#111827` | Section backgrounds |
| Card | `#151C2C` | Cards, panels |
| Sidebar | `#0F172A` | Sidebar background |
| Accent Primary | `#4F7DF3` | Primary actions, links, active states |
| Accent Secondary | `#6D5EF7` | Gradient partner, secondary highlights |
| Border | `rgba(255,255,255,.06)` | Dividers, card outlines |
| Text Primary | `#F8FAFC` | Headings, primary text |
| Text Secondary | `#94A3B8` | Captions, muted text |
| Success | `#22C55E` | Completed states, positive metrics |
| Warning | `#F59E0B` | Low credits, caution states |
| Danger | `#EF4444` | Errors, destructive actions |

## Marketing Colors (landing page / external, if built later)
- Hero gradient: `#4F7DF3` → `#6D5EF7` (same as the wordmark and primary buttons — brand consistency between product and marketing).
- Dark background throughout, matching the in-product theme (no separate "light marketing site" identity — one brand, one mode).

## Icon Style
- Lucide icons (free, open-source, consistent stroke width ~1.5-2px), used at 18-20px in nav/sidebar, 16px inline.
- No mixed icon sets — Lucide only, for visual consistency.

## Illustration Style
- Minimal — the product relies on real UI screenshots and generated content (code, images, charts) as its visual language, not custom illustrations. If illustration is needed (e.g., empty states), keep it line-art, single-color (`--accent-primary`), no complex scenes.

## Dashboard Branding
- Logo (compact "N" mark only) top-left of sidebar, full wordmark only on the login screen and marketing contexts.
- Credits badge, notification icon, and avatar always in the top-right of the navbar — this placement is consistent brand furniture across every page.

## App Icon
- The hexagonal "N" mark alone (no wordmark), on the `#0B0F19` dark background, exported at standard app-icon sizes (512x512 down to 16x16).

## Favicon
- Simplified version of the app icon — the "N" mark only, may need to lose the fine circuit-line details at 16x16/32x32 for legibility; keep just the bold "N" and hexagon outline at the smallest sizes.

## Open Graph Image
- 1200x630px, dark background (`#0B0F19`), centered logo + tagline, subtle circuit-line texture echoing the logo motif, no screenshot clutter (OG images with UI screenshots read poorly at social-preview thumbnail size).

## Email Branding
- Dark-background HTML email template matching the product theme is ideal, but **plain, high-contrast light-background transactional emails are acceptable and more broadly compatible** across email clients — logo + minimal accent-color CTA button (`--accent-primary`) is sufficient for MVP; don't over-invest here.

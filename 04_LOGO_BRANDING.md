# 04_LOGO_BRANDING.md — NovaAgent Logo & Branding Package

Based on the provided logo reference image (hexagonal circuit-node "N" mark + gradient wordmark).

## Primary Logo
- Full lockup: icon mark + "NovaAgent" wordmark ("Nova" in white/`--text-primary`, "Agent" in `--accent-gradient`) + optional tagline beneath in `--text-secondary`, small caps.
- Used on: login screen, marketing/landing contexts, README/documentation headers.

## Secondary Logo
- Icon mark + wordmark, no tagline — used in tighter horizontal spaces (e.g., a compact top bar) where the full lockup doesn't fit.

## Monogram
- The "N" mark alone, extracted from inside the hexagon — used for very small spaces (browser tab favicon, small avatar-style placements).

## App Icon
- Hexagon + "N" + circuit-node details, on solid `--bg-primary` (#0B0F19) background, exported as a square (512, 256, 192, 128, 64, 32px) PNG set.

## Favicon
- Simplified monogram (hexagon + bold "N" only — drop fine circuit-line/spark details that won't render at 16x16), exported as `.ico` (16, 32, 48px) and `favicon.svg`.

## Color Variants
- **Full color** (default): blue-to-purple gradient mark on dark background — primary usage.
- **Single color (white)**: for placements where the gradient can't render (e.g., some email clients, embroidered swag) — flat white mark.
- **Single color (accent)**: flat `--accent-primary` (#4F7DF3) mark — for monochrome contexts needing brand color but not the full gradient.

## Dark Version
- The default/native version — mark as designed, on `--bg-primary` (#0B0F19) or any sufficiently dark surface.

## Light Version
- White or `--accent-primary` flat monogram on a light/white background, for the rare case a light-background placement is unavoidable (e.g., a partner's light-themed page). Not used anywhere in-product since NovaAgent is dark-mode-only.

## Logo Spacing (Safe Area)
- Minimum clear space on all sides of the full lockup = the height of the hexagon icon mark. No other UI element, text, or edge of the frame should enter this zone.

## Do
- Use the logo on dark backgrounds only (its native context).
- Maintain the icon-to-wordmark spacing and relative sizing from the reference.
- Use the monogram alone when space is under ~120px wide.

## Don't
- Don't recolor the gradient outside the defined blue→purple range.
- Don't stretch/skew the mark or wordmark.
- Don't place the full lockup on busy/photographic backgrounds without a solid dark backing plate.
- Don't rotate the icon mark.

## Prompt to Recreate the Logo (AI image generation)
```
A modern tech logo icon: a hexagonal outline made of circuit-board style
lines with small connector nodes (small hollow circles) branching off
three sides, containing a bold, slightly 3D-extruded letter "N" in a
blue-to-purple gradient (#4F7DF3 to #6D5EF7), with a small four-point
sparkle/star accent near the top-right of the hexagon. Background: solid
very dark navy (#0B0F19). Flat vector illustration style, clean lines,
no text, centered composition, square canvas.
```

## Prompt to Recreate the Favicon
```
A minimal square app icon: a hexagon outline in blue-to-purple gradient
(#4F7DF3 to #6D5EF7) containing a bold, simplified letter "N" in the same
gradient, no fine detail lines, no sparkle accent, optimized for
legibility at 16x16 pixels. Background: solid dark navy (#0B0F19). Flat
vector style, square canvas, high contrast, centered.
```

## Prompt to Recreate the App Icon
```
A square app icon at 512x512: hexagonal circuit-line outline with small
node circles, containing a bold 3D-extruded letter "N" in a blue-to-purple
gradient (#4F7DF3 to #6D5EF7), small sparkle accent top-right, solid dark
navy background (#0B0F19), soft inner glow around the "N" for depth, flat
vector illustration style suitable for an iOS/Android/desktop app icon
grid, centered composition with balanced padding from the edges.
```

## SVG Guidelines
- Export the icon mark as a standalone SVG with a `viewBox="0 0 512 512"`, gradient defined via `<linearGradient>` (not flattened to a raster gradient), so it scales cleanly at any size.
- Keep the SVG to a single `<g>` group per visual layer (hexagon, N shape, nodes, sparkle) for easy recoloring (e.g., swapping to the flat single-color variant) without redrawing.
- Avoid embedding raster images inside the SVG — vector paths only, to keep file size small and edges crisp at all resolutions.

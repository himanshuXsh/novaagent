# 03_UI_UX_DESIGN_SYSTEM.md — NovaAgent UI/UX Design System

This extends `02_BRAND_GUIDELINES.md`'s tokens into full interaction/layout rules. Reference screens: the attached NovaAgent showcase (Login, Dashboard, Chat, Coding, Search, PDF/PPT, Image, RAG, Billing, Settings).

## Design Tokens (canonical — same as Brand Guidelines)

```css
--bg-primary: #0B0F19;
--bg-secondary: #111827;
--bg-card: #151C2C;
--bg-sidebar: #0F172A;
--accent-primary: #4F7DF3;
--accent-secondary: #6D5EF7;
--accent-gradient: linear-gradient(135deg, #4F7DF3, #6D5EF7);
--border: rgba(255,255,255,.06);
--text-primary: #F8FAFC;
--text-secondary: #94A3B8;
--success: #22C55E;
--warning: #F59E0B;
--danger: #EF4444;
--radius-card: 20px;
--radius-button: 12px;
--space-unit: 8px;
--font-family: 'Inter', sans-serif;
```

## Grid System & Layout
- **Desktop (≥1200px)**: 3-column shell — sidebar (270px fixed) + main content (fluid) + optional right panel (artifact/detail, ~380px, Coding page only).
- **Tablet (768-1199px)**: sidebar collapses to icon-only rail (~72px, tooltips on hover); main content full width; right panel becomes a slide-over drawer instead of a fixed column.
- **Mobile (<768px)**: sidebar becomes a bottom nav bar or hamburger-triggered full-screen drawer; single-column content; artifact panel becomes a full-screen modal.
- Content max-width on very large screens: 1440px, centered, to avoid overly stretched cards.

## Spacing
- 8px base unit; all margins/padding are multiples of 8 (8/16/24/32/40).
- Card internal padding: 24px. Section gaps: 32px. Inline element gaps: 8-12px.

## Sidebar
- 270px desktop width, `--bg-sidebar` background.
- Logo mark + wordmark top, nav list (icon + label, rounded hover, accent-tinted active state with left accent bar), credits card + profile card pinned at bottom (see reference Dashboard screen).

## Navbar
- Sticky top, `--bg-primary` background, thin bottom border (`--border`).
- Search bar (center-left, ⌘K shortcut hint per reference), credits badge, notification bell (with unread-count dot), avatar + name + plan badge + dropdown chevron.

## Cards
- `--radius-card` (20px), `--bg-card`, 1px `--border`, soft shadow `0 4px 24px rgba(0,0,0,.25)`, 24px padding.
- Metric cards (Dashboard): icon in a colored rounded square, large number, label, small delta ("+12% from last month") in `--success` or `--danger`.

## Buttons
- **Primary**: `--accent-gradient`, white text, `--radius-button`, hover = slight brightness/lift.
- **Secondary**: transparent, 1px `--accent-primary` border, `--accent-primary` text.
- **Ghost**: no border, hover background `--bg-card`.
- **Icon button**: 36-40px square/circle, centered icon, hover background change.
- **Destructive**: `--danger` text/border, used for Delete actions only.

## Inputs
- `--bg-secondary` background, 1px `--border`, `--radius-button`, 12-16px padding, `--text-primary` value text, `--text-secondary` placeholder.
- Focus state: 2px `--accent-primary` ring + border color shift — never rely on color alone (see Accessibility).

## Dropdowns
- Same card styling as Cards, appears with a subtle fade+scale-in (120ms), items have hover background `--bg-secondary`, selected item shows a checkmark or accent-colored text.

## Tables
- Rounded container matching card radius, sticky header (`--bg-secondary`), row hover highlight, status values as small pill badges (colored per Success/Warning/Danger tokens), right-aligned numeric columns.

## Charts
- Plotly, dark template, `--accent-primary`/`--accent-secondary`/`--success` for series colors, transparent background matching the containing card, gridlines at low opacity (`rgba(255,255,255,.05)`).

## Progress Bars
- Track: `--bg-secondary`. Fill: `--accent-gradient` (usage/credits) or `--success` (completion). Height 8-10px, fully rounded ends.

## Dialogs / Modals
- Centered, `--bg-card` background, `--radius-card`, dimmed backdrop (`rgba(0,0,0,.6)`), fade+scale-in entrance (150ms), close (X) top-right, primary action bottom-right, secondary/cancel bottom-left or ghost-styled next to it.

## Loading States
- Skeleton screens (pulsing `--bg-secondary` blocks matching the final content's shape) for cards/tables on initial load.
- Inline spinner (small, `--accent-primary`) for button-triggered actions ("Generating...").
- Chat: animated three-dot typing indicator while a response streams.

## Empty States
- Centered icon (line-art, `--accent-primary`, ~48px) + short heading + one-line description + a primary CTA where relevant (e.g., RAG page with no documents: "Upload your first document").

## Error States
- Inline banner, `--danger` left border + tinted background, short human-readable message + a retry action where applicable. Never a raw stack trace shown to the user.

## Typography

| Level | Size | Weight |
|---|---|---|
| H1 | 28px | 700 |
| H2 | 20px | 600 |
| H3 | 16px | 600 |
| Body | 14px | 400 |
| Caption | 12px | 400 |

## Responsive Rules
- Breakpoints: 1200px (desktop), 768px (tablet), <768px (mobile) — see Grid System above.
- Touch targets on mobile/tablet: minimum 44x44px.
- Charts reflow to full-width single-column stacking below 768px.

## Dark Theme
- Dark mode only for v1 — all tokens above are dark-mode-native, not a "dark variant" of a light theme.

## Animations
- Subtle only: 120-200ms ease-out for hovers, dropdown/modal entrances, and tab switches. No parallax, no bouncing, no neon glow effects.

## Hover States
- Cards: slight elevation (shadow increases) + border brightens to `rgba(255,255,255,.12)`.
- Buttons: brightness/lift per Buttons section.
- Nav items: background fill `--bg-card`.

## Focus States
- Every interactive element gets a visible 2px `--accent-primary` focus ring on keyboard focus (not just hover) — required for accessibility, not optional polish.

## Accessibility
- Minimum contrast ratio 4.5:1 for body text against its background (verify `--text-secondary` on `--bg-card` meets this).
- Never convey state (error/success/active) through color alone — pair with an icon or text label.
- All icon-only buttons need an `aria-label` / Streamlit equivalent tooltip text.
- Full keyboard navigability for nav, forms, and modals (tab order, Escape closes modals).

## Page-by-Page Visual Description
(Full detail lives in the CotexAI frontend `Design.md` already built — same specs apply here 1:1, just rebranded to NovaAgent's logo/name.) Summary:
- **Login**: centered card, logo, Google OAuth primary button, email/password secondary path.
- **Dashboard**: metric row (4 cards) → agent grid (6 agents + "Add Custom Agent" placeholder) → usage line chart + agent-distribution donut chart → recent activity + storage overview.
- **Chat/Coding/Search/PDF/Image/RAG**: consistent sidebar+navbar shell, agent-specific main panel per `03_UI_UX_DESIGN_SYSTEM.md`'s component specs above, matching the reference screenshots exactly.
- **Billing**: balance card + usage bar, 3 plan cards (Pro highlighted), transaction table.
- **Settings**: left tab list, right form panel.

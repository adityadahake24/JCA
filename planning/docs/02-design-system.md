# Design System — Tokens & Palette

jca-ny-app_vSHARE.html is authoritative (RFP §2.2: "white marble, crimson, and gold — never saffron/orange"). jca-app-mockup.html and the entire jca-admin-mocukups.html file use an indigo/saffron palette and are treated as superseded design-exploration artifacts (Discovery item DISC-8). The admin utility's visual language is re-derived from these vSHARE tokens, not carried forward from its own mockup file.

## Color tokens

Contrast ratios computed via the WCAG 2.1 relative-luminance formula
against `--cream` (#faf6ef), verified programmatically (see
`planning/build_workbook.py`'s verification pass). AA thresholds: 4.5:1
normal text, 3.0:1 large text (>=24px or >=19px bold) and UI
components/graphics.

| Token | Value | Role | Contrast vs Cream | AA Verdict |
|---|---|---|---|---|
| `--crimson` | `#a8202c` | Primary brand color. Body text, primary buttons, active states, links. | 6.70:1 | Pass — AA normal text and AA large text |
| `--crimson-deep` | `#7a1620` | Pressed/active states, headings on light backgrounds. | 9.93:1 | Pass — AAA normal text |
| `--crimson-soft` | `#c84252` | Secondary accents, badges, non-critical highlights. | 4.47:1 | Pass — AA large text/UI only (fails AA normal text by 0.03; do not use for body copy) |
| `--gold` | `#c9a961` | Ornamental only — borders, dividers, icon fills, decorative rules, ratnatraya/aṣṭamaṅgala motifs. | 2.09:1 | Fail — never use for text of any size |
| `--gold-light` | `#e3c889` | Subtle background tints, hover fills behind icons — never text, never adjacent to cream as a foreground. | 1.51:1 | Fail — decorative background use only |
| `--gold-deep` | `#8c6f30` | Legacy 'deep gold' token from vSHARE — retained only for large display headings (>=24px). | 4.40:1 | Fail — AA normal text (misses 4.5:1 threshold by 0.10); Pass — AA large text only |
| `--gold-text (NEW — Discovery item DISC-10)` | `#7d6229` | AA-safe gold for any place gold-colored TEXT is genuinely needed (e.g. a gold pill label). Introduced because the vSHARE --gold and --gold-deep tokens both fail AA body text. | 5.34:1 | Pass — AA normal text |
| `--cream` | `#faf6ef` | Primary light background across all member-facing surfaces. | n/a (background reference) | n/a |
| `--cream-warm` | `#f4ecdd` | Secondary background — cards, elevated surfaces on cream. | n/a (background) | n/a |
| `--paper` | `#ffffff` | Elevated surfaces (modals, sheets) requiring maximum contrast. | n/a (background) | n/a |
| `--ink` | `#1c1410` | Primary body text color. | 16.85:1 | Pass — AAA normal text |
| `--ink-soft` | `#4a3d35` | Secondary text — captions, metadata, timestamps. | 9.70:1 | Pass — AAA normal text |
| `--muted` | `#8a7864` | Tertiary text and disabled states — placeholder text, inactive tab labels. | 3.94:1 | Pass — AA large text/UI only (fails AA normal text; do not use for body copy or form labels) |
| `--good` | `#3f7d5e` | Success states — confirmed payment, approved content, open/available status. | n/a (compute per use; verify before shipping any new success-state text) | Verify per use |

## Typography

| Role | Family | Usage |
|---|---|---|
| Display / serif headings | Playfair Display (serif) | Screen titles, ornamental headings, the JCA wordmark treatment. |
| Body / UI text | Inter (sans-serif), -apple-system fallback | All body copy, form labels, buttons, navigation labels. |
| Dynamic Type / accessibility | Both families scale with iOS Dynamic Type and Android font scaling; no hard-coded pixel line-heights — RFP §2.2 multi-generational accessibility requirement. | Applies platform-wide; verified per screen in the accessibility audit (Localization & Accessibility module). |

## Spacing & shape

| Token | Value |
|---|---|
| Border radius (member surfaces) | Card: 16-20px · Button/chip: full-pill · Modal sheet: 24px top corners |
| Border radius (admin utility, from indigo mockup's --r tokens, re-themed) | --r: 12px · --r-sm: 8px · --r-lg: 18px (denser than member surfaces, matches admin's productivity-first brief) |
| Shadow — small | 0 1px 2px rgba(28,20,16,0.04), 0 1px 3px rgba(28,20,16,0.06) |
| Shadow — medium | 0 4px 12px rgba(28,20,16,0.08), 0 2px 4px rgba(28,20,16,0.04) |

## Iconography

Jain symbology only: siddhachakra, swastika (Jain form), aṣṭamaṅgala, ratnatraya (three-jewel ornament), the five-shrine iconset (Mahavir, Adinath, Upashray, Shrimad, Dadawadi). Explicitly excluded: Om, Ganesha, trishul, or any Hindu iconography — RFP §2.2 "Jain, not Hindu."

## Dark mode

Live Darshan and Virtual Tour ship dedicated dark-mode UI per the walkthrough deck (slides 4 and 6). Dark-mode tokens are derived from the same crimson/gold/ink palette, not a separate theme, so brand identity holds in both modes.

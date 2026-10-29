# Visual Design Brief

## Direction

**Editorial export house:** confident, composed, tactile and globally legible. The identity should connect Indian spice origins with international trade through precise product storytelling, restrained typography and beautiful real material photography—not through generic “AI” gradients or ornamental cultural clichés.

This brief informed the Phase 2 homepage and shared visual foundation. The current implementation uses the approved palette and system Georgia/Segoe UI fallbacks; it does not yet load the proposed Fraunces/DM Sans fonts. Typography, contrast, layout, and component guidance below remains the reference for later routes.

## Brand palette

Owner-provided colors:

| Token | Value | Intended use |
|---|---|---|
| Forest green | `#203B30` | Primary brand field, headings on ivory, primary CTA |
| Warm ivory | `#F7F3E9` | Main canvas and breathing room |
| Muted gold | `#C49A55` | Fine rules, small highlights, icon/label accents; not small body text without contrast verification |

Proposed supporting neutrals (provisional; verify contrast in implementation): deep ink `#242822`, muted olive-grey `#687067`, pale stone `#E5E0D5`, clean white `#FFFFFF`. Use the core palette as the signature; do not add gradients or a large unrelated accent spectrum.

### Accessibility

Check every foreground/background combination against WCAG 2.2 AA in the implemented states. Forest on ivory and ink on ivory are default text pairings; gold is decorative/highlight only unless a specific text size/contrast test passes. Add visible focus, error, success and disabled states that do not depend on color alone. Support keyboard use, zoom and reduced-motion preferences.

## Typography

Proposed pairing: a distinctive editorial serif for large display headings (e.g. **Fraunces**) with a highly readable sans serif for UI/body (e.g. **DM Sans**). Confirm font licensing, final weights, language glyph coverage and self-hosting before use. If self-hosting is not approved/available, use system fallbacks; avoid remote font requests that add unreviewed tracking or privacy dependencies.

- Display: expressive serif, sparingly used, short line lengths and calm leading.
- Section headings: serif or a restrained sans hierarchy, consistent across pages.
- Body/UI: neutral sans with legible numerals, visible labels and generous line height.
- Product/category labels: small uppercase or sentence case with careful letter spacing; never reduce legibility for style.

## Layout and components

- Use a centered, editorial content grid with wide outer margins on desktop and a consistent readable text measure.
- Alternate full-bleed photographic moments with quiet ivory sections; use asymmetry sparingly to create rhythm.
- Prefer open layouts, fine rules, intentional whitespace and strong type scale over floating cards, dashboard panels or excessive borders/shadows.
- Category/product tiles may use a simple image, name and short approved description. Avoid app-like metric cards.
- Buttons should be clear, high-contrast and purposeful; one primary CTA per decision area, with secondary links visually quieter.
- Forms use persistent visible labels, concise help text, inline errors and clear success feedback.
- Use Lucide icons only where they clarify an action; do not substitute icons for navigation labels.

## Photography and content

- Prioritize authentic, high-resolution spice, ingredient, processing or landscape photography with confirmed provenance and usage rights.
- Captions must describe the actual image; never imply that stock imagery depicts SPICEORA’s own farm, facility, lot, or supplier.
- Use deliberate close-up texture, natural light and restrained color grading. Avoid oversaturated color casts, repeated generic spice piles, flags/maps as decoration, and unverifiable origin imagery.
- Product images must represent the actual item/grade offered. If that cannot be confirmed, omit the image rather than mislead.
- Crop responsively with meaningful `alt` text for informative images and empty alt for purely decorative imagery.
- **Phase 2 asset:** `frontend/public/images/spice-study.jpg` is a locally stored illustrative image downloaded from Unsplash photo `photo-1596040033229-a9821ebd058d`. The [Unsplash license](https://unsplash.com/license) permits commercial use. It shows assorted spices, seeds, turmeric and dried chillies; it is captioned as editorial/illustrative and explicitly is not evidence of SPICEORA inventory, facilities, sourcing or product grade. Replace or supplement it with owner-approved, rights-cleared brand/product photography before representing specific offered products.

## Motion

Use only short, purposeful transitions for hover/focus and route feedback. No parallax, autoplay video, scroll hijacking, animated counters, carousels that hide content, or decorative motion that competes with reading. Honor `prefers-reduced-motion`.

## Responsive guidance

Design mobile-first; breakpoints are implementation decisions, not fixed in Phase 1. Preserve editorial hierarchy and text measure as the viewport narrows. Stack image/text sections, use a compact accessible menu, keep forms single-column, provide reachable CTA controls, and test at narrow widths, tablet, desktop and zoom. Never crop critical product information or place essential text over busy photography.

## Design review checklist

- Does the page read like a premium export business rather than a dashboard/template?
- Is each business claim backed by owner-approved evidence?
- Is real photography licensed, accurately captioned and representative?
- Is text contrast/focus/form feedback accessible?
- Does the layout work with keyboard, mobile, zoom and reduced motion?
- Are gold accents restrained and gradients/glassmorphism absent?

## Phase 2 implementation notes

- Implemented in `frontend/src/index.css` as Tailwind CSS v4 `@theme` tokens plus semantic component styles.
- Uses the owner-provided forest/ivory/gold palette, forest focus rings on light surfaces and a contrasting muted-gold focus ring on dark surfaces; gold remains a restrained decorative accent.
- Uses Georgia and Segoe UI system fallbacks. Proposed font files/licensing have not been added.
- The homepage reuses editorial spice photography in the hero and illustrative category crops; category availability/specifications are not asserted.
- Header, mobile menu, homepage, category preview, proposed-process block, enquiry placeholder, and footer are implemented. The placeholder does not submit data.

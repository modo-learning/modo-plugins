---
name: modo-design
description: Modo's visual style for anything this plugin draws: the AI capability card, the exported PDF report, or any other page or visual of an assessment. Plain HTML and CSS with Modo's colours (navy, Modo yellow, warm neutrals) and a card layout close to shadcn/ui. Use whenever you make a card, report, PDF, page or visual for Modo AI Skills, so they all look the same.
---

# Modo design

Every visual this plugin makes looks like the Modo app: a navy header, Modo
yellow as the accent, warm neutral surfaces and Inter type. This skill holds
the style so the card, the PDF report and anything new stay consistent.

## Ground rules

- **Use a template when one exists.** The capability card is
  `assess-my-ai-work/passport-card.html`; the PDF report is
  `export-assessment/report-template.html`. Fill only the JSON between the
  MODO-DATA markers and change nothing else.
- **For anything new**, start from [modo-tokens.css](modo-tokens.css): copy the
  whole block between the MODO-TOKENS markers into the page's `<style>`, unchanged,
  and build with the components below. Never invent new colours.
- **Plain HTML and CSS only.** No frameworks, no libraries, no build step.
- **Self-contained.** No network requests of any kind: no web fonts, images,
  scripts or stylesheets from other sites. Inter is used when the viewer has
  it, otherwise the system font.
- **Light and dark.** The tokens already switch for dark mode; use the
  variables, never raw colours.
- **Accessible.** Yellow is an accent for borders, marks and fills next to
  navy, never for text on a light surface (it fails contrast). Level segments
  are navy on light and yellow on dark.
- **Wording.** Don't call anything a badge, a rank, a percentile, a benchmark
  or "Modo verified". Every visual ends with the rubric label line.

## Components

| Component | Look | Used for |
|---|---|---|
| Card | white surface, 1px `--border-default`, radius `--radius-xl`, `--shadow-sm` | the outer frame |
| Header | `--nav-bg` navy, `--nav-text`, a yellow square mark with "M", an uppercase kicker in `--nav-text-muted` | title and subtitle |
| Section title | 11px uppercase, letter-spacing .06em, `--text-muted` | "Capabilities", "Evidence" |
| Capability row | name left, "Level N of 5" right, five rounded segments; the strongest row gets a yellow border on `--accent-faint` | each capability |
| Confidence | high = solid segments, medium = lighter, low = striped | the segment fill |
| Not shown | a dashed empty track and "Not shown in this chat" | missing capability |
| Pill | rounded outline, 12px, `--text-secondary` | confidence, run agreement |
| Notice | `--warning-bg` with `--warning-border` | the coverage line |
| Quote | `--surface-2` with a 3px yellow left border, capability underneath | the user's own words |
| Tip | `--accent-faint` box, capability name above | one thing to try |
| Footer label | `--surface-2` strip, 12px `--text-muted` | the rubric label line |

Spacing follows a 4px grid (4, 8, 12, 16, 20, 24). Body text is 14px, titles
21px at weight 650.

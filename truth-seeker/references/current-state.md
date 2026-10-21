# Current State SVG spec (Signal theme)

`scripts/cs_svg.py` draws all of this from a stages JSON; this page explains the layout and the rules it follows, for when you need to adjust the script.

A vertical flowchart, 680px wide, height fitting the content, centred in `#cs-wrap`. Inline SVG only (no script), square corners.

## Structure

Trace the real workflow top to bottom, in numbered sections with a small mono label above each (`1 · YOU SAVE SOMETHING`):
1. Trigger (who or what starts it)
2. Collection / setup steps
3. The store the work lands in
4. Processing jobs in time order (nightly jobs, pipelines)
5. Slower jobs (weekly, monthly)
6. Rebuild / publish (compound node with inner boxes connected by arrows)
7. Checks and safety gates (gates are "decision" nodes)
8. A "BACK TO YOU" divider, then what reaches the person (summary, reading, asking)
9. North-star stages (planned ideas) marked NONE
A dashed loop arrow on the right edge back to the trigger ("next save → next night"). It starts from the section named in `loop.from`, or else the last section with anything LIVE or PARTIAL in it, so it never starts from the not-built stages.

A section is one or more rows; each row holds 1–3 nodes (full, half, third width). Use `"rows"` for several rows under one label; a row of more than 3 is split with a warning. Rows in a section are equally tall per row.

Each node: `<!-- Name — STATUS -->` comment, then `<g opacity="…">` holding the node rect, the badge rect + badge text at the top-left corner, a title (12px, weight 600, wraps to 2 lines), optional inner boxes (`"inner": [...]`, steps joined by small arrows), 1–3 lines of plain-English description (10px), and a mono tech line (8.5px). Description text wraps at about 95 characters per line for a full-width node, 52 for half-width, 33 for third-width; tech lines wrap too (110 / 58 / 36). Anything longer is cut with "…" and the script prints a warning, so shorten the text rather than ignore it.

## Colours

| Element | Fill | Stroke | Title |
|---|---|---|---|
| Processing node | `rgba(52,212,171,0.07)` | `rgba(52,212,171,0.45)` | `#34D4AB` |
| Gate / decision (a person decides, a safety check) | `rgba(255,196,0,0.07)` | `rgba(255,196,0,0.5)` | `#FFC400` |
| Trigger / person | `rgba(246,187,247,0.08)` | `#F6BBF7` | `#F4F4F0` |
| System / store | `rgba(244,244,240,0.03)` | `#3A3A3F` | `#F4F4F0` |
| Inner boxes | `#17171A` | `#3A3A3F` | kind colour |

Text `#F4F4F0`, section labels `#8C8C88` (JetBrains Mono 9px, letter-spacing 1.5), tech lines `#5E5E5B` mono. Arrows fan out from the bottom centre of every box in a row, through a shared horizontal bus, to the top centre of every box in the next row, ending in an open chevron. They are `#5E5E5B` solid when every box above is LIVE, otherwise `#3A3A3F` dashed `4 3`. "BACK TO YOU" divider: `#FFC400` dotted line, label `#FFC400` on a `#0D0D0E` plate; the arrow runs through it, behind the label. Rows made only of ghosts (the leftovers section at the end) have no arrows at all.

Fonts: `Inter Tight, Helvetica Neue, Arial, sans-serif` for titles and text; `JetBrains Mono, monospace` for labels, badges and tech lines.

## Badges and opacity

| Status | Badge fill | Badge text | Group opacity |
|---|---|---|---|
| LIVE | `#4CD38A` | `#0D0D0E` | 1.0 |
| PARTIAL | `#F49122` | `#0D0D0E` | 0.6 |
| NONE | `#FF5B45` | `#0D0D0E` | 0.35 |
| GHOST | outline `#FF5B45`, dashed | `#FF5B45` | 0.5 (shown, not counted as a stage) |

Badge: rect 13px high (34px wide for LIVE/NONE, 52 for PARTIAL), text 8px JetBrains Mono weight 700.

## Coverage scoreboard and legend (bottom)

"Coverage summary · N workflow stages" in the sans font, 14px weight 800. Three bars (480px track `#17171A`, stroke `#26262A`): LIVE `#4CD38A`, PARTIAL `#F49122`, NONE `#FF5B45`, each with "x / N · y%". Percentages use largest-remainder rounding so they add up to 100. Then one line: "y% fully operational · y% built, not yet proven · y% not started · n ghosts (not counted)". Legend: Live / Partial / None / Ghost, plus Processing / Gate / System / Trigger swatches. The SVG carries `role="img"` and an `aria-label` (from `"aria"` in the JSON).

## Update mode

Change the `status` values in the stages JSON and run `cs_svg.py` again. Positions, labels and arrows come from the order, so nothing else moves. Unknown statuses stop the script with an error (WIRED, HALF-BUILT and PLANNED are accepted as aliases). Only restructure the stages if asked.

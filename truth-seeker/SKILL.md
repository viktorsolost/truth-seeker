---
name: truth-seeker
description: "Audits a repo (or a system of folders, scheduled jobs and data stores) and builds one HTML map page: a plain-English System Doc, a left-to-right Mind Map from where the work starts to where it ends, and a Current State flowchart where every step is proven LIVE, PARTIAL or NONE by real tests, runs and code. Use when the user says 'truth seeker', 'map this repo', 'what's really built', 'update the map', 'refresh the badges', or asks for an honest picture of what a project actually does versus what its docs claim."
metadata:
  author: Viktor
  version: 4.0.0
  license: MIT
---
# Truth Seeker

Use this to see what is *really* built, not what the docs claim. The value is the proof: every status comes from code, test runs, job state and logs, and anything that disagrees with the docs is called out. The page is written in plain English so someone who doesn't know the code can follow it.

The output is one HTML page with three tabs:

1. **System Doc**: what exists, how it fits, what's proven, what contradicts the docs, what's left.
2. **Mind Map**: a left-to-right flow in columns, from where the work starts (usually the user or a trigger) to where it ends (usually what the user gets). Every part is a node; edges show work or data moving forward; loops back are dotted underneath.
3. **Current State**: a top-to-bottom flowchart of the real workflow, each stage with a LIVE / PARTIAL / NONE badge and a coverage scoreboard. It is a north-star diagram: planned stages stay on it, marked NONE.

## Scope first

A project is usually one repo. It can also be a whole system spread over several folders, scheduled jobs (cron, launchd, CI), data stores and services. Before auditing, write down the in-scope list (folders, jobs, data stores, services) and what is out of scope. If the user only gave a name, find the parts from READMEs, handoff notes, CI config and the scheduler, and say what you included.

Never put secrets, tokens, credentials, personal data or private client data in the page. If the project has its own rules about what may be shared, follow them.

## Output location and name

- Single repo: `<repo>/docs/<repo-name>.html`. Multi-folder system: the folder that holds its tools (e.g. `tools/docs/<system-name>.html`).
- Read-only audit (the user doesn't want the project touched): write to a folder they name instead, or to a temp folder, and say where.
- Keep the source you wrote as `docs/<name>.content.html` next to it, so an update edits content, not the built page.
- If your environment can publish pages (for example the Artifact tool in Claude Code), publish it and record the URL in `docs/.truth-seeker.json` (`{"artifact": "<url>", "built": "<date>"}`). On later runs, publish to that same URL so the link keeps working.

## Step 1: Audit (prove, don't assume)

Adapt to what the system contains; for each part collect evidence:

1. Read CLAUDE.md / README / HANDOFF / rule files for intended structure and rules.
2. List modules, scripts, config, pages, API routes, data stores. Count real data (notes, pages, rows) live.
3. Scheduled jobs (cron, launchd, systemd, CI schedules): read the schedule and command, check that it is loaded or enabled, and read the latest log or run output for what the last real run did. A job installed today with no scheduled run yet is not LIVE.
4. Run every test suite and record real counts. If a test needs something the environment lacks (GPU/Metal, network), say so; never guess a number. Don't rely on `timeout` (missing on macOS by default); use the test runner's own timeout or `gtimeout` if installed. A test that fails some runs and passes others is flaky: re-run it about three times and report the ratio. A failure that doesn't come back is only a note under Tests; one that repeats makes PARTIAL the stage that test checks.
5. Services: probe them (HTTP status, a real request). If a real request costs money or reaches a person (paid AI calls, sending a message or email), make at most one cheapest possible request, or skip it and list it under "checks not done".
6. Compare docs vs reality and list contradictions with the file evidence.

Classify each component. The same verdict has a name in each tab:

| Verdict | System Doc badge | Current State badge | Mind map |
|---|---|---|---|
| Exists, used, proven by a real run, test or probe | `WIRED` (`b w`) | `LIVE` | solid node, green dot |
| Exists but not proven end to end: never ran on schedule, failing, flaky, untested where it matters, capped or blocked | `HALF-BUILT` (`b h`) | `PARTIAL` | solid node, orange dot |
| Documented or wanted, no code | `PLANNED` (`b p`) | `NONE` | hollow dashed node |
| Left behind with no purpose, or doing work nobody uses | `GHOST` (`b g`) | `GHOST` (red dashed, not counted as a stage) | node with a red dot |

A stage is one thing that can be proven or fail on its own: don't merge two parts that could get different verdicts, and don't split one that can't. A second machine or install running the same thing is its own stage. Tests are evidence for stages, not stages.

Always flag ghosts. Judge them by what they do now, not why they were kept: something that runs or sits there with nothing to act on in the live data (a poller for things that no longer exist, an old copy of the app) is a GHOST, even if it has tests. If the live system still uses it, it isn't, and neither is one-time setup or migration code that already did its job. A job that was installed, **moved or rescheduled** since its last run is PARTIAL until it has run in its current place and time, even if the same code ran before.

If you can't check something (sandbox, no access, no network), list it under "checks not done"; never mark it LIVE, NONE or GHOST because of that.

## Step 2: Write the content file

Write `docs/<name>.content.html` with:

- `<title>` = a real name ("Lumen Repo Map"), then `<!--BRAND-CSS-->` on its own line.
- Header: `<div class="slug">Truth Seeker · audited <date></div>`, an `h1` (name, with an optional `<em>` second word), a `.sub` line saying what the system is and what the audit was based on, and the tab buttons (`nav.tabs` with `data-t="doc" | "mm" | "cs"`).
- **System Doc panel** (`section.panel#doc`), plain English first, technical detail after a "─" or in `.tech` spans:
  - *In one minute* (`.lead` paragraphs): what works, what isn't proven, what's broken.
  - KPI grid (`.grid > .kpi`) with the numbers that matter.
  - *Architecture*: a `pre` diagram of the wired flow.
  - *Schedule* table for jobs (job, when, what it does, last real run with evidence, status badge).
  - *Modules* tables grouped by stage (module, plain English ─ technical, reads → writes, tests, status).
  - *Planned*, *Contradictions and ghosts* (`.card.flag` for real problems, `.card.warn` for stale docs), *Current data*, *Tests* (every suite, real counts), *Directory structure*, *Rules* (say "implemented" or "rule declared, not yet implemented"), *Infrastructure*, *Next steps*.
  - Badges: `<span class="b w">WIRED</span>`, `b h` HALF-BUILT, `b p` PLANNED, `b g` GHOST, `b ok` for passing tests, `b n` for neutral.
- **Mind Map panel** (`section.panel#mm`): `<div id="mm-filters"></div>`, a status legend (below), `<div id="mm-wrap"><svg id="mm-svg"></svg><div id="mm-tip"></div></div>`, and one line telling the reader to go left to right from the start column to the end column.
- **Current State panel** (`section.panel#cs`): one intro line (for example "Every stage of the workflow, top to bottom. Green runs today, orange is built but not proven, red is not built; dashed red ghosts are leftovers, shown but not counted."), then `<div id="cs-wrap"><svg …></svg></div>`. Don't draw the SVG by hand: write the stages to `docs/<name>.stages.json` and run `python3 <skill folder>/scripts/cs_svg.py docs/<name>.stages.json` to get the SVG (format in the script header, layout in `references/current-state.md`). Every node is one stage in the score, planned ones included; ghosts are shown but not counted. Put ghosts in one last section (`LEFTOVERS (NOT COUNTED)`); the script draws it without arrows.
- A `<script>` defining the mind map data, then `<!--MINDMAP-JS-->`, then a small script for tab switching that calls `drawMindMap()` when the Mind Map tab opens.

### Mind map data

```js
const COLS = [                       // left to right; every node id appears in exactly one column
  ['Start: you', ['you','app','web'], 'start'],
  ['Collect', ['api','queue']],
  …,
  ['End: you', ['you2'], 'end'],
  ['Not built yet', ['weekly'], 'planned'],
];
const N = [ // [id, label, kind, status, plain English, technical]
  ['you','You upload','you','w','Where it all starts: …','—'],
  ['store','Photo store','store','w','Where the files land …','38,420 photos · S3'],
];
const E = [['you','app'], ['app','api'], …];   // forward = left to right; edges into an earlier column draw as dotted loops
```

Kinds: `you`, `source`, `step` (collection), `store`, `engine` (processing jobs), `output`, `search`, `monitor`, `planned`. They set the shape (store = circle, search = diamond, everything else = square; `you` is larger, bold and yellow). Colour also follows the kind (see Design); a small dot shows status (green live, orange half-built, red ghost); planned nodes are hollow and dashed. Put the person or trigger in the first column and the result in a later column, both marked `start` / `end`, so the reader always sees where it begins and ends. Group columns by stage in the order the work happens; keep each column under ~12 nodes (split a crowded stage in two).

Legend snippet for the Mind Map tab:

```html
<div class="legend"><span><i style="background:var(--yellow)"></i>You</span><span><i style="background:var(--k-source)"></i>Source</span><span><i style="background:var(--k-step)"></i>Collection</span><span><i style="background:var(--k-store);border-radius:50%!important"></i>Store</span><span><i style="background:var(--k-engine)"></i>Processing</span><span><i style="background:var(--k-output)"></i>Output</span><span><i style="background:var(--k-search);transform:rotate(45deg) scale(.8)"></i>Search</span><span><i style="background:var(--k-monitor)"></i>Monitoring</span><span><i style="outline:1px dashed var(--muted)"></i>Not built</span><span>· dot: <b style="color:var(--ok)">●</b> live <b style="color:var(--part)">●</b> half-built <b style="color:var(--stop)">●</b> ghost</span></div>
```

## Step 3: Build, check, publish

1. `python3 <skill folder>/scripts/build_page.py docs/<name>.content.html docs/<name>.html`. This adds the theme CSS, the fonts and the shared mind map code.
2. Look at it once: a screenshot of each tab, then fix what's visibly wrong and stop. The page loads d3 and the fonts from CDNs, so the browser needs network access. With Playwright:
   ```
   python3 -c "import asyncio;from playwright.async_api import async_playwright as A
   async def m():
     async with A() as p:
       b=await p.chromium.launch();g=await b.new_page(viewport={'width':1300,'height':1000});await g.goto('file://'+__import__('os').path.abspath('docs/<name>.html'))
       for t in ('doc','mm','cs'):
         await g.click(f'[data-t={t}]');await g.wait_for_timeout(800);await g.screenshot(path=f'tab-{t}.png',full_page=True)
       await b.close()
   asyncio.run(m())"
   ```
   If `playwright` isn't installed, run the same code with `uv run --with playwright python -c "…"` (first time only: `uv run --with playwright playwright install chromium`), or use Node Playwright (`npx playwright`) with the same steps.
3. Publish with the Artifact tool (same URL as before if `docs/.truth-seeker.json` has one) and update that file.
   No way to publish: give the user the path to `docs/<name>.html`; it opens in any browser.

## Design: Signal theme (full colour, dark)

These pages carry a lot of information, so colour is used for separation and focus: each colour has one job, and the jobs never overlap. Keep it full colour; a monochrome theme loses the separation.

| Job | Token | Hex |
|---|---|---|
| Page / cards / code well | `--ground` / `--raised` / `--sunk` | #0D0D0E / #17171A / #08080A |
| Lines | `--line` / `--line2` | #26262A / #3A3A3F |
| Text / secondary / tertiary | `--text` / `--muted` / `--dim` | #F4F4F0 / #8C8C88 / #5E5E5B |
| Brand emphasis: start and end, tabs, headings accent | `--yellow` | #FFC400 |
| Status LIVE / WIRED | `--ok` | #4CD38A |
| Status HALF-BUILT / PARTIAL | `--part` | #F49122 |
| Status NONE / GHOST / problems | `--stop` | #FF5B45 |
| Kind: source | `--k-source` | #F6BBF7 |
| Kind: collection step | `--k-step` | #10D5D2 |
| Kind: store / data | `--k-store` | #EE8E6A |
| Kind: processing job | `--k-engine` | #34D4AB |
| Kind: output | `--k-output` | #DFF25C |
| Kind: search | `--k-search` | #869D96 |
| Kind: monitoring | `--k-monitor` | #BDBAB2 |

In the mind map, a node's colour and shape tell its kind and the small dot tells its status; in Current State, badges use the status colours and node tints follow the kind (processing mint, gates yellow, trigger blossom, system neutral).

Type: Inter Tight weight 800 with tight tracking for headings and the body; Source Serif 4 for lead paragraphs; JetBrains Mono for labels, badges, paths and data (all free Google Fonts; `TRUTH_SEEKER_FONTS` can embed your own). Square corners everywhere.

## Update mode

When the page already exists and the user asks to refresh it ("update the system map", "refresh the badges"):
- Re-run the audit, then edit `docs/<name>.content.html`.
- Current State: change the `status` values in `docs/<name>.stages.json` and rebuild the SVG with `cs_svg.py`; positions, labels and arrows stay because they come from the order. Only restructure it if asked.
- Mind map: update statuses, add new parts in the right column, drop removed parts (mention them under Contradictions and ghosts).
- Rebuild, look once, publish to the same URL.

## Rules

- Never document what doesn't exist; planned things are marked planned.
- Privacy: never put secrets, tokens, personal data or private client data in the page, and don't copy names from a project's private rules (people, legal matters, off-limits subjects) into the Rules table; describe them generally ("off-limits subjects").
- Test counts and data are real and current, from runs and files, never guessed.
- All three tabs agree: a WIRED module in the doc is LIVE in Current State and a solid node in the map.
- Plain English (short sentences, no jargon up front); technical detail goes after "─" or in `.tech`.
- Flag ghosts and contradictions with the file that proves them.

#!/usr/bin/env python3
"""Build the Current State flowchart SVG from a list of stages (see references/current-state.md).

Usage: cs_svg.py STAGES.json [OUT.svg]        (prints the <svg> to stdout when OUT is left out)

STAGES.json:
{
  "aria": "Current state of the Lumen repo",   optional accessible name for the SVG
  "title": "Coverage summary",                 optional heading of the scoreboard
  "loop": {"label": "next upload → next night", "from": "5 · WHAT YOU SEE"},
                    optional dashed loop arrow on the right edge, from the last row of the named section back to the
                    first row (a plain string = the label, starting from the last section that isn't all NONE)
  "sections": [
    {"label": "1 · YOU UPLOAD", "nodes": [ {...}, {...} ]},               one row of 1–3 nodes
    {"label": "2 · PROCESS", "rows": [ [ {...}, {...} ], [ {...} ] ]},     several rows under one label
    {"divider": "BACK TO YOU"},                                          a yellow dotted divider; arrows run through it
    ...
  ]
}
Node: {"name": "Upload API", "status": "LIVE", "kind": "processing", "text": "plain English", "tech": "file · test · run",
       "inner": ["build", "sign", "verify", "install"]}      inner = optional steps drawn as small boxes with arrows
status: LIVE | PARTIAL | NONE | GHOST   (WIRED, HALF-BUILT and PLANNED are accepted as aliases). GHOST is shown but not
        counted as a stage. kind: trigger | processing | gate | system (default system).
Arrows fan out from every box of a row to every box of the next row; they are dashed when any box above isn't LIVE.
Rows made only of GHOST nodes get no arrows: put leftovers in a last section such as "LEFTOVERS (NOT COUNTED)".
Update mode: change "status" and rebuild; positions come from the order, so nothing else moves.
"""
import html
import json
import pathlib
import sys

W, PAD, GAP = 680, 20, 16
SANS = 'Inter Tight, Helvetica Neue, Arial, sans-serif'
MONO = 'JetBrains Mono, monospace'
KIND = {'processing': ('rgba(52,212,171,0.07)', 'rgba(52,212,171,0.45)', '#34D4AB'),
        'gate':       ('rgba(255,196,0,0.07)', 'rgba(255,196,0,0.5)', '#FFC400'),
        'trigger':    ('rgba(246,187,247,0.08)', '#F6BBF7', '#F4F4F0'),
        'system':     ('rgba(244,244,240,0.03)', '#3A3A3F', '#F4F4F0')}
BADGE = {'LIVE': ('#4CD38A', 34, 1.0), 'PARTIAL': ('#F49122', 52, 0.6), 'NONE': ('#FF5B45', 34, 0.35), 'GHOST': ('#FF5B45', 40, 0.5)}
ALIAS = {'WIRED': 'LIVE', 'HALF-BUILT': 'PARTIAL', 'HALF BUILT': 'PARTIAL', 'PLANNED': 'NONE'}
WRAP = {1: 95, 2: 52, 3: 33}
TECH = {1: 110, 2: 58, 3: 36}
WARN = []


def esc(s):
    return html.escape(str(s), quote=True)


def wrap(text, n, max_lines, what=''):
    lines, line = [], ''
    for w in str(text).split():
        t = f'{line} {w}'.strip()
        if len(t) > n and line:
            lines.append(line)
            line = w
        else:
            line = t
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        WARN.append(f'cut to {max_lines} lines: {what}')
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:n - 1].rstrip() + '…'
    return lines


def status_of(nd):
    s = str(nd.get('status', '')).strip().upper()
    s = ALIAS.get(s, s)
    if s not in BADGE:
        sys.exit(f'error: unknown status {nd.get("status")!r} on node {nd.get("name")!r} (use LIVE, PARTIAL, NONE or GHOST)')
    return s


def node(x, y, w, n_cols, nd):
    status = status_of(nd)
    fill, stroke, title_col = KIND.get(nd.get('kind', 'system'), KIND['system'])
    bcol, bw, op = BADGE[status]
    name = nd.get('name', '')
    title = wrap(name, max(8, int((w - bw - 30) / 7)), 2, f'title of {name}')
    desc = wrap(nd.get('text', ''), WRAP[n_cols], 3, f'text of {name}')
    tech = wrap(nd.get('tech', ''), TECH[n_cols], 2, f'tech of {name}') if nd.get('tech') else []
    inner = nd.get('inner') or []
    h = 22 + 15 * len(title) + 13 * len(desc) + (34 if inner else 0) + 13 * len(tech) + 6
    out = [f'<!-- {esc(name)} — {status} -->', f'<g opacity="{op}">',
           f'<rect x="{x}" y="{y}" width="{w}" height="@H@" fill="{fill}" stroke="{stroke}"'
           + (' stroke-dasharray="4 3"' if status in ('NONE', 'GHOST') else '') + '/>']
    if status == 'GHOST':
        out.append(f'<rect x="{x + 8}" y="{y + 8}" width="{bw}" height="13" fill="none" stroke="{bcol}" stroke-dasharray="2 2"/>')
        out.append(f'<text x="{x + 8 + bw / 2}" y="{y + 17.5}" font-family="{MONO}" font-size="8" font-weight="700" fill="{bcol}" text-anchor="middle">GHOST</text>')
    else:
        out.append(f'<rect x="{x + 8}" y="{y + 8}" width="{bw}" height="13" fill="{bcol}"/>')
        out.append(f'<text x="{x + 8 + bw / 2}" y="{y + 17.5}" font-family="{MONO}" font-size="8" font-weight="700" fill="#0D0D0E" text-anchor="middle">{status}</text>')
    ty = y + 19
    for i, line in enumerate(title):
        out.append(f'<text x="{x + 16 + bw}" y="{ty}" font-size="12" font-weight="600" fill="{title_col}">{esc(line)}</text>')
        ty += 15
    ty += 4
    for line in desc:
        out.append(f'<text x="{x + 10}" y="{ty}" font-size="10" fill="#F4F4F0">{esc(line)}</text>')
        ty += 13
    if inner:                                          # compound node: inner steps joined by arrows
        n = len(inner)
        iw = (w - 20 - 14 * (n - 1)) / n
        iy = ty - 2
        for i, step in enumerate(inner):
            ix = x + 10 + i * (iw + 14)
            out.append(f'<rect x="{ix:.1f}" y="{iy}" width="{iw:.1f}" height="20" fill="#17171A" stroke="#3A3A3F"/>')
            out.append(f'<text x="{ix + iw / 2:.1f}" y="{iy + 13}" font-family="{MONO}" font-size="8.5" fill="{title_col}" text-anchor="middle">{esc(step)}</text>')
            if i < n - 1:
                ax = ix + iw
                out.append(f'<path d="M{ax + 2:.1f} {iy + 10} L{ax + 12:.1f} {iy + 10}" stroke="#5E5E5B" fill="none"/>')
                out.append(f'<path d="M{ax + 8:.1f} {iy + 7} L{ax + 12:.1f} {iy + 10} L{ax + 8:.1f} {iy + 13}" stroke="#5E5E5B" fill="none"/>')
        ty += 34
    for line in tech:
        out.append(f'<text x="{x + 10}" y="{ty + 3}" font-family="{MONO}" font-size="8.5" fill="#5E5E5B">{esc(line)}</text>')
        ty += 13
    out.append('</g>')
    return out, h, status


def fan(tops, bottoms, y1, y2, solid, divider=None):
    """Arrows from the bottom centre of each box above to the top centre of each box below, through a shared bus."""
    col, dash = ('#5E5E5B', '') if solid else ('#3A3A3F', ' stroke-dasharray="4 3"')
    out = []
    if len(tops) == 1 and len(bottoms) == 1 and abs(tops[0] - bottoms[0]) < 1:
        out.append(f'<path d="M{tops[0]} {y1} L{tops[0]} {y2}" stroke="{col}" fill="none"{dash}/>')
    else:
        bus = y1 + (y2 - y1) * (.35 if divider is None else .2)
        for x in tops:
            out.append(f'<path d="M{x} {y1} L{x} {bus}" stroke="{col}" fill="none"{dash}/>')
        xs = tops + bottoms
        out.append(f'<path d="M{min(xs)} {bus} L{max(xs)} {bus}" stroke="{col}" fill="none"{dash}/>')
        for x in bottoms:
            out.append(f'<path d="M{x} {bus} L{x} {y2}" stroke="{col}" fill="none"{dash}/>')
    for x in bottoms:
        out.append(f'<path d="M{x - 4} {y2 - 5} L{x} {y2} L{x + 4} {y2 - 5}" stroke="{col}" fill="none"/>')
    return out + (divider or [])           # divider plate on top, so the line runs behind its label


def rows_of(sec):
    rows = sec.get('rows') or ([sec['nodes']] if 'nodes' in sec else [])
    out = []
    for r in rows:
        if len(r) > 3:
            WARN.append(f'row with {len(r)} nodes in "{sec.get("label", "")}" split into rows of 3')
        out += [r[i:i + 3] for i in range(0, len(r), 3)]
    return out


def round_pct(counts, total):                          # largest remainder, so the three add up to 100
    if not total:
        return {k: 0 for k in counts}
    raw = {k: 100 * v / total for k, v in counts.items()}
    pct = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - pct[k], reverse=True)[:100 - sum(pct.values())]:
        pct[k] += 1
    return pct


def build(data):
    body, y = [], 10
    counts = {'LIVE': 0, 'PARTIAL': 0, 'NONE': 0, 'GHOST': 0}
    prev = None                     # (bottom y, centres, all live)
    pending_divider = None
    row_spans = []                  # (section label, row top, row bottom, statuses)
    for sec in data['sections']:
        if 'divider' in sec:
            pending_divider = sec['divider']
            continue
        label = sec.get('label', '')
        for ri, row in enumerate(rows_of(sec)):
            gap = 30 if pending_divider is None else 58
            show_label = ri == 0 and label
            ghost_row = all(status_of(nd) == 'GHOST' for nd in row)
            if prev is not None:
                n = len(row)
                w = (W - 2 * PAD - GAP * (n - 1)) / n
                centres = [round(PAD + i * (w + GAP) + w / 2, 1) for i in range(n)]
                div = None
                if pending_divider is not None:
                    dy = y + gap / 2
                    lw = len(pending_divider) * 7 + 20
                    div = [f'<path d="M{PAD} {dy} L{W - PAD} {dy}" stroke="#FFC400" stroke-dasharray="2 3"/>',
                           f'<rect x="{W / 2 - lw / 2}" y="{dy - 8}" width="{lw}" height="16" fill="#0D0D0E"/>',
                           f'<text x="{W / 2}" y="{dy + 3}" font-family="{MONO}" font-size="9" letter-spacing="1.5" fill="#FFC400" text-anchor="middle">{esc(pending_divider)}</text>']
                if ghost_row or prev[3]:              # leftovers are not steps: no arrows into, between or out of them
                    body += div or []
                else:
                    body += fan(prev[1], centres, prev[0], y + gap - (4 if show_label else 0), prev[2], div)
                y += gap
            pending_divider = None
            if show_label:
                body.append(f'<text x="{PAD}" y="{y + 12}" font-family="{MONO}" font-size="9" letter-spacing="1.5" fill="#8C8C88">{esc(label)}</text>')
                y += 20
            n = len(row)
            w = (W - 2 * PAD - GAP * (n - 1)) / n
            parts, heights, statuses, centres = [], [], [], []
            for i, nd in enumerate(row):
                x = round(PAD + i * (w + GAP), 1)
                p, h, st = node(x, y, round(w, 1), n, nd)
                parts.append(p)
                heights.append(h)
                statuses.append(st)
                centres.append(round(x + w / 2, 1))
            hmax = max(heights)
            for p in parts:
                body += [line.replace('@H@', str(hmax)) for line in p]
            for st in statuses:
                counts[st] += 1
            row_spans.append((label, y, y + hmax, statuses))
            prev = (y + hmax, centres, all(st == 'LIVE' for st in statuses), ghost_row)
            y += hmax
    # loop arrow on the right edge
    loop = data.get('loop')
    if loop and row_spans:
        if isinstance(loop, str):
            loop = {'label': loop}
        src = None
        if loop.get('from'):
            src = [r for r in row_spans if r[0] == loop['from']]
            if not src:
                WARN.append(f'loop "from" section {loop["from"]!r} not found; using the last built section')
        if not src:
            src = [r for r in row_spans if any(s in ('LIVE', 'PARTIAL') for s in r[3])]
        a = (src[-1][1] + src[-1][2]) / 2
        b = (row_spans[0][1] + row_spans[0][2]) / 2
        lx = W - 6
        body.append(f'<path d="M{W - PAD} {a} L{lx} {a} L{lx} {b} L{W - PAD + 4} {b}" stroke="#3A3A3F" stroke-dasharray="4 3" fill="none"/>')
        body.append(f'<path d="M{W - PAD + 8} {b - 4} L{W - PAD + 4} {b} L{W - PAD + 8} {b + 4}" stroke="#3A3A3F" fill="none"/>')
        mid, tl = (a + b) / 2, len(loop.get('label', '')) * 5.2 + 10
        body.append(f'<rect x="{lx - 6}" y="{mid - tl / 2}" width="12" height="{tl}" fill="#0D0D0E"/>')
        body.append(f'<text x="{lx + 3}" y="{mid}" font-family="{MONO}" font-size="8.5" fill="#5E5E5B" text-anchor="middle" transform="rotate(-90 {lx + 3} {mid})">{esc(loop.get("label", ""))}</text>')
    # scoreboard
    total = counts['LIVE'] + counts['PARTIAL'] + counts['NONE']
    pct = round_pct({k: counts[k] for k in ('LIVE', 'PARTIAL', 'NONE')}, total)
    y += 40
    body.append(f'<text x="{PAD}" y="{y}" font-size="14" font-weight="800" fill="#F4F4F0">{esc(data.get("title", "Coverage summary"))} · {total} workflow stages</text>')
    y += 18
    for k, col in (('LIVE', '#4CD38A'), ('PARTIAL', '#F49122'), ('NONE', '#FF5B45')):
        bw = round(480 * counts[k] / total, 1) if total else 0
        body += [f'<text x="{PAD}" y="{y + 11}" font-family="{MONO}" font-size="9" fill="#8C8C88">{k}</text>',
                 f'<rect x="80" y="{y}" width="480" height="14" fill="#17171A" stroke="#26262A"/>',
                 f'<rect x="80" y="{y}" width="{bw}" height="14" fill="{col}"/>',
                 f'<text x="570" y="{y + 11}" font-family="{MONO}" font-size="9" fill="#F4F4F0">{counts[k]} / {total} · {pct[k]}%</text>']
        y += 24
    ghosts = f' · {counts["GHOST"]} ghost{"s" if counts["GHOST"] != 1 else ""} (not counted)' if counts['GHOST'] else ''
    body.append(f'<text x="{PAD}" y="{y + 4}" font-size="10" fill="#8C8C88">{pct["LIVE"]}% fully operational · {pct["PARTIAL"]}% built, not yet proven · {pct["NONE"]}% not started{ghosts}</text>')
    y += 18
    x = PAD
    for label, fill, stroke in (('Live', '#4CD38A', None), ('Partial', '#F49122', None), ('None', '#FF5B45', None), ('Ghost', 'none', '#FF5B45'),
                                ('Processing', 'rgba(52,212,171,0.25)', '#34D4AB'), ('Gate', 'rgba(255,196,0,0.25)', '#FFC400'),
                                ('System', 'rgba(244,244,240,0.06)', '#3A3A3F'), ('Trigger', 'rgba(246,187,247,0.2)', '#F6BBF7')):
        body.append(f'<rect x="{x}" y="{y}" width="10" height="10" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + '/>')
        body.append(f'<text x="{x + 15}" y="{y + 9}" font-family="{MONO}" font-size="9" fill="#8C8C88">{label}</text>')
        x += 15 + len(label) * 6 + 22
    H = int(y + 30)
    aria = esc(data.get('aria', 'Current state flowchart'))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="{aria}">\n'
            f'<rect width="{W}" height="{H}" fill="#0D0D0E"/>\n' + '\n'.join(body) + '\n</svg>\n'), counts


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    svg, counts = build(json.loads(pathlib.Path(sys.argv[1]).read_text()))
    for w in WARN:
        print('warning: ' + w, file=sys.stderr)
    if len(sys.argv) > 2:
        pathlib.Path(sys.argv[2]).write_text(svg)
        print(f'wrote {sys.argv[2]} · ' + ' '.join(f'{k} {v}' for k, v in counts.items()), file=sys.stderr)
    else:
        sys.stdout.write(svg)


if __name__ == '__main__':
    main()

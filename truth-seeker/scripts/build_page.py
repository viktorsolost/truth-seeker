#!/usr/bin/env python3
"""Assemble a Truth Seeker page.

Usage: build_page.py CONTENT.html OUT.html
  CONTENT.html  the page body the agent wrote: <title>, header, the three tab panels, and a <script> that defines
                COLS, N and E (mind map data). It must contain the markers <!--BRAND-CSS--> (where the styles go)
                and <!--MINDMAP-JS--> (where the shared mind map code goes, after the data script).
  OUT.html      self-contained result: theme CSS, d3 from cdnjs, mindmap.js inlined.

Fonts: Inter Tight, Source Serif 4 and JetBrains Mono load from Google Fonts. To embed your own instead, set
TRUTH_SEEKER_FONTS to a folder holding sans.woff2 and/or serif.woff2 (variable fonts work best). Only embed fonts
whose licence allows it if you share the page.
"""
import base64
import os
import pathlib
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
D3 = '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>'
GOOGLE = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600;800&family=Source+Serif+4:wght@400;600'
          '&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">')


def font_css():
    folder = os.environ.get('TRUTH_SEEKER_FONTS')
    if not folder:
        return ''
    out = []
    for fam, name, weight in (('Custom Sans', 'sans.woff2', '300 800'), ('Custom Serif', 'serif.woff2', '200 700')):
        f = pathlib.Path(folder).expanduser() / name
        if f.exists():
            b64 = base64.b64encode(f.read_bytes()).decode()
            out.append(f'@font-face{{font-family:"{fam}";src:url(data:font/woff2;base64,{b64}) format("woff2");'
                       f'font-weight:{weight};font-display:swap}}')
    return '\n'.join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    body = pathlib.Path(sys.argv[1]).read_text()
    for marker in ('<!--BRAND-CSS-->', '<!--MINDMAP-JS-->'):
        if marker not in body:
            sys.exit(f'missing marker {marker} in {sys.argv[1]}')
    css = (SKILL / 'assets/brand.css').read_text().replace('/*FONTS*/', font_css())
    js = (SKILL / 'assets/mindmap.js').read_text()
    page = body.replace('<!--BRAND-CSS-->', f'{GOOGLE}\n{D3}\n<style>\n{css}\n</style>', 1)
    page = page.replace('<!--MINDMAP-JS-->', f'<script>\n{js}\n</script>', 1)
    if '<meta charset' not in page[:500]:
        page = '<meta charset="utf-8">\n' + page
    pathlib.Path(sys.argv[2]).write_text(page)
    print(f'wrote {sys.argv[2]} ({len(page) // 1024} KB)')


if __name__ == '__main__':
    main()

"""Rendert dark_mode.svg und light_mode.svg: ASCII-Portraet ueber die volle Breite,
darunter Sprachen und Kontakt. Nur Standardbibliothek.

  python3 scripts/render.py
"""
import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = 9          # px, Portraet
CHAR_W = FONT * 0.602
LINE_H = CHAR_W * 2  # passt zum Seitenverhaeltnis aus make_ascii.py
PAD = 24

FOOTER = [
    ("TypeScript · Python · SQL · React · Next.js · Node.js", "value"),
    ("contact@nikola-vujovic.de", "key"),
]

THEMES = {
    "dark": dict(bg="#161b22", ascii="#c9d1d9", key="#ffa657", value="#a5d6ff", rule="#30363d"),
    "light": dict(bg="#f6f8fa", ascii="#24292f", key="#953800", value="#0a3069", rule="#d0d7de"),
}


def render(theme):
    c = THEMES[theme]
    art = (ROOT / f"ascii_{theme}.txt").read_text().rstrip("\n").split("\n")
    cols = max(len(l) for l in art)
    width = round(PAD * 2 + cols * CHAR_W)
    art_h = len(art) * LINE_H
    rule_y = PAD + art_h + 20
    height = round(rule_y + 24 + len(FOOTER) * 26 + PAD - 6)
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        "font-family=\"ConsolasFallback,Consolas,'SF Mono',Menlo,monospace\">",
        f'<rect width="{width}" height="{height}" rx="15" fill="{c["bg"]}"/>',
        f'<text font-size="{FONT}" fill="{c["ascii"]}" xml:space="preserve">',
    ]
    for i, line in enumerate(art):
        out.append(f'<tspan x="{PAD}" y="{PAD + (i + 1) * LINE_H - 2:.1f}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<line x1="{PAD}" x2="{width - PAD}" y1="{rule_y:.1f}" y2="{rule_y:.1f}" stroke="{c["rule"]}"/>')
    for i, (txt, cls) in enumerate(FOOTER):
        y = rule_y + 30 + i * 26
        out.append(f'<text x="{width / 2:.1f}" y="{y:.1f}" font-size="16" text-anchor="middle" '
                   f'fill="{c[cls]}">{escape(txt)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


for theme in THEMES:
    (ROOT / f"{theme}_mode.svg").write_text(render(theme))
print("SVGs geschrieben")

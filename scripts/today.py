"""Rendert dark_mode.svg und light_mode.svg (neofetch-Stil) mit aktuellen GitHub-Zahlen.

Lokal:   GITHUB_TOKEN=$(gh auth token) python3 scripts/today.py
Action:  laeuft taeglich ueber .github/workflows/build.yml
Nur Standardbibliothek, damit die Action ohne pip install auskommt.
"""
import datetime as dt
import json
import os
import pathlib
import urllib.request
from xml.sax.saxutils import escape

LOGIN = "NikolaVujovic1988"
CODING_SINCE = 2007
ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDTH_CHARS = 56  # Breite der Infospalte in Zeichen

THEMES = {
    "dark": dict(bg="#161b22", border="#30363d", text="#c9d1d9", key="#ffa657",
                 value="#a5d6ff", dots="#616e7f", accent="#3fb950", ascii="#c9d1d9"),
    "light": dict(bg="#f6f8fa", border="#d0d7de", text="#24292f", key="#953800",
                  value="#0a3069", dots="#c2cfde", accent="#1a7f37", ascii="#24292f"),
}


def gql(query, variables):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


def stats():
    base = gql(
        """query($login: String!) {
          user(login: $login) {
            createdAt
            followers { totalCount }
            repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
              totalCount nodes { stargazerCount }
            }
            repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
            pullRequests { totalCount }
            contributionsCollection { contributionCalendar { totalContributions } }
          }
        }""",
        {"login": LOGIN},
    )["user"]

    # Beitraege ueber alle Jahre seit Kontoerstellung aufsummieren
    start = dt.datetime.fromisoformat(base["createdAt"].replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)
    total = 0
    year_from = start
    while year_from < now:
        year_to = min(year_from + dt.timedelta(days=365), now)
        total += gql(
            """query($login: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                  contributionCalendar { totalContributions }
                }
              }
            }""",
            {"login": LOGIN, "from": year_from.isoformat(), "to": year_to.isoformat()},
        )["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        year_from = year_to

    return {
        "repos": base["repositories"]["totalCount"],
        "contributed": base["repositoriesContributedTo"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in base["repositories"]["nodes"]),
        "followers": base["followers"]["totalCount"],
        "prs": base["pullRequests"]["totalCount"],
        "total": total,
        "year": base["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    }


def uptime():
    today = dt.date.today()
    years = today.year - CODING_SINCE
    return f"coding since {CODING_SINCE} ({years} years)"


def build_lines(s):
    """Jede Zeile ist eine Liste von (Klasse, Text)-Segmenten."""
    def kv(key, value):
        dots = WIDTH_CHARS - len(key) - len(value) - 4
        return [("dots", ". "), ("key", key), ("text", ":"),
                ("dots", " " + "." * max(dots, 1) + " "), ("value", value)]

    def header(title, top=False):
        prefix = "" if top else "- "
        rule = "-" * (WIDTH_CHARS - len(prefix) - len(title) - 1)
        return [("text", prefix), ("key" if top else "text", title), ("dots", " " + rule)]

    def pair(k1, v1, k2, v2):
        left = f"{k1}: "
        right_key = f" | {k2}: "
        dots2 = 14 - len(v2)
        dots1 = WIDTH_CHARS - len(left) - len(v1) - len(right_key) - len(v2) - max(dots2, 1) - 4
        return [("dots", ". "), ("key", k1), ("text", ":"), ("dots", " " + "." * max(dots1, 1) + " "),
                ("value", v1), ("text", " | "), ("key", k2), ("text", ":"),
                ("dots", " " + "." * max(dots2, 1) + " "), ("value", v2)]

    blank = []
    return [
        header("nikola@vujovic", top=True),
        kv("OS", "macOS, Linux"),
        kv("Uptime", uptime()),
        kv("Host", "Wuppertal, Germany (from Serbia)"),
        kv("Role", "Senior Developer"),
        kv("Focus", "Web Apps, Automation & AI"),
        kv("IDE", "VS Code, Claude Code"),
        blank,
        kv("Languages.Programming", "TypeScript, Python, SQL"),
        kv("Languages.Frameworks", "React, Next.js, Node.js"),
        kv("Languages.Tools", "PostgreSQL, Supabase, n8n"),
        kv("Languages.Real", "Serbian, German, English"),
        blank,
        header("Contact"),
        kv("Email", "contact@nikola-vujovic.de"),
        kv("Website", "nikola-vujovic.de"),
        kv("LinkedIn", "nikola-vujovic"),
        blank,
        header("GitHub Stats"),
        pair("Repos", f"{s['repos']} {{Contributed: {s['contributed']}}}", "Stars", str(s["stars"])),
        pair("Contributions", f"{s['total']:,}", "Followers", str(s["followers"])),
        pair("Pull Requests", str(s["prs"]), "Last year", f"{s['year']:,}"),
    ]


def render(theme, lines, ascii_art):
    c = THEMES[theme]
    font, lh, pad = 16, 20, 24
    a_font, a_lh = 10, 12  # Portraet kleiner gesetzt, damit das Gesicht erkennbar bleibt
    ascii_x, info_x = pad, 500
    a_height, i_height = len(ascii_art) * a_lh, len(lines) * lh
    height = pad * 2 + max(a_height, i_height)
    i_top = pad + max(0, (a_height - i_height) // 2)
    width = info_x + int(WIDTH_CHARS * 9.7) + pad
    out = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,\'SF Mono\',Menlo,monospace" '
        f'width="{width}px" height="{height}px" font-size="{font}px">',
        "<style>",
        f".text{{fill:{c['text']}}} .key{{fill:{c['key']}}} .value{{fill:{c['value']}}} "
        f".dots{{fill:{c['dots']}}} .accent{{fill:{c['accent']}}} .ascii{{fill:{c['ascii']}}}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
        f'<text x="{ascii_x}" y="{pad + a_lh}" class="ascii" font-size="{a_font}px" xml:space="preserve">',
    ]
    for i, line in enumerate(ascii_art):
        out.append(f'<tspan x="{ascii_x}" y="{pad + (i + 1) * a_lh - 2}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{info_x}" y="{i_top + lh - 4}" class="text" xml:space="preserve">')
    for i, segs in enumerate(lines):
        y = i_top + (i + 1) * lh - 4
        if not segs:
            continue
        body = "".join(f'<tspan class="{cls}">{escape(t)}</tspan>' for cls, t in segs)
        out.append(f'<tspan x="{info_x}" y="{y}">{body}</tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    lines = build_lines(stats())
    for theme in THEMES:
        ascii_art = (ROOT / f"ascii_{theme}.txt").read_text().rstrip("\n").split("\n")
        (ROOT / f"{theme}_mode.svg").write_text(render(theme, lines, ascii_art))
    print("SVGs aktualisiert")


if __name__ == "__main__":
    main()

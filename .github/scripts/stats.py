"""Genera assets/stats.svg con datos de la API de GitHub (sin servicios externos).

Uso: GH_TOKEN=... python .github/scripts/stats.py [usuario]
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USER = sys.argv[1] if len(sys.argv) > 1 else "Justin-Ocana"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = Path(__file__).resolve().parents[2] / "assets" / "stats.svg"

SANS = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'SFMono-Regular', Menlo, monospace"
VIOLET, CYAN = "#8B5CF6", "#22D3EE"
PANEL, LINE, MUTED = "#161b22", "#30363d", "#9da7b3"

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#8b6bd0", "Java": "#b07219", "C#": "#38b349", "GDScript": "#4f86b8", "C++": "#f34b7d",
}
NOISE = {"Dockerfile", "Shell", "Batchfile", "PowerShell", "Makefile"}


def api(path, data=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(data).encode() if data else None,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-stats",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    repos = [r for r in repos if not r["fork"]]
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    active = sum(1 for r in repos if datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) >= cutoff)

    weights = {}
    for r in repos:
        langs = {k: v for k, v in api(f"/repos/{USER}/{r['name']}/languages").items() if k not in NOISE}
        total = sum(langs.values())
        for k, v in langs.items():
            weights[k] = weights.get(k, 0) + v / total  # cada repo pesa igual

    contributions = None
    if TOKEN:
        q = {"query": 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions}}}}',
             "variables": {"u": USER}}
        res = api("/graphql", q)
        contributions = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    return len(repos), active, weights, contributions


def render(n_repos, active, weights, contributions):
    W, H = 880, 250
    tiles = [
        ("REPOS PÚBLICOS", str(n_repos), VIOLET),
        ("ACTIVOS ESTE MES", str(active), CYAN),
        ("LENGUAJES", str(len(weights)), "#F472B6"),
        ("CONTRIBUCIONES · 1 AÑO", "—" if contributions is None else f"{contributions:,}", "#FB923C"),
    ]
    body = ""
    tw, gap = 205, 20
    for i, (label, val, col) in enumerate(tiles):
        x = i * (tw + gap)
        body += (
            f'<g transform="translate({x},0)"><rect x="0.5" y="0.5" width="{tw-1}" height="92" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
            f'<rect x="16" y="0" width="44" height="3" rx="1.5" fill="{col}"/>'
            f'<text x="18" y="40" font-size="32" font-weight="800" fill="#ffffff">{escape(val)}</text>'
            f'<text style="font-family:{MONO}" x="18" y="68" font-size="10.5" fill="{col}" letter-spacing="1.1">{escape(label)}</text></g>'
        )

    total = sum(weights.values()) or 1
    top = sorted(weights.items(), key=lambda kv: -kv[1])[:6]
    shown = sum(v for _, v in top)
    bar_x, bar_w, bar_y = 0, W, 130
    body += f'<text style="font-family:{MONO}" x="0" y="118" font-size="11" fill="{MUTED}" letter-spacing="1.6">LENGUAJES MÁS USADOS</text>'
    body += f'<clipPath id="bar"><rect x="0" y="{bar_y}" width="{bar_w}" height="14" rx="7"/></clipPath><g clip-path="url(#bar)">'
    x = bar_x
    for name, v in top:
        w = v / shown * bar_w
        body += f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="14" fill="{LANG_COLORS.get(name, "#8b949e")}"/>'
        x += w
    body += "</g>"
    cols = 3
    for i, (name, v) in enumerate(top):
        cx = (i % cols) * (W / cols)
        cy = 178 + (i // cols) * 30
        pct = v / total * 100
        body += (
            f'<circle cx="{cx+7:.0f}" cy="{cy-4}" r="6" fill="{LANG_COLORS.get(name, "#8b949e")}"/>'
            f'<text x="{cx+22:.0f}" y="{cy}" font-size="14" font-weight="600" fill="#e6edf3">{escape(name)}</text>'
            f'<text style="font-family:{MONO}" x="{cx+W/cols-40:.0f}" y="{cy}" font-size="12" fill="{MUTED}" text-anchor="end">{pct:.0f}%</text>'
        )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Estadísticas de GitHub: {n_repos} repos, {active} activos este mes, {len(weights)} lenguajes">'
        f"<style>text{{font-family:{SANS}}}</style>{body}</svg>"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(*collect()), encoding="utf-8")
    print("ok", OUT)

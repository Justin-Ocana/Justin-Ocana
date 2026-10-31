"""Genera los SVG estáticos/animados del README (banner, secciones, tarjetas, stack, contacto).

Uso: python .github/scripts/build_assets.py
Salida: assets/*.svg
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[2] / "assets"
OUT.mkdir(exist_ok=True)

SANS = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'SFMono-Regular', Menlo, monospace"
VIOLET, CYAN, PINK = "#8B5CF6", "#22D3EE", "#F472B6"
BG, PANEL, LINE, MUTED = "#0d1117", "#161b22", "#30363d", "#9da7b3"


def svg(w, h, body, defs="", extra_style=""):
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
        f"<defs>{defs}<style>text{{font-family:{SANS}}}.m{{font-family:{MONO}}}{extra_style}</style></defs>"
        f"{body}</svg>"
    )


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("ok", name)


def wave_path(y, amp, period, n):
    d = f"M0,{y} Q{period/4},{y-amp} {period/2},{y}"
    for _ in range(n):
        d += f" T{period*(1+_*0.5)+period/2},{y}"
    return d


def sine(y, amp, period, periods, bottom):
    d = f"M0,{y}"
    x = 0
    up = True
    for _ in range(periods * 2):
        cx = x + period / 4
        d += f" Q{cx},{y - amp if up else y + amp} {x + period/2},{y}"
        x += period / 2
        up = not up
    d += f" L{x},{bottom} L0,{bottom} Z"
    return d


# ---------------------------------------------------------------- banner
def typing_group(i, text, x0, y, char_w, total=12.0, per=4.0):
    n = len(text)
    full = n * char_w
    s = i * per
    t1, t2, t3 = s + 1.7, s + 3.5, s + 3.9
    pts = [(0, 0)]
    if s > 0:
        pts.append((s, 0))
    pts += [(t1, 1), (t2, 1), (t3, 0), (total, 0)]
    kt = ";".join(f"{t/total:.4f}" for t, _ in pts)
    wv = ";".join(f"{f*full:.1f}" for _, f in pts)
    tv = ";".join(f"{f*full:.1f} 0" for _, f in pts)
    vis = [(0, 1 if s == 0 else 0)]
    if s > 0:
        vis.append((s, 1))
    vis += [(t3 + 0.1, 0), (total, 0)]
    vkt = ";".join(f"{t/total:.4f}" for t, _ in vis)
    vvl = ";".join(str(v) for _, v in vis)
    clip = (
        f'<clipPath id="tc{i}"><rect x="{x0}" y="{y-28}" width="0" height="40">'
        f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{wv}"/>'
        f"</rect></clipPath>"
    )
    text_el = (
        f'<text class="m" x="{x0}" y="{y}" font-size="{char_w/0.6:.1f}" fill="#e6edf3" '
        f'textLength="{full:.1f}" lengthAdjust="spacing" clip-path="url(#tc{i})">{escape(text)}</text>'
    )
    cursor = (
        f'<g opacity="0"><animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" '
        f'calcMode="discrete" keyTimes="{vkt}" values="{vvl}"/>'
        f'<g><animateTransform attributeName="transform" type="translate" dur="{total}s" repeatCount="indefinite" '
        f'keyTimes="{kt}" values="{tv}"/>'
        f'<rect x="{x0 + 2}" y="{y-26}" width="3" height="32" rx="1.5" fill="{CYAN}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite" calcMode="discrete"/>'
        f"</rect></g></g>"
    )
    return clip, text_el + cursor


def banner():
    W, H = 1200, 380
    phrases = ["construyo webs que escalan", "hago juegos y mods", "creo apps para TV y móvil"]
    char_w = 15.6
    clips, texts = "", ""
    for i, p in enumerate(phrases):
        c, t = typing_group(i, p, 104, 306, char_w)
        clips += c
        texts += t

    chips = ""
    for (cx, cy, label, d) in [(850, 96, "Web", 0), (1020, 158, "Juegos", -1.2), (880, 262, "Apps", -2.4)]:
        chips += (
            f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="5s" begin="{d}s" repeatCount="indefinite"/>'
            f'<rect x="{cx}" y="{cy}" width="118" height="42" rx="13" fill="#ffffff" fill-opacity="0.07" stroke="#ffffff" stroke-opacity="0.22"/>'
            f'<circle cx="{cx+20}" cy="{cy+21}" r="5" fill="{CYAN if label!="Juegos" else PINK}"/>'
            f'<text x="{cx+36}" y="{cy+27}" font-size="16" fill="#e6edf3" font-weight="600">{label}</text></g>'
        )

    rings = ""
    for r, dur, rev in [(70, 18, 1), (118, 26, -1), (166, 38, 1)]:
        a, b = (0, 360) if rev == 1 else (360, 0)
        rings += (
            f'<g><animateTransform attributeName="transform" type="rotate" from="{a} 940 190" to="{b} 940 190" dur="{dur}s" repeatCount="indefinite"/>'
            f'<ellipse cx="940" cy="190" rx="{r*1.55:.0f}" ry="{r}" fill="none" stroke="url(#brand)" stroke-width="1.4" stroke-opacity="0.55" stroke-dasharray="3 7"/>'
            f'<circle cx="{940 + r*1.55:.0f}" cy="190" r="{5 if r != 118 else 4}" fill="{[CYAN, PINK, VIOLET][[70,118,166].index(r)]}"/></g>'
        )

    body = f"""
<clipPath id="round"><rect width="{W}" height="{H}" rx="22"/></clipPath>
{clips}
<g clip-path="url(#round)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <g filter="url(#blur)">
    <circle cx="160" cy="70" r="190" fill="{VIOLET}" fill-opacity="0.55">
      <animate attributeName="cx" values="160;330;160" dur="14s" repeatCount="indefinite"/>
      <animate attributeName="cy" values="70;140;70" dur="14s" repeatCount="indefinite"/>
    </circle>
    <circle cx="1040" cy="330" r="210" fill="{CYAN}" fill-opacity="0.38">
      <animate attributeName="cx" values="1040;880;1040" dur="16s" repeatCount="indefinite"/>
    </circle>
    <circle cx="760" cy="40" r="120" fill="{PINK}" fill-opacity="0.25">
      <animate attributeName="cy" values="40;120;40" dur="12s" repeatCount="indefinite"/>
    </circle>
  </g>
  {rings}
  <circle cx="940" cy="190" r="20" fill="url(#brand)"/>
  <circle cx="940" cy="190" r="34" fill="none" stroke="{CYAN}" stroke-opacity="0.5">
    <animate attributeName="r" values="26;48;26" dur="4s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="4s" repeatCount="indefinite"/>
  </circle>
  {chips}
  <g opacity="0.9">
    <path d="{sine(334, 16, 600, 4, H)}" fill="url(#brand)" fill-opacity="0.22">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="-600 0" dur="14s" repeatCount="indefinite"/>
    </path>
    <path d="{sine(348, 12, 400, 6, H)}" fill="url(#brand)" fill-opacity="0.16">
      <animateTransform attributeName="transform" type="translate" from="-400 0" to="0 0" dur="10s" repeatCount="indefinite"/>
    </path>
  </g>
  <text x="70" y="140" font-size="76" font-weight="800" fill="#ffffff" letter-spacing="-1">Justin <tspan fill="url(#brand)">Ocaña</tspan></text>
  <text x="72" y="196" font-size="30" font-weight="600" fill="#e6edf3">Full Stack Developer <tspan fill="{MUTED}" font-weight="400">→</tspan> <tspan fill="url(#brand)">Product Engineer</tspan></text>
  <text x="72" y="238" font-size="17" fill="{MUTED}">17 años  ·  Ecuador  ·  abierto a oportunidades</text>
  <text class="m" x="72" y="306" font-size="26" fill="{CYAN}">&gt;</text>
  {texts}
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21" fill="none" stroke="#ffffff" stroke-opacity="0.12"/>
</g>"""
    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d17"/><stop offset="1" stop-color="#150f2e"/></linearGradient>
<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#ffffff" stroke-opacity="0.05"/></pattern>
<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="70"/></filter>"""
    write("banner.svg", svg(W, H, body, defs).replace('role="img"', 'role="img" aria-label="Justin Ocaña, Full Stack Developer rumbo a Product Engineer"'))


# ---------------------------------------------------------------- secciones
def section(name, title, tag):
    W, PH, TOP = 880, 56, 30
    H = TOP + PH + 12
    tw = len(title) * 14.2 + 22
    body = f"""<g transform="translate(0,{TOP})">
<rect x="0.5" y="0.5" width="{W-1}" height="{PH-1}" rx="14" fill="{PANEL}" stroke="{LINE}"/>
<rect x="0" y="0" width="7" height="{PH}" rx="3" fill="url(#b)"/>
<text x="30" y="35" font-size="19" font-weight="700" fill="#ffffff" letter-spacing="2.2">{escape(title.upper())}</text>
<rect x="{30 + tw}" y="27" width="{W - 30 - tw - 120}" height="2" rx="1" fill="url(#l)"/>
<text class="m" x="{W-24}" y="34" font-size="13" fill="{MUTED}" text-anchor="end">{escape(tag)}</text></g>"""
    defs = f"""<linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<linearGradient id="l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.8"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>"""
    write(name, svg(W, H, body, defs).replace('role="img"', f'role="img" aria-label="{escape(title)}"'))


# ---------------------------------------------------------------- qué hago
def about():
    W, H = 880, 190
    cards = [
        ("Web y backend", ["Apps completas, de la base de", "datos a la pantalla."], "Django · React · PostgreSQL", VIOLET, "web"),
        ("Juegos y mods", ["Mundos que se juegan: motores,", "mods y sistemas en tiempo real."], "Godot · Unity · Fabric", PINK, "game"),
        ("Apps y TV", ["Launchers, PWAs y extensiones", "pensadas para usarse todos los días."], "Android · PWA · Chrome", CYAN, "tv"),
    ]
    body, cw, gap = "", 280, 20
    for i, (t, lines, stack, col, icon) in enumerate(cards):
        x = i * (cw + gap)
        if icon == "web":
            ic = f'<rect x="0" y="4" width="40" height="30" rx="5" fill="none" stroke="{col}" stroke-width="2.4"/><path d="M0 13H40" stroke="{col}" stroke-width="2.4"/><circle cx="7" cy="8.5" r="1.8" fill="{col}"/><circle cx="13" cy="8.5" r="1.8" fill="{col}"/><path d="M13 22l-4 4 4 4M27 22l4 4-4 4" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        elif icon == "game":
            ic = f'<rect x="0" y="8" width="42" height="26" rx="13" fill="none" stroke="{col}" stroke-width="2.4"/><path d="M12 15v12M6 21h12" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/><circle cx="29" cy="18" r="2.4" fill="{col}"/><circle cx="35" cy="24" r="2.4" fill="{col}"/>'
        else:
            ic = f'<rect x="0" y="4" width="42" height="26" rx="5" fill="none" stroke="{col}" stroke-width="2.4"/><path d="M13 36h16M21 30v6" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/><path d="M17 11l10 6-10 6z" fill="{col}"/>'
        body += f"""
<g transform="translate({x},0)">
  <rect x="0.5" y="0.5" width="{cw-1}" height="{H-1}" rx="16" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="24" y="0" width="64" height="3" rx="1.5" fill="{col}"/>
  <g transform="translate(24,28)">{ic}</g>
  <text x="24" y="98" font-size="20" font-weight="700" fill="#ffffff">{t}</text>
  <text x="24" y="124" font-size="13.5" fill="{MUTED}">{escape(lines[0])}</text>
  <text x="24" y="143" font-size="13.5" fill="{MUTED}">{escape(lines[1])}</text>
  <text class="m" x="24" y="172" font-size="12" fill="{col}">{escape(stack)}</text>
</g>"""
    write("about.svg", svg(W, H, body).replace('role="img"', 'role="img" aria-label="Qué hago: web y backend, juegos y mods, apps y TV"'))


# ---------------------------------------------------------------- tarjetas
def iso_cube(cx, cy, s, top, left, right):
    k = 0.866
    t = f"{cx},{cy-s} {cx+k*s},{cy-s/2} {cx},{cy} {cx-k*s},{cy-s/2}"
    l = f"{cx-k*s},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx-k*s},{cy+s/2}"
    r = f"{cx+k*s},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx+k*s},{cy+s/2}"
    return f'<polygon points="{l}" fill="{left}"/><polygon points="{r}" fill="{right}"/><polygon points="{t}" fill="{top}"/>'


def art_lightcode(w, h):
    cx, cy, s = w / 2, h / 2 + 16, 30
    k = 0.866

    def pos(i, j, kk):
        return cx + (i - j) * k * s, cy + (i + j) * s / 2 - kk * s

    out = ""
    cubes = [(0, 0, 0, "g"), (1, 0, 0, "g"), (0, 1, 0, "g"), (1, 1, 0, "g"), (0, 0, 1, "g"), (1, 1, 1, "p")]
    cubes.sort(key=lambda c: (c[2], c[0] + c[1]))
    for (i, j, kk, c) in cubes:
        x, y = pos(i, j, kk)
        x -= k * s * 0.5 * 0
        pal = ("#6EE7B7", "#059669", "#047857") if c == "g" else ("#C4B5FD", "#7C3AED", "#5B21B6")
        cube = iso_cube(x, y, s, *pal)
        if c == "p":
            cube = f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="3.2s" repeatCount="indefinite"/>{cube}</g>'
        out += cube
    out += f'<circle cx="{w-34}" cy="34" r="3" fill="#6EE7B7"><animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle>'
    out += f'<text class="m" x="18" y="{h-18}" font-size="11" fill="#6EE7B7" fill-opacity="0.8">$ rcon give Steve</text>'
    return out


def art_aurora(w, h):
    out = f"""
<g filter="url(#soft)">
  <path d="M-20,{h*0.55} C{w*0.2},{h*0.1} {w*0.5},{h*0.9} {w+20},{h*0.3}" fill="none" stroke="#2DD4BF" stroke-width="34" stroke-linecap="round" opacity="0.75">
    <animate attributeName="d" dur="7s" repeatCount="indefinite" values="M-20,{h*0.55} C{w*0.2},{h*0.1} {w*0.5},{h*0.9} {w+20},{h*0.3};M-20,{h*0.4} C{w*0.25},{h*0.8} {w*0.55},{h*0.1} {w+20},{h*0.5};M-20,{h*0.55} C{w*0.2},{h*0.1} {w*0.5},{h*0.9} {w+20},{h*0.3}"/>
  </path>
  <path d="M-20,{h*0.7} C{w*0.3},{h*0.3} {w*0.6},{h*0.8} {w+20},{h*0.45}" fill="none" stroke="#A78BFA" stroke-width="26" stroke-linecap="round" opacity="0.6">
    <animate attributeName="d" dur="9s" repeatCount="indefinite" values="M-20,{h*0.7} C{w*0.3},{h*0.3} {w*0.6},{h*0.8} {w+20},{h*0.45};M-20,{h*0.5} C{w*0.3},{h*0.9} {w*0.6},{h*0.2} {w+20},{h*0.65};M-20,{h*0.7} C{w*0.3},{h*0.3} {w*0.6},{h*0.8} {w+20},{h*0.45}"/>
  </path>
  <path d="M-20,{h*0.3} C{w*0.3},{h*0.6} {w*0.7},{h*0.1} {w+20},{h*0.2}" fill="none" stroke="#F472B6" stroke-width="18" stroke-linecap="round" opacity="0.5"/>
</g>"""
    tw, gap = 34, 10
    x0 = (w - (3 * tw + 2 * gap)) / 2
    for i, col in enumerate(["#ffffff", "#ffffff", "#ffffff"]):
        big = i == 1
        s = tw + (6 if big else 0)
        x = x0 + i * (tw + gap) - (3 if big else 0)
        y = h - 54 - (3 if big else 0)
        out += f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="10" fill="#ffffff" fill-opacity="{0.28 if big else 0.14}" stroke="#ffffff" stroke-opacity="{0.7 if big else 0.3}"/>'
    out += f'<rect x="{w/2-30}" y="{h-12}" width="60" height="3" rx="1.5" fill="#ffffff" fill-opacity="0.6"/>'
    return out


def art_cn(w, h):
    out = ""
    sq = 20
    for r in range(0, int(h / sq) + 1):
        for c in range(0, int(w / sq) + 1):
            if (r + c) % 2 == 0:
                out += f'<rect x="{c*sq}" y="{r*sq}" width="{sq}" height="{sq}" fill="#ffffff" fill-opacity="0.045"/>'
    tx, ty, tw, th = w / 2 - 54, h / 2 - 40, 108, 84
    out += f'<path d="M{w/2-14},{ty} L{w/2-30},{ty-22} M{w/2+14},{ty} L{w/2+30},{ty-22}" stroke="#FB923C" stroke-width="3" stroke-linecap="round"/>'
    out += f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="#111827" stroke="#FB923C" stroke-width="3"/>'
    cols = ["#ffffff", "#FACC15", "#22D3EE", "#4ADE80", "#F472B6", "#EF4444", "#3B82F6"]
    bw = (tw - 28 - 28) / 7
    for i, c in enumerate(cols):
        out += f'<rect x="{tx+12+i*bw}" y="{ty+12}" width="{bw}" height="{th-36}" fill="{c}" opacity="0.92"/>'
    out += f'<rect x="{tx+12}" y="{ty+12}" width="{tw-24-28}" height="{th-36}" rx="3" fill="none"/>'
    out += f'<circle cx="{tx+tw-14}" cy="{ty+22}" r="5" fill="#FB923C"/><circle cx="{tx+tw-14}" cy="{ty+40}" r="5" fill="#FB923C" fill-opacity="0.5"/>'
    out += f'<text class="m" x="{tx+12}" y="{ty+th-7}" font-size="10" fill="#FB923C" font-weight="700">24/7</text>'
    out += f'<rect x="{w-38}" y="{h-84}" width="22" height="58" rx="8" fill="#1f2937" stroke="#ffffff" stroke-opacity="0.4"/><circle cx="{w-27}" cy="{h-70}" r="4" fill="#EF4444"/><circle cx="{w-27}" cy="{h-56}" r="3" fill="#ffffff" fill-opacity="0.6"/><circle cx="{w-27}" cy="{h-46}" r="3" fill="#ffffff" fill-opacity="0.6"/><circle cx="{w-27}" cy="{h-36}" r="3" fill="#ffffff" fill-opacity="0.6"/>'
    return out


def art_lemon(w, h):
    cx, cy = w / 2 - 14, h / 2 + 4
    out = f'<circle cx="{cx}" cy="{cy}" r="62" fill="#FACC15" fill-opacity="0.16"/>'
    out += f'<g transform="rotate(-24 {cx} {cy})"><ellipse cx="{cx}" cy="{cy}" rx="46" ry="34" fill="#FACC15"/><ellipse cx="{cx-46}" cy="{cy}" rx="7" ry="5" fill="#EAB308"/><ellipse cx="{cx+46}" cy="{cy}" rx="7" ry="5" fill="#EAB308"/><ellipse cx="{cx-12}" cy="{cy-12}" rx="18" ry="8" fill="#FEF08A" fill-opacity="0.7"/></g>'
    out += f'<path d="M{cx+22},{cy-34} q18,-24 40,-14 q-8,22 -40,14z" fill="#4ADE80"/>'
    rx, ry = w - 66, h - 112
    out += f'<path d="M{rx},{ry} h46 v78 l-6,-5 l-6,5 l-6,-5 l-6,5 l-6,-5 l-6,5 l-4,-4 z" fill="#ffffff" fill-opacity="0.92"/>'
    for i, lw in enumerate([30, 22, 30, 16]):
        out += f'<rect x="{rx+8}" y="{ry+10+i*12}" width="{lw}" height="3" rx="1.5" fill="#CA8A04" fill-opacity="{0.9 if i != 3 else 1}"/>'
    return out


def art_academic(w, h):
    out = ""
    x, y, cw, ch = 20, 30, w - 40, h - 60
    out += f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.22"/>'
    for i, (done, lw) in enumerate([(True, 70), (True, 52), (False, 62)]):
        ry = y + 20 + i * 34
        if done:
            out += f'<rect x="{x+14}" y="{ry}" width="18" height="18" rx="5" fill="#60A5FA"/><path d="M{x+18},{ry+9} l4,4 l7,-8" fill="none" stroke="#0b1020" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            out += f'<rect x="{x+14}" y="{ry}" width="18" height="18" rx="5" fill="none" stroke="#60A5FA" stroke-width="2"/>'
        out += f'<rect x="{x+42}" y="{ry+4}" width="{lw}" height="5" rx="2.5" fill="#ffffff" fill-opacity="{0.45 if done else 0.8}"/>'
        out += f'<rect x="{x+42}" y="{ry+13}" width="{lw*0.6}" height="3" rx="1.5" fill="#ffffff" fill-opacity="0.25"/>'
    for i, col in enumerate(["#F472B6", "#34D399", "#FACC15"]):
        out += f'<circle cx="{x+cw-16-i*15}" cy="{y-2}" r="11" fill="{col}" stroke="#0b1020" stroke-width="3"/>'
    return out


def card(name, w, h, art_w, a1, a2, art_bg, art_fn, tag, title, lines, chips, soft=False):
    # texto
    tx = art_w + 26
    ty = 52
    text = f'<text class="m" x="{tx}" y="{ty}" font-size="11" fill="{a1}" letter-spacing="1.6">{escape(tag)}</text>'
    text += f'<text x="{tx}" y="{ty+32}" font-size="{26 if w > 600 else 23}" font-weight="800" fill="#ffffff">{escape(title)}</text>'
    for i, ln in enumerate(lines):
        text += f'<text x="{tx}" y="{ty+60+i*20}" font-size="13.5" fill="{MUTED}">{escape(ln)}</text>'
    cx, cy = tx, h - 52
    for c in chips:
        cw = len(c) * 6.6 + 20
        text += (
            f'<rect x="{cx}" y="{cy}" width="{cw:.0f}" height="24" rx="12" fill="{a1}" fill-opacity="0.14" stroke="{a1}" stroke-opacity="0.45"/>'
            f'<text class="m" x="{cx+cw/2:.0f}" y="{cy+16}" font-size="11" fill="#e6edf3" text-anchor="middle">{escape(c)}</text>'
        )
        cx += cw + 8
    text += f'<text x="{w-24}" y="{ty}" font-size="12.5" font-weight="600" fill="{a1}" text-anchor="end">ver repo →</text>'

    soft_filter = '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>'
    body = f"""
<clipPath id="cc"><rect width="{w}" height="{h}" rx="20"/></clipPath>
<clipPath id="ca"><rect width="{art_w}" height="{h}"/></clipPath>
<g clip-path="url(#cc)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <circle cx="{w-30}" cy="10" r="140" fill="{a1}" fill-opacity="0.10"/>
  <g clip-path="url(#ca)">
    <rect width="{art_w}" height="{h}" fill="{art_bg}"/>
    {art_fn(art_w, h)}
  </g>
  <rect x="{art_w}" y="0" width="1" height="{h}" fill="{a1}" fill-opacity="0.35"/>
  {text}
</g>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="19" fill="none" stroke="url(#bd)" stroke-width="1.6"/>"""
    defs = f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a1}" stop-opacity="0.75"/><stop offset="1" stop-color="{a2}" stop-opacity="0.35"/></linearGradient>{soft_filter}'
    write(name, svg(w, h, body, defs).replace('role="img"', f'role="img" aria-label="{escape(title)}: {escape(" ".join(lines))}"'))


def cards():
    card("card-lightcode-core.svg", 880, 220, 270, "#34D399", "#8B5CF6", "#06201a", art_lightcode,
         "E-COMMERCE · MINECRAFT", "LightCode-Core",
         ["Tienda para servidores de Minecraft: catálogo, panel de admin",
          "y entrega automática de las compras al juego por RCON.",
          "Open source, listo para desplegar con Docker."],
         ["Django", "React", "Docker", "MIT"])
    card("card-aurora-tv.svg", 440, 210, 150, "#2DD4BF", "#A78BFA", "#0a1224", art_aurora,
         "ANDROID · FIRE TV", "Aurora TV",
         ["Launcher cinematográfico inspirado", "en tvOS: luz ambiental por app y", "vidrio líquido. Nativo, ~150 KB."],
         ["Java", "Android TV"])
    card("card-cn-recreations.svg", 440, 210, 150, "#FB923C", "#F472B6", "#0b0b10", art_cn,
         "EXTENSIÓN · REACT", "CN Recreations",
         ["Canal 24/7 estilo Cartoon Network", "desde HBO Max, con control", "remoto web."],
         ["JavaScript", "Chrome", "React"])
    card("card-lemon-pos.svg", 440, 210, 150, "#FACC15", "#FB923C", "#1a1405", art_lemon,
         "POS · ECUADOR", "Lemon POS",
         ["Sistema de punto de venta web", "para pequeños negocios de", "Ecuador."],
         ["Django", "Python", "Docker"])
    card("card-academic-task-manager.svg", 440, 210, 150, "#60A5FA", "#8B5CF6", "#0b1020", art_academic,
         "DJANGO · EQUIPOS", "Academic Tasks",
         ["Gestor de tareas académicas con", "grupos colaborativos y flujo de", "solicitudes."],
         ["Django", "Python"])


# ---------------------------------------------------------------- stack
def stack():
    W = 880
    groups = [
        ("WEB", VIOLET, ["Python", "Django", "React", "TypeScript", "JavaScript", "HTML", "CSS"]),
        ("DATOS E INFRA", CYAN, ["PostgreSQL", "Docker", "Linux", "Git", "GitHub Actions"]),
        ("JUEGOS", PINK, ["Godot", "GDScript", "Unity", "C#", "Fabric"]),
        ("MÓVIL Y TV", "#FB923C", ["Java", "Android", "PWA", "Fire TV"]),
    ]
    body, y = "", 0
    for label, col, items in groups:
        body += f'<text class="m" x="4" y="{y+22}" font-size="12" fill="{col}" letter-spacing="1.8">{escape(label)}</text>'
        x = 4
        for it in items:
            w = len(it) * 8.2 + 38
            body += (
                f'<g transform="translate({x},{y+34})"><rect width="{w:.0f}" height="34" rx="17" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.45"/>'
                f'<circle cx="17" cy="17" r="4.5" fill="{col}"/>'
                f'<text x="30" y="22" font-size="14" font-weight="600" fill="#e6edf3">{escape(it)}</text></g>'
            )
            x += w + 10
        y += 82
    H = y
    inner = f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>'
    inner += f'<g transform="translate(20,10)">{body}</g>'
    write("stack.svg", svg(W, H + 10, f'<rect width="{W}" height="{H+10}" rx="18" fill="{PANEL}" stroke="{LINE}"/><g transform="translate(16,8)">{body}</g>').replace('role="img"', 'role="img" aria-label="Stack: Python, Django, React, TypeScript, PostgreSQL, Docker, Godot, Unity, Java, Android"'))


# ---------------------------------------------------------------- contacto y pie
def pill(name, label, value, col, icon):
    W, H = 280, 64
    ic = {
        "mail": f'<rect x="0" y="3" width="26" height="19" rx="4" fill="none" stroke="{col}" stroke-width="2.2"/><path d="M1 6l12 9 12-9" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>',
        "web": f'<circle cx="13" cy="13" r="11" fill="none" stroke="{col}" stroke-width="2.2"/><ellipse cx="13" cy="13" rx="5" ry="11" fill="none" stroke="{col}" stroke-width="2"/><path d="M2 13h22" stroke="{col}" stroke-width="2"/>',
        "git": f'<circle cx="13" cy="13" r="11" fill="none" stroke="{col}" stroke-width="2.2"/><path d="M9 20v-5l4-4 4 4v5M9 12l2-3h4l2 3" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>',
    }[icon]
    body = f"""
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{PANEL}" stroke="{LINE}"/>
<rect x="0" y="14" width="4" height="{H-28}" rx="2" fill="{col}"/>
<g transform="translate(24,19)">{ic}</g>
<text class="m" x="66" y="27" font-size="11" fill="{col}" letter-spacing="1.4">{escape(label)}</text>
<text x="66" y="46" font-size="14" font-weight="600" fill="#e6edf3">{escape(value)}</text>"""
    write(name, svg(W, H, body).replace('role="img"', f'role="img" aria-label="{escape(label)}: {escape(value)}"'))


def footer():
    W, H = 1200, 110
    body = f"""
<clipPath id="r"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <path d="{sine(60, 14, 600, 4, H)}" fill="url(#brand)" fill-opacity="0.25"><animateTransform attributeName="transform" type="translate" from="0 0" to="-600 0" dur="14s" repeatCount="indefinite"/></path>
  <path d="{sine(74, 10, 400, 6, H)}" fill="url(#brand)" fill-opacity="0.18"><animateTransform attributeName="transform" type="translate" from="-400 0" to="0 0" dur="10s" repeatCount="indefinite"/></path>
  <text x="{W/2}" y="46" font-size="22" font-weight="600" fill="#e6edf3" text-anchor="middle">Diseño primero, <tspan fill="url(#brand)">código después.</tspan></text>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21" fill="none" stroke="#ffffff" stroke-opacity="0.12"/>
</g>"""
    defs = f"""<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0d17"/><stop offset="1" stop-color="#150f2e"/></linearGradient>
<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>"""
    write("footer.svg", svg(W, H, body, defs).replace('role="img"', 'role="img" aria-label="Diseño primero, código después."'))


if __name__ == "__main__":
    banner()
    section("h-about.svg", "Qué hago", "01")
    section("h-projects.svg", "Proyectos destacados", "02")
    section("h-stack.svg", "Stack", "03")
    section("h-activity.svg", "Actividad", "04")
    section("h-contact.svg", "Hablemos", "05")
    about()
    cards()
    stack()
    pill("contact-email.svg", "EMAIL", "justin.ocana.molina@gmail.com", VIOLET, "mail")
    pill("contact-portfolio.svg", "PORTAFOLIO", "justin-ocana.github.io", CYAN, "web")
    pill("contact-github.svg", "GITHUB", "@Justin-Ocana", PINK, "git")
    footer()

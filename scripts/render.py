"""Gera os SVGs animados do perfil: cabeçalho, cartão e mapa de contribuições.

Só biblioteca padrão. Roda local ou na Action diária:
    python3 scripts/render.py            # tudo
    python3 scripts/render.py --offline  # sem buscar contribuições
"""
import datetime as dt
import html
import re
import sys
import urllib.request
from pathlib import Path

USER = "lavinialencar"
OUT = Path(__file__).resolve().parent.parent / "assets"
MONO = "'IBM Plex Mono','SFMono-Regular',Menlo,Consolas,monospace"
SANS = "Archivo,'Helvetica Neue',Arial,sans-serif"

# Paleta de lavinialencar.com.br (assets/tokens.css): carvão com o azul sinal.
BG = "#1A1C21"       # carvao2
EDGE = "#2A2D34"     # regua-esc
INK = "#F2F2F0"      # claro
MUTED = "#B8BAC2"    # claro-esc
BLUES = ["#2A2D34", "#1D2E85", "#2B41B8", "#8497EE", "#CBD3F6"]  # vazio, sinal escuro, sinal, sinal-cl, sinal claro
ACCENT = "#8497EE"   # sinal-cl

W = 840


def write(name, svg):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")
    print("ok", name)


# ---------------------------------------------------------------- cabeçalho
PHRASES = ["Analytics engineer", "Maker from the Amazon", "Code, electronics, 3D printing"]


def header():
    fs, cw = 24, 24 * 0.6  # monoespaçada: largura do caractere ~0.6 do corpo
    x0, y0 = 72, 132
    slot, cycle = 4.0, 4.0 * len(PHRASES)
    type_t, hold_t, del_t = 1.3, 2.9, 3.4

    def pct(t):
        return f"{t / cycle * 100:.3f}%"

    css, texts, cursor_frames = [], [], []
    for i, p in enumerate(PHRASES):
        s = i * slot
        w = len(p) * cw
        n = len(p)
        css.append(
            f"@keyframes t{i}{{0%{{width:0}}"
            f"{pct(s)}{{width:0;animation-timing-function:steps({n},end)}}"
            f"{pct(s + type_t)}{{width:{w:.1f}px}}"
            f"{pct(s + hold_t)}{{width:{w:.1f}px;animation-timing-function:steps({n},end)}}"
            f"{pct(s + del_t)}{{width:0}}100%{{width:0}}}}"
            f"#c{i} rect{{animation:t{i} {cycle}s linear infinite;animation-delay:-{type_t}s}}"
        )
        cursor_frames += [
            f"{pct(s)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}",
            f"{pct(s + type_t)}{{transform:translateX({w:.1f}px)}}",
            f"{pct(s + hold_t)}{{transform:translateX({w:.1f}px);animation-timing-function:steps({n},end)}}",
            f"{pct(s + del_t)}{{transform:translateX(0)}}",
        ]
        texts.append(
            f'<clipPath id="c{i}"><rect x="{x0}" y="{y0 - fs}" height="{fs + 8}" width="0"/></clipPath>'
            f'<text x="{x0}" y="{y0}" clip-path="url(#c{i})" class="ty">{html.escape(p)}</text>'
        )
    css.append("@keyframes cur{0%{transform:translateX(0)}" + "".join(cursor_frames) + "100%{transform:translateX(0)}}")
    css.append(f".cur{{animation:cur {cycle}s linear infinite;animation-delay:-{type_t}s}}")
    css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur rect{animation:blink 1s step-end infinite}")

    H = 240
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lavínia Alencar: {', '.join(PHRASES)}">
<defs>{GRAIN_DEFS}</defs>
<style>
.cap{{font:600 11px {MONO};fill:{MUTED};letter-spacing:2px}}
.nm{{font:800 54px {SANS};fill:{INK};letter-spacing:-1.5px}}
.pr{{font:500 {fs}px {MONO};fill:{MUTED}}}
.ty{{font:500 {fs}px {MONO};fill:{ACCENT}}}
{''.join(css)}
{RIDGE_CSS}
</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
{ridges(H, x_from=430, rows=16, y_top=58, gap=10, seed=7, peak=(4, 700, 70))}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".5"/>
<text x="{x0 - 2}" y="44" class="cap">BELÉM, PA  ·  1°27′S 48°30′W</text>
<text x="{x0 - 4}" y="104" class="nm">Lavínia Alencar</text>
<text x="{x0 - 26}" y="{y0 + 20}" class="pr">›</text>
<g transform="translate(0,20)">{''.join(texts)}
<g class="cur"><rect x="{x0 + 2}" y="{y0 - fs + 2}" width="3" height="{fs + 2}" fill="{ACCENT}"/></g></g>
</svg>"""
    write("header.svg", svg)


# ---------------------------------------------------------------- ridgelines
# Linhas empilhadas: ao mesmo tempo gráfico de dados, camada de impressão 3D
# e curva de nível de rio. Um trecho claro corre na linha da frente, como o bico.
GRAIN_DEFS = (
    '<filter id="grain" x="0" y="0" width="100%" height="100%">'
    '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
    '<feColorMatrix values="0 0 0 0 .95  0 0 0 0 .95  0 0 0 0 .94  0 0 0 .08 0"/></filter>'
    '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
    '<stop offset=".35" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>'
)
RIDGE_CSS = (
    "@keyframes head{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}"
    ".head{animation:head 7s linear infinite;animation-delay:-2.5s}"
)


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def ridges(h, x_from, rows, y_top, gap, seed, peak=None, amp=34, x_to=None):
    import math
    import random

    rnd = random.Random(seed)
    x_to = x_to or W + 20
    span = x_to - x_from
    xs = [x_from + span * k / 120 for k in range(121)]
    mid = x_from + span * 0.55
    out = []
    front = ""
    for i in range(rows):
        base = y_top + i * gap
        bumps = [(rnd.uniform(x_from + span * .2, x_to - span * .1), rnd.uniform(.3, 1) * amp, rnd.uniform(14, 40))
                 for _ in range(rnd.randint(3, 6))]
        if peak and peak[0] == i:
            bumps.append((peak[1], peak[2], 34))
        pts = []
        for x in xs:
            env = math.exp(-((x - mid) / (span * .42)) ** 2)
            y = sum(a * math.exp(-((x - c) / w) ** 2) for c, a, w in bumps) * env
            y += rnd.uniform(0, 1.6) * env
            pts.append((x, base - y))
        line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        t = i / (rows - 1)
        stroke = _mix("#1D2E85", "#8497EE", t ** 1.2)
        out.append(
            f'<path d="{line} L{x_to},{h + 2} L{x_from},{h + 2}Z" fill="{BG}"/>'
            f'<path d="{line}" fill="none" stroke="{stroke}" stroke-width="{1 + t * .6:.2f}"/>'
        )
        front = line
    head = f'<path class="head" d="{front}" pathLength="1000" fill="none" stroke="#E7EAF8" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="36 964"/>'
    return f'<mask id="m{seed}"><rect x="{x_from}" width="{span}" height="{h}" fill="url(#fade)"/></mask><g mask="url(#m{seed})">{"".join(out)}{head}</g>'


def footer():
    H = 110
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Built with SQL, Python and a 3D printer humming nearby">
<defs>{GRAIN_DEFS}</defs>
<style>{RIDGE_CSS}.q{{font:13px {MONO};fill:{MUTED}}}</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
{ridges(H, x_from=480, rows=7, y_top=50, gap=9, seed=11, amp=22)}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".5"/>
<text x="46" y="{H / 2 + 5}" class="q">built with SQL, Python and a 3D printer humming nearby</text>
</svg>"""
    write("footer.svg", svg)


# ---------------------------------------------------------------- cartão
# Duas colunas no espírito do neofetch: quem sou e com o que trabalho.
WHOAMI = ("lavinia@github", [
    ("Role", "analytics engineer, maker"),
    ("Based", "Belém, Brazilian Amazon"),
    ("Exp", "iFood, Nuvemshop"),
    ("Data", "SQL, Spark, Databricks, Airflow"),
    ("Web", "Astro, Cloudflare Workers"),
    ("Make", "Fusion, OrcaSlicer, electronics"),
    ("AI", "Claude Code, my own skills"),
    ("Site", "lavinialencar.com.br"),
])
SETUP = ("~/setup", [
    ("OS", "macOS, Linux (Windows for games)"),
    ("Laptop", "MacBook Air M4"),
    ("Desktop", "Ryzen 5 5600GT, RTX 5060"),
    ("NAS", "ZimaOS home server, on 24/7"),
    ("Runs", "Docker, self-hosted apps"),
    ("Lab", "mini PC test box, on 24/7"),
    ("Printer", "Bambu Lab P2S + AMS 2 Pro"),
])


def card():
    lh, top, pad = 26, 56, 36
    col_w = (W - 2 * pad) / 2
    rows = max(len(WHOAMI[1]), len(SETUP[1]))
    h = top + (rows + 1) * lh + 24

    def column(x, title, items, t0):
        kw = max(len(k) for k, _ in items) + 1
        out = [
            f'<text x="{x}" y="{top}" class="hd ln" style="animation-delay:{t0:.2f}s">{html.escape(title)}</text>',
            f'<text x="{x}" y="{top + lh}" class="mu ln" style="animation-delay:{t0 + .1:.2f}s">{"-" * len(title)}</text>',
        ]
        for i, (k, v) in enumerate(items):
            y = top + (i + 2) * lh
            d = t0 + 0.2 + i * 0.1
            label = html.escape((k + ":").ljust(kw + 1)).replace(" ", "&#160;")
            out.append(
                f'<text x="{x}" y="{y}" class="ln" style="animation-delay:{d:.2f}s">'
                f'<tspan class="k">{label}</tspan><tspan class="v">{html.escape(v)}</tspan></text>'
            )
        return "".join(out)

    left = column(pad, *WHOAMI, 0.2)
    right = column(pad + col_w + 12, *SETUP, 0.6)
    divider = f'<line x1="{pad + col_w - 6}" y1="{top - 18}" x2="{pad + col_w - 6}" y2="{top + (rows + 1) * lh + 4}" stroke="{EDGE}"/>'
    alt = "; ".join(f"{k}: {v}" for k, v in WHOAMI[1] + SETUP[1])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(alt)}">
<style>
text{{font:13.5px {MONO};fill:{INK}}}
.hd{{fill:{ACCENT};font-weight:700}}
.k{{fill:{ACCENT};font-weight:700}}
.mu{{fill:{MUTED}}}
.v{{fill:{INK}}}
@keyframes glow{{0%,100%{{opacity:1}}40%{{opacity:.25}}}}
.ln{{animation:glow .9s ease-in-out}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{EDGE}"/>
{divider}
{left}
{right}
</svg>"""
    write("card.svg", svg)


# ---------------------------------------------------------------- contribuições
def fetch_contributions():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-art"}
    )
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        n = re.match(r"(\d[\d,]*) contribution", m.group(2))
        counts[m.group(1)] = int(n.group(1).replace(",", "")) if n else 0
    days = []
    for m in re.finditer(r"<td[^>]*ContributionCalendar-day[^>]*>", page):
        tag = m.group(0)
        date = re.search(r'data-date="([^"]+)"', tag)
        if not date:
            continue
        lvl = int(re.search(r'data-level="(\d)"', tag).group(1))
        cid = re.search(r'id="([^"]+)"', tag).group(1)
        days.append((dt.date.fromisoformat(date.group(1)), lvl, counts.get(cid, 0)))
    days.sort()
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    total = int(total.group(1).replace(",", "")) if total else sum(d[2] for d in days)
    return days, total


def contrib():
    days, total = fetch_contributions()
    cell, gap, left, top = 12, 3, 52, 64
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # semana começa no domingo
    cells, months, seen = [], [], set()
    for date, lvl, n in days:
        col = (date - start).days // 7
        row = (date.weekday() + 1) % 7
        x = left + col * (cell + gap)
        y = top + row * (cell + gap)
        delay = (col + row) * 0.018
        cells.append(
            f'<rect class="d" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{BLUES[lvl]}">'
            f"<title>{n} on {date.isoformat()}</title></rect>"
        )
        key = (date.year, date.month)
        if date.day <= 7 and key not in seen and col < 52:
            seen.add(key)
            months.append(f'<text x="{x}" y="{top - 10}" class="mo">{date.strftime("%b")}</text>')
    cols = (days[-1][0] - start).days // 7 + 1
    width = max(W, left + cols * (cell + gap) + 36)
    h = top + 7 * (cell + gap) + 44
    wd = "".join(
        f'<text x="{left - 10}" y="{top + r * (cell + gap) + 10}" class="mo" text-anchor="end">{t}</text>'
        for r, t in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_x = width - 36 - 5 * (cell + gap) - 70
    legend = (
        f'<text x="{legend_x}" y="{h - 18}" class="mo">less</text>'
        + "".join(
            f'<rect x="{legend_x + 34 + k * (cell + gap)}" y="{h - 28}" width="{cell}" height="{cell}" rx="3" fill="{c}"/>'
            for k, c in enumerate(BLUES)
        )
        + f'<text x="{legend_x + 40 + 5 * (cell + gap)}" y="{h - 18}" class="mo">more</text>'
    )
    stamp = dt.date.today().strftime("%d %b %Y")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-label="{total} contributions in the last year">
<style>
.tt{{font:600 15px {SANS};fill:{INK}}}
.mo{{font:11px {SANS};fill:{MUTED}}}
@keyframes glow{{0%,100%{{opacity:1}}40%{{opacity:.2}}}}
.d{{animation:glow 1s ease-in-out}}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{EDGE}"/>
<text x="{left}" y="30" class="tt">{total} contributions in the last year</text>
<text x="{width - 36}" y="30" class="mo" text-anchor="end">updated {stamp}</text>
{''.join(months)}{wd}
{''.join(cells)}
{legend}
</svg>"""
    write("contrib.svg", svg)


if __name__ == "__main__":
    header()
    card()
    footer()
    if "--offline" not in sys.argv:
        contrib()

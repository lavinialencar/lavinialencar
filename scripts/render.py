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
MONO = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

# Paleta azul do padrão visual: degradê de #0F2E57 a #C4D7EE.
BG = "#0A1F3B"
EDGE = "#1E4270"
INK = "#E6EEF8"
MUTED = "#8FA9CB"
BLUES = ["#15355E", "#2F5A8C", "#5E88BC", "#92B3DA", "#C4D7EE"]
ACCENT = "#92B3DA"

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

    H = 230
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lavínia Alencar: {', '.join(PHRASES)}">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A1F3B"/><stop offset=".6" stop-color="#0F2E57"/><stop offset="1" stop-color="#1D4677"/></linearGradient>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<style>
.nm{{font:700 46px {SANS};fill:{INK};letter-spacing:-.5px}}
.pr{{font:500 {fs}px {MONO};fill:{MUTED}}}
.ty{{font:500 {fs}px {MONO};fill:{ACCENT}}}
{''.join(css)}
{WAVE_CSS}
</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{waves(H, 168)}
</g>
<text x="{x0 - 2}" y="84" class="nm">Lavínia Alencar</text>
<text x="{x0 - 26}" y="{y0}" class="pr">›</text>
{''.join(texts)}
<g class="cur"><rect x="{x0 + 2}" y="{y0 - fs + 2}" width="3" height="{fs + 2}" fill="{ACCENT}"/></g>
</svg>"""
    write("header.svg", svg)


# ---------------------------------------------------------------- ondas
WAVE_CSS = (
    "@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-840px)}}"
    ".w1{animation:slide 14s linear infinite}.w2{animation:slide 9s linear infinite reverse}"
    ".w3{animation:slide 20s linear infinite}"
)


def wave_path(base, amp, phase, h):
    # duas voltas de 840px, pra deslizar sem emenda
    pts = [f"M{-840},{h}", f"L{-840},{base}"]
    step = 210
    for k in range(-4, 9):
        x = k * step
        y = base + (amp if (k + phase) % 2 else -amp)
        pts.append(f"Q{x + step / 2},{y} {x + step},{base}")
    pts.append(f"L{8 * step + 210},{h}Z")
    return " ".join(pts)


def waves(h, base, flip=False):
    layers = [(BLUES[1], 12, 0, "w1", 0.55), (BLUES[2], 9, 1, "w2", 0.35), (BLUES[4], 6, 0, "w3", 0.18)]
    out = []
    for i, (c, amp, ph, cls, op) in enumerate(layers):
        b = base + i * 12
        out.append(f'<g class="{cls}"><path d="{wave_path(b, amp, ph, h)}" fill="{c}" opacity="{op}"/></g>')
    g = "".join(out)
    return f'<g transform="translate(0,{h}) scale(1,-1)">{g}</g>' if flip else g


def footer():
    H = 120
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Thanks for stopping by">
<defs><linearGradient id="sea" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0A1F3B"/><stop offset="1" stop-color="#1D4677"/></linearGradient>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<style>{WAVE_CSS}.q{{font:italic 15px {SANS};fill:{INK}}}</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sea)"/>
{waves(H, 58, flip=True)}
</g>
<text x="{W / 2}" y="{H - 26}" text-anchor="middle" class="q">Built with SQL, Python and a 3D printer humming nearby.</text>
</svg>"""
    write("footer.svg", svg)


# ---------------------------------------------------------------- cartão
INFO = [
    ("lavinia@github", None),
    ("-" * 14, None),
    ("Role", "Analytics engineer and maker"),
    ("Based in", "Belém, Brazilian Amazon"),
    ("Experience", "iFood, Nuvemshop"),
    ("Data", "SQL, Spark, Databricks, Airflow"),
    ("Web", "Astro, Cloudflare Pages and Workers"),
    ("Making", "Bambu Lab P2S, Fusion, OrcaSlicer"),
    ("AI", "Claude Code, my own skills"),
    ("Site", "lavinialencar.com.br"),
]
BARS = [3, 5, 4, 7, 6, 9, 8, 11]  # desenho da esquerda: um gráfico de barras


def card():
    lh, top, tx = 26, 52, 330
    rows = len(INFO)
    h = top + rows * lh + 56
    lines = []
    for i, (k, v) in enumerate(INFO):
        y = top + i * lh
        d = 0.35 + i * 0.12
        if v is None:
            cls = "hd" if i == 0 else "mu"
            lines.append(f'<text x="{tx}" y="{y}" class="{cls} ln" style="animation-delay:{d:.2f}s">{html.escape(k)}</text>')
        else:
            lines.append(
                f'<text x="{tx}" y="{y}" class="ln" style="animation-delay:{d:.2f}s">'
                f'<tspan class="k">{html.escape(k)}</tspan><tspan class="mu">: </tspan>'
                f'<tspan class="v">{html.escape(v)}</tspan></text>'
            )
    sw_y = top + rows * lh + 4
    d = 0.35 + rows * 0.12
    swatches = "".join(
        f'<rect x="{tx + k * 30}" y="{sw_y}" width="26" height="14" fill="{c}"/>' for k, c in enumerate(BLUES)
    )

    cell, gap, base, bx = 14, 4, h - 56, 52
    bars = []
    for j, n in enumerate(BARS):
        x = bx + j * (cell + gap)
        for r in range(n):
            y = base - (r + 1) * (cell + gap) + gap
            c = BLUES[min(4, 1 + r * 4 // max(BARS))]
            dl = 0.1 + j * 0.06 + r * 0.035
            bars.append(f'<rect class="px" style="animation-delay:{dl:.2f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Lavínia Alencar, analytics engineer and maker from Belém. Data: SQL, Spark, Databricks, Airflow. Web: Astro, Cloudflare. Making: Bambu Lab P2S, Fusion, OrcaSlicer.">
<style>
text{{font:15px {MONO};fill:{INK}}}
.hd{{fill:{ACCENT};font-weight:700}}
.k{{fill:{ACCENT};font-weight:700}}
.mu{{fill:{MUTED}}}
.v{{fill:{INK}}}
@keyframes glow{{0%,100%{{opacity:1}}40%{{opacity:.25}}}}
.ln{{animation:glow .9s ease-in-out}}
.px{{animation:glow 1.2s ease-in-out 2}}
.sw{{animation:glow 1s ease-in-out;animation-delay:{d:.2f}s}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{EDGE}"/>
{''.join(bars)}
{''.join(lines)}
<g class="sw">{swatches}</g>
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

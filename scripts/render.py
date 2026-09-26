"""Gera os SVGs animados do perfil: cabeçalho, cartão e rodapé.

Só biblioteca padrão. Depois de mudar um texto aqui:
    python3 scripts/render.py
"""
import html
import re
from pathlib import Path

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
PHRASES = ["Analytics engineer", "Code, electronics, 3D printing"]


def header():
    fs, cw = 18, 18 * 0.6  # monoespaçada: largura do caractere ~0.6 do corpo
    x0, y0 = 72, 116
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

    H = 146
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lavínia Alencar: {', '.join(PHRASES)}">
<defs>{GRAIN_DEFS}</defs>
<style>
.cap{{font:600 11px {MONO};fill:{MUTED};letter-spacing:2px}}
.nm{{font:800 54px {SANS};fill:{INK};letter-spacing:-1.5px}}
.pr{{font:500 {fs}px {MONO};fill:{MUTED}}}
.ty{{font:500 {fs}px {MONO};fill:{ACCENT}}}
{''.join(css)}
{NET_CSS}
</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
{network(H, x_from=440, n=38, seed=7)}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".5"/>
<text x="{x0 - 2}" y="25" class="cap">TECHNOLOGY  ·  DESIGN  ·  CREATION  ·  COFFEE</text>
<text x="{x0 - 4}" y="80" class="nm">Lavínia Alencar</text>
<text x="{x0 - 26}" y="{y0}" class="pr">›</text>
<g>{''.join(texts)}
<g class="cur"><rect x="{x0 + 2}" y="{y0 - fs + 2}" width="3" height="{fs + 2}" fill="{ACCENT}"/></g></g>
</svg>"""
    write("header.svg", svg)


# ---------------------------------------------------------------- rede
# Pontos conectados: nós de um grafo de dados. Alguns nós pulsam e um sinal
# claro corre por algumas arestas. O quadro parado já mostra a rede inteira.
GRAIN_DEFS = (
    '<filter id="grain" x="0" y="0" width="100%" height="100%">'
    '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
    '<feColorMatrix values="0 0 0 0 .95  0 0 0 0 .95  0 0 0 0 .94  0 0 0 .08 0"/></filter>'
    '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
    '<stop offset=".4" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>'
)
NET_CSS = (
    "@keyframes run{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}"
    ".sig{animation:run 2.4s linear infinite}"
    "@keyframes beat{0%,100%{opacity:1}50%{opacity:.35}}"
    ".hub{animation:beat 3s ease-in-out infinite}"
)


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def network(h, x_from, n, seed, k=3, min_d=34):
    import math
    import random

    rnd = random.Random(seed)
    x_to = W + 10
    span = x_to - x_from
    pts = []
    tries = 0
    while len(pts) < n and tries < 5000:  # amostragem com distância mínima, pra não embolar
        tries += 1
        x = x_from + span * (rnd.random() ** 0.7)  # mais denso à direita
        y = rnd.uniform(-8, h + 8)
        if all((x - px) ** 2 + (y - py) ** 2 > min_d ** 2 for px, py in pts):
            pts.append((x, y))
    edges = set()
    for i, (x, y) in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:k + 1]
        for j in near:
            edges.add((min(i, j), max(i, j)))
    lines, sigs = [], []
    for e, (i, j) in enumerate(sorted(edges)):
        (x1, y1), (x2, y2) = pts[i], pts[j]
        t = min(1, max(0, ((x1 + x2) / 2 - x_from) / span))
        col = _mix("#2A2D34", "#2B41B8", t)
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="1"/>')
        if rnd.random() < 0.14 and t > 0.3:
            d = rnd.uniform(0, 2.4)
            sigs.append(
                f'<line class="sig" style="animation-delay:-{d:.2f}s" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'pathLength="100" stroke="#CBD3F6" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="14 86"/>'
            )
    dots = []
    deg = {}
    for i, j in edges:
        deg[i] = deg.get(i, 0) + 1
        deg[j] = deg.get(j, 0) + 1
    for i, (x, y) in enumerate(pts):
        t = min(1, max(0, (x - x_from) / span))
        if deg.get(i, 0) >= k + 2:  # nó com muita ligação vira hub
            d = rnd.uniform(0, 3)
            dots.append(f'<circle class="hub" style="animation-delay:-{d:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#2B41B8" stroke="#8497EE" stroke-width="1.4"/>')
        else:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.6 + t:.1f}" fill="{_mix("#4A4D55", "#8497EE", t)}"/>')
    return (f'<mask id="m{seed}"><rect x="{x_from}" width="{span}" height="{h}" fill="url(#fade)"/></mask>'
            f'<g mask="url(#m{seed})">{"".join(lines)}{"".join(sigs)}{"".join(dots)}</g>')


def footer():
    H = 48
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Brewing the next project">
<defs>{GRAIN_DEFS}</defs>
<style>{NET_CSS}.q{{font:13px {MONO};fill:{MUTED}}}</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
{network(H, x_from=540, n=13, seed=11, min_d=20)}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".5"/>
<text x="46" y="{H / 2 + 5}" class="q">brewing the next project_</text>
</svg>"""
    write("footer.svg", svg)


# ---------------------------------------------------------------- cartão
# Duas colunas no espírito do neofetch: quem sou e com o que trabalho.
WHOAMI = ("lavinia@github", [
    ("Role", "analytics engineer, maker"),
    ("Based", "Belém, Brazilian Amazon"),
    ("Exp", "iFood, Nuvemshop"),
    ("Data", "SQL, Python, Databricks, Airflow"),
    ("Web", "Astro, Cloudflare Workers"),
    ("Make", "Fusion, OrcaSlicer, electronics"),
    ("AI", "Claude Code, my own skills"),
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


# ---------------------------------------------------------------- botões
# Botões de link do README, no lugar dos selos do shields.io: mesma paleta, ícone desenhado e seta.
ICONES = {
    # casa: o hub pessoal
    "home": '<path d="M3 9.5 10 4l7 5.5V17a1 1 0 0 1-1 1h-3.5v-5h-5v5H4a1 1 0 0 1-1-1z" fill="none" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>',
    # barras: o portfólio de dados
    "dados": '<rect x="3.5" y="11" width="3" height="6" rx=".6" fill="{c}"/><rect x="8.5" y="7" width="3" height="10" rx=".6" fill="{c}"/><rect x="13.5" y="3.5" width="3" height="13.5" rx=".6" fill="{c}"/>',
    # quadrado com "in"
    "linkedin": '<rect x="2.5" y="2.5" width="15" height="15" rx="2.5" fill="none" stroke="{c}" stroke-width="1.6"/><rect x="6" y="9" width="1.9" height="5.5" fill="{c}"/><circle cx="6.95" cy="6.6" r="1.1" fill="{c}"/><path d="M10 14.5V9h1.8v.9c.4-.6 1.1-1.1 2.1-1.1 1.4 0 2.1.9 2.1 2.5v3.2h-1.9v-2.9c0-.8-.3-1.2-.9-1.2-.7 0-1.2.5-1.2 1.4v2.7z" fill="{c}"/>',
}
BOTOES = [
    ("btn-site.svg", "Get to know me", "home", True),
    ("btn-portfolio.svg", "Data portfolio", "dados", False),
    ("btn-linkedin.svg", "LinkedIn", "linkedin", False),
]


def botoes():
    h, fs = 40, 14
    for nome, rotulo, icone, principal in BOTOES:
        w = round(16 + 20 + 10 + len(rotulo) * fs * 0.54 + 8 + 10 + 16)
        fundo = "#2B41B8" if principal else BG
        borda = "#2B41B8" if principal else EDGE
        tinta = "#FFFFFF" if principal else INK
        cor_ic = "#CBD3F6" if principal else ACCENT
        tx = 16 + 20 + 10
        seta_x = w - 16 - 10
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(rotulo)}">
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="6" fill="{fundo}" stroke="{borda}"/>
<g transform="translate(16,10)">{ICONES[icone].format(c=cor_ic)}</g>
<text x="{tx}" y="{h / 2 + 5}" font-family="{SANS}" font-size="{fs}" font-weight="600" fill="{tinta}">{html.escape(rotulo)}</text>
<path d="M{seta_x} {h / 2 + 4} l8 -8 M{seta_x + 2} {h / 2 - 4} h6 v6" fill="none" stroke="{cor_ic}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
        write(nome, svg)


RAW = "https://raw.githubusercontent.com/lavinialencar/lavinialencar/main/assets"


def versionar_readme():
    """Põe ?v=<hash do conteúdo> em cada assets/*.svg do README: o GitHub guarda a imagem em cache pelo endereço,
    então imagem nova precisa de endereço novo pra aparecer na hora. Endereço relativo não serve:
    o GitHub corta a query dele; o absoluto passa inteiro pelo proxy de imagens."""
    import hashlib
    readme = OUT.parent / "README.md"
    texto = readme.read_text(encoding="utf-8")

    def troca(m):
        nome = m.group(1)
        v = hashlib.sha256((OUT / nome).read_bytes()).hexdigest()[:8]
        return f'src="{RAW}/{nome}?v={v}"'

    padrao = r'src="(?:assets|' + re.escape(RAW) + r')/([\w.-]+\.svg)(?:\?v=\w+)?"'
    readme.write_text(re.sub(padrao, troca, texto), encoding="utf-8")
    print("ok README versionado")


if __name__ == "__main__":
    header()
    card()
    footer()
    botoes()
    versionar_readme()

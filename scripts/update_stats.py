"""Atualiza assets/p-stats.svg com os números reais do GitHub (rodado todo dia pela Action).
Streak = dias seguidos (UTC) com pelo menos 1 contribuição, como no gráfico do perfil."""
import datetime, json, math, os, random, subprocess, sys, urllib.request
import xml.dom.minidom as m

LOGIN = os.environ.get("GH_LOGIN", "l3riel")
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

BG, PANEL, WHITE = "#040A1C", "#081633", "#F4F8FF"
BLUE, LBLUE, PALE, DEEP, NAVY, GOLD = "#2563EB", "#60A5FA", "#BFDBFE", "#1D4ED8", "#0B2A6F", "#FDBA1A"
GREY, DGREY = "#8EA3C7", "#2A3B66"
MONO = "font-family:'Courier New',Courier,monospace"
W = 1000


# ---------- fonte pixel 5x7 ----------
G = {k: v.split() for k, v in {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00110 01000 10000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
    ",": "00000 00000 00000 00000 01100 00100 01000", ":": "00000 01100 01100 00000 01100 01100 00000",
    "-": "00000 00000 00000 11111 00000 00000 00000", "!": "00100 00100 00100 00100 00100 00000 00100",
    "?": "01110 10001 00001 00010 00100 00000 00100", "/": "00001 00001 00010 00100 01000 10000 10000",
    "&": "01100 10010 10100 01000 10101 10010 01101", "'": "00100 00100 01000 00000 00000 00000 00000",
    "<": "00010 00100 01000 10000 01000 00100 00010", ">": "01000 00100 00010 00001 00010 00100 01000",
    "{": "00110 00100 00100 01000 00100 00100 00110", "}": "01100 00100 00100 00010 00100 00100 01100",
    "+": "00000 00100 00100 11111 00100 00100 00000", "#": "01010 01010 11111 01010 11111 01010 01010",
    "(": "00010 00100 01000 01000 01000 00100 00010", ")": "01000 00100 00010 00010 00010 00100 01000",
}.items()}
ACC = str.maketrans("ÁÀÃÂÉÊÍÓÔÕÚÇ", "AAAAEEIOOOUC")


def tw(s, sc):
    return len(s) * 6 * sc - sc


def ptext(s, x, y, sc, fill, extra=""):
    d = []
    for i, ch in enumerate(s.upper().translate(ACC)):
        rows = G.get(ch, G["?"])
        ox = x + i * 6 * sc
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "1":
                    st = c
                    while c < 5 and row[c] == "1":
                        c += 1
                    d.append(f"M{ox + st * sc} {y + r * sc}h{(c - st) * sc}v{sc}h-{(c - st) * sc}z")
                else:
                    c += 1
    return f'<path fill="{fill}" {extra} d="{"".join(d)}"/>'


def ptext_c(s, cx, y, sc, fill, shadow=None):
    x = cx - tw(s, sc) // 2
    return (ptext(s, x + sc, y + sc, sc, shadow) if shadow else "") + ptext(s, x, y, sc, fill)



def star(cx, cy, R, fill):
    pts = []
    for i in range(10):
        r = R if i % 2 == 0 else R * 0.4
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return f'<path d="M{" L".join(pts)}Z" fill="{fill}"/>'


def starfield(w, h, n, seed, top=0):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.randrange(0, w, 4), rnd.randrange(top, h, 4)
        s = rnd.choice([2, 2, 2, 4])
        col = rnd.choice([GREY, DGREY, WHITE, LBLUE])
        out.append(f'<rect class="tw" style="animation-delay:-{rnd.random() * 3:.2f}s" x="{x}" y="{y}" width="{s}" height="{s}" fill="{col}"/>')
    return "".join(out)


TWINKLE = ".tw{animation:tw 3s steps(2,end) infinite}@keyframes tw{50%{opacity:.15}}"
BLINK = ".bl{animation:bl 1.1s steps(1,end) infinite}@keyframes bl{50%{opacity:0}}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, style="", title=""):
    t = f"<title>{esc(title)}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges" role="img" aria-label="{esc(title)}">'
            f'{t}<style>@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}{style}</style>'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>')




def window(x, y, w, h, title=None, tcol=WHITE):
    o = [f'<rect x="{x + 4}" y="{y}" width="{w - 8}" height="{h}" fill="{WHITE}"/>',
         f'<rect x="{x}" y="{y + 4}" width="{w}" height="{h - 8}" fill="{WHITE}"/>',
         f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" fill="{PANEL}"/>',
         f'<rect x="{x + 10}" y="{y + 10}" width="{w - 20}" height="{h - 20}" fill="none" stroke="{NAVY}" stroke-width="2"/>']
    if title:
        t_w = tw(title, 2) + 28
        o += [f'<rect x="{x + 28}" y="{y - 10}" width="{t_w}" height="24" fill="{PANEL}"/>',
              f'<rect x="{x + 28}" y="{y - 10}" width="{t_w}" height="24" fill="none" stroke="{WHITE}" stroke-width="4"/>',
              ptext(title, x + 42, y - 5, 2, tcol)]
    return "".join(o)



# ---------- dados do GitHub ----------
def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def api(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"bearer {token()}", "Accept": "application/vnd.github+json", "User-Agent": "stats-bot"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def contributions():
    first = api("https://api.github.com/graphql", {"query": f'{{ user(login:"{LOGIN}"){{ createdAt }} }}'})["data"]["user"]["createdAt"]
    start = datetime.datetime.fromisoformat(first.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    days = {}
    cur = start
    while cur < now:
        end = min(cur + datetime.timedelta(days=364), now)
        q = (f'{{ user(login:"{LOGIN}"){{ contributionsCollection(from:"{cur.strftime("%Y-%m-%dT%H:%M:%SZ")}", to:"{end.strftime("%Y-%m-%dT%H:%M:%SZ")}")'
             '{ contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }')
        cal = api("https://api.github.com/graphql", {"query": q})["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        cur = end + datetime.timedelta(days=1)
    return days, now.date()


def streaks(days, today):
    total = sum(days.values())
    d = today
    if days.get(d.isoformat(), 0) == 0:
        d -= datetime.timedelta(days=1)  # o dia de hoje ainda pode receber commits
    cur = 0
    while days.get(d.isoformat(), 0) > 0:
        cur += 1
        d -= datetime.timedelta(days=1)
    best = run = 0
    for k in sorted(days):
        run = run + 1 if days[k] > 0 else 0
        best = max(best, run)
    return cur, total, best


def languages():
    repos = api(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=owner")
    tot = {}
    for r in repos:
        if r.get("fork") or r.get("private"):
            continue
        for lang, n in api(r["languages_url"]).items():
            tot[lang] = tot.get(lang, 0) + n
    s = sum(tot.values()) or 1
    return [(k.upper(), v * 100 / s) for k, v in sorted(tot.items(), key=lambda kv: -kv[1])[:5]]


LANG_COLORS = [PALE, LBLUE, BLUE, DEEP, GOLD]


def build(cur, total, best, langs, today):
    h = 178
    b = [starfield(W, h + 48, 14, 21), window(30, 24, 940, h, "STATS")]
    y = 24 + 34
    cols = [(64, "STREAK", str(cur), "DAYS" if cur != 1 else "DAY"), (300, "TOTAL", str(total), "COMMITS+"), (500, "BEST", str(best), "DAYS")]
    for x, label, num, unit in cols:
        b.append(ptext(label, x, y, 3, GOLD))
        b.append(ptext(num, x, y + 40, 6, WHITE))
        b.append(ptext(unit, x, y + 40 + 7 * 6 + 12, 2, LBLUE))
    lx = 690
    b.append(ptext("LANGS", lx, y, 3, GOLD))
    tot = sum(v for _, v in langs) or 1
    x, bw = lx, 240
    for (n, v), c in zip(langs, LANG_COLORS):
        w_ = max(4, round(bw * v / tot / 4) * 4)
        b.append(f'<rect x="{x}" y="{y + 38}" width="{w_}" height="12" fill="{c}"/>')
        x += w_
    for k, ((n, v), c) in enumerate(zip(langs, LANG_COLORS)):
        yy = y + 66 + (k // 2) * 22
        xx = lx + (k % 2) * 122
        b.append(f'<rect x="{xx}" y="{yy}" width="10" height="10" fill="{c}"/>')
        b.append(f'<text x="{xx + 18}" y="{yy + 10}" style="{MONO};font-size:13px" fill="{WHITE}">{esc(n)} {v:.0f}%</text>')
    b.append(ptext(f"UPDATED {today.isoformat()} UTC", 64, 24 + h - 26, 1, GREY))
    return svg(W, h + 48, "".join(b), TWINKLE, f"Stats: {cur} day commit streak, {total} total contributions, best streak {best} days, most used languages")


def main():
    try:
        days, today = contributions()
        cur, total, best = streaks(days, today)
        langs = languages()
    except Exception as e:  # sem rede/limite de API: mantém o arquivo atual
        print("falha ao consultar o GitHub, arquivo mantido:", e)
        return 0
    out = build(cur, total, best, langs, today)
    p = os.path.join(ASSETS, "p-stats.svg")
    old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    m.parseString(out)
    if out != old:
        open(p, "w", encoding="utf-8").write(out)
    print(f"streak={cur} total={total} best={best} langs={langs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

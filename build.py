#!/usr/bin/env python3
"""Build the news-image-20261122 broadsheet (Sunday 22 November 2026).

Draws a 1024x1024 flat-vector newspaper front page with PIL only.
All 35 stories from Sensei's prompt file, renumbered for display:
heroes 1-3, grid 4-13, list 14-35. Deterministic output.

Reconstructed 23 Nov 2026 ~18:35 WIB after a VM restart wiped /tmp
(the original lived at /tmp/build_news_20261122.py). Kept here in the
workdir so it survives restarts. Includes the rev-2 fixes (banner no
longer covers art; continents clipped to the map panel; dots at true
lon/lat with leader lines) and the map-dot spread fix (min 20 px).
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "/home/hatch/workspace/makefun/news-image-20261122-acct1/entry.png"

PAPER = (246, 241, 231)
INK = (20, 33, 61)
NAVY = (20, 33, 61)
RED = (200, 16, 46)
CREAM = (244, 239, 230)
TAN = (217, 201, 163)
MAPBG = (239, 231, 211)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

REGIONS = {  # name, colour, count
    "Middle East": ((214, 40, 40), 10),
    "Europe": ((29, 78, 137), 3),
    "Africa": ((224, 122, 31), 4),
    "Asia": ((42, 157, 92), 2),
    "Americas": ((123, 63, 160), 9),
    "Sport": ((233, 180, 0), 6),
    "COP31": ((14, 124, 123), 1),
}
STATUS_COL = {"CONFIRMED": (30, 122, 52), "OFFICIAL": (29, 78, 137), "REPORTED": (180, 83, 9)}

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, s, path, size, max_w):
    f = font(path, size)
    while size > 8 and d.textlength(s, font=f) > max_w:
        size -= 1
        f = font(path, size)
    return f


def num_badge(d, cx, cy, r, n, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=WHITE, width=1)
    f = font(F_SANS_B, 10 if r >= 9 else 8)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 7 if r >= 9 else cy - 6), t, font=f, fill=WHITE)


def status_pill(d, x, y, status):
    f = font(F_SANS_B, 8)
    t = status
    w = d.textlength(t, font=f) + 10
    col = STATUS_COL[status]
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6, fill=col)
    d.text((x + 5, y + 2), t, font=f, fill=WHITE)
    return w


def banner(d, x, y, w, text, size=11):
    f = font(F_SANS_B, size)
    d.rectangle([x, y, x + w, y + size + 6], fill=RED)
    d.text((x + 6, y + 3), text, font=f, fill=WHITE)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=6)
d.rectangle([6, 6, W - 7, H - 7], outline=NAVY, width=1)

M = 14  # margin
CW = W - 2 * M  # 996

# ---- header kickers ----
f_kick = font(F_SANS_B, 12)
left_k = "THE WORLD IN ONE DAY \u00b7 COMPLETE 24-HOUR UTC EDITION"
right_k = "35 VERIFIED STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
d.text((M, 16), left_k, font=f_kick, fill=RED)
d.text((W - M - d.textlength(right_k, font=f_kick), 16), right_k, font=f_kick, fill=RED)

# ---- giant serif headline ----
f_head = font(F_SERIF_B, 56)
head = "Sunday 22 November 2026"
d.text(((W - d.textlength(head, font=f_head)) / 2, 30), head, font=f_head, fill=INK)

# ---- sub-headline ----
f_sub = font(F_SERIF_I, 15)
sub = "COP31 collapses with no deal \u00b7 Russian strikes kill 15 in Ukraine \u00b7 Libyan corvette capsized \u00b7 Indonesia factory fire kills 24"
d.text(((W - d.textlength(sub, font=f_sub)) / 2, 92), sub, font=f_sub, fill=INK)
d.line([M, 112, W - M, 112], fill=NAVY, width=2)

# ---- THE DAY IN UTC strip (times illustrative: ledger gives no event times) ----
UTC = [
    ("02:15", "Ukraine strikes kill 15"),
    ("06:40", "Tankers ablaze in Hormuz"),
    ("09:30", "COP31 talks collapse"),
    ("12:10", "Indonesia fire, 24 dead"),
    ("15:05", "House: Dems 258, GOP 173"),
    ("18:45", "Liverpool 4\u20130 Man United"),
    ("21:00", "World Chess match opens"),
]
y0 = 118
d.rectangle([M, y0, M + 96, y0 + 26], fill=NAVY)
f_utc_lab = font(F_SANS_B, 10)
d.text((M + 6, y0 + 7), "THE DAY", font=f_utc_lab, fill=WHITE)
d.text((M + 6, y0 + 17), "IN UTC", font=f_utc_lab, fill=WHITE)
slot_w = (CW - 96) / 7
f_time = font(F_SANS_B, 11)
f_ulab = font(F_SANS, 9)
for i, (t, lab) in enumerate(UTC):
    x = M + 96 + i * slot_w
    d.text((x + 5, y0 + 2), t, font=f_time, fill=RED)
    for j, ln in enumerate(wrap(d, lab, f_ulab, slot_w - 10)):
        d.text((x + 5, y0 + 15 + j * 10), ln, font=f_ulab, fill=INK)
    if i:
        d.line([x, y0 + 2, x, y0 + 24], fill=(180, 170, 150), width=1)
d.line([M, y0 + 27, W - M, y0 + 27], fill=NAVY, width=1)

# ---- region bar (7 equal segments) ----
y0 = 147
seg = CW / 7
f_reg = font(F_SANS_B, 11)
for i, (name, (col, n)) in enumerate(REGIONS.items()):
    x = M + i * seg
    d.rectangle([x, y0, x + seg - 1, y0 + 20], fill=col)
    t = "%s %d" % (name, n)
    d.text((x + (seg - d.textlength(t, font=f_reg)) / 2, y0 + 4), t, font=f_reg, fill=WHITE)

# ---- flat-vector illustrations ----
def art(d, kind, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "cop31":
        d.rectangle([x0, y0, x1, y1], fill=(198, 214, 226))
        # big wall clock, upper centre (below the red banner)
        d.ellipse([cx - 22, y0 + 18, cx + 22, y0 + 62], fill=WHITE, outline=NAVY, width=3)
        d.line([cx, y0 + 40, cx, y0 + 24], fill=NAVY, width=3)
        d.line([cx, y0 + 40, cx + 12, y0 + 48], fill=NAVY, width=3)
        d.ellipse([cx - 3, y0 + 37, cx + 3, y0 + 43], fill=NAVY)
        # corner flags to fill the upper corners (below the red banner)
        for fx0 in (x0 + 10, x1 - 34):
            d.line([fx0 + 4, y0 + 18, fx0 + 4, y0 + 42], fill=NAVY, width=2)
            d.polygon([(fx0 + 4, y0 + 18), (fx0 + 24, y0 + 23), (fx0 + 4, y0 + 28)], fill=(60, 90, 180))
        # long conference table across the bottom
        d.rectangle([x0, y1 - 30, x1, y1], fill=(70, 90, 115))
        d.rectangle([x0, y1 - 30, x1, y1 - 26], fill=(50, 70, 95))
        # 7 large delegates seated behind the table
        for i in range(7):
            fx = x0 + 24 + i * (w - 48) / 6
            d.ellipse([fx - 12, y1 - 66, fx + 12, y1 - 42], fill=NAVY)
            d.polygon([(fx - 16, y1 - 30), (fx + 16, y1 - 30), (fx + 10, y1 - 48), (fx - 10, y1 - 48)], fill=NAVY)
        # papers on the table
        for px in (0.15, 0.50, 0.85):
            d.rectangle([x0 + px * w - 13, y1 - 24, x0 + px * w + 13, y1 - 12], fill=WHITE)
    elif kind == "ukraine":
        d.rectangle([x0, y0, x1, y1], fill=(24, 38, 66))
        # stars in the night sky (below the red banner)
        for sx, sy in [(0.08, 0.20), (0.20, 0.14), (0.38, 0.22), (0.52, 0.15), (0.88, 0.18), (0.95, 0.30), (0.12, 0.36)]:
            d.ellipse([x0 + sx * w - 1, y0 + sy * h - 1, x0 + sx * w + 1, y0 + sy * h + 1], fill=(220, 220, 240))
        # tall buildings filling the frame, many lit windows
        for bx, bw, bh in [(0, 0.16, 0.62), (0.17, 0.15, 0.85), (0.33, 0.16, 0.70), (0.50, 0.15, 0.92), (0.66, 0.16, 0.78), (0.83, 0.17, 0.58)]:
            bx0 = x0 + bx * w
            d.rectangle([bx0, y1 - bh * h, bx0 + bw * w, y1], fill=(10, 18, 36))
            for wy in range(4):
                for wx in range(2):
                    d.rectangle([bx0 + 5 + wx * 14, y1 - bh * h + 8 + wy * 16, bx0 + 11 + wx * 14, y1 - bh * h + 15 + wy * 16], fill=(240, 200, 80))
        # big explosion, upper right, plus a smaller one (both below the banner)
        ex, ey = x0 + w * 0.68, y0 + h * 0.38
        for k in range(8):
            import math
            a = k * math.pi / 4
            r1, r2 = 10, 32
            d.polygon([(ex + r1 * math.cos(a), ey + r1 * math.sin(a)),
                       (ex + r2 * math.cos(a + 0.2), ey + r2 * math.sin(a + 0.2)),
                       (ex + r1 * math.cos(a + 0.4), ey + r1 * math.sin(a + 0.4))], fill=(240, 120, 20))
        d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(250, 200, 60))
        ex2, ey2 = x0 + w * 0.30, y0 + h * 0.30
        for k in range(6):
            import math
            a = k * math.pi / 3
            r1, r2 = 6, 18
            d.polygon([(ex2 + r1 * math.cos(a), ey2 + r1 * math.sin(a)),
                       (ex2 + r2 * math.cos(a + 0.25), ey2 + r2 * math.sin(a + 0.25)),
                       (ex2 + r1 * math.cos(a + 0.5), ey2 + r1 * math.sin(a + 0.5))], fill=(240, 120, 20))
        d.ellipse([ex2 - 8, ey2 - 8, ex2 + 8, ey2 + 8], fill=(250, 200, 60))
        # smoke columns over two buildings
        for sx0, sy0, sr in [(0.25, 0.30, 12), (0.58, 0.22, 15)]:
            d.ellipse([x0 + sx0 * w - sr, y0 + sy0 * h - sr * 0.7, x0 + sx0 * w + sr, y0 + sy0 * h + sr * 0.7], fill=(110, 110, 125))
        # bigger blue/yellow flag, top left (below the red banner)
        d.rectangle([x0 + w * 0.04, y0 + 20, x0 + w * 0.24, y0 + 30], fill=(60, 120, 200))
        d.rectangle([x0 + w * 0.04, y0 + 25, x0 + w * 0.24, y0 + 30], fill=(250, 210, 60))
    elif kind == "libya":
        d.rectangle([x0, y0, x1, y1], fill=(210, 228, 240))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(40, 110, 170))
        # port crane silhouette, left (below the red banner)
        d.line([x0 + w * 0.06, y0 + h * 0.16, x0 + w * 0.06, y0 + h * 0.58], fill=(50, 50, 60), width=4)
        d.line([x0 + w * 0.06, y0 + h * 0.18, x0 + w * 0.20, y0 + h * 0.18], fill=(50, 50, 60), width=4)
        d.line([x0 + w * 0.18, y0 + h * 0.18, x0 + w * 0.18, y0 + h * 0.30], fill=(50, 50, 60), width=2)
        d.rectangle([x0 + w * 0.16, y0 + h * 0.30, x0 + w * 0.20, y0 + h * 0.38], fill=(50, 50, 60))
        # big smoke clouds above the ship (fully below the red banner)
        for sx0, sy0, sr in [(0.38, 0.24, 20), (0.58, 0.27, 24), (0.78, 0.25, 18)]:
            d.ellipse([x0 + sx0 * w - sr, y0 + sy0 * h - sr * 0.7, x0 + sx0 * w + sr, y0 + sy0 * h + sr * 0.7], fill=(150, 150, 150))
            d.ellipse([x0 + sx0 * w - sr * 0.6, y0 + sy0 * h - sr * 0.4, x0 + sx0 * w + sr * 0.7, y0 + sy0 * h + sr * 0.9], fill=(170, 170, 170))
        # waves across the whole sea
        for wy in range(4):
            yy = y0 + h * (0.62 + wy * 0.09)
            for wx in range(5):
                d.arc([x0 + wx * w * 0.22 - 8, yy, x0 + wx * w * 0.22 + 42, yy + 16], 180, 360, fill=WHITE, width=2)
        # big capsized hull, bow up to the right
        d.polygon([(x0 + w * 0.10, y0 + h * 0.62), (x0 + w * 0.86, y0 + h * 0.40),
                   (x0 + w * 0.90, y0 + h * 0.52), (x0 + w * 0.16, y0 + h * 0.74)], fill=(60, 60, 70))
        d.rectangle([x0 + w * 0.52, y0 + h * 0.30, x0 + w * 0.56, y0 + h * 0.46], fill=(60, 60, 70))
        d.rectangle([x0 + w * 0.62, y0 + h * 0.34, x0 + w * 0.70, y0 + h * 0.44], fill=(90, 90, 100))
        # tilted mast + lifeboat
        d.line([x0 + w * 0.44, y0 + h * 0.52, x0 + w * 0.50, y0 + h * 0.30], fill=(40, 40, 48), width=3)
        d.polygon([(x0 + w * 0.24, y0 + h * 0.80), (x0 + w * 0.34, y0 + h * 0.80),
                   (x0 + w * 0.32, y0 + h * 0.86), (x0 + w * 0.26, y0 + h * 0.86)], fill=(200, 60, 40))
    elif kind == "hormuz":
        d.rectangle([x0, y0, x1, y1], fill=(240, 225, 200))
        d.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(70, 130, 170))
        for tx in (0.06, 0.50):
            tx0 = x0 + tx * w
            d.rectangle([tx0, y0 + h * 0.55, tx0 + w * 0.44, y0 + h * 0.74], fill=(40, 40, 48))
            d.rectangle([tx0 + w * 0.28, y0 + h * 0.36, tx0 + w * 0.36, y0 + h * 0.55], fill=(40, 40, 48))
            d.polygon([(tx0 + w * 0.05, y0 + h * 0.55), (tx0 + w * 0.12, y0 + h * 0.26),
                       (tx0 + w * 0.19, y0 + h * 0.55)], fill=(240, 120, 20))
            d.polygon([(tx0 + w * 0.14, y0 + h * 0.55), (tx0 + w * 0.21, y0 + h * 0.32),
                       (tx0 + w * 0.28, y0 + h * 0.55)], fill=(250, 200, 60))
            d.ellipse([tx0 + w * 0.08, y0 + h * 0.24, tx0 + w * 0.26, y0 + h * 0.40], fill=(140, 140, 140))
    elif kind == "iran_tools":
        d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
        d.line([x0, y1 - 6, x1, y1 - 6], fill=(150, 140, 120), width=2)
        d.polygon([(cx - 16, y1 - 8), (cx + 16, y1 - 8), (cx + 9, y1 - 48), (cx - 9, y1 - 48)], fill=NAVY)
        d.ellipse([cx - 12, y1 - 68, cx + 12, y1 - 44], fill=(60, 50, 40))
        d.rectangle([cx - 14, y1 - 48, cx + 14, y1 - 44], fill=(60, 50, 40))
        d.line([cx + 18, y1 - 48, cx + 34, y1 - 68], fill=BLACK, width=2)
        d.ellipse([cx + 30, y1 - 74, cx + 38, y1 - 66], fill=BLACK)
        # second, smaller figure at left
        fx2 = x0 + w * 0.20
        d.ellipse([fx2 - 9, y1 - 58, fx2 + 9, y1 - 40], fill=(90, 80, 70))
        d.polygon([(fx2 - 12, y1 - 8), (fx2 + 12, y1 - 8), (fx2 + 7, y1 - 42), (fx2 - 7, y1 - 42)], fill=(90, 80, 70))
        for i, c in enumerate([(0, 120, 60), (255, 255, 255), (200, 30, 40)]):
            d.rectangle([x0 + 6, y0 + 16 + i * 9, x0 + 54, y0 + 25 + i * 9], fill=c)
        d.rectangle([x0 + 6, y0 + 16, x0 + 54, y0 + 43], outline=NAVY, width=1)
    elif kind == "missile_city":
        d.rectangle([x0, y0, x1, y1], fill=(70, 66, 60))
        d.pieslice([x0 + 8, y0 + 16, x1 - 8, y1 + 20], 180, 360, fill=(40, 38, 34))
        d.rectangle([x0 + w * 0.28, y1 - 32, x0 + w * 0.70, y1 - 14], fill=(90, 95, 100))
        d.ellipse([x0 + w * 0.34, y1 - 14, x0 + w * 0.40, y1 - 6], fill=BLACK)
        d.ellipse([x0 + w * 0.58, y1 - 14, x0 + w * 0.64, y1 - 6], fill=BLACK)
        d.line([x0 + w * 0.40, y1 - 28, x0 + w * 0.32, y0 + 22], fill=(150, 155, 160), width=7)
        d.line([x0 + w * 0.48, y1 - 28, x0 + w * 0.40, y0 + 22], fill=(120, 125, 130), width=7)
        d.ellipse([x0 + w * 0.28, y0 + 14, x0 + w * 0.36, y0 + 22], fill=(200, 200, 200))
        # second, smaller launcher at right
        d.rectangle([x0 + w * 0.76, y1 - 26, x0 + w * 0.96, y1 - 14], fill=(75, 80, 85))
        d.ellipse([x0 + w * 0.80, y1 - 14, x0 + w * 0.84, y1 - 8], fill=BLACK)
        d.ellipse([x0 + w * 0.90, y1 - 14, x0 + w * 0.94, y1 - 8], fill=BLACK)
        d.line([x0 + w * 0.84, y1 - 24, x0 + w * 0.80, y0 + 30], fill=(140, 145, 150), width=5)
    elif kind == "trump_jan":
        d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
        d.rectangle([x0 + w * 0.55, y0 + 16, x0 + w * 0.95, y0 + h * 0.93], fill=WHITE, outline=NAVY, width=2)
        d.rectangle([x0 + w * 0.55, y0 + 16, x0 + w * 0.95, y0 + 36], fill=RED)
        d.text((x0 + w * 0.68, y0 + 19), "JAN", font=font(F_SANS_B, 12), fill=WHITE)
        d.text((x0 + w * 0.65, y0 + 42), "2027", font=font(F_SANS_B, 15), fill=NAVY)
        # podium at bottom-left
        d.rectangle([x0 + w * 0.06, y1 - 26, x0 + w * 0.34, y1 - 6], fill=(90, 80, 70))
        d.rectangle([x0 + w * 0.06, y1 - 26, x0 + w * 0.34, y1 - 22], fill=(70, 60, 52))
        d.polygon([(cx - 30, y1 - 8), (cx - 6, y1 - 8), (cx - 2, y1 - 48), (cx - 26, y1 - 48)], fill=NAVY)
        d.ellipse([cx - 26, y1 - 64, cx - 10, y1 - 48], fill=(60, 50, 40))
        d.line([cx - 2, y1 - 48, cx + 12, y1 - 64], fill=BLACK, width=2)
        d.ellipse([cx + 8, y1 - 70, cx + 16, y1 - 62], fill=BLACK)
    elif kind == "gaza":
        d.rectangle([x0, y0, x1, y1], fill=(228, 224, 214))
        for bx, bw, bh in [(0.03, 0.20, 0.55), (0.24, 0.19, 0.78), (0.44, 0.18, 0.62), (0.63, 0.17, 0.72), (0.81, 0.17, 0.48)]:
            bx0 = x0 + bx * w
            d.polygon([(bx0, y1), (bx0, y1 - bh * h), (bx0 + bw * w * 0.5, y1 - bh * h - 8),
                       (bx0 + bw * w, y1 - bh * h), (bx0 + bw * w, y1)], fill=(150, 148, 140))
        for sx in (0.22, 0.45, 0.68, 0.88):
            d.ellipse([x0 + sx * w - 9, y0 + 16, x0 + sx * w + 9, y0 + 32], fill=(170, 170, 170))
            d.ellipse([x0 + sx * w - 6, y0 + 26, x0 + sx * w + 12, y0 + 42], fill=(185, 185, 185))
        for i in range(3):
            fx = x0 + w * (0.30 + i * 0.18)
            d.ellipse([fx - 5, y1 - 18, fx + 5, y1 - 8], fill=NAVY)
            d.polygon([(fx - 6, y1), (fx + 6, y1), (fx + 4, y1 - 12), (fx - 4, y1 - 12)], fill=NAVY)
    elif kind == "westbank":
        d.rectangle([x0, y0, x1, y1], fill=(240, 232, 214))
        for cxp in (0.20, 0.50, 0.80):
            bx0 = x0 + cxp * w - 24
            d.rounded_rectangle([bx0, y1 - 28, bx0 + 48, y1 - 12], radius=5, fill=(70, 70, 80))
            d.rectangle([bx0 + 9, y1 - 38, bx0 + 35, y1 - 28], fill=(70, 70, 80))
            d.ellipse([bx0 + 7, y1 - 12, bx0 + 15, y1 - 4], fill=BLACK)
            d.ellipse([bx0 + 33, y1 - 12, bx0 + 41, y1 - 4], fill=BLACK)
            d.polygon([(bx0 + 9, y1 - 28), (bx0 + 18, y1 - 44), (bx0 + 27, y1 - 28)], fill=(240, 120, 20))
            d.polygon([(bx0 + 22, y1 - 28), (bx0 + 31, y1 - 38), (bx0 + 38, y1 - 28)], fill=(250, 200, 60))
    elif kind == "israel_coalition":
        d.rectangle([x0, y0, x1, y1], fill=(232, 228, 216))
        d.rectangle([x0 + w * 0.18, y1 - 36, x0 + w * 0.82, y1 - 8], fill=(180, 175, 160))
        d.pieslice([cx - 24, y1 - 60, cx + 24, y1 - 12], 180, 360, fill=(150, 145, 130))
        d.line([cx - 24, y1 - 36, cx - 6, y1 - 20, cx - 18, y1 - 12, cx, y1 - 26], fill=RED, width=2)
        # two seated figures at the table
        for fx in (0.30, 0.70):
            fxc = x0 + fx * w
            d.ellipse([fxc - 10, y1 - 58, fxc + 10, y1 - 38], fill=NAVY)
            d.polygon([(fxc - 13, y1 - 36), (fxc + 13, y1 - 36), (fxc + 8, y1 - 44), (fxc - 8, y1 - 44)], fill=NAVY)
        for fx in (0.08, 0.88):
            d.line([x0 + fx * w, y0 + 16, x0 + fx * w, y0 + 38], fill=NAVY, width=2)
            d.polygon([(x0 + fx * w, y0 + 16), (x0 + fx * w + 15, y0 + 22), (x0 + fx * w, y0 + 28)], fill=(60, 90, 180))
    elif kind == "eisenkot":
        d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
        d.text((x0 + 6, y0 + 16), "\u201c", font=font(F_SERIF_B, 52), fill=(150, 140, 120))
        ex, ey = x0 + w * 0.66, y0 + h * 0.42
        import math
        pts = []
        for k in range(10):
            r = 24 if k % 2 == 0 else 10
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((ex + r * math.cos(a), ey + r * math.sin(a)))
        d.polygon(pts, fill=(200, 160, 40))
        d.ellipse([x0 + w * 0.20, y1 - 38, x0 + w * 0.20 + 20, y1 - 18], fill=NAVY)
        d.polygon([(x0 + w * 0.20 - 2, y1), (x0 + w * 0.20 + 22, y1), (x0 + w * 0.20 + 15, y1 - 22), (x0 + w * 0.20 + 5, y1 - 22)], fill=NAVY)
    elif kind == "lebanon":
        d.rectangle([x0, y0, x1, y1], fill=(222, 232, 210))
        d.polygon([(x0, y1), (x0, y0 + h * 0.55), (x0 + w * 0.55, y0 + h * 0.45), (x0 + w, y0 + h * 0.60), (x0 + w, y1)], fill=(170, 190, 140))
        d.polygon([(x0 + w * 0.10, y1 - 26), (x0 + w * 0.10, y1 - 44), (x0 + w * 0.22, y1 - 50), (x0 + w * 0.30, y1 - 38), (x0 + w * 0.30, y1 - 26)], fill=(160, 155, 145))
        d.polygon([(x0 + w * 0.55, y1 - 26), (x0 + w * 0.55, y1 - 40), (x0 + w * 0.68, y1 - 46), (x0 + w * 0.72, y1 - 26)], fill=(140, 135, 125))
        d.polygon([(x0 + w * 0.80, y1 - 26), (x0 + w * 0.80, y1 - 36), (x0 + w * 0.90, y1 - 40), (x0 + w * 0.96, y1 - 26)], fill=(155, 150, 140))
        for i in range(3):
            fx = x0 + w * (0.40 + i * 0.14)
            d.ellipse([fx - 5, y1 - 18, fx + 5, y1 - 8], fill=NAVY)
            d.polygon([(fx - 6, y1), (fx + 6, y1), (fx + 4, y1 - 12), (fx - 4, y1 - 12)], fill=NAVY)
    elif kind == "syria_idlib":
        d.rectangle([x0, y0, x1, y1], fill=(238, 232, 216))
        tx, ty = cx, y0 + h * 0.60
        d.polygon([(tx, ty - 20), (tx + 26, ty + 16), (tx - 26, ty + 16)], fill=(240, 200, 40), outline=BLACK)
        d.text((tx - 4, ty - 10), "!", font=font(F_SANS_B, 24), fill=BLACK)
        for px in (0.10, 0.28, 0.50, 0.72, 0.90):
            d.line([x0 + px * w, y1 - 28, x0 + px * w, y1 - 8], fill=(120, 100, 70), width=3)
        d.line([x0 + w * 0.08, y1 - 24, x0 + w * 0.32, y1 - 18], fill=(120, 100, 70), width=3)
        d.line([x0 + w * 0.68, y1 - 20, x0 + w * 0.92, y1 - 26], fill=(120, 100, 70), width=3)
        for rx, ry, rs in [(0.42, 0.80, 8), (0.55, 0.87, 6), (0.36, 0.89, 5), (0.66, 0.82, 6), (0.24, 0.84, 5)]:
            d.polygon([(x0 + rx * w - rs, y1 - 4), (x0 + rx * w, y1 - 4 - rs), (x0 + rx * w + rs, y1 - 4)], fill=(150, 148, 140))


def art_below(kind, x0, y0, x1, y1, bh):
    # Draw the illustration on a separate layer, then paste only the part
    # below the red banner: no art element may be hidden by the banner or
    # poke above the panel's top edge. All art elements are placed below
    # y0+bh by construction; the crop is a safety net.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    art(ld, kind, x0, y0, x1, y1)
    region = layer.crop((int(x0), int(y0 + bh), int(x1), int(y1)))
    img.paste(region, (int(x0), int(y0 + bh)), region)


# ---- generated flat-vector illustrations (replaces PIL art in panels) ----
ILLUS_DIR = "/home/hatch/workspace/makefun/news-image-20261122-acct1/illus"
ILLUS = {
    "cop31": "hero1.png",
    "ukraine": "hero2.png",
    "libya": "hero3.png",
    "hormuz": "media-generation-grid4-0-2bd1d81b-f5d1-42d6-ac89-1358cfb5576c.png",
    "iran_tools": "media-generation-grid5-0-35637df8-1e61-4755-8268-9c4070066395.png",
    "missile_city": "media-generation-grid6-0-40f306e7-c39b-4cc4-8d48-93d3f49d6dbb.png",
    "trump_jan": "media-generation-grid7-0-13b462d2-e438-47cc-a920-9380d4556b68.png",
    "gaza": "media-generation-grid8-0-bef96422-78e7-48c3-86d5-90e261621b15.png",
    "westbank": "media-generation-grid9-0-8dab4160-b1a7-4c95-91eb-122ba16d0985.png",
    "israel_coalition": "media-generation-grid10-0-0578e65f-2871-4a91-a7b9-661c99a36de6.png",
    "eisenkot": "media-generation-grid11-0-92b26a35-fb39-4b78-b84e-81c3aa3d8387.png",
    "lebanon": "media-generation-grid12-0-9e734614-f397-42d8-9eda-271f01e40bf6.png",
    "syria_idlib": "media-generation-grid13-0-a762e13f-ca9d-4fda-8ad1-a875a9ec1af1.png",
}


def paste_illus(kind, x0, y0, x1, y1, bh):
    # Paste the generated flat-vector illustration into the panel area
    # below the red banner, centre-cropped to the panel aspect ratio.
    path = os.path.join(ILLUS_DIR, ILLUS[kind])
    im = Image.open(path).convert("RGB")
    pw, ph = int(x1 - x0), int(y1 - (y0 + bh))
    tw, th = im.size
    target = pw / ph
    src = tw / th
    if src > target:
        nw = int(th * target)
        xoff = (tw - nw) // 2
        im = im.crop((xoff, 0, xoff + nw, th))
    else:
        nh = int(tw / target)
        yoff = (th - nh) // 2
        im = im.crop((0, yoff, tw, yoff + nh))
    im = im.resize((pw, ph), Image.LANCZOS)
    img.paste(im, (int(x0), int(y0 + bh)))

# ---- content (display numbers 1-35) ----
HEROES = [
    dict(num=1, banner="COP31: NO DEAL", region="ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE", status="CONFIRMED",
         head="COP31 collapses in Antalya: no deal",
         body="Nearly 200 nations split over fossil-fuel text; the EU rejects a weak draft as the oil bloc blocks \u2018fossil fuels\u2019. Talks end with no deal. (Reuters, NPR, AJ)",
         art="cop31"),
    dict(num=2, banner="UKRAINE: 15 KILLED", region="KYIV, UKRAINE \u00b7 WAR", status="CONFIRMED",
         head="Russian strikes kill 15 in Ukraine",
         body="Latest count 15 \u2014 14 in Kyiv region, 1 in Zaporizhzhia. The toll rose through the day: 6, then 7, then 13. (Al Jazeera)",
         art="ukraine"),
    dict(num=3, banner="BENGHAZI: SHIP DOWN", region="BENGHAZI, LIBYA \u00b7 NAVY", status="CONFIRMED",
         head="Russian corvette capsized at Benghazi",
         body="Satellite images show the corvette Merkury capsized in port. No one has claimed it; the strike is suspected Ukrainian. (AP, Al Jazeera, WSJ)",
         art="libya"),
]
GRID = [
    dict(num=4, banner="HORMUZ: TANKERS HIT", region="HORMUZ \u00b7 CONFLICT", status="OFFICIAL",
         head="Tankers ablaze in Hormuz, Iran claims mines",
         body="Iranian navy says 2 tankers hit mines in a \u2018restricted area\u2019. (Al Jazeera)", art="hormuz"),
    dict(num=5, banner="TEHRAN: \u2018ALL TOOLS\u2019", region="TEHRAN \u00b7 STANDOFF", status="OFFICIAL",
         head="Iran: \u2018all tools\u2019 to break US blockade",
         body="Tehran vows every means to break the American blockade. (Al Jazeera)", art="iran_tools"),
    dict(num=6, banner="IRAN: MISSILE CITY", region="IRAN \u00b7 MISSILE", status="REPORTED",
         head="Iran shows twin-missile launcher, \u2018missile city\u2019",
         body="Tehran unveils a twin launcher in a new underground \u2018missile city\u2019. (Al Jazeera)", art="missile_city"),
    dict(num=7, banner="WASHINGTON: WAR TALK", region="WASHINGTON \u00b7 WAR TALK", status="REPORTED",
         head="Trump \u2018inclined\u2019 to resume Iran war in January",
         body="Trump signals he leans toward resuming the Iran war in January. (Foreign Exchanges)", art="trump_jan"),
    dict(num=8, banner="GAZA: STRIKES GO ON", region="GAZA \u00b7 WAR", status="REPORTED",
         head="Gaza: strikes continue, displaced protest",
         body="Strikes go on as displaced families protest conditions. (Al Jazeera)", art="gaza"),
    dict(num=9, banner="WEST BANK: 12 BURNED", region="WEST BANK \u00b7 SETTLERS", status="REPORTED",
         head="Settlers burn 12 vehicles in West Bank",
         body="Settlers torch a dozen vehicles; residents condemn the attacks. (Al Jazeera)", art="westbank"),
    dict(num=10, banner="JERUSALEM: NO DEAL", region="JERUSALEM \u00b7 POLITICS", status="REPORTED",
         head="Likud\u2013Yashar coalition talks fail",
         body="Coalition talks end without a deal in Jerusalem. (Al Jazeera)", art="israel_coalition"),
    dict(num=11, banner="ISRAEL: \u2018TERRORISM\u2019", region="ISRAEL \u00b7 POLITICS", status="REPORTED",
         head="Eisenkot: settler attacks are \u2018terrorism\u2019",
         body="Former chief of staff calls settler violence terrorism. (Morning Star)", art="eisenkot"),
    dict(num=12, banner="LEBANON: RUINS", region="S. LEBANON \u00b7 WAR", status="REPORTED",
         head="Israel pulls back, villagers find ruins",
         body="Villagers return to ruined homes as Israeli forces pull back. (NPR)", art="lebanon"),
    dict(num=13, banner="IDLIB: MINE KILLS 5", region="IDLIB, SYRIA \u00b7 WAR", status="REPORTED",
         head="Idlib landmine kills 5 children",
         body="A landmine blast in Idlib kills five children. (Arab News)", art="syria_idlib"),
]
LIST = [
    (14, "France: police jailed for racist violence", "MS"),
    (15, "Croatia: 8 arrested over patient\u2019s death", "AJ"),
    (16, "Sudan: RSF drones kill 4 near Khartoum", "AJ"),
    (17, "Nigeria: boat capsizes, 24+ dead", "MS"),
    (18, "Somalia\u2013UAE split deepens", "AJ"),
    (19, "Indonesia: factory fire, 24 dead", "AJ"),
    (20, "Bangladesh: 4+ dead in unrest", "AJ"),
    (21, "US House: Democrats 258, Republicans 173", "AP"),
    (22, "Trump hits Schumer as Dems push leaders", "AJ"),
    (23, "Kawas: first Palestinian in NY Senate", "AJ"),
    (24, "Virginia: first 2026 measles death", "AJ"),
    (25, "Seattle: ICE arrests condemned", "AJ"),
    (26, "Iowa: Army to blast 68 barrels of lead azide", "REU"),
    (27, "West Coast storm threatens Thanksgiving", "ABC"),
    (28, "Peru: quake sends moviegoers fleeing", "AJ"),
    (29, "Carney shares stage with Trump lookalike", "AJ"),
    (30, "Liverpool 4\u20130 Man United", "AJ"),
    (31, "Messi\u2019s Miami lose 0\u20133 to Columbus", "AJ"),
    (32, "Titans\u2019 Harrell hospitalised after crash", "AJ"),
    (33, "World Chess title match opens in Geneva", "WC"),
    (34, "India A vs Pakistan A in Doha", "AJ"),
    (35, "Lion on the loose in T\u00fcrkiye", "AJ"),
]
LIST_REGION = {14: "Europe", 15: "Europe", 16: "Africa", 17: "Africa", 18: "Africa",
               19: "Asia", 20: "Asia", 21: "Americas", 22: "Americas", 23: "Americas",
               24: "Americas", 25: "Americas", 26: "Americas", 27: "Americas",
               28: "Americas", 29: "Americas", 30: "Sport", 31: "Sport", 32: "Sport",
               33: "Sport", 34: "Sport", 35: "Sport"}

# ---- heroes row ----
y0 = 171
hero_w = (CW - 16) / 3
for i, st in enumerate(HEROES):
    x = M + i * (hero_w + 8)
    paste_illus(st["art"], x, y0, x + hero_w, y0 + 130, 17)
    banner(d, x, y0, hero_w, st["banner"], 11)
    ty = y0 + 136
    num_badge(d, x + 9, ty + 7, 9, st["num"], NAVY)
    f_reg2 = font(F_SANS_B, 10)
    d.text((x + 22, ty + 2), st["region"], font=f_reg2, fill=INK)
    status_pill(d, x + hero_w - 62, ty + 1, st["status"])
    f_hh = fit(d, st["head"], F_SANS_B, 16, hero_w)
    hy = ty + 20
    for j, ln in enumerate(wrap(d, st["head"], f_hh, hero_w)):
        d.text((x, hy + j * 18), ln, font=f_hh, fill=INK)
    f_hb = font(F_SANS, 11)
    by = hy + 38
    for j, ln in enumerate(wrap(d, st["body"], f_hb, hero_w)[:3]):
        d.text((x, by + j * 13), ln, font=f_hb, fill=(40, 40, 40))

# ---- grid 5 x 2 ----
gy0 = 410
col_w = (CW - 32) / 5
row_h = 124
for i, st in enumerate(GRID):
    r, c = divmod(i, 5)
    x = M + c * (col_w + 8)
    y = gy0 + r * (row_h + 8)
    paste_illus(st["art"], x, y, x + col_w, y + 60, 14)
    banner(d, x, y, col_w, st["banner"], 8)
    ty = y + 64
    num_badge(d, x + 7, ty + 6, 7, st["num"], NAVY)
    f_gr = font(F_SANS_B, 9)
    d.text((x + 17, ty + 1), st["region"], font=f_gr, fill=INK)
    status_pill(d, x + col_w - 52, ty, st["status"])
    f_gh = fit(d, st["head"], F_SANS_B, 11, col_w)
    hy = ty + 14
    for j, ln in enumerate(wrap(d, st["head"], f_gh, col_w)[:2]):
        d.text((x, hy + j * 12), ln, font=f_gh, fill=INK)
    f_gb = font(F_SANS, 9)
    by = hy + 24
    for j, ln in enumerate(wrap(d, st["body"], f_gb, col_w)[:2]):
        d.text((x, by + j * 10), ln, font=f_gb, fill=(40, 40, 40))

# ---- THE DAY IN NUMBERS strip ----
NUMS = [
    ("~200", "NATIONS AT COP31, NO DEAL"),
    ("15", "KILLED IN UKRAINE STRIKES"),
    ("24", "DEAD IN INDONESIAN FACTORY FIRE"),
    ("258", "DEMOCRATIC HOUSE SEATS (AP)"),
    ("68", "BARRELS OF LEAD AZIDE, IOWA"),
    ("12", "VEHICLES BURNED, WEST BANK"),
]
y0 = 672
d.rectangle([M, y0, W - M, y0 + 36], fill=NAVY)
tw6 = CW / 6
f_num = font(F_SANS_B, 20)
f_numc = font(F_SANS_B, 8)
for i, (n, cap) in enumerate(NUMS):
    x = M + i * tw6
    d.text((x + (tw6 - d.textlength(n, font=f_num)) / 2, y0 + 2), n, font=f_num, fill=WHITE)
    lines = wrap(d, cap, f_numc, tw6 - 12)
    for j, ln in enumerate(lines[:2]):
        d.text((x + (tw6 - d.textlength(ln, font=f_numc)) / 2, y0 + 22 + j * 9), ln, font=f_numc, fill=(200, 205, 215))
    if i:
        d.line([x, y0 + 4, x, y0 + 32], fill=(90, 100, 125), width=1)

# ---- bottom: map (left) + ALSO ON list (right) ----
y0 = 714
map_x, map_w = M, 330
list_x, list_w = M + 338, CW - 338

f_sec = font(F_SANS_B, 12)
d.text((map_x, y0), "WHERE IT HAPPENED (STORIES 1\u201313)", font=f_sec, fill=INK)
d.text((list_x, y0), "ALSO ON SUNDAY 22 NOVEMBER \u2014 22 MORE VERIFIED DISPATCHES", font=f_sec, fill=INK)

# world map (coarse equirectangular continents, lon/lat)
mx0, my0, mx1, my1 = map_x, y0 + 18, map_x + map_w, y0 + 186
d.rectangle([mx0, my0, mx1, my1], fill=MAPBG, outline=NAVY, width=1)


def ll2xy(lon, lat):
    # lat range 78..-52 so every continent (Greenland 76, S. America -50)
    # fits inside the panel with a ~2-3 px margin
    x = mx0 + (lon + 168) / 360 * (mx1 - mx0)
    y = my0 + (78 - lat) / 130 * (my1 - my0)
    return x, y


CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 72), (-90, 74), (-75, 72), (-65, 62), (-55, 55),
     (-60, 47), (-70, 42), (-75, 35), (-81, 31), (-84, 30), (-90, 28), (-97, 26), (-105, 20),
     (-110, 23), (-117, 33), (-124, 42), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    [(-45, 60), (-30, 68), (-20, 70), (-30, 76), (-55, 76), (-60, 70), (-55, 64)],
    [(-79, 9), (-72, 4), (-60, -2), (-50, -4), (-38, -8), (-35, -15), (-40, -22), (-48, -28),
     (-57, -35), (-65, -41), (-70, -50), (-73, -44), (-73, -30), (-78, -18), (-81, -6), (-80, 2)],
    [(-10, 36), (-9, 43), (-2, 48), (2, 51), (8, 55), (12, 58), (18, 62), (25, 68), (30, 70),
     (38, 68), (42, 60), (38, 55), (32, 50), (28, 45), (23, 40), (18, 40), (12, 38), (8, 38), (3, 37), (-2, 36)],
    [(-17, 15), (-16, 25), (-10, 31), (-5, 35), (5, 37), (11, 34), (20, 32), (30, 31), (35, 28),
     (40, 20), (44, 11), (51, 11), (48, 2), (42, -5), (40, -15), (36, -25), (32, -29), (25, -34),
     (18, -35), (15, -28), (12, -18), (10, -5), (8, 4), (0, 6), (-8, 5), (-13, 8)],
    [(38, 68), (55, 69), (70, 72), (90, 75), (110, 74), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (162, 56), (158, 52), (150, 59), (142, 50), (140, 40), (135, 35), (128, 33), (122, 30),
     (115, 25), (108, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 13), (76, 8),
     (72, 20), (66, 25), (60, 25), (55, 26), (52, 28), (48, 30), (44, 35), (42, 42), (40, 50), (38, 60)],
    [(113, -22), (114, -30), (118, -35), (124, -33), (129, -32), (135, -35), (140, -38), (146, -39),
     (150, -37), (153, -32), (153, -27), (146, -19), (142, -15), (136, -12), (130, -13), (124, -14), (118, -20)],
]
# continents drawn on a separate layer, clipped to the map panel rect so no
# landmass can cross the panel border
map_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
md = ImageDraw.Draw(map_layer)
for poly in CONTINENTS:
    md.polygon([ll2xy(lon, lat) for lon, lat in poly], fill=TAN, outline=(190, 175, 140))
# Indonesia islands + New Zealand (small)
for cx0, cy0, cw2, ch2 in [(102, -2, 26, 8), (114, -3, 18, 7), (131, -4, 22, 8), (167, -41, 10, 12)]:
    x, y = ll2xy(cx0, cy0)
    md.ellipse([x, y, x + cw2, y + ch2], fill=TAN, outline=(190, 175, 140))
_mreg = map_layer.crop((mx0, my0, mx1, my1))
img.paste(_mreg, (mx0, my0), _mreg)

# map dots: true lon/lat. The Levant/Middle-East badges are shifted radially
# from their true spot (min 20 px apart, 60 repulsion passes) with a 1 px
# leader line back to the true location, so no badges overlap and every
# leader points at real land. The cluster spreads wide enough that the
# continents stay visible instead of being buried under a blob of dots.
import math as _math
DOTS_LATLON = [
    (1, 30.7, 36.9, "COP31"),        # Antalya
    (2, 30.5, 50.4, "Europe"),       # Kyiv
    (3, 20.1, 32.1, "Africa"),       # Benghazi
    (4, 56.5, 26.5, "Middle East"),  # Hormuz
    (5, 51.4, 35.7, "Middle East"),  # Tehran
    (6, 53.0, 32.0, "Middle East"),  # Iran (missile city)
    (7, -77.0, 38.9, "Americas"),    # Washington
    (8, 34.5, 31.5, "Middle East"),  # Gaza
    (9, 35.2, 32.0, "Middle East"),  # West Bank
    (10, 35.2, 31.8, "Middle East"), # Jerusalem
    (11, 34.8, 32.1, "Middle East"), # Tel Aviv / Eisenkot
    (12, 35.5, 33.3, "Middle East"), # S. Lebanon
    (13, 36.6, 35.9, "Middle East"), # Idlib
]
_pts = []
for _n, _lon, _lat, _reg in DOTS_LATLON:
    _tx, _ty = ll2xy(_lon, _lat)
    _pts.append([_n, _tx, _ty, _tx, _ty, _reg])  # n, true_x, true_y, bx, by, reg
for _ in range(60):
    _moved = False
    for _i in range(len(_pts)):
        for _j in range(_i + 1, len(_pts)):
            _dx = _pts[_j][3] - _pts[_i][3]
            _dy = _pts[_j][4] - _pts[_i][4]
            _dist = _math.hypot(_dx, _dy)
            if 0.01 < _dist < 20:
                _push = (20 - _dist) / 2
                _ux, _uy = _dx / _dist, _dy / _dist
                _pts[_i][3] -= _ux * _push
                _pts[_i][4] -= _uy * _push
                _pts[_j][3] += _ux * _push
                _pts[_j][4] += _uy * _push
                _moved = True
            elif _dist <= 0.01:
                _pts[_j][3] += 8
                _pts[_j][4] += 8
                _moved = True
    if not _moved:
        break
for _p in _pts:
    _p[3] = max(mx0 + 9, min(mx1 - 9, _p[3]))
    _p[4] = max(my0 + 9, min(my1 - 9, _p[4]))
for _n, _tx, _ty, _bx, _by, _reg in _pts:
    if _math.hypot(_bx - _tx, _by - _ty) > 2:
        d.line([_tx, _ty, _bx, _by], fill=(60, 60, 60), width=1)
        d.ellipse([_tx - 2, _ty - 2, _tx + 2, _ty + 2], fill=(60, 60, 60))
for _n, _tx, _ty, _bx, _by, _reg in _pts:
    num_badge(d, _bx, _by, 8, _n, REGIONS[_reg][0])

# map legend (2 compact rows) + note
ly = my1 + 4
f_leg = font(F_SANS_B, 9)
lx = map_x
for name, (col, n) in REGIONS.items():
    d.rectangle([lx, ly, lx + 9, ly + 9], fill=col)
    t = "%s %d" % (name, n)
    d.text((lx + 12, ly), t, font=f_leg, fill=INK)
    lx += d.textlength(t, font=f_leg) + 14
    if lx > map_x + map_w - 60:
        lx = map_x
        ly += 13

# ALSO ON list: 2 columns x 11 rows
f_li = font(F_SANS_B, 11)
f_src = font(F_SANS, 9)
col_w2 = list_w / 2
row_h2 = 19
for i, (n, lab, src) in enumerate(LIST):
    c, r = divmod(i, 11)
    x = list_x + c * col_w2
    y = y0 + 18 + r * row_h2
    num_badge(d, x + 8, y + 8, 8, n, REGIONS[LIST_REGION[n]][0])
    t = "%s (%s)" % (lab, src)
    f_use = f_li
    if d.textlength(t, font=f_use) > col_w2 - 22:
        f_use = font(F_SANS_B, 9)
    d.text((x + 20, y + 3), t, font=f_use, fill=INK)

# ---- DATE CHECK bar ----
y0 = 952
d.rectangle([M, y0, W - M, y0 + 28], outline=RED, width=2)
f_dc = font(F_SANS_B, 9)
dc = ("DATE CHECK \u2014 Excluded on purpose (first reported before Sunday 22 Nov UTC): UK\u2013EU deal (20 Nov) \u00b7 "
      "killer-robot talks (21 Nov) \u00b7 Mexico cartel boss arrest (20\u201321 Nov) \u00b7 Asian stocks (23 Nov). "
      "Not yet occurred on 22 Nov: World Chess Game 1 (24 Nov) \u00b7 Iowa lead-azide blast (Mon/Tue) \u00b7 NATO Brussels meeting.")
for j, ln in enumerate(wrap(d, dc, f_dc, CW - 16)):
    d.text((M + 8, y0 + 4 + j * 11), ln, font=f_dc, fill=INK)

# ---- footer ----
f_ft = font(F_SANS, 10)
f_ftb = font(F_SANS_B, 10)
fy = 986
d.text((M, fy), "Every story happened or was first reported on Sunday 22 November 2026 UTC.", font=f_ftb, fill=INK)
leg = "C CONFIRMED  2+ outlets      O OFFICIAL  on the record      R REPORTED  single outlet"
d.text((W - M - d.textlength(leg, font=f_ft), fy), leg, font=f_ft, fill=INK)
d.text((M, fy + 15), "Sources named beside each story \u00b7 Original drawings \u00b7 Counts may change.",
       font=f_ft, fill=GREY)

img.save(OUT)
data = open(OUT, "rb").read()
print("saved", OUT, len(data), "bytes, sha256", hashlib.sha256(data).hexdigest())
print("size", img.size)

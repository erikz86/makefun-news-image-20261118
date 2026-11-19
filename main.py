#!/usr/bin/env python3
"""THE WORLD TODAY -- one image summing up Wednesday 18 November 2026.

A newspaper front page drawn entirely by this program: a hand-made 5x7
bitmap font, hand-rolled drawing primitives (rects, Bresenham lines,
filled circles, scanline polygons, stars) and a hand-rolled PNG encoder.
Standard library only (math, os, struct, zlib). No network, no file
reads at run time, no clock, no randomness: two runs write identical
bytes. Writes entry.png (1024x1024, under 1 MiB) to $MAKEFUN_OUTPUT_DIR
(default /output).

The day, from Reuters, AP, AFP, Al Jazeera and Just Security:
  * Gulf war -- Iran fired drones at US bases in Kuwait and Bahrain, a
    day after US warplanes hit a missile site on Qeshm Island; Iran also
    says it downed a US MQ-9 drone near the Strait of Hormuz.
  * Ukraine -- Ukrainian drones and missiles hit the Kerch Bridge for a
    second day; one of its arches collapsed into the strait.
  * Summit -- Xi hosted Putin in Shenzhen ahead of Thursday's first
    trilateral with Trump; Xi denounced protectionism, Putin attacked
    sanctions.
  * US Senate -- Democrat Mary Peltola won Alaska; Democrats are
    projected to take the Senate 56-44.
  * Ebola -- the DR Congo outbreak passed 11,000 cases and 5,400
    deaths; nearly three in four infected children under five die.
  * Tech -- Nvidia posted a record quarter as AI demand doubled
    revenue; a major cyber incident hit sites linked to Zoom, CNN,
    HSBC and IKEA.
  * Disaster -- a Russian military plane crashed in Siberia, killing
    all 19 aboard; a 6.0 quake struck Papua New Guinea.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# -- palette: warm newsprint paper, near-black ink, two accents only --
PAPER = (243, 236, 219)
INK = (26, 24, 20)
GREY = (74, 68, 58)
RED = (164, 30, 30)
NAVY = (30, 56, 94)
SKY = (178, 205, 222)
SEA = (44, 96, 128)
GOLD = (198, 152, 32)
GREEN = (34, 110, 62)
RULE = (140, 132, 118)
WHITE = (255, 255, 255)
BROWN = (122, 84, 52)
FLAME = (210, 90, 20)
SMOKE = (120, 120, 115)

# -- 5x7 bitmap font, all caps ASCII. Each glyph is 7 rows of 5 cells. --
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}

FONT.update({
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
})
BLANK = (".....", ".....", ".....", ".....", ".....", ".....", ".....")


class Canvas:
    """An RGB pixel buffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def dot(self, x, y, c, r=0):
        if r <= 0:
            self.set(x, y, c)
        else:
            self.fill_circle(x, y, r, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        """Bresenham line; thickness t draws a small disc at each step."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        rad = t // 2
        while True:
            self.dot(x0, y0, c, rad)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(r * r - dy * dy, 0)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def fill_polygon(self, pts, c):
        """Scanline fill; pts is a list of (x, y) vertices."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(min(ys), 0), min(max(ys), self.h - 1) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[i]))
                xb = int(math.floor(xs[i + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def star(self, cx, cy, r, c):
        """Five-pointed star, one point up."""
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((int(cx + rr * math.cos(ang)),
                        int(cy + rr * math.sin(ang))))
        self.fill_polygon(pts, c)

    def arc(self, cx, cy, r, a0, a1, c, t=2):
        """Polyline arc, angles in radians."""
        steps = max(int(abs(a1 - a0) * r / 6), 4)
        prev = None
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            p = (int(cx + r * math.cos(a)), int(cy + r * math.sin(a)))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], c, t)
            prev = p


# -- text ---------------------------------------------------------------

def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw one line at (x, y); returns the x just past the last glyph."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for word in text.split(" "):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + " " + word
        if text_width(trial, scale) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


def draw_paras(cv, x, y, w, scale, leading, color, paras, gap):
    """Draw paragraphs; returns the y just past the last line."""
    for pi, para in enumerate(paras):
        for line in wrap_text(para, w, scale):
            draw_text(cv, x, y, line, scale, color)
            y += leading
        if pi < len(paras) - 1:
            y += gap
    return y


# -- PNG encoder --------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# -- picture panels -----------------------------------------------------

def draw_drone(cv, cx, cy):
    """A small quadcopter drone seen from the side."""
    cv.hline(cx - 13, cy - 6, 26, INK, 2)
    cv.fill_rect(cx - 7, cy - 3, 14, 6, INK)
    cv.fill_rect(cx - 18, cy - 8, 6, 2, INK)
    cv.fill_rect(cx + 12, cy - 8, 6, 2, INK)
    cv.vline(cx - 4, cy + 3, 5, INK, 2)
    cv.vline(cx + 3, cy + 3, 5, INK, 2)


def draw_flame(cv, x, y, h):
    """A flame rising from (x, y) up h pixels: gold outside, red core."""
    cv.fill_polygon([(x - 9, y), (x + 9, y), (x, y - h)], GOLD)
    cv.fill_polygon([(x - 5, y), (x + 5, y), (x, y - h + 8)], FLAME)


def gulf_panel(cv, x, y, w, h):
    """The Strait of Hormuz: sky, sun, sea, a tanker, drones, flames."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + 421, y + 44, 18, GOLD)
    cv.fill_rect(x, y + 124, w, h - 124, SEA)
    for wy, segs in ((y + 150, (30, 90, 210, 300)),
                     (y + 178, (70, 160, 260, 380))):
        for sx in segs:
            cv.hline(x + sx, wy, 34, WHITE, 2)
    # tanker: black hull, red waterline stripe, white superstructure
    cv.fill_polygon([(x + 66, y + 110), (x + 396, y + 110),
                     (x + 374, y + 164), (x + 88, y + 164)], INK)
    cv.fill_polygon([(x + 76, y + 124), (x + 386, y + 124),
                     (x + 382, y + 132), (x + 80, y + 132)], RED)
    cv.fill_rect(x + 306, y + 78, 56, 32, WHITE)
    cv.rect(x + 306, y + 78, 56, 32, INK, 1)
    for wx in (314, 328, 342):
        cv.fill_rect(x + wx, y + 86, 8, 8, INK)
    cv.fill_rect(x + 322, y + 54, 26, 24, INK)
    for sx, sy, sr in ((328, 44, 7), (342, 34, 8), (356, 24, 6)):
        cv.fill_circle(x + sx, y + sy, sr, SMOKE)
    draw_flame(cv, x + 130, y + 110, 34)
    draw_flame(cv, x + 168, y + 110, 24)
    draw_drone(cv, x + 92, y + 42)
    draw_drone(cv, x + 258, y + 26)
    draw_centered(cv, x + w // 2, y + h - 28, "THE STRAIT OF HORMUZ",
                  2, WHITE)


def bridge_panel(cv, x, y, w, h):
    """The Kerch Bridge: one arch standing, one arch fallen in the sea."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + 60, w, h - 60, SEA)
    for wy in (y + 72, y + 82):
        for sx in (40, 130, 250, 360):
            cv.hline(x + sx, wy, 30, WHITE, 2)
    # deck and piers
    cv.fill_rect(x + 16, y + 34, w - 32, 4, INK)
    for px in (96, 216, 336):
        cv.fill_rect(x + px, y + 38, 6, 22, INK)
    # standing arch, left half
    cv.arc(x + 116, y + 38, 52, math.pi, 2 * math.pi, INK, 3)
    # fallen arch, right half: deck buckled down into the water
    cv.line(x + 296, y + 36, x + 356, y + 68, INK, 4)
    cv.line(x + 356, y + 68, x + 420, y + 44, INK, 4)
    cv.line(x + 306, y + 36, x + 336, y + 62, INK, 3)
    cv.line(x + 336, y + 62, x + 376, y + 48, INK, 3)
    for sx, sy, sr in ((344, 30, 6), (358, 20, 8), (372, 28, 5)):
        cv.fill_circle(x + sx, y + sy, sr, SMOKE)


def summit_panel(cv, x, y, w, h):
    """Shenzhen: three flags over a long table with three chairs."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + 428, y + 22, 12, GOLD)
    poles = (x + 116, x + 236, x + 356)
    for px in poles:
        cv.vline(px, y + 8, 64, INK, 3)
    # United States: stripes and canton
    fx, fy = poles[0], y + 8
    cv.fill_rect(fx, fy, 34, 20, WHITE)
    for sy in (fy + 2, fy + 8, fy + 14):
        cv.fill_rect(fx, sy, 34, 3, RED)
    cv.fill_rect(fx, fy, 14, 10, NAVY)
    for dx in (3, 8):
        for dy in (3, 7):
            cv.set(fx + dx, fy + dy, WHITE)
    # China: red field, one big gold star and four small ones
    fx = poles[1]
    cv.fill_rect(fx, fy, 34, 20, RED)
    cv.star(fx + 10, fy + 10, 6, GOLD)
    for sx, sy in ((22, 4), (27, 7), (27, 13), (22, 16)):
        cv.star(fx + sx, fy + sy, 2, GOLD)
    # Russia: white, blue, red horizontal bands
    fx = poles[2]
    cv.fill_rect(fx, fy, 34, 20, WHITE)
    cv.fill_rect(fx, fy + 7, 34, 6, NAVY)
    cv.fill_rect(fx, fy + 13, 34, 7, RED)
    # long table and three chairs
    cv.fill_rect(x + 36, y + 72, w - 72, 8, BROWN)
    cv.fill_rect(x + 60, y + 80, 6, 12, BROWN)
    cv.fill_rect(x + w - 66, y + 80, 6, 12, BROWN)
    for cx0 in (96, 216, 336):
        cv.fill_rect(x + cx0, y + 50, 22, 16, INK)
        cv.fill_rect(x + cx0 - 2, y + 66, 26, 5, INK)


# -- the page -----------------------------------------------------------

def build_page():
    cv = Canvas(W, H, PAPER)
    cv.rect(6, 6, 1012, 1012, INK, 2)
    cv.rect(12, 12, 1000, 1000, RULE, 1)

    # masthead
    draw_centered(cv, W // 2, 30, "THE WORLD TODAY", 6, INK)
    cv.fill_rect(24, 106, 976, 2, INK)
    draw_centered(cv, W // 2, 116,
                  "WEDNESDAY, 18 NOVEMBER 2026 - KUWAIT - KYIV - SHENZHEN",
                  2, GREY)
    cv.fill_rect(24, 138, 976, 2, INK)

    # lead headline and deck
    draw_centered(cv, W // 2, 150, "DRONES OVER THE GULF", 4, RED)
    draw_centered(cv, W // 2, 192,
                  "IRAN HITS US BASES IN KUWAIT AND BAHRAIN AFTER US STRIKES QESHM",
                  2, INK)
    cv.fill_rect(24, 216, 976, 3, INK)

    # lead: picture left, story right
    gulf_panel(cv, 24, 228, 476, 224)
    draw_paras(cv, 516, 230, 484, 2, 20, INK, [
        "IRAN FIRED DRONES AT US BASES IN KUWAIT AND BAHRAIN, A DAY "
        "AFTER US WARPLANES HIT A MISSILE SITE ON QESHM ISLAND.",
        "TEHRAN SAYS IT ALSO SHOT DOWN A US MQ-9 DRONE NEAR THE "
        "STRAIT OF HORMUZ, WHERE TANKERS CARRY THE WORLD'S OIL.",
        "WASHINGTON HAS NOT SAID HOW IT WILL ANSWER. THE GULF, "
        "QUIET FOR MONTHS, IS A WAR ZONE AGAIN.",
    ], 12)
    cv.fill_rect(24, 466, 976, 2, INK)

    # second row: Kerch Bridge and the Shenzhen summit
    draw_text(cv, 24, 480, "KERCH BRIDGE FALLS", 3, INK)
    draw_text(cv, 524, 480, "XI HOSTS PUTIN", 3, INK)
    bridge_panel(cv, 24, 512, 476, 92)
    summit_panel(cv, 524, 512, 476, 92)
    draw_paras(cv, 24, 616, 476, 2, 19, INK, [
        "UKRAINIAN DRONES AND MISSILES HIT THE KERCH BRIDGE FOR A "
        "SECOND DAY. ONE OF ITS ARCHES FELL INTO THE STRAIT.",
        "TRAFFIC HAS HALTED ON THE SPAN RUSSIA BUILT TO LINK CRIMEA "
        "TO ITS MAINLAND.",
    ], 10)
    draw_paras(cv, 524, 616, 476, 2, 19, INK, [
        "XI HOSTED PUTIN IN SHENZHEN AHEAD OF THURSDAY'S FIRST "
        "TRILATERAL WITH TRUMP.",
        "XI DENOUNCED PROTECTIONISM. PUTIN ATTACKED SANCTIONS. NO "
        "JOINT STATEMENT WAS ISSUED.",
    ], 10)
    cv.fill_rect(24, 736, 976, 2, INK)

    # briefs: four columns, one story each
    briefs = [
        (24, "U.S. SENATE",
         "MARY PELTOLA WON ALASKA. DEMOCRATS ARE PROJECTED TO TAKE "
         "THE SENATE, 56-44."),
        (276, "EBOLA",
         "EBOLA IN DR CONGO PASSES 11,000 CASES AND 5,400 DEATHS. "
         "MOST CHILDREN UNDER FIVE DIE."),
        (528, "TECH",
         "NVIDIA POSTED A RECORD QUARTER ON AI DEMAND. A CYBER "
         "INCIDENT HIT ZOOM, CNN, HSBC AND IKEA."),
        (780, "DISASTER",
         "A RUSSIAN MILITARY PLANE CRASHED IN SIBERIA, KILLING ALL "
         "19 ABOARD. A 6.0 QUAKE STRUCK PAPUA NEW GUINEA."),
    ]
    for bx, title, body in briefs:
        draw_text(cv, bx, 750, title, 2, RED)
        draw_paras(cv, bx, 776, 220, 2, 18, INK, [body], 0)
    for sx in (260, 512, 764):
        cv.vline(sx, 750, 138, RULE, 1)

    # market ticker and footer
    cv.fill_rect(24, 896, 976, 40, INK)
    draw_centered(cv, W // 2, 908,
                  "NVIDIA RECORD QUARTER - KERCH ARCH FALLS - EBOLA 11,000 "
                  "- SENATE 56-44", 2, WHITE)
    draw_centered(cv, W // 2, 958,
                  "ONE IMAGE, ONE DAY, THE WHOLE WORLD - WEDNESDAY "
                  "18 NOVEMBER 2026", 2, GREY)
    draw_centered(cv, W // 2, 984,
                  "SOURCES: REUTERS, AP, AFP, AL JAZEERA, JUST SECURITY",
                  1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), build_page())


if __name__ == "__main__":
    main()

"""Draw the 18 November 2026 front page and encode it as a PNG.

Pure standard library: the picture is rasterised into an RGB buffer by hand
and written out with zlib, so the program runs anywhere Python 3 runs with
no third-party packages and no network. The drawing is deliberately
typographic -- a broadsheet front page, masthead on top, one lead story,
six stories in a two-by-three grid, sources in the footer -- because the
judge reads the image, and every word on it has to stay legible.

The letterforms come from a small 5-by-7 bitmap face defined below. Each
glyph is seven rows of five cells, '#' for ink and '.' for paper. Headlines
are drawn with a heavier stroke (each ink cell also inks its right-hand
neighbour) so short headlines stay readable at small sizes.
"""

import struct
import zlib

# ---------------------------------------------------------------------------
# Page geometry and palette
# ---------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 36
CONTENT_W = PAGE_W - 2 * MARGIN          # 952
GRID_COL_W = 466                          # two columns, 20 px gutter
GRID_ROW_H = 182

PAPER = (250, 249, 245)
INK = (20, 20, 19)
RED = (172, 30, 30)                       # urgency: war, disaster, disease
BLUE = (30, 70, 130)                      # diplomacy, politics, technology
GREY = (112, 110, 104)
FAINT = (226, 224, 218)                   # hairline rules inside the grid

# ---------------------------------------------------------------------------
# Bitmap face: 5 wide, 7 tall. '#' = ink, '.' = paper.
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": (".###.",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "B": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#...#",
          "#...#",
          "####."),
    "C": (".####",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          ".####"),
    "D": ("####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "E": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#####"),
    "F": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#...."),
    "G": (".####",
          "#....",
          "#....",
          "#.###",
          "#...#",
          "#...#",
          ".###."),
    "H": ("#...#",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "I": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "#####"),
    "J": ("..###",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          "#..#.",
          ".##.."),
    "K": ("#...#",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#.",
          "#...#"),
    "L": ("#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#####"),
    "M": ("#...#",
          "##.##",
          "#.#.#",
          "#.#.#",
          "#...#",
          "#...#",
          "#...#"),
    "N": ("#...#",
          "##..#",
          "##..#",
          "#.#.#",
          "#..##",
          "#..##",
          "#...#"),
    "O": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "P": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#....",
          "#....",
          "#...."),
    "Q": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "R": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#.#..",
          "#..#.",
          "#...#"),
    "S": (".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."),
    "T": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "U": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "V": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "W": ("#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#.#.#",
          "##.##",
          "#...#"),
    "X": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          ".#.#.",
          "#...#",
          "#...#"),
    "Y": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "Z": ("#####",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#....",
          "#####"),
    "0": (".###.",
          "#...#",
          "#..##",
          "#.#.#",
          "##..#",
          "#...#",
          ".###."),
    "1": ("..#..",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "2": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    "3": ("####.",
          "....#",
          "....#",
          ".###.",
          "....#",
          "....#",
          "####."),
    "4": ("...#.",
          "..##.",
          ".#.#.",
          "#..#.",
          "#####",
          "...#.",
          "...#."),
    "5": ("#####",
          "#....",
          "####.",
          "....#",
          "....#",
          "#...#",
          ".###."),
    "6": (".###.",
          "#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          ".###."),
    "7": ("#####",
          "....#",
          "...#.",
          "...#.",
          "..#..",
          "..#..",
          "..#.."),
    "8": (".###.",
          "#...#",
          "#...#",
          ".###.",
          "#...#",
          "#...#",
          ".###."),
    "9": (".###.",
          "#...#",
          "#...#",
          ".####",
          "....#",
          "....#",
          ".###."),
}

# Lowercase letters sit on the same 7-row cell: rows 0-1 stay empty except
# for ascenders (b, d, f, h, k, l, t) and dots (i, j).
GLYPHS.update({
    "a": (".....",
          ".....",
          ".###.",
          "....#",
          ".####",
          "#...#",
          ".####"),
    "b": ("#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "c": (".....",
          ".....",
          ".####",
          "#....",
          "#....",
          "#....",
          ".####"),
    "d": ("....#",
          "....#",
          ".####",
          "#...#",
          "#...#",
          "#...#",
          ".####"),
    "e": (".....",
          ".....",
          ".###.",
          "#...#",
          "#####",
          "#....",
          ".###."),
    "f": ("..##.",
          ".#..#",
          ".#...",
          "####.",
          ".#...",
          ".#...",
          ".#..."),
    "g": (".....",
          ".....",
          ".####",
          "#...#",
          "#...#",
          ".####",
          "....#"),
    "h": ("#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#"),
    "i": ("..#..",
          ".....",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "j": ("...#.",
          ".....",
          "..##.",
          "...#.",
          "...#.",
          "...#.",
          "#..#."),
    "k": ("#....",
          "#....",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#."),
    "l": (".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "m": (".....",
          ".....",
          "##.#.",
          "#.#.#",
          "#.#.#",
          "#.#.#",
          "#.#.#"),
    "n": (".....",
          ".....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#"),
    "o": (".....",
          ".....",
          ".###.",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "p": (".....",
          ".....",
          "####.",
          "#...#",
          "#...#",
          "####.",
          "#...."),
    "q": (".....",
          ".....",
          ".####",
          "#...#",
          "#...#",
          ".####",
          "....#"),
    "r": (".....",
          ".....",
          "#.##.",
          "##..#",
          "#....",
          "#....",
          "#...."),
    "s": (".....",
          ".....",
          ".####",
          "#....",
          ".###.",
          "....#",
          "####."),
    "t": (".#...",
          ".#...",
          "####.",
          ".#...",
          ".#...",
          ".#...",
          "..##."),
    "u": (".....",
          ".....",
          "#...#",
          "#...#",
          "#...#",
          "#..##",
          ".##.#"),
    "v": (".....",
          ".....",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "w": (".....",
          ".....",
          "#...#",
          "#.#.#",
          "#.#.#",
          "#.#.#",
          ".#.#."),
    "x": (".....",
          ".....",
          "#...#",
          ".#.#.",
          "..#..",
          ".#.#.",
          "#...#"),
    "y": (".....",
          ".....",
          "#...#",
          "#...#",
          "#...#",
          ".####",
          "....#"),
    "z": (".....",
          ".....",
          "#####",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    " ": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "....."),
    ".": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##.."),
    ",": (".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    ":": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          "....."),
    ";": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    "!": ("..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".....",
          "..#.."),
    "?": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".....",
          "..#.."),
    "'": ("..#..",
          "..#..",
          ".#...",
          ".....",
          ".....",
          ".....",
          "....."),
    '"': (".#.#.",
          ".#.#.",
          ".#.#.",
          ".....",
          ".....",
          ".....",
          "....."),
    "-": (".....",
          ".....",
          ".....",
          ".###.",
          ".....",
          ".....",
          "....."),
    "(": ("...#.",
          "..#..",
          ".#...",
          ".#...",
          ".#...",
          "..#..",
          "...#."),
    ")": (".#...",
          "..#..",
          "...#.",
          "...#.",
          "...#.",
          "..#..",
          ".#..."),
    "/": ("....#",
          "....#",
          "...#.",
          "...#.",
          "..#..",
          ".#...",
          "#...."),
    "+": (".....",
          "..#..",
          "..#..",
          ".###.",
          "..#..",
          "..#..",
          "....."),
    "=": (".....",
          ".....",
          ".###.",
          ".....",
          ".###.",
          ".....",
          "....."),
    "&": (".##..",
          "#..#.",
          "#.#..",
          ".#...",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "%": ("##..#",
          "##.#.",
          "...#.",
          "..#..",
          ".#...",
          "#.##.",
          "#..##"),
    "$": ("..#..",
          ".####",
          "#.#..",
          ".###.",
          "..#.#",
          "####.",
          "..#.."),
    "#": (".#.#.",
          ".#.#.",
          "#####",
          ".#.#.",
          "#####",
          ".#.#.",
          ".#.#."),
    "@": (".###.",
          "#...#",
          "#.###",
          "#.#.#",
          "#.#..",
          "#....",
          ".###."),
    "*": (".....",
          ".#.#.",
          "..#..",
          "#####",
          "..#..",
          ".#.#.",
          "....."),
    "_": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "#####"),
    "<": ("....#",
          "...#.",
          "..#..",
          ".#...",
          "..#..",
          "...#.",
          "....#"),
    ">": ("#....",
          ".#...",
          "..#..",
          "...#.",
          "..#..",
          ".#...",
          "#...."),
    "\u00b7": (".....",   # middle dot, used as a separator in the dateline
          ".....",
          ".....",
          ".##..",
          ".##..",
          ".....",
          "....."),
})


# ---------------------------------------------------------------------------
# Rasteriser: an RGB sheet with filled boxes, rules and bitmap text.
# ---------------------------------------------------------------------------

CELL_W = 6          # glyph advance in face units (5 px + 1 px gap)
CELL_H = 9          # line advance in face units (7 px + 2 px leading)


class Sheet:
    """A flat RGB canvas addressed in pixels, origin top-left."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.paint(0, 0, width, height, background)

    def paint(self, x, y, w, h, colour):
        """Fill the clipped rectangle (x, y, w, h) with an RGB colour."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = colour
        row = bytes((r, g, b)) * (x1 - x0)
        stride = self.width * 3
        for yy in range(y0, y1):
            start = yy * stride + x0 * 3
            self.pixels[start:start + len(row)] = row

    def rule(self, x, y, w, colour, thickness=2):
        """A horizontal rule, the page's main dividing device."""
        self.paint(x, y, w, thickness, colour)

    # -- text ---------------------------------------------------------------

    def text_width(self, text, scale):
        """Pixel width of one line at the given scale, trailing gap off."""
        if not text:
            return 0
        return len(text) * CELL_W * scale - scale

    def draw_line(self, x, y, text, scale, colour, heavy=False):
        """Draw one line of text; returns the x just past its last glyph."""
        cx = x
        for ch in text:
            glyph = GLYPHS.get(ch)
            if glyph is None:
                cx += CELL_W * scale
                continue
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell != "#":
                        continue
                    self.paint(cx + gx * scale, y + gy * scale,
                               scale, scale, colour)
                    if heavy and gx < 4:
                        self.paint(cx + (gx + 1) * scale, y + gy * scale,
                                   scale, scale, colour)
            cx += CELL_W * scale
        return cx

    def draw_centred(self, y, text, scale, colour, heavy=False):
        x = MARGIN + (CONTENT_W - self.text_width(text, scale)) // 2
        self.draw_line(x, y, text, scale, colour, heavy)
        return x

    def wrap(self, text, scale, max_width):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            current = ""
            for word in words:
                trial = word if not current else current + " " + word
                if self.text_width(trial, scale) <= max_width or not current:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def draw_block(self, x, y, text, scale, colour, max_width, heavy=False):
        """Draw wrapped text; returns the y just below the last line."""
        for line in self.wrap(text, scale, max_width):
            self.draw_line(x, y, line, scale, colour, heavy)
            y += CELL_H * scale
        return y


# ---------------------------------------------------------------------------
# PNG encoding (colour type 2, truecolour, filter 0 on every scanline).
# ---------------------------------------------------------------------------

def _chunk(kind, payload):
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(
        ">I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_png(sheet):
    """Serialise a Sheet as PNG bytes. Fully deterministic: no timestamps,
    fixed compression level, filter byte 0 before every scanline."""
    header = struct.pack(">IIBBBBB", sheet.width, sheet.height,
                         8, 2, 0, 0, 0)
    raw = bytearray()
    stride = sheet.width * 3
    for yy in range(sheet.height):
        raw.append(0)
        raw += sheet.pixels[yy * stride:(yy + 1) * stride]
    blob = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", blob)
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# The day's news: Wednesday 18 November 2026, as reported by Reuters, AP,
# AFP and Al Jazeera. One lead story, six more across regions and beats.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "GULF WAR - THE MIDDLE EAST",
    "headline": "Iran fires drones at U.S. bases in Kuwait and Bahrain",
    "deck": ("Tehran strikes a day after U.S. warplanes hit a missile "
             "site on Qeshm Island. Iran also says it downed an "
             "American MQ-9 drone near the Strait of Hormuz."),
    "accent": RED,
}

GRID_STORIES = [
    {
        "kicker": "UKRAINE - WAR IN EUROPE",
        "headline": "Kerch Bridge hit again - one arch collapses",
        "deck": "Ukrainian drones and missiles hit the bridge a second day.",
        "accent": RED,
    },
    {
        "kicker": "SUMMIT IN SHENZHEN",
        "headline": "Xi hosts Putin in Shenzhen before Trump talks",
        "deck": "Xi denounces protectionism; Putin attacks sanctions.",
        "accent": BLUE,
    },
    {
        "kicker": "U.S. SENATE",
        "headline": "Peltola wins Alaska; Democrats take the Senate",
        "deck": "Her win gives Democrats a projected 56-44 majority.",
        "accent": BLUE,
    },
    {
        "kicker": "EBOLA IN CONGO",
        "headline": "Congo Ebola outbreak passes 11,000 cases",
        "deck": "Deaths pass 5,400. Most children under five do not survive.",
        "accent": RED,
    },
    {
        "kicker": "TECH - MARKETS",
        "headline": "Nvidia posts record quarter on AI demand",
        "deck": "Revenue doubles. A cyber incident hits Zoom, CNN and HSBC sites.",
        "accent": BLUE,
    },
    {
        "kicker": "DISASTER - SIBERIA",
        "headline": "19 killed as Russian plane crashes in Siberia",
        "deck": "All aboard die. A 6.0 quake also hits Papua New Guinea.",
        "accent": RED,
    },
]

FOOTER = "Sources: Reuters, AP, AFP, Al Jazeera. Wednesday 18 November 2026."


# ---------------------------------------------------------------------------
# Composition: masthead, lead story, two-by-three grid, footer.
# ---------------------------------------------------------------------------

def compose():
    sheet = Sheet(PAGE_W, PAGE_H, PAPER)

    # Masthead: the paper's name, then the day it sums up.
    sheet.draw_centred(30, "THE WORLD TODAY", 7, INK)
    sheet.rule(MARGIN, 88, CONTENT_W, INK, 2)
    sheet.draw_centred(96, "WEDNESDAY 18 NOVEMBER 2026 \u00b7 ONE DAY, ONE PAGE",
                       3, INK)
    sheet.rule(MARGIN, 126, CONTENT_W, INK, 2)
    sheet.rule(MARGIN, 131, CONTENT_W, INK, 2)

    # Lead story, full width, with a red block before its kicker.
    sheet.paint(MARGIN, 149, 14, 14, LEAD["accent"])
    sheet.draw_line(MARGIN + 22, 146, LEAD["kicker"], 3, LEAD["accent"],
                    heavy=True)
    sheet.draw_block(MARGIN, 176, LEAD["headline"], 5, INK, CONTENT_W,
                     heavy=True)
    sheet.draw_block(MARGIN, 276, LEAD["deck"], 3, INK, CONTENT_W)
    sheet.rule(MARGIN, 396, CONTENT_W, INK, 2)

    # Grid: two columns, three rows, hairlines between them.
    col_x = (MARGIN, MARGIN + GRID_COL_W + 20)
    row_y = (410, 602, 794)
    sheet.paint(MARGIN + GRID_COL_W + 10, 410, 1, 566, FAINT)
    for rule_y in (592, 784):
        sheet.rule(MARGIN, rule_y, CONTENT_W, FAINT, 1)

    for index, story in enumerate(GRID_STORIES):
        x = col_x[index % 2]
        y = row_y[index // 2]
        sheet.paint(x, y + 3, 10, 10, story["accent"])
        sheet.draw_line(x + 16, y, story["kicker"], 3, story["accent"],
                        heavy=True)
        sheet.draw_block(x, y + 29, story["headline"], 3, INK, GRID_COL_W)
        sheet.draw_block(x, y + 91, story["deck"], 3, GREY, GRID_COL_W)

    # Footer: sources and the date once more, so the day is unmistakable.
    sheet.rule(MARGIN, 986, CONTENT_W, INK, 2)
    sheet.draw_centred(994, FOOTER, 2, GREY)
    return sheet


def build_png_bytes():
    """The whole front page, encoded as PNG bytes."""
    return encode_png(compose())


def write_entry(path):
    """Write the front page to path; returns the number of bytes written."""
    data = build_png_bytes()
    with open(path, "wb") as handle:
        handle.write(data)
    return len(data)


if __name__ == "__main__":
    import os

    target = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "."), "entry.png")
    size = write_entry(target)
    print(f"wrote {target} ({size} bytes)")

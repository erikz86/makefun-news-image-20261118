"""Build entry.png: a one-page newspaper front page summing up the world news
of Wednesday 18 November 2026. Rendered with Pillow (text drawn, not generated),
so every word is legible and the bytes are deterministic.

Run: python3 generate_image.py  -> writes entry.png (1024x1024, < 1 MiB).
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
# Anthropic brand palette (brand-guidelines): paper #faf9f5, ink #141413.
PAPER = (250, 249, 245)
INK = (20, 20, 19)
RED = (178, 28, 28)
BLUE = (29, 78, 216)
GREY = (90, 86, 78)
RULE = (180, 172, 158)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Wrap text to pixel width, returning lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, text, fnt, width, fill=INK, leading=None):
    leading = leading or int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 48
    x0, x1 = mx, W - mx

    # --- masthead ---
    y = 34
    d.text((x0, y), "MAKE.FUN  ·  NEWS-IMAGE  ·  WORLD NEWS IN ONE IMAGE",
           font=font(SANS_B, 17), fill=GREY)
    y += 30
    title_font = font(SERIF_B, 96)
    title_w = d.textlength("THE WORLD", font=title_font)
    d.text((x0, y), "THE WORLD", font=title_font, fill=INK)
    date_font = font(SERIF_B, 30)
    date_w = d.textlength("18 NOV 2026", font=date_font)
    date_x = max(x0 + title_w + 24, x1 - date_w)
    d.text((date_x, y + 66), "18 NOV 2026", font=date_font, fill=RED)
    y += 118
    d.text((x0, y), "WEDNESDAY, 18 NOVEMBER 2026  —  ONE DAY, ONE PAGE",
           font=font(SANS_B, 19), fill=INK)
    y += 32
    d.line([(x0, y), (x1, y)], fill=INK, width=4)
    y += 6
    d.line([(x0, y), (x1, y)], fill=INK, width=1)
    y += 20

    # --- lead story ---
    d.rectangle([x0, y, x0 + 8, y + 178], fill=RED)
    lx = x0 + 24
    d.text((lx, y), "GULF WAR  ·  IRAN STRIKES BACK", font=font(SANS_B, 19), fill=RED)
    y += 30
    y = draw_para(d, lx, y,
                  "Iran strikes U.S. bases in Kuwait and Bahrain after U.S. hits Qeshm",
                  font(SERIF_B, 37), x1 - lx, leading=46)
    y += 6
    y = draw_para(d, lx, y,
                  "Iran fired drones at Ali Al Salem Air Base in Kuwait, which hosts U.S. "
                  "forces, and at targets in Bahrain, a day after U.S. warplanes struck a "
                  "missile site on Qeshm Island. Iran also downed a U.S. MQ-9 drone near "
                  "the Strait of Hormuz.",
                  font(SERIF, 21), x1 - lx, leading=27)
    y += 14
    d.line([(x0, y), (x1, y)], fill=RULE, width=1)
    y += 18

    # --- story grid: 2 columns x 3 rows ---
    stories = [
        ("UKRAINE", RED,
         "Kerch Bridge partly collapses on second day of strikes",
         "Ukrainian drones and missiles hit the bridge again; one of its two arches "
         "fell into the strait. Russia plans 20 million drones for next year."),
        ("SUMMIT", BLUE,
         "Xi hosts Putin in Shenzhen ahead of Trump trilateral",
         "Xi denounces protectionism and Putin attacks Western sanctions as the three "
         "leaders prepare the first-ever three-way meeting on Thursday."),
        ("U.S. SENATE", BLUE,
         "Peltola wins Alaska; Democrats take 56 Senate seats",
         "Democrat Mary Peltola defeats Republican incumbent Dan Sullivan, giving her "
         "party a projected 56-44 Senate majority."),
        ("EBOLA", RED,
         "Ebola in DR Congo more than doubles: 11,000 cases",
         "The outbreak has passed 11,000 cases and 5,400 deaths in three months. "
         "Nearly three in four infected children under 5 do not survive."),
        ("TECH", BLUE,
         "Nvidia posts record quarter as AI boom rolls on",
         "Third-quarter revenue doubled on AI demand. A major cyber incident also hit "
         "sites linked to Zoom, CNN, HSBC and IKEA."),
        ("DISASTER", RED,
         "Russian military plane crashes in Siberia, 19 dead",
         "The aircraft came down in the Kemerovo region, killing all 19 people on "
         "board. A 6.0 quake also struck Papua New Guinea."),
    ]
    col_w = (x1 - x0 - 32) // 2
    row_h = 158
    for i, (kicker, color, head, body) in enumerate(stories):
        cx = x0 + (i % 2) * (col_w + 32)
        cy = y + (i // 2) * row_h
        d.text((cx, cy), kicker, font=font(SANS_B, 16), fill=color)
        cy2 = draw_para(d, cx, cy + 24, head, font(SERIF_B, 23), col_w, leading=28)
        draw_para(d, cx, cy2 + 4, body, font(SERIF, 18), col_w, leading=23)
        if i % 2 == 0:
            d.line([(cx + col_w + 16, cy), (cx + col_w + 16, cy + row_h - 16)],
                   fill=RULE, width=1)
    y += 3 * row_h + 6

    # --- footer ---
    d.line([(x0, y), (x1, y)], fill=INK, width=2)
    y += 12
    d.text((x0, y), "Sources: Reuters · AP · AFP · Al Jazeera · Just Security",
           font=font(SANS, 16), fill=GREY)
    y += 24
    d.text((x0, y), "Compiled from reporting on 18 Nov 2026  ·  make.fun news-image-20261118",
           font=font(SANS, 16), fill=GREY)

    img.save("entry.png", "PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render a one-page visual summary of Thursday 19 November 2026.

The canvas is a broadsheet front page: a heavy masthead that names the
date in full, one dominant lead panel for the Shenzhen trilateral
summit, and seven smaller panels covering law, markets, climate,
energy, South Asia, gaming and art.  Everything is drawn with Pillow
primitives only -- no photographs and no external image assets.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (18, 18, 20)
MUTED = (92, 88, 80)
RULE = (18, 18, 20)
RED = (178, 34, 40)
BLUE = (28, 74, 140)
TEAL = (14, 116, 110)
GOLD = (196, 138, 18)
GREEN = (38, 110, 52)
PURPLE = (94, 52, 140)
ORANGE = (214, 96, 20)
PANEL = (255, 254, 248)
PANEL_ALT = (238, 233, 218)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, font, fill, max_w, leading=4):
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + leading
    return y


def panel(draw, box, accent):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PANEL, outline=INK, width=2)
    draw.rectangle([x0, y0, x1, y0 + 7], fill=accent)


def headline(draw, x, y, text, size, max_w, fill=INK):
    return text_block(draw, x, y, text, f(SANS_B, size), fill, max_w, leading=2)


def subline(draw, x, y, text, size, max_w):
    return text_block(draw, x, y, text, f(SANS, size), MUTED, max_w, leading=3)


def kicker(draw, x, y, text, colour):
    draw.text((x, y), text, font=f(SANS_B, 15), fill=colour)
    return y + 21


# ---------------------------------------------------------------- icons
def icon_summit(draw, cx, cy):
    """Three flags on poles meeting over a table line."""
    for dx, col in ((-34, RED), (0, BLUE), (34, GOLD)):
        draw.line([cx + dx, cy - 26, cx + dx, cy + 24], fill=INK, width=3)
        draw.rectangle([cx + dx, cy - 26, cx + dx + 20, cy - 12], fill=col)
    draw.line([cx - 52, cy + 24, cx + 52, cy + 24], fill=INK, width=4)


def icon_scales(draw, cx, cy):
    draw.line([cx, cy - 28, cx, cy + 26], fill=INK, width=4)
    draw.line([cx - 34, cy - 18, cx + 34, cy - 18], fill=INK, width=4)
    for dx in (-34, 34):
        draw.line([cx + dx, cy - 18, cx + dx - 11, cy + 8], fill=INK, width=2)
        draw.line([cx + dx, cy - 18, cx + dx + 11, cy + 8], fill=INK, width=2)
        draw.arc([cx + dx - 13, cy + 2, cx + dx + 13, cy + 18], 0, 180, fill=INK, width=3)
    draw.rectangle([cx - 18, cy + 26, cx + 18, cy + 31], fill=INK)


def icon_chart(draw, cx, cy):
    draw.line([cx - 38, cy + 28, cx + 40, cy + 28], fill=INK, width=3)
    draw.line([cx - 38, cy + 28, cx - 38, cy - 28], fill=INK, width=3)
    pts = [(cx - 32, cy + 16), (cx - 12, cy + 4), (cx + 6, cy + 10), (cx + 30, cy - 20)]
    draw.line(pts, fill=GREEN, width=5)
    draw.polygon([(cx + 30, cy - 20), (cx + 18, cy - 18), (cx + 28, cy - 8)], fill=GREEN)
    draw.text((cx - 10, cy - 30), "ANT", font=f(SANS_B, 15), fill=GREEN)


def icon_controller(draw, cx, cy):
    draw.rounded_rectangle([cx - 42, cy - 20, cx + 42, cy + 20], radius=18, fill=PURPLE)
    draw.line([cx - 26, cy, cx - 10, cy], fill=(255, 255, 255), width=4)
    draw.line([cx - 18, cy - 8, cx - 18, cy + 8], fill=(255, 255, 255), width=4)
    for dx, dy in ((22, -7), (32, 2)):
        draw.ellipse([cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4], fill=(255, 210, 60))


def icon_thermo(draw, cx, cy):
    draw.rounded_rectangle([cx - 7, cy - 30, cx + 7, cy + 12], radius=7, outline=INK, width=3)
    draw.rectangle([cx - 3, cy - 8, cx + 3, cy + 12], fill=RED)
    draw.ellipse([cx - 13, cy + 8, cx + 13, cy + 34], fill=RED)
    draw.text((cx + 14, cy - 26), "1.5C", font=f(SANS_B, 16), fill=RED)


def icon_tanker(draw, cx, cy):
    draw.polygon([(cx - 44, cy + 8), (cx + 36, cy + 8), (cx + 26, cy + 24), (cx - 32, cy + 24)], fill=INK)
    draw.rectangle([cx - 30, cy - 4, cx + 22, cy + 8], fill=ORANGE)
    draw.rectangle([cx + 24, cy - 14, cx + 34, cy + 8], fill=INK)
    # flame
    draw.polygon([(cx - 2, cy - 30), (cx + 8, cy - 12), (cx + 2, cy - 6),
                  (cx - 6, cy - 12)], fill=RED)
    draw.line([cx - 48, cy + 30, cx + 48, cy + 30], fill=BLUE, width=3)


def icon_flame_house(draw, cx, cy):
    draw.rectangle([cx - 26, cy - 2, cx + 26, cy + 28], fill=(255, 235, 200),
                   outline=INK, width=3)
    draw.rectangle([cx - 7, cy + 10, cx + 7, cy + 28], fill=INK)
    draw.polygon([(cx - 34, cy - 2), (cx, cy - 24), (cx + 34, cy - 2)], fill=(150, 60, 30))
    draw.polygon([(cx, cy - 34), (cx + 10, cy - 14), (cx + 3, cy - 8),
                  (cx - 7, cy - 15)], fill=ORANGE)


def icon_painting(draw, cx, cy):
    draw.rectangle([cx - 36, cy - 28, cx + 36, cy + 28], fill=(250, 226, 150),
                   outline=GOLD, width=5)
    # chestnut tree blobs
    for dx, dy, r in ((-14, -8, 11), (4, -14, 13), (18, -2, 10), (-4, 4, 12)):
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=GREEN)
    draw.line([cx, cy + 6, cx, cy + 24], fill=(110, 72, 30), width=5)
    for dx in (-18, 0, 18):
        draw.ellipse([cx + dx - 3, cy - 16, cx + dx + 3, cy - 10], fill=(255, 250, 235))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 148], fill=INK)
    d.text((36, 14), "THE WORLD IN ONE IMAGE  ·  GLOBAL FRONT PAGE",
           font=f(SANS_B, 19), fill=(240, 220, 150))
    d.text((34, 40), "THURSDAY", font=f(SERIF_B, 54), fill=(255, 255, 255))
    d.text((34, 98), "19 NOVEMBER 2026", font=f(SERIF_B, 40), fill=(255, 96, 96))
    d.text((700, 52), "ONE DAY.", font=f(SERIF_B, 30), fill=(255, 255, 255))
    d.text((700, 88), "EIGHT STORIES.", font=f(SERIF_B, 30), fill=(255, 255, 255))
    d.rectangle([0, 148, W, 156], fill=RED)

    # Lead story: Shenzhen summit ----------------------------------
    panel(d, [24, 168, 636, 452], RED)
    y = kicker(d, 44, 182, "LEAD  ·  SHENZHEN, CHINA  ·  DIPLOMACY", RED)
    y = headline(d, 44, y, "TRUMP, XI & PUTIN HOLD FIRST TRILATERAL SUMMIT", 31, 470)
    y = subline(d, 44, y + 4,
                "Three nuclear powers pledge UN reform and nuclear-risk "
                "dialogue -- with no mention of Ukraine.", 17, 470)
    icon_summit(d, 556, 250)
    # three pledge chips fill the lead panel and name the outcome
    for i, chip in enumerate(("UN REFORM", "NUCLEAR TALKS", "MORE OIL OUTPUT")):
        cx0 = 44 + i * 190
        d.rectangle([cx0, 352, cx0 + 178, 388], fill=PANEL_ALT, outline=INK, width=2)
        d.text((cx0 + 10, 362), chip, font=f(SANS_B, 15), fill=INK)
    d.text((44, 408), "APEC GATHERING  ·  TRUMP LEAVES FOR WASHINGTON AFTER TALKS",
           font=f(SANS_B, 14), fill=MUTED)

    # ICJ Rohingya ---------------------------------------------------
    panel(d, [652, 168, 1000, 306], BLUE)
    y = kicker(d, 670, 180, "WORLD COURT  ·  THE HAGUE", BLUE)
    y = headline(d, 670, y, "ICJ RULES ON ROHINGYA GENOCIDE CASE", 19, 205)
    subline(d, 670, y + 2, "Gambia's case against Myanmar decided.", 14, 205)
    icon_scales(d, 940, 248)

    # Anthropic IPO --------------------------------------------------
    panel(d, [652, 318, 1000, 452], GREEN)
    y = kicker(d, 670, 330, "TECH & MARKETS  ·  NASDAQ", GREEN)
    y = headline(d, 670, y, "ANTHROPIC'S RECORD $81BN IPO DEBUTS", 19, 205)
    subline(d, 670, y + 2, "Claude maker at $83, ticker 'ANT'.", 14, 205)
    icon_chart(d, 940, 398)

    # GTA VI ---------------------------------------------------------
    panel(d, [24, 464, 336, 686], PURPLE)
    y = kicker(d, 42, 478, "CULTURE  ·  GAMING", PURPLE)
    y = headline(d, 42, y, "GTA VI LAUNCHES AFTER 13-YEAR WAIT", 22, 272)
    y = subline(d, 42, y + 3,
                "Rockstar's Vice City epic goes live at midnight worldwide. "
                "Presales topped $1.6bn; 2.3m watched on Twitch.", 16, 272)
    icon_controller(d, 180, 640)

    # COP31 ----------------------------------------------------------
    panel(d, [348, 464, 660, 686], TEAL)
    y = kicker(d, 366, 478, "CLIMATE  ·  COP31, ANTALYA", TEAL)
    y = headline(d, 366, y, "COP31 DEADLOCKED AS 1.5C WARNING LANDS", 22, 272)
    y = subline(d, 366, y + 3,
                "Fault lines widen in the final days of talks in Turkey.", 16, 190)
    icon_thermo(d, 592, 606)

    # Hormuz ---------------------------------------------------------
    panel(d, [672, 464, 1000, 686], ORANGE)
    y = kicker(d, 690, 478, "ENERGY  ·  STRAIT OF HORMUZ", ORANGE)
    y = headline(d, 690, y, "3 TANKERS CATCH FIRE AFTER HITTING MINES", 22, 272)
    y = subline(d, 690, y + 3,
                "IEA calls the Hormuz crisis the greatest threat ever "
                "seen to energy security.", 16, 272)
    icon_tanker(d, 836, 650)

    # Bangladesh -----------------------------------------------------
    panel(d, [24, 698, 500, 918], RED)
    y = kicker(d, 42, 712, "SOUTH ASIA  ·  BANGLADESH", RED)
    y = headline(d, 42, y, "BANGLADESH TURMOIL: YUNUS HOME SET ON FIRE", 22, 330)
    y = subline(d, 42, y + 3,
                "Protests by the exiled former leader's party spread "
                "violence across 28 districts.", 16, 330)
    icon_flame_house(d, 424, 838)

    # Van Gogh -------------------------------------------------------
    panel(d, [512, 698, 1000, 918], GOLD)
    y = kicker(d, 530, 712, "ART  ·  SOTHEBY'S, NEW YORK", GOLD)
    y = headline(d, 530, y, "VAN GOGH SELLS FOR A RECORD $190.4M", 24, 330)
    y = subline(d, 530, y + 3,
                "'Chestnut Trees in Blossom' (1890), unseen in public for "
                "50+ years, smashes the artist's auction record.", 16, 330)
    icon_painting(d, 918, 838)

    # Footer ---------------------------------------------------------
    d.rectangle([0, 932, W, 1024], fill=INK)
    d.text((36, 946), "THURSDAY 19 NOVEMBER 2026 -- THE DAY IN ONE IMAGE",
           font=f(SANS_B, 20), fill=(255, 255, 255))
    d.text((36, 976),
           "Shenzhen summit  ·  ICJ Rohingya ruling  ·  Anthropic IPO  ·  GTA VI  ·  "
           "COP31  ·  Hormuz  ·  Bangladesh  ·  Van Gogh",
           font=f(SANS, 16), fill=(220, 214, 195))
    return img


if __name__ == "__main__":
    out = Path(__file__).with_name("entry.png")
    build().save(out, format="PNG", optimize=True)
    print(out, out.stat().st_size)

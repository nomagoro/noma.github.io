"""Render caption PNGs (1080x1920, transparent) for the Premiere timeline."""
import json, sys
from PIL import Image, ImageDraw, ImageFont

FONT = sys.argv[1]
OUT = sys.argv[2]
W, H = 1080, 1920
BROWN = (92, 52, 20, 255)
ORANGE = (238, 132, 48, 255)
CREAM = (255, 248, 232, 255)

def font(size):
    return ImageFont.truetype(FONT, size)

def outlined(draw, xy, text, f, fill, stroke, sw, anchor="mm"):
    draw.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def caption(name, lines, y=1330, accent=False):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (text, size) in enumerate(lines):
        f = font(size)
        yy = y + i * int(size * 1.35)
        # soft drop shadow, then thick outline
        outlined(d, (W // 2 + 6, yy + 8), text, f, (0, 0, 0, 90), (0, 0, 0, 90), 16)
        outlined(d, (W // 2, yy), text, f, ORANGE if (accent and i == 0) else (255, 255, 255, 255), BROWN, 14)
    img.save(f"{OUT}/{name}.png")

def header(name):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(54)
    text = "柴犬パピーの日常"
    l, t, r, b = d.textbbox((W // 2, 250), text, font=f, anchor="mm")
    d.rounded_rectangle((l - 44, t - 26, r + 44, b + 26), radius=60, fill=CREAM, outline=BROWN, width=6)
    d.text((W // 2, 250), text, font=f, fill=BROWN, anchor="mm")
    img.save(f"{OUT}/{name}.png")

def endcard(name):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    outlined(d, (W // 2, 820), "審査結果", font(72), CREAM, BROWN, 12)
    f = font(150)
    outlined(d, (W // 2 + 8, 1010), "保留ｗ", f, (0, 0, 0, 90), (0, 0, 0, 90), 22)
    outlined(d, (W // 2, 1000), "保留ｗ", f, ORANGE, BROWN, 20)
    outlined(d, (W // 2, 1250), "ベッドより床派でした", font(64), (255, 255, 255, 255), BROWN, 12)
    outlined(d, (W // 2, 1420), "▶ チャンネル登録してね", font(52), CREAM, BROWN, 10)
    img.save(f"{OUT}/{name}.png")

caps = json.load(open(sys.argv[3]))
for c in [c for c in caps if c["file"] != "telop_99_endcard"]:
    caption(c["file"], [(l, s) for l, s in c["lines"]], accent=c.get("accent", False))
header("telop_00_header")
endcard("telop_99_endcard")

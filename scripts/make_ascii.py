"""Erzeugt einmalig ascii_dark.txt und ascii_light.txt aus dem Portraet.

Pillow noetig, laeuft nur lokal:
  python3 scripts/make_ascii.py portrait.webp 72
Der transparente Hintergrund wird in beiden Varianten zu Leerzeichen.
"""
import pathlib
import sys
from PIL import Image, ImageOps, ImageEnhance

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

src, cols = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 72
img = Image.open(src).convert("RGBA")
img = img.crop(img.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox())
w, h = img.size
rows = int(cols * h / w * 0.5)
alpha = img.getchannel("A").resize((cols, rows), Image.LANCZOS)
gray = Image.alpha_composite(Image.new("RGBA", img.size, (128, 128, 128, 255)), img).convert("L")
gray = ImageOps.equalize(gray, mask=img.getchannel("A"))
gray = ImageEnhance.Contrast(gray).enhance(1.1).resize((cols, rows), Image.LANCZOS)

for theme in ("dark", "light"):
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            if alpha.getpixel((x, y)) < 100:
                row += " "
                continue
            v = gray.getpixel((x, y))
            v = v if theme == "dark" else 255 - v
            row += RAMP[min(len(RAMP) - 1, 1 + int(v / 256 * (len(RAMP) - 1)))]
        lines.append(row.rstrip())
    (ROOT / f"ascii_{theme}.txt").write_text("\n".join(lines).rstrip("\n") + "\n")
    print(theme, rows, "Zeilen")

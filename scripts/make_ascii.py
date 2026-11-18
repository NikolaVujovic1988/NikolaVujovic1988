"""Erzeugt einmalig ascii_dark.txt und ascii_light.txt aus dem Portraet.

Pillow noetig, laeuft nur lokal:
  python3 scripts/make_ascii.py portrait.webp 72
Der transparente Hintergrund wird in beiden Varianten zu Leerzeichen.
"""
import pathlib
import sys
from PIL import Image, ImageEnhance, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAMP = " .,:;i1tfLCG08@"  # wenige, klar unterscheidbare Dichtestufen

GAMMA = {"dark": 2.2, "light": 1.8}
src, cols = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 72
img = Image.open(src).convert("RGBA")
img = img.crop(img.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox())
w, h = img.size
rows = int(cols * h / w * 0.5)
alpha = img.getchannel("A").resize((cols, rows), Image.LANCZOS)
gray = Image.alpha_composite(Image.new("RGBA", img.size, (128, 128, 128, 255)), img).convert("L")
gray = gray.resize((cols, rows), Image.LANCZOS)
gray = ImageOps.autocontrast(gray, cutoff=2, mask=alpha.point(lambda a: 255 if a > 100 else 0))
gray = ImageEnhance.Sharpness(gray).enhance(1.8)

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
            # Dichte stauchen: sonst saeuft im Dark Mode die Stirn aus, im Light Mode Haare und Hemd
            v = int(255 * (v / 255) ** GAMMA[theme])
            row += RAMP[min(len(RAMP) - 1, 1 + int(v / 256 * (len(RAMP) - 1)))]
        lines.append(row.rstrip())
    (ROOT / f"ascii_{theme}.txt").write_text("\n".join(lines).rstrip("\n") + "\n")
    print(theme, rows, "Zeilen")

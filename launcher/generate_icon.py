"""Generate assets/icon.ico for the Windows launcher."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Install Pillow first: pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

SIZE = 256
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Rounded rectangle background — n8n orange gradient approximation
for i in range(SIZE):
    t = i / SIZE
    r = int(255 * (1 - t * 0.1))
    g = int(109 * (1 - t * 0.2) + 159 * t)
    b = int(90 * (1 - t) + 67 * t)
    draw.line([(0, i), (SIZE, i)], fill=(r, g, b, 255))

# Clip to rounded rect via mask
mask = Image.new("L", (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(mask)
radius = 56
mask_draw.rounded_rectangle((8, 8, SIZE - 8, SIZE - 8), radius=radius, fill=255)
img.putalpha(mask)

# "n8" text
try:
    font = ImageFont.truetype("arialbd.ttf", 110)
except OSError:
    font = ImageFont.load_default()

text = "n8"
bbox = draw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((SIZE - tw) / 2, (SIZE - th) / 2 - 10), text, fill=(255, 255, 255, 255), font=font)

ico_path = ASSETS / "icon.ico"
img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print(f"Icon saved to {ico_path}")

#!/usr/bin/env python3
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SIZE = (640, 480)
BG_TOP = (26, 26, 46)
BG_BOTTOM = (14, 14, 28)
SILVER = (192, 192, 200)
CRATER = (160, 160, 172)
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a1a2e"/>
      <stop offset="1" stop-color="#0e0e1c"/>
    </linearGradient>
  </defs>
  <rect width="640" height="480" fill="url(#bg)"/>
  <circle cx="320" cy="62" r="30" fill="#c0c0c8"/>
  <circle cx="308" cy="54" r="5" fill="#a0a0ac"/>
  <circle cx="332" cy="68" r="7" fill="#a0a0ac"/>
  <circle cx="314" cy="76" r="4" fill="#a0a0ac"/>
  <text x="320" y="130" font-family="DejaVu Sans, Sans" font-weight="bold" font-size="26" letter-spacing="4" text-anchor="middle" fill="#e0e0f0">LUNAR OS</text>
  <rect x="270" y="142" width="100" height="3" rx="1.5" fill="#6c5ce7"/>
</svg>
"""


def gradient():
    image = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(image)
    for y in range(SIZE[1]):
        t = y / (SIZE[1] - 1)
        color = tuple(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (SIZE[0], y)], fill=color)
    return image


def render():
    image = gradient()
    draw = ImageDraw.Draw(image)
    draw.ellipse((290, 32, 350, 92), fill=SILVER)
    for cx, cy, r in ((308, 54, 5), (332, 68, 7), (314, 76, 4)):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CRATER)
    font = None
    for path in FONT_PATHS:
        if os.path.exists(path):
            font = ImageFont.truetype(path, 26)
            break
    if font is None:
        font = ImageFont.load_default()
    text = "LUNAR OS"
    width = draw.textlength(text, font=font)
    draw.text(((SIZE[0] - width) / 2, 108), text, font=font, fill=(224, 224, 240))
    draw.rounded_rectangle((270, 142, 370, 145), radius=1, fill=(108, 92, 231))
    return image


def main():
    image = render()
    syslinux = os.path.join(ROOT, "config", "bootloaders", "syslinux")
    grub = os.path.join(ROOT, "config", "bootloaders", "grub-pc")
    os.makedirs(syslinux, exist_ok=True)
    os.makedirs(grub, exist_ok=True)
    image.save(os.path.join(syslinux, "splash.png"))
    image.save(os.path.join(grub, "splash.png"))
    with open(os.path.join(syslinux, "splash.svg"), "w") as handle:
        handle.write(SVG)


if __name__ == "__main__":
    main()

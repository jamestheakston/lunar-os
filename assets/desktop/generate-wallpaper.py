#!/usr/bin/env python3
import random

from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1920, 1080
TOP = (26, 26, 46)
BOTTOM = (12, 12, 26)
MOON_CENTER = (1480, 330)
MOON_RADIUS = 120


def gradient():
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    return image


def glow(image):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = MOON_CENTER
    radius = MOON_RADIUS * 3
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(108, 92, 231, 55))
    layer = layer.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(image.convert("RGBA"), layer)


def stars(image):
    rng = random.Random(7)
    draw = ImageDraw.Draw(image)
    for _ in range(90):
        x = rng.randrange(WIDTH)
        y = rng.randrange(int(HEIGHT * 0.8))
        shade = rng.randrange(110, 200)
        size = rng.choice((1, 1, 1, 2))
        draw.ellipse((x, y, x + size, y + size), fill=(shade, shade, shade + 30, 255))


def moon(image):
    draw = ImageDraw.Draw(image)
    cx, cy = MOON_CENTER
    r = MOON_RADIUS
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(196, 196, 208, 255))
    for dx, dy, cr in ((-38, -30, 22), (32, 20, 30), (-12, 56, 14), (46, -52, 12)):
        draw.ellipse((cx + dx - cr, cy + dy - cr, cx + dx + cr, cy + dy + cr), fill=(166, 166, 182, 255))


def main():
    image = glow(gradient())
    stars(image)
    moon(image)
    image.convert("RGB").save("wallpaper.png")
    print("Wallpaper saved to wallpaper.png")


if __name__ == "__main__":
    main()

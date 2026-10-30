#!/usr/bin/env python3
from PIL import Image, ImageChops, ImageDraw, ImageFilter

SIZE = 64
SCALE = 8


def ellipse_mask(size, box):
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    return mask


def make_orb():
    big = SIZE * SCALE
    pad = int(big * 0.06)
    box = (pad, pad, big - pad, big - pad)
    orb_mask = ellipse_mask(big, box)

    body = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(body)
    for step in range(60):
        t = step / 59
        color = (int(120 - 70 * t), int(100 - 60 * t), int(240 - 90 * t), 255)
        shrink = int((big * 0.30) * t)
        draw.ellipse((pad + shrink, pad, big - pad, big - pad - shrink // 3), fill=color)
    base = Image.new("RGBA", (big, big), (58, 48, 140, 255))
    base.paste(body, (0, 0), body)

    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    image.paste(base, (0, 0), orb_mask)

    ring = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse(box, outline=(235, 235, 255, 230), width=int(big * 0.03))
    image = Image.alpha_composite(image, ring)

    cx, cy, r = big * 0.5, big * 0.5, big * 0.24
    disc = ellipse_mask(big, (cx - r, cy - r, cx + r, cy + r))
    cutter = ellipse_mask(big, (cx - r * 0.1, cy - r * 1.1, cx + r * 1.7, cy + r * 0.9))
    crescent_mask = ImageChops.subtract(disc, cutter)
    crescent = Image.new("RGBA", (big, big), (240, 240, 250, 255))
    crescent.putalpha(crescent_mask)
    image = Image.alpha_composite(image, crescent)

    gloss = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).ellipse((big * 0.16, big * 0.08, big * 0.84, big * 0.5), fill=(255, 255, 255, 60))
    gloss = gloss.filter(ImageFilter.GaussianBlur(big * 0.015))
    image = Image.alpha_composite(image, gloss)

    return image.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    make_orb().save("start-orb.png")
    print("Start orb saved to start-orb.png")


if __name__ == "__main__":
    main()

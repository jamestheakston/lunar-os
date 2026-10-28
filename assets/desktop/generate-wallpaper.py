#!/usr/bin/env python3
"""
Generate Lunar OS desktop wallpaper
Creates a lunar-themed gradient with abstract moon imagery
"""

from PIL import Image, ImageDraw, ImageFilter
import math

def create_wallpaper(width=1920, height=1080, output_path="wallpaper.png"):
    """
    Create a lunar-themed wallpaper with gradient and moon imagery
    """
    # Create new image
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Define lunar color palette
    # Deep charcoal/midnight blue gradient
    top_color = (26, 26, 46)    # #1a1a2e
    bottom_color = (22, 33, 62) # #16213e
    accent_color = (108, 92, 231)  # #6c5ce7 (violet accent)
    silver_color = (192, 192, 192)  # #c0c0c0

    # Create vertical gradient
    for y in range(height):
        # Interpolate between top and bottom colors
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw moon (off-center)
    moon_x = int(width * 0.7)
    moon_y = int(height * 0.4)
    moon_radius = 120

    # Moon glow (larger, semi-transparent circle)
    glow_radius = moon_radius + 40
    glow = Image.new("RGBA", (width, height))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        [moon_x - glow_radius, moon_y - glow_radius,
         moon_x + glow_radius, moon_y + glow_radius],
        fill=(108, 92, 231, 30)  # Violet with low alpha
    )
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    # Main moon circle
    draw.ellipse(
        [moon_x - moon_radius, moon_y - moon_radius,
         moon_x + moon_radius, moon_y + moon_radius],
        fill=silver_color
    )

    # Moon craters (subtle circles)
    craters = [
        (moon_x - 30, moon_y - 20, 15),
        (moon_x + 40, moon_y + 10, 20),
        (moon_x - 10, moon_y + 50, 12),
        (moon_x + 20, moon_y - 40, 8),
    ]

    for cx, cy, cr in craters:
        crater_color = (160, 160, 160)  # Slightly darker silver
        draw.ellipse(
            [cx - cr, cy - cr, cx + cr, cy + cr],
            fill=crater_color
        )

    # Add subtle stars
    import random
    random.seed(42)  # For reproducibility
    for _ in range(100):
        star_x = random.randint(0, width)
        star_y = random.randint(0, height)
        star_size = random.randint(1, 2)
        star_brightness = random.randint(200, 255)
        draw.ellipse(
            [star_x, star_y, star_x + star_size, star_y + star_size],
            fill=(star_brightness, star_brightness, star_brightness)
        )

    # Apply subtle blur for softness
    img = img.filter(ImageFilter.SMOOTH)

    # Save wallpaper
    img.save(output_path, "PNG")
    print(f"Wallpaper saved to {output_path}")

if __name__ == "__main__":
    create_wallpaper()

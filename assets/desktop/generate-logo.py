#!/usr/bin/env python3
"""
Generate Lunar OS logo
Creates a simple moon logo in multiple sizes
"""

from PIL import Image, ImageDraw

def create_logo(size=256, output_path="logo.png"):
    """
    Create a moon logo
    """
    # Create new image with transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Lunar colors
    silver_color = (192, 192, 192, 255)  # #c0c0c0
    crater_color = (160, 160, 160, 255)

    # Center
    center = size // 2
    radius = int(size * 0.4)

    # Main moon circle
    draw.ellipse(
        [center - radius, center - radius,
         center + radius, center + radius],
        fill=silver_color
    )

    # Moon craters
    craters = [
        (center - int(radius * 0.25), center - int(radius * 0.15), int(radius * 0.12)),
        (center + int(radius * 0.33), center + int(radius * 0.08), int(radius * 0.16)),
        (center - int(radius * 0.08), center + int(radius * 0.42), int(radius * 0.1)),
        (center + int(radius * 0.17), center - int(radius * 0.33), int(radius * 0.07)),
    ]

    for cx, cy, cr in craters:
        draw.ellipse(
            [cx - cr, cy - cr, cx + cr, cy + cr],
            fill=crater_color
        )

    # Save logo
    img.save(output_path, "PNG")
    print(f"Logo saved to {output_path}")

def create_logos():
    """Create logos in multiple sizes"""
    sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in sizes:
        create_logo(size, f"logo-{size}x{size}.png")

if __name__ == "__main__":
    create_logos()

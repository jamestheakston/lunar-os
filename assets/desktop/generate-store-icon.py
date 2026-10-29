#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

def create_store_icon():
    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    bag_color = (108, 92, 231, 255)  # Purple
    bag_dark = (88, 72, 211, 255)  # Darker purple
    moon_color = (240, 240, 245, 255)  # Light gray/white
    
    # Draw shopping bag
    bag_x = 64
    bag_y = 80
    bag_width = 128
    bag_height = 120
    
    # Bag body
    draw.rectangle([bag_x, bag_y, bag_x + bag_width, bag_y + bag_height], 
                   fill=bag_color, outline=bag_dark, width=4)
    
    # Bag top fold
    draw.rectangle([bag_x, bag_y, bag_x + bag_width, bag_y + 20], 
                   fill=bag_dark, outline=bag_dark)
    
    # Bag handle
    handle_x1 = bag_x + 30
    handle_x2 = bag_x + bag_width - 30
    handle_y = bag_y - 30
    handle_width = 8
    
    draw.line([handle_x1, handle_y, handle_x1, bag_y], fill=bag_dark, width=handle_width)
    draw.line([handle_x2, handle_y, handle_x2, bag_y], fill=bag_dark, width=handle_width)
    draw.arc([handle_x1 - 10, handle_y - 20, handle_x2 + 10, bag_y - 10], 
             start=0, end=180, fill=bag_dark, width=handle_width)
    
    # Draw moon icon on the bag
    moon_center_x = bag_x + bag_width // 2
    moon_center_y = bag_y + bag_height // 2 + 10
    moon_radius = 35
    
    # Moon shape (crescent)
    draw.ellipse([moon_center_x - moon_radius, moon_center_y - moon_radius,
                  moon_center_x + moon_radius, moon_center_y + moon_radius],
                 fill=moon_color)
    
    # Shadow on moon to make crescent
    shadow_x = moon_center_x + 15
    shadow_y = moon_center_y - 5
    shadow_radius = 30
    draw.ellipse([shadow_x - shadow_radius, shadow_y - shadow_radius,
                  shadow_x + shadow_radius, shadow_y + shadow_radius],
                 fill=bag_color)
    
    # Save the icon
    img.save("lunar-store-icon.png")
    print("Icon saved as lunar-store-icon.png")
    
    # Also save in different sizes
    for icon_size in [16, 32, 48, 64, 128]:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        resized.save(f"lunar-store-icon-{icon_size}x{icon_size}.png")
        print(f"Icon saved as lunar-store-icon-{icon_size}x{icon_size}.png")

if __name__ == "__main__":
    create_store_icon()

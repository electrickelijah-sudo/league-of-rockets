"""
Generates ultra-high-resolution (2048x2048) PBR Livery Texture for the Blender 1:1 Blueprint Car.
Matches media_1790263831226.png:
- Rich Cobalt Blue Metallic base (#0052F5) with micro metallic fleck
- Dual Alpine White Racing Stripes (#FFFFFF) running straight down the center
- Cyan accent pinstripes (#00F0FF)
- Titanium White hood chamfers (#FFFFFF)
- Carbon fiber cooling louvers (#10141D)
- Side rocker racing streaks
"""

from PIL import Image, ImageDraw, ImageFilter
import random
import os

def create_blueprint_livery(filepath="car_livery_blueprint.png", size=(2048, 2048)):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 82, 245, 255)) # Cobalt Blue base
    draw = ImageDraw.Draw(img)

    # 1. Subtle Metallic Fleck Shimmer
    random.seed(42)
    for _ in range(35000):
        rx = random.randint(0, w - 1)
        ry = random.randint(0, h - 1)
        brightness = random.randint(30, 90)
        draw.point((rx, ry), fill=(0 + brightness // 2, 82 + brightness, min(255, 245 + brightness // 4), 255))

    # 2. Dual Alpine White Racing Stripes (Continuous Center Spine)
    stripe_w = 96
    stripe_gap = 52
    left_stripe_x = w // 2 - stripe_gap // 2 - stripe_w
    right_stripe_x = w // 2 + stripe_gap // 2

    # Draw Dual White Stripes from top (nose) to bottom (tail)
    draw.rectangle([left_stripe_x, 0, left_stripe_x + stripe_w, h], fill=(255, 255, 255, 255))
    draw.rectangle([right_stripe_x, 0, right_stripe_x + stripe_w, h], fill=(255, 255, 255, 255))

    # Cyan Outer Accent Pinstripes
    draw.rectangle([left_stripe_x - 14, 0, left_stripe_x - 4, h], fill=(0, 240, 255, 255))
    draw.rectangle([right_stripe_x + stripe_w + 4, 0, right_stripe_x + stripe_w + 14, h], fill=(0, 240, 255, 255))

    # Center Spine Crease
    draw.line([w // 2, 0, w // 2, h], fill=(0, 50, 180, 180), width=4)

    # 3. Titanium White Hood Chamfer Decals (Upper Third)
    draw.polygon([(640, 180), (760, 150), (780, 360), (660, 390)], fill=(255, 255, 255, 255))
    draw.polygon([(w - 640, 180), (w - 760, 150), (w - 780, 360), (w - 660, 390)], fill=(255, 255, 255, 255))

    # 4. Carbon Fiber Hood Louvers (Flanking Center Stripes)
    for ly in range(450, 720, 36):
        # Left slats
        draw.rectangle([760, ly, 880, ly + 14], fill=(16, 20, 29, 255))
        draw.line([760, ly + 2, 880, ly + 2], fill=(45, 54, 72, 255), width=2)
        # Right slats
        draw.rectangle([w - 880, ly, w - 760, ly + 14], fill=(16, 20, 29, 255))
        draw.line([w - 880, ly + 2, w - 760, ly + 2], fill=(45, 54, 72, 255), width=2)

    # 5. Side Rocker White Racing Swooshes (Middle Third)
    draw.polygon([(180, 950), (440, 1200), (410, 1230), (150, 980)], fill=(255, 255, 255, 255))
    draw.polygon([(w - 180, 950), (w - 440, 1200), (w - 410, 1230), (w - 150, 980)], fill=(255, 255, 255, 255))

    # Cyan Accent on Side Swooshes
    draw.polygon([(140, 990), (400, 1240), (390, 1250), (130, 1000)], fill=(0, 240, 255, 255))
    draw.polygon([(w - 140, 990), (w - 400, 1240), (w - 390, 1250), (w - 130, 1000)], fill=(0, 240, 255, 255))

    # 6. Rear Engine Hatch Heat Shield & Mesh (Lower Third)
    draw.rectangle([700, 1550, w - 700, 1980], fill=(18, 22, 32, 255))
    for ry in range(1560, 1970, 28):
        draw.line([710, ry, w - 710, ry], fill=(40, 48, 64, 255), width=4)

    # Save texture
    abs_path = os.path.abspath(filepath)
    img.save(abs_path, format="PNG")
    print(f"High-res blueprint livery saved: {abs_path}")
    return abs_path

if __name__ == '__main__':
    create_blueprint_livery()

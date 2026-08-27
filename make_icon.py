"""Script to generate app.ico for PyInstaller using Pillow."""
import math
from PIL import Image, ImageDraw

SIZE = 256


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + 2 * radius, y0 + 2 * radius], fill=fill)
    draw.ellipse([x1 - 2 * radius, y0, x1, y0 + 2 * radius], fill=fill)
    draw.ellipse([x0, y1 - 2 * radius, x0 + 2 * radius, y1], fill=fill)
    draw.ellipse([x1 - 2 * radius, y1 - 2 * radius, x1, y1], fill=fill)


def make_icon(size=SIZE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg = (26, 43, 74)       # deep navy
    fg = (224, 244, 255)    # cyan-white
    gold = (245, 200, 66)   # accent gold

    # Rounded square background
    r = size // 8
    draw_rounded_rect(draw, [0, 0, size - 1, size - 1], r, bg)

    # --- Three person icons (org chart) ---
    # Central person (top)
    cx, cy = size // 2, size * 22 // 100
    head_r = size * 9 // 100
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=fg)
    body_w, body_h = size * 16 // 100, size * 12 // 100
    draw.ellipse(
        [cx - body_w, cy + head_r, cx + body_w, cy + head_r + body_h],
        fill=fg,
    )

    # Left person (bottom-left)
    lx, ly = size * 28 // 100, size * 60 // 100
    hr2 = size * 7 // 100
    draw.ellipse([lx - hr2, ly - hr2, lx + hr2, ly + hr2], fill=fg)
    bw2, bh2 = size * 12 // 100, size * 10 // 100
    draw.ellipse([lx - bw2, ly + hr2, lx + bw2, ly + hr2 + bh2], fill=fg)

    # Right person (bottom-right)
    rx, ry = size * 72 // 100, size * 60 // 100
    draw.ellipse([rx - hr2, ry - hr2, rx + hr2, ry + hr2], fill=fg)
    draw.ellipse([rx - bw2, ry + hr2, rx + bw2, ry + hr2 + bh2], fill=fg)

    # --- Connecting lines ---
    line_w = max(3, size // 50)
    mid_y = size * 48 // 100
    # Vertical from center person down to horizontal bar
    draw.line([(cx, cy + head_r + body_h), (cx, mid_y)], fill=gold, width=line_w)
    # Horizontal bar
    draw.line([(lx, mid_y), (rx, mid_y)], fill=gold, width=line_w)
    # Down to left
    draw.line([(lx, mid_y), (lx, ly - hr2)], fill=gold, width=line_w)
    # Down to right
    draw.line([(rx, mid_y), (rx, ry - hr2)], fill=gold, width=line_w)

    return img


if __name__ == "__main__":
    img = make_icon(SIZE)

    # Save as PNG for reference
    img.save("assets/icon.png")
    print("Saved assets/icon.png")

    # Save as multi-resolution ICO
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [make_icon(s) for s in sizes]
    imgs[0].save(
        "assets/app.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=imgs[1:],
    )
    print("Saved assets/app.ico")

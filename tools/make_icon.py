"""Generates the application icon.

Drawn at eight times the size and downsampled so the edges come out smooth.
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets"
BG_OUTER = (28, 30, 38)
BG_INNER = (20, 22, 28)
RING = (77, 163, 255)
TRACE = (233, 90, 156)
TRACE_HI = (255, 141, 194)
SIZES = [256, 128, 64, 48, 32, 16]
SS = 8


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render(size: int) -> Image.Image:
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    rounded(d, (0, 0, s - 1, s - 1), int(s * 0.22), BG_OUTER)
    pad = s * 0.045
    rounded(d, (pad, pad, s - 1 - pad, s - 1 - pad), int(s * 0.19), BG_INNER)

    c = s / 2

    r = s * 0.335
    w = max(1, int(s * 0.075))
    d.ellipse((c - r, c - r, c + r, c + r), outline=RING, width=w)

    k = s * 0.145
    top = c - k * 0.72
    body = (c - k, top, c + k, c + k * 1.02)
    rounded(d, body, int(k * 0.34), TRACE)
    cap = (c - k * 0.66, top + k * 0.16, c + k * 0.66, c + k * 0.22)
    rounded(d, cap, int(k * 0.26), TRACE_HI)

    return img.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(exist_ok=True)
    frames = [render(n) for n in SIZES]
    big = render(512)
    big.save(OUT / "logo.png")
    frames[0].save(OUT / "icon.ico", format="ICO",
                   sizes=[(n, n) for n in SIZES],
                   append_images=frames[1:])
    print(f"written: {OUT / 'icon.ico'} and {OUT / 'logo.png'}")


if __name__ == "__main__":
    main()

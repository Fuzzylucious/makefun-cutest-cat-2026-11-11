#!/usr/bin/env python3
"""make.fun bounty entry: cutest-cat-01.

Draws the cutest cat -- a big-eyed ginger kitten sitting front-on with a
head tilt, pink inner ears and nose, whiskers, blush, a curled tail and a
little ball of yarn -- and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).

Standard library only (zlib + struct build the PNG bytes by hand; no PIL,
no network). The picture is fully deterministic: the same code always
writes the same bytes, so both graded runs are identical.
"""

import binascii
import math
import os
import struct
import zlib
from pathlib import Path

W = 1024
H = 1024

# --- palette ---------------------------------------------------------------
GINGER = (243, 164, 88)
GINGER_DARK = (214, 126, 50)
GINGER_LIGHT = (250, 190, 120)
CREAM = (255, 250, 242)
PINK = (255, 158, 178)
PINK_DARK = (235, 110, 132)
PINK_SOFT = (255, 182, 196)
BROWN = (96, 62, 44)
EYE_DARK = (58, 38, 28)
YARN = (235, 90, 100)
YARN_DARK = (200, 60, 75)

# --- canvas ----------------------------------------------------------------
img = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i], img[i + 1], img[i + 2] = color


def blend_px(x, y, color, alpha):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = int(color[0] * alpha + img[i] * (1 - alpha))
        img[i + 1] = int(color[1] * alpha + img[i + 1] * (1 - alpha))
        img[i + 2] = int(color[2] * alpha + img[i + 2] * (1 - alpha))


def fill_background():
    """Warm vertical gradient, pale peach at the top to soft apricot below."""
    top = (255, 246, 233)
    bottom = (255, 226, 196)
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        row = bytes((r, g, b)) * W
        img[y * W * 3:(y + 1) * W * 3] = row


def fill_ellipse(cx, cy, rx, ry, color, alpha=1.0):
    """Filled ellipse, scanline by scanline."""
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        rem = 1.0 - dy * dy
        if rem <= 0:
            continue
        dx = int(rx * math.sqrt(rem))
        x0 = max(0, cx - dx)
        x1 = min(W - 1, cx + dx)
        if alpha >= 1.0:
            row = bytes(color) * (x1 - x0 + 1)
            i = (y * W + x0) * 3
            img[i:i + len(row)] = row
        else:
            for x in range(x0, x1 + 1):
                blend_px(x, y, color, alpha)


def fill_circle(cx, cy, r, color, alpha=1.0):
    fill_ellipse(cx, cy, r, r, color, alpha)


def _edge(ax, ay, bx, by, px, py):
    return (px - ax) * (by - ay) - (py - ay) * (bx - ax)


def fill_triangle(p1, p2, p3, color):
    """Filled triangle via edge functions."""
    xs = [p1[0], p2[0], p3[0]]
    ys = [p1[1], p2[1], p3[1]]
    x0, x1 = max(0, min(xs)), min(W - 1, max(xs))
    y0, y1 = max(0, min(ys)), min(H - 1, max(ys))
    area = _edge(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
    if area == 0:
        return
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            w0 = _edge(p2[0], p2[1], p3[0], p3[1], x, y)
            w1 = _edge(p3[0], p3[1], p1[0], p1[1], x, y)
            w2 = _edge(p1[0], p1[1], p2[0], p2[1], x, y)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or \
               (w0 <= 0 and w1 <= 0 and w2 <= 0):
                set_px(x, y, color)


def stamp(x, y, r, color):
    fill_circle(int(round(x)), int(round(y)), r, color)


def draw_line(x0, y0, x1, y1, width, color):
    dist = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(dist))
    r = max(1, width // 2)
    for i in range(n + 1):
        t = i / n
        stamp(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, color)


def draw_curve(p0, p1, p2, width, color, steps=48):
    """Quadratic bezier, stamped with circles."""
    r = max(1, width // 2)
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        stamp(x, y, r, color)


def draw_heart(cx, cy, s, color):
    """Small heart: two circles plus a downward triangle."""
    fill_circle(cx - s // 2, cy - s // 4, s // 2, color)
    fill_circle(cx + s // 2, cy - s // 4, s // 2, color)
    fill_triangle((cx - s, cy), (cx + s, cy), (cx, cy + s), color)


# --- the cat ---------------------------------------------------------------
def draw_cat():
    fill_background()

    # soft sun disc behind the cat, so it pops off the background
    fill_circle(512, 430, 360, (255, 222, 178))

    # tiny hearts floating in the corners, for charm
    draw_heart(150, 150, 26, PINK_SOFT)
    draw_heart(878, 168, 20, PINK_SOFT)

    # soft ground shadow
    fill_ellipse(512, 925, 270, 34, (214, 164, 130), alpha=0.45)

    # curled tail, wrapping around the body's right side: one smooth
    # curve out and up, two thin bands, and a cream tip on its end
    draw_curve((680, 840), (860, 850), (860, 700), 58, GINGER)
    draw_line(790, 790, 840, 830, 10, GINGER_DARK)
    draw_line(830, 735, 872, 772, 10, GINGER_DARK)
    fill_circle(860, 700, 30, CREAM)

    # body: darker outline, then ginger, then a cream chest
    fill_ellipse(512, 735, 222, 192, GINGER_DARK)
    fill_ellipse(512, 732, 212, 182, GINGER)
    fill_ellipse(512, 775, 132, 122, CREAM)

    # ears, with a slight head tilt: the right ear sits a little lower
    fill_triangle((312, 306), (384, 108), (482, 272), GINGER_DARK)
    fill_triangle((542, 272), (640, 132), (712, 306), GINGER_DARK)
    fill_triangle((322, 298), (388, 122), (472, 264), GINGER)
    fill_triangle((552, 264), (636, 146), (702, 298), GINGER)
    # pink inner ears
    fill_triangle((356, 256), (394, 162), (446, 246), PINK)
    fill_triangle((578, 246), (630, 170), (668, 256), PINK)

    # head: darker outline, then ginger
    fill_circle(512, 400, 238, GINGER_DARK)
    fill_circle(512, 400, 228, GINGER)

    # forehead stripes
    fill_ellipse(472, 222, 11, 30, GINGER_DARK)
    fill_ellipse(512, 212, 11, 32, GINGER_DARK)
    fill_ellipse(552, 222, 11, 30, GINGER_DARK)

    # cream muzzle
    fill_ellipse(512, 512, 96, 58, CREAM)

    # eyes: big, bright, the right one a touch higher (head tilt)
    for (ex, ey) in ((428, 394), (598, 388)):
        fill_ellipse(ex, ey, 62, 72, BROWN)          # outline
        fill_ellipse(ex, ey, 57, 67, (255, 255, 255))  # white
        fill_ellipse(ex, ey + 4, 36, 46, EYE_DARK)    # iris
        fill_circle(ex - 13, ey - 18, 13, (255, 255, 255))  # sparkle
        fill_circle(ex + 12, ey + 14, 6, (255, 255, 255))   # sparkle 2

    # pink nose: a little upside-down triangle
    fill_triangle((490, 478), (534, 478), (512, 504), PINK_DARK)
    fill_circle(512, 482, 10, PINK_DARK)

    # mouth: a small "w" under the nose
    draw_curve((512, 506), (498, 528), (482, 516), 5, BROWN)
    draw_curve((512, 506), (526, 528), (542, 516), 5, BROWN)

    # blush on both cheeks
    fill_ellipse(362, 480, 40, 22, PINK, alpha=0.55)
    fill_ellipse(662, 474, 40, 22, PINK, alpha=0.55)

    # whiskers: three a side, gently curved
    draw_curve((352, 468), (290, 448), (212, 436), 4, BROWN)
    draw_curve((350, 494), (282, 496), (210, 500), 4, BROWN)
    draw_curve((354, 520), (292, 540), (224, 560), 4, BROWN)
    draw_curve((672, 464), (734, 444), (812, 432), 4, BROWN)
    draw_curve((674, 490), (742, 492), (814, 496), 4, BROWN)
    draw_curve((670, 516), (732, 536), (800, 556), 4, BROWN)

    # front paws, with toe lines
    fill_ellipse(438, 878, 64, 42, GINGER_DARK)
    fill_ellipse(588, 878, 64, 42, GINGER_DARK)
    fill_ellipse(438, 874, 58, 36, GINGER_LIGHT)
    fill_ellipse(588, 874, 58, 36, GINGER_LIGHT)
    for px in (438, 588):
        draw_line(px - 16, 862, px - 16, 892, 3, BROWN)
        draw_line(px + 16, 862, px + 16, 892, 3, BROWN)

    # favourite toy: a ball of yarn by the right paw, string curling to it
    draw_curve((640, 892), (700, 920), (760, 900), 4, YARN_DARK)
    fill_circle(812, 884, 48, YARN_DARK)
    fill_circle(812, 884, 44, YARN)
    draw_curve((772, 852), (812, 884), (852, 916), 5, YARN_DARK)
    draw_curve((772, 916), (812, 884), (852, 852), 5, YARN_DARK)
    draw_curve((768, 884), (812, 884), (856, 884), 5, YARN_DARK)


# --- PNG writer ------------------------------------------------------------
def _chunk(kind, data):
    crc = binascii.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def encode_png():
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: None
        raw += img[y * W * 3:(y + 1) * W * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", idat)
            + _chunk(b"IEND", b""))


def main():
    draw_cat()
    data = encode_png()
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Draw the project's original 256x256 icon (no game art)."""
import math
import struct
import sys
import zlib

S = 256


def in_round_rect(x, y, x0, y0, x1, y1, r):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def main(path):
    px = [[(0, 0, 0, 0) for _ in range(S)] for _ in range(S)]
    # Deep blue rounded panel.
    for y in range(S):
        for x in range(S):
            if in_round_rect(x, y, 8, 8, 247, 247, 42):
                px[y][x] = (8, 16, 38, 255)
    # Two offset wind arcs, drawn as original geometry.
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - 128, y - 128)
            if 80 <= d <= 88:
                px[y][x] = (226, 177, 58, 255)
            if 52 <= d <= 57 and x > 118:
                px[y][x] = (72, 156, 214, 255)
    # Wind streaks.
    for y, x0, x1, colour in ((78, 52, 126, (226, 236, 255, 255)),
                              (98, 38, 118, (226, 236, 255, 255)),
                              (178, 138, 218, (226, 236, 255, 255)),
                              (198, 146, 226, (226, 236, 255, 255))):
        for x in range(x0, x1):
            if 0 <= x < S:
                px[y][x] = colour
                px[y + 1][x] = colour
    # Original forward-swept craft mark.
    for y in range(96, 168):
        for x in range(96, 190):
            t = (y - 96) / 72.0
            half = 10 + 38 * (1 - abs(t - 0.55) * 1.6)
            if half > 0 and abs(x - 140) <= half:
                px[y][x] = (238, 244, 255, 255)
    for y in range(112, 136):
        for x in range(126, 154):
            if (x - 140) ** 2 / 196 + (y - 124) ** 2 / 49 <= 1:
                px[y][x] = (226, 177, 58, 255)
    # Stars (original decoration).
    for sx, sy, r in ((44, 54, 3), (208, 62, 2), (62, 206, 2), (204, 206, 3), (36, 140, 2)):
        for y in range(sy - r, sy + r + 1):
            for x in range(sx - r, sx + r + 1):
                if 0 <= x < S and 0 <= y < S and (x - sx) ** 2 + (y - sy) ** 2 <= r * r:
                    px[y][x] = (220, 235, 255, 255)

    raw = bytearray()
    for y in range(S):
        raw.append(0)
        for x in range(S):
            raw.extend(px[y][x])

    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", S, S, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "blast-wind.png")

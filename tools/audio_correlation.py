#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Compare a headerless 16-bit stereo output dump with the CD-DA source dump.

  tools/audio_correlation.py OUTPUT.raw SOURCE.raw [OUT_START] [SRC_START] [SECONDS]

Both files are 16-bit little-endian stereo at 44.1 kHz, as written by
SATRECOMP_AUDIO_DUMP and SATRECOMP_CD_SOURCE_DUMP. The output contains the SCSP mix
as well as CD audio, so the correlation is expected to be well below 1.0; a near-zero
result means the CD source is not reaching the output. Use the music log's
"PlaySectors ... sample N" to choose OUT_START (the CD source starts at SRC_START).
"""
import math
import struct
import sys

RATE = 44100


def read_stereo(path, start, count):
    with open(path, "rb") as f:
        f.seek(start * 4)
        raw = f.read(count * 4)
    n = len(raw) // 4
    left = [0] * n
    right = [0] * n
    for i in range(n):
        l, r = struct.unpack_from("<hh", raw, i * 4)
        left[i] = l
        right[i] = r
    return left, right


def corr(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    ma = sum(a[:n]) / n
    mb = sum(b[:n]) / n
    sa = sb = sab = 0.0
    for i in range(n):
        da = a[i] - ma
        db = b[i] - mb
        sa += da * da
        sb += db * db
        sab += da * db
    if sa == 0 or sb == 0:
        return 0.0
    return sab / math.sqrt(sa * sb)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out_path, src_path = sys.argv[1], sys.argv[2]
    out_start = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0
    src_start = float(sys.argv[4]) if len(sys.argv) > 4 else out_start
    seconds = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
    count = int(seconds * RATE)
    ol, orr = read_stereo(out_path, int(out_start * RATE), count)
    sl, sr = read_stereo(src_path, int(src_start * RATE), count)
    # The source starts when the music player first delivers a sample; search a
    # small lag window rather than assuming the two files begin on the same sample.
    best = (-2.0, 0)
    for lag in range(-2048, 2049, 16):
        if lag >= 0:
            c = corr(ol[lag:], sl)
        else:
            c = corr(ol, sl[-lag:])
        if c > best[0]:
            best = (c, lag)
    c, lag = best
    peak = max(max(abs(v) for v in ol), max(abs(v) for v in orr))
    src_peak = max(max(abs(v) for v in sl), max(abs(v) for v in sr))
    print("output %s: %d samples, peak %d" % (out_path, len(ol), peak))
    print("source %s: %d samples, peak %d" % (src_path, len(sl), src_peak))
    print("correlation %.4f at lag %d samples" % (c, lag))
    return 0 if abs(c) > 0.1 else 1


if __name__ == "__main__":
    sys.exit(main())

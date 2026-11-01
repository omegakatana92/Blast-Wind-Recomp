#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check a CUE/BIN disc image before building or running the port.

  tools/check_disc.py IMAGE.cue [--hashes]

It reads the CUE in place (never changing or extracting it), resolves every FILE
entry relative to the CUE's folder, checks each file and track, reads the Saturn
header from the first data sector, and prints the track map. Exit status is nonzero
for a missing file, an unsupported track format, or a header that is not the game
named in games/<id>/game.cfg (when run from the project root).
"""
import hashlib
import os
import re
import struct
import sys

# The toolkit's port/disc_image.cpp reads 2048-byte user data or raw 2352-byte
# sectors; 2324/2336-byte modes are not modelled and are reported, not guessed.
SUPPORTED = {
    "AUDIO": (2352, 0),
    "MODE1/2048": (2048, 0),
    "MODE1/2352": (2352, 16),
    "MODE2/2048": (2048, 0),
    "MODE2/2352": (2352, 24),
}

def parse_cue(path):
    """Return [(file_name, [track dicts])] and the CUE's folder."""
    folder = os.path.dirname(os.path.abspath(path))
    entries = []
    current_file = None
    current_track = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.upper().startswith("FILE "):
                m = re.match(r'FILE\s+"(.*)"\s+\w+', stripped, re.IGNORECASE)
                if m:
                    name = m.group(1)
                else:
                    parts = stripped.split()
                    if len(parts) < 2:
                        raise ValueError("bad FILE line: " + stripped)
                    name = parts[1]
                current_file = {"name": name, "tracks": []}
                entries.append(current_file)
                current_track = None
            elif stripped.upper().startswith("TRACK "):
                parts = stripped.split()
                if len(parts) < 3 or current_file is None:
                    raise ValueError("TRACK without FILE: " + stripped)
                current_track = {"number": int(parts[1]), "kind": parts[2].upper(),
                                 "indexes": {}}
                current_file["tracks"].append(current_track)
            elif stripped.upper().startswith("INDEX "):
                parts = stripped.split()
                if len(parts) < 3 or current_track is None:
                    raise ValueError("INDEX without TRACK: " + stripped)
                m, s, fr = (int(x) for x in parts[2].split(":"))
                current_track["indexes"][int(parts[1])] = (m * 60 + s) * 75 + fr
    return entries, folder


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    cue = args[0]
    show_hashes = "--hashes" in sys.argv
    entries, folder = parse_cue(cue)
    if not entries:
        print("error: no FILE entries in the CUE")
        return 1

    errors = []
    warnings = []
    fad = 150
    tracks = []
    for entry in entries:
        file_path = os.path.join(folder, entry["name"])
        if not os.path.isfile(file_path):
            errors.append("missing FILE: %s" % entry["name"])
            continue
        size = os.path.getsize(file_path)
        if not entry["tracks"]:
            errors.append("FILE has no TRACK: %s" % entry["name"])
            continue
        first_kind = entry["tracks"][0]["kind"]
        if first_kind not in SUPPORTED:
            errors.append("FILE %s starts with unsupported track type %s"
                          % (entry["name"], first_kind))
            continue
        if show_hashes:
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            print("sha256 %s  %s" % (h.hexdigest(), entry["name"]))
        for track in entry["tracks"]:
            kind = track["kind"]
            if kind not in SUPPORTED:
                errors.append("unsupported track type %s (track %d); supported: %s"
                              % (kind, track["number"], ", ".join(sorted(SUPPORTED))))
                continue
            sector_size, user_offset = SUPPORTED[kind]
            frames = size // sector_size
            if frames == 0:
                errors.append("%s has no complete %d-byte sector"
                              % (entry["name"], sector_size))
                continue
            if size % sector_size:
                warnings.append("%s is not a whole number of %d-byte sectors"
                                % (entry["name"], sector_size))
            idx = track["indexes"].get(1)
            if idx is None:
                errors.append("track %d has no INDEX 01" % track["number"])
                continue
            if idx >= frames:
                errors.append("track %d has INDEX 01 %d beyond its %d frames"
                              % (track["number"], idx, frames))
                continue
            start = fad + idx
            end = fad + frames - 1
            tracks.append({"number": track["number"], "kind": kind, "start": start,
                           "end": end, "pregap": idx, "file": entry["name"]})
        fad += size // SUPPORTED[first_kind][0]

    # The first data track's first sector carries IP.BIN.
    header = None
    data_tracks = [t for t in tracks if t["kind"].startswith("MODE")]
    if data_tracks:
        t = data_tracks[0]
        sector_size, user_offset = SUPPORTED[t["kind"]]
        with open(os.path.join(folder, t["file"]), "rb") as f:
            raw = f.read(sector_size)
        header = raw[user_offset:user_offset + 256]

    print("cue        %s" % cue)
    print("files      %d/%d present" % (sum(1 for e in entries if os.path.isfile(os.path.join(folder, e["name"]))), len(entries)))
    print("tracks     %d" % len(tracks))
    for t in tracks:
        dur = (t["end"] - t["start"] + 1) / 75.0
        print("  track %2d  %-10s  FAD %6d..%6d  %7.2fs  %s"
              % (t["number"], t["kind"], t["start"], t["end"], dur, t["file"]))
    if header:
        # Saturn IP.BIN: product 10 bytes, version 6, date 8, disc number 8, area 8
        product = header[0x20:0x2A].decode("ascii", "replace").strip()
        version = header[0x2A:0x30].decode("ascii", "replace").strip()
        date = header[0x30:0x38].decode("ascii", "replace").strip()
        region = header[0x40:0x48].decode("ascii", "replace").strip()
        name = header[0x60:0x70].decode("ascii", "replace").strip()
        print("header     %s  %s  %s  area %s  name '%s'" % (product, version, date, region, name))

        cfg = os.path.join("games", "blastwind", "game.cfg")
        if os.path.isfile(cfg):
            values = {}
            with open(cfg, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        values[k.strip()] = v.strip()
            if values.get("disc_product") and product != values["disc_product"]:
                errors.append("disc product %r is not %r from game.cfg" % (product, values["disc_product"]))
            if values.get("disc_version") and version != values["disc_version"]:
                errors.append("disc version %r is not %r from game.cfg" % (version, values["disc_version"]))

    for w in warnings:
        print("warning: " + w)
    for e in errors:
        print("error: " + e)
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

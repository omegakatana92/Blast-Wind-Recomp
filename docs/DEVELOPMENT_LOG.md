# Development log

## 2026-11-01 — inspection, first boot, gameplay

### Inspection

- Installed toolkit: `C:\Users\omega\Documents\satrecomp-0.2.0\satrecomp-0.2.0`.
  It has no `.git` directory and no `example/`; it is the 0.2.0 source snapshot.
- Read `README.md`, `docs/NEXT_GAME.md`, `MACHINE.md`, `VIDEO.md`, `SOUND.md`,
  `VERIFYING.md`, `FEATURES.md`, `build.mk`, `CMakeLists.txt`, `tools/check.sh`,
  `tools/gamecfg.py`, `tools/sync-toolkit.sh`, `port/disc_image.cpp`,
  `machine/cd.cpp`, `runtime/music.cpp`, and the launcher sources.
- A sibling development checkout exists at `C:\Users\omega\Documents\satrecomp`
  (clean 0.2.0 snapshot plus four commits, `b0e19d1`..`7460350`, adding the CD
  buffer commands and the Hyper Duel CD-DA fixes). It has one uncommitted
  `video/renderer.cpp` colour-calculation diagnostic, which is not copied.
- The fork `satrecomp-omega-edtion` is newer upstream satrecomp (Fighters Megamix,
  Display page, recomp-common 0.5) plus its own diagnostics and a different CD-DA
  implementation (`b635271`, SCU A-Bus interrupt `4a216e2`). Its `machine/cd.cpp`,
  `runtime/music.cpp`, `machine/machine.cpp` and `port/main.cpp` differ substantially
  from the 0.2.0 API this project uses.

**Decision:** build on the local `satrecomp` checkout (`7460350`). It contains the
CD-DA path already validated on the sibling Hyper Duel port, which is the fix this
task asked to locate and reuse. The fork's newer features were not adopted: they
would require a merge across the port/machine API, and none is needed by Blast Wind
(the game works without the SCU A-Bus interrupt and without the fork's boot-file
override). This is recorded rather than silently mixing toolkits.

### Disc

- CUE: 20 `FILE` entries, all present; track 1 `MODE1/2352`, tracks 2-20 `AUDIO`
  with a 2-second pregap (`INDEX 00` at file start, `INDEX 01` at `00:02:00`).
- Header: `T-1810G`, `V1.003`, `19961210`, area `J`, name `BLAST WIND`.
- SHA-256 of every file recorded in `work/blastwind/disc-sha256.txt` (not committed;
  the image is the user's).
- `tools/check_disc.py` validates all of the above, handles quoted names, spaces,
  brackets and multiple BIN files, and rejects unsupported track types.

### Project

- Created `games/blastwind/` with `game.cfg`, a minimal `src/game.cpp` and
  `movies/`, a root `Makefile`, `local.mk` (git-ignored) and the usual notices.
- `satrecomp/` was made by `sync-toolkit.sh --first` from the local toolkit at
  commit `7460350`; `make check-toolkit` passes.

### Boot

- First interpreter-only run: Technosoft logo (frame 300), opening movie
  (750-4500), title (5750), attract demo, stage 1 title (7100).
- The game reads its files through its own `0KERNEL.BIN` loader with CD buffer
  commands `0x50`-`0x53`, `0x60`-`0x63`; no missing command was reported.
- Recorded 13,075 blocks over 8,000 frames, translated them, and rebuilt. The
  translated build runs 7,200 frames in 65 s (about 111 fps headless).

### Menus and sound test

- Holding Down and pressing Start at the title opens `GAME START` / `OPTION`.
- OPTION contains DIP SWITCH, KEY ASSIGN, SOUND TEST, INFORMATION, RANKING and
  EXIT/DEFAULT.
- SOUND TEST lists BGM 00-18 and SE 00-62. Selecting BGM 01 ("ULTIMATE
  DESTROYER") issues `PLAY` for track 3 (`0x000300`) and the toolkit plays FAD
  8376..20936. This proves the later CD-DA tracks work, not just the opening.
- KEY ASSIGN confirms A = switch shot, B = homing shot, C = bomb for both players.
- RANKING displays the table read through the game's library.

### Audio

- The opening movie issues `PLAY` with `track:index` `0x000200` (track 2). The
  toolkit resolves it to FAD 2330..8226 and plays raw 2352-byte sectors at 588
  stereo samples/sector. 3,513,310 CD samples are delivered; the SCSP routes them
  (send 6, pan 31/15) and the WAV dump is non-silent.
- Stage/attract music is SCSP, not CD-DA: a spectrogram shows harmonic, rhythmic
  content while the CD player is stopped, and the chip reports six keyed voices.
- The title screen was silent in the tested run. It is left as a validation question
  rather than "fixed" without evidence.

### Saves

- The game writes a 32 KiB internal backup file containing a `BLASTWIND_0` record.
  The file is opened by the port, written at exit and survives a restart. The
  in-game ranking screen has not yet been opened.

### Final build and checks

- Merged the recordings from the 8,000-frame boot, the 30,000-frame auto run, the
  option/sound-test run and the 12,000/18,000-frame stage runs: 16,515 blocks,
  1,650 multi-block functions, 250,933 instructions, 42 generated files (about
  77 MB of C++).
- `make check FRAMES=300`: interpreter == translated; two runs identical.
- `make check FRAMES=6000 MOVIE=games/blastwind/movies/start.txt`: interpreter ==
  translated; two runs identical.
- `make check FRAMES=6000 MOVIE=work/blastwind/auto.txt`: interpreter ==
  translated; two runs identical.
- 12,000-frame title -> stage path: 100.00% recompiled, 0 interpreted.
- 6,000 frames in 74.2 s headless software video (80.9 fps, 1.35x real time).
- Saves: a 30,000-frame auto run changed 36 bytes of the `BLASTWIND_0` record; the
  ranking screen reads the file back. The default page displayed the same five
  names, so the specific saved page is left to manual validation.

### Packaging

- Windows: `dist/Blast-Wind-Windows-x64/` and `.zip`. Run from a path with spaces
  and a different working directory: 600 frames, 100% recompiled. Launcher
  screenshot shows "Blast Wind (Japan), verified."; a Radiant Silvergun CUE is
  rejected as "a different game (RADIANT S.G.), not Blast Wind."
- Linux: built in WSL2 Ubuntu 22.04 with GCC 11.4 and static SDL 3.4.16. GCC at
  `-j4` was OOM-killed by the 7.6 GB WSL limit on `blocks_031.cpp`; `-j2` completed.
  The AppImage is `dist/Blast-Wind-v0.1.0-SteamDeck-x86_64.AppImage`.
- The extracted AppImage's port gives the same 600-frame state hashes as the
  Windows and native Linux builds. The bundled launcher opens under Xvfb and shows
  the disc as verified.

## Pending

- User validation of title music, controller hardware, the exact saved ranking
  page, windowed audio/frame pacing, and Steam Deck hardware.

# Blast Wind — native recompilation

A native Windows/Linux port of **Blast Wind (Japan)** for the Sega Saturn, built with
[satrecomp](https://github.com/tmcleroy/satrecomp) 0.2.0. The Saturn's two SH-2 programs are
translated to C++ ahead of time and run on satrecomp's own machine; no emulator and no BIOS image
is part of the port. The player supplies their own disc image.

This project is not affiliated with or endorsed by Sega or Technosoft. No game data, disc image,
BIOS, save, generated translated code or recording is distributed here.

## Disc

The port expects an unmodified **Blast Wind (Japan)** Saturn disc:

| Header field | Value |
| --- | --- |
| Product number | `T-1810G` |
| Version | `V1.003` |
| Release date | `19961210` |
| Area | `J` |
| Data track | track 1, MODE1/2352 |
| Audio tracks | 2-20, AUDIO (CD-DA) |

The supplied image is a 20-file CUE/BIN set. Every `FILE` entry in the CUE must exist; the
toolkit reads the files in place and never copies or rewrites them.

The launcher checks these values from the first sector of the data track. A different release may
boot but is not the validated target.

## Build (Windows 11 x64)

Toolchain used and tested by this project (matching satrecomp's Windows CI):

- MSYS2, `MINGW64` environment
- `mingw-w64-x86_64-gcc`, `mingw-w64-x86_64-cmake`, `mingw-w64-x86_64-ninja`,
  `mingw-w64-x86_64-python`, `mingw-w64-x86_64-sdl3`, `mingw-w64-x86_64-zlib`, `make`

From an MSYS2 MINGW64 shell at the project root:

```sh
make            # translated code (if any) + port
make launcher   # launcher beside the port
```

Build output:

- `build/blastwind/blastwind.exe` — the port
- `build/blastwind/blastwind-launcher.exe` — the launcher

Portable Windows package:

```sh
tools/package_windows.sh
# dist/Blast-Wind-Windows-x64/
```

## Linux x86_64 / Steam Deck

The AppImage is built on Ubuntu 22.04 (glibc 2.35) with GCC 11 and a static SDL 3.4.x, which is
older than current SteamOS. On a Linux x86_64 host with the project's development packages, a
static SDL3 install, and `appimagetool`:

```sh
export CMAKE_PREFIX_PATH=/path/to/sdl3-static
APPIMAGETOOL=/path/to/appimagetool tools/package_appimage.sh
# dist/Blast-Wind-v0.1.0-SteamDeck-x86_64.AppImage
```

The AppImage carries the runtime, launcher, its original icon, licenses and the C++ runtime; it
does not carry glibc, graphics drivers, X11/Wayland/audio system libraries, or any game data.
SteamOS's system libraries and Mesa drivers are used. `make app` is the toolkit's macOS bundle
target, not an AppImage target.

For Desktop Mode, make the AppImage executable and run it, or add it to Steam. For Gaming Mode,
add it as a non-Steam game in Desktop Mode, then launch it from the Deck; the launcher opens full
screen when it detects gamescope/Steam Game Mode. Controller bindings use SDL3 gamepads. Actual
Steam Deck hardware validation is still pending.

The first build is interpreter-only. Translated code is generated later from a block recording;
the current recorded paths are fully translated.

## Run

The launcher stores the chosen disc, saves and settings under the game's home folder
(`BLASTWIND_HOME`, otherwise the platform's normal application-data folder). Choose the `.cue`
file once, then Play.

For a direct run (from the project root, with a developer-local `local.mk` defining `DISC`):

```sh
make run
```

or explicitly:

```sh
build/blastwind/blastwind.exe \
  --disc "C:/path/to/Blast Wind (Japan).cue" \
  --backup work/blastwind/backup.bin \
  --settings work/blastwind/settings.ini
```

Headless deterministic run:

```sh
build/blastwind/blastwind.exe --disc "C:/path/to/game.cue" --headless --frames 600 \
  --backup work/blastwind/backup.bin --hash-log work/blastwind/boot.hashes
```

## Saves, settings and logs

- Saves: `saves/backup.bin` in the launcher's game folder (or the `--backup` path).
- Settings: `settings.ini` in the launcher's game folder (or the `--settings` path).
- Per-run logs and generated files: `work/blastwind/` (git-ignored).
- Build output: `build/blastwind/` (git-ignored).

## Controls and modes

Keyboard: arrows move; Return is Start; Z/X/C are A/B/C; A/S/D are X/Y/Z; Q/E are L/R.
A gamepad's lower face buttons are A/B/C, and Start is Start. Change them on the
launcher's Controllers page.

At the title screen, press Start. The game goes to the stage 1 title and then into play. Start
also pauses during play.

## Audio

The opening movie's sound is CD-DA track 2. Stage, boss and attract music is sequenced on the
SCSP; sound effects are also SCSP. The CD-DA path reads raw 2352-byte audio sectors at 588 stereo
samples per sector on the 44.1 kHz clock, separately from the CD data FIFO. See
`docs/AUDIO.md` for the diagnosis and the checks performed.

## Legal

GPL-3.0-only (`LICENSE`). See `THIRD_PARTY_NOTICES.md` and `LICENSES/`. This repository and its
packages contain no game image, no extracted game assets, no BIOS, no saves, no recordings and no
generated translated C++.

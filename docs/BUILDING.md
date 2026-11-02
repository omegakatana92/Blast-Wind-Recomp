# Building

## Windows 11 x64

Use an **MSYS2 MINGW64** shell. The package set is the one satrecomp's Windows CI
uses:

```sh
pacman -S --needed make git \
  mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja \
  mingw-w64-x86_64-python mingw-w64-x86_64-sdl3 mingw-w64-x86_64-zlib
```

From the project root:

```sh
make -j$(nproc)          # translated code (if any) + build/blastwind/blastwind.exe
make -j$(nproc) launcher # build/blastwind/blastwind-launcher.exe
```

`make` uses the toolkit copy in `satrecomp/`, which must be the copy made by
`satrecomp/tools/sync-toolkit.sh` (`make check-toolkit` verifies it). To develop the
toolkit itself, build against the separate checkout:

```sh
make SR=../satrecomp -j$(nproc)
```

That writes to `build/blastwind-dev/` instead of `build/blastwind/`.

## Disc path

The disc is never part of the repository. Put the absolute path in the git-ignored
`local.mk`:

```make
DISC := C:/path/to/Blast Wind (Japan)/Blast Wind (Japan).cue
```

`make run`, `make record` and `make check` then use it.

## Linux x86_64

The same CMake targets build on Linux. The package list satrecomp's CI installs:

```sh
sudo apt-get install -y --no-install-recommends \
  build-essential cmake ninja-build pkg-config zlib1g-dev \
  libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxi-dev libxss-dev \
  libxtst-dev libxkbcommon-dev libwayland-dev wayland-protocols libdecor-0-dev \
  libegl-dev libgl-dev libvulkan-dev libpulse-dev libasound2-dev libudev-dev \
  libdbus-1-dev libpipewire-0.3-dev
```

Install SDL 3 (system package or the toolkit's pinned 3.4.x source build), then:

```sh
make -j"$(nproc)"
make -j"$(nproc)" launcher
```

`make app` is the **macOS app bundle** target in satrecomp 0.2.0; it does not create
a Linux AppImage. `tools/package_appimage.sh` builds the AppImage with `appimagetool`.

The generated files are large; on a 7.6 GB WSL2 VM, `-j4` was OOM-killed while
compiling `blocks_031.cpp`. `-j2` completes. If `make check` cannot execute
`satrecomp/tools/check.sh` because the toolkit copy's execute bit is not set on a
fresh non-Windows checkout, run it through the shell:

```sh
GAME=blastwind B=build/blastwind DISC="$DISC" sh satrecomp/tools/check.sh 300
GAME=blastwind B=build/blastwind DISC="$DISC" sh satrecomp/tools/check.sh 6000 games/blastwind/movies/start.txt
```

## Generated code

`work/blastwind/blocks.txt` is the block database (git-ignored and never shipped).
`work/blastwind/gen/blocks_*.cpp` is generated from it. It is large (about 65 MB of C++
for the recorded paths) and takes roughly 20 minutes to compile with GCC 16 at `-O3`.
The generated code is game-derived and must not be committed or distributed.

## Packaging

```sh
tools/package_windows.sh
```

produces `dist/Blast-Wind-Windows-x64/` with the port, launcher, the MinGW/SDL/zlib
runtime DLLs, license texts and first-run instructions. It copies no disc image, BIOS,
save or build output.

```sh
APPIMAGETOOL=/path/to/appimagetool tools/package_appimage.sh
```

produces `dist/Blast-Wind-v0.1.0-SteamDeck-x86_64.AppImage`.

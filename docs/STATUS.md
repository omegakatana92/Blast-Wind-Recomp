# Blast Wind recompilation — status

Updated: 2026-11-01 (local build)

## What works

- **Boot:** the native BIOS path (`runtime/hle_bios.cpp`) starts the disc, the game's
  own CD loader (`0KERNEL.BIN`) reads the ISO 9660 data track, and `GAME.BIN` runs.
- **Opening:** the Technosoft logo, the full opening movie (with CD-DA track 2), the
  title screen and the attract demonstration have been reached and captured.
- **Gameplay:** title -> stage 1 ("IRON SKYSCRAPER"), scrolling, sprites, bullets,
  explosions, the stage 1 boss, pause and game over have been reached.
- **Audio:** the opening movie uses CD-DA track 2; stage/attract music and all sound
  effects use the SCSP. Both are non-silent in the audio dump. See `AUDIO.md`.
- **Menus:** title -> hold Down + Start opens GAME START / OPTION; the OPTION page
  reaches DIP SWITCH, KEY ASSIGN, SOUND TEST, INFORMATION, RANKING and EXIT/DEFAULT.
- **Sound test:** BGM 00-18 and SE 00-62; BGM 01 plays CD-DA track 3 (FAD
  8376..20936).
- **Controls:** Start, A/B/C, directions and pause were exercised through input
  movies. KEY ASSIGN shows A/B/C for switch shot, homing shot and bomb.
- **Saves:** the internal backup file is opened, written and kept across runs; it
  contains the game's `BLASTWIND_0` record. The RANKING screen displays the table.
- **Translation:** 16,515 blocks (1,650 multi-block functions, 250,933 instructions).
  The 12,000-frame title -> stage 1 path is 100.00% recompiled, 0 interpreted.

## Checks actually run

| Check | Command | Result |
| --- | --- | --- |
| Disc files | `tools/check_disc.py <cue>` | 20/20 FILE entries present |
| Disc header | same | `T-1810G`, `V1.003`, `19961210`, area `J` |
| Track layout | same | track 1 MODE1/2352; tracks 2-20 AUDIO; pregaps 00:02:00 |
| Image hashes | `Get-FileHash` on all 20 bins and the cue | recorded in `work/blastwind/disc-sha256.txt` |
| Baseline build | `make SR=../satrecomp` | succeeds (Windows x64, MSYS2 MINGW64, GCC 16.2) |
| Boot screenshots | `--headless --shot-every` | logo 300, opening 750-4500, title 5750-6600, stage 6100+ |
| CD-DA | `SATRECOMP_CD_LOG=1`, `SATRECOMP_MUSIC_LOG=1` | track 2 FAD 2330..8226; 3,513,310 samples delivered |
| SCSP | `SATRECOMP_SOUND_LOG=1`, audio dump | six keyed voices; harmonic stage/attract music |
| Translation coverage | `--stats` at 12,000 frames | 100.00% recompiled, 0 interpreted |
| Boot equivalence | `make check FRAMES=300` | interpreter == translated; two runs identical |
| Title/stage equivalence | `make check FRAMES=6000 MOVIE=games/blastwind/movies/start.txt` | interpreter == translated; two runs identical |
| Gameplay equivalence | `make check FRAMES=6000 MOVIE=work/blastwind/auto.txt` | interpreter == translated; two runs identical |
| Speed | 6,000 frames headless, software video | 74.2 s (80.9 fps, 1.35x real time) |
| Windows package run | path with spaces, CWD `C:\Windows\Temp` | 600 frames, 100% recompiled |
| Cross-platform hashes | Windows and Linux 600-frame hash logs | identical |
| AppImage | extracted, bundled port 600 frames | hashes identical to the native build |
| CD-DA output correlation | output vs CD source, first 5 s of the opening | 0.774 at 256-sample lag |
| Backup | auto run, then ranking | 32 KiB file with `BLASTWIND_0`; the record changes after play and is read again |

## Not yet validated

- Full playthrough of all six stages, bosses, endings and loops.
- Title-screen music: the tested run had no CD-DA command and no keyed SCSP voices
  between the opening and the attract demo. Whether the retail title is silent is
  not established; this needs a comparison on hardware or in a known-good emulator.
- The in-game options/ranking screens and the exact save/load behaviour (the backup
  file is written; the ranking UI has not been opened).
- A windowed session with the real SDL audio device, frame pacing and audio underruns.
- Actual gamepad hardware and the launcher's Controllers page.
- Actual Steam Deck hardware: Gaming Mode/gamescope, Deck controller, Deck audio.
- Reference verification against Ymir: the unpublished reference patch is not
  available locally, so no `make verify` was claimed or performed.

## Known limitations

- The software renderer reports VDP2 colour-calculation lines drawn without the
  requested effect (about 300 lines per frame in the tested areas). Sprites,
  backgrounds, priorities and colour offset are drawn; inter-layer transparency is
  approximate. See `satrecomp/docs/VIDEO.md`.
- The CD-DA path models one buffer partition and the commands the Technosoft loader
  uses; multiple partitions and filters are not modelled.
- Generated code is large and takes roughly 20 minutes to compile on this machine.

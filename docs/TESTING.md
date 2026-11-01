# Testing

## Automated checks actually run

From the project root in MSYS2 MINGW64:

```sh
export DISC="C:/path/to/Blast Wind (Japan)/Blast Wind (Japan).cue"

tools/check_disc.py "$DISC"

make SR=../satrecomp
make SR=../satrecomp check FRAMES=300
make SR=../satrecomp check FRAMES=6000 MOVIE=work/blastwind/auto.txt
make SR=../satrecomp check-rewrites
```

`check` runs four headless processes: the SH-2 interpreter against the translated
code, and the game twice, comparing a state hash after every frame. It needs both the
disc path and the movie path.

The recording and translation workflow:

```sh
# Explore with deterministic random input and record both the input and the blocks.
build/blastwind-dev/blastwind.exe --disc "$DISC" --headless --frames 12000 \
  --backup work/blastwind/backup.bin --auto 1234:6000 \
  --record work/blastwind/auto.txt --record-blocks work/blastwind/blocks.txt --stats

# Translate the recorded blocks and rebuild.
make SR=../satrecomp
```

## Manual checks that need the user

These cannot be completed by the headless harness.

1. **Start the launcher.** Run `dist/Blast-Wind-Windows-x64/Play Blast Wind.bat`
   (or the AppImage). Choose the `.cue`. The launcher must show
   `Blast Wind (Japan), verified.` and enable Play. A different game's CUE must be
   rejected.
2. **Title and attract.** Watch the logo, the opening movie (CD-DA audio), the title
   and the attract demo. Confirm whether the title screen has background music on
   real hardware or a known-good emulator. This is the one open audio question.
3. **Play stage 1.** Press Start at the title. Confirm the stage title, scrolling,
   sprites, bullets, explosions, stage music (SCSP) and sound effects. Press Start to
   pause and resume.
4. **Controls.** With a Saturn-style pad or an Xbox/PlayStation pad, confirm the
   launcher's Controllers page mapping for A/B/C, X/Y/Z, L/R, Start and the D-pad.
   Confirm the keyboard defaults: arrows, Return, Z/X/C, A/S/D, Q/E.
5. **Saves.** Finish a run so the game writes its record, quit, start again, and open
   the ranking screen (or whatever screen the game offers) to confirm the record is
   loaded. The file is `%APPDATA%\Blast Wind\backup.bin` (or `BLASTWIND_HOME`).
6. **Long session.** Play through several stages, a boss and a game over; check for
   missing graphics, hangs, audio underruns and timing drift.
7. **Steam Deck (only with the device).** Add the AppImage as a non-Steam game in
   Desktop Mode, launch it in Gaming Mode, confirm the launcher, controller, audio and
   save location. Do not call the AppImage "Steam Deck verified" without this.

## What to report if something fails

Record the exact build, the frame number, the screen, the last 50 lines of the log,
and whether the failure is visual, audio, input, save or a hang. The useful
diagnostics are listed in `AUDIO.md`; add `--stats` for CD command counts and
coverage.

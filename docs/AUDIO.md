# Audio: what Blast Wind uses, and what was checked

Blast Wind uses **two separate audio paths**:

| Source | Used for | Path |
| --- | --- | --- |
| CD-DA (red book) | the opening movie, track 2 | CD block PLAY -> the toolkit's music player -> raw 2352-byte sectors -> SCSP CD input |
| SCSP | stage, boss and attract music, and all sound effects | the sound 68000 driver in `sound/m68k.cpp` -> `sound/chip.cpp` |

This matters because the earlier Hyper Duel investigation found a silent-CD-DA bug. The fix for
that bug is in this project's toolkit copy and was rechecked here, but Blast Wind's **stage music
does not use CD-DA at all**, so a stage-music silence would not be a CD-DA bug.

## How the image is read

`port/disc_image.cpp` parses the CUE line by line. Each `FILE` is opened relative to the CUE's
own folder; quoted names with spaces and brackets are kept whole. For this image:

- 20 `FILE` entries, all 20 `.bin` files present;
- track 1 `MODE1/2352`, `INDEX 01 00:00:00`;
- tracks 2-20 `AUDIO`, each with `INDEX 00` at the file start and `INDEX 01` at `00:02:00`;
- the 2-second pregap is therefore inside each track's file and is excluded from the track's
  playable range (`endFAD` is the track's last sector, not the next file's start).

The computed ranges match the CUE:

| Track | Start FAD | End FAD | Length |
| --- | --- | --- | --- |
| 1 (data) | 150 | 2179 | 27.07 s |
| 2 (opening) | 2330 | 8225 | 78.61 s |
| 3 | 8376 | 20935 | 167.47 s |
| ... | ... | ... | ... |
| 20 | 243184 | 243672 | 6.52 s |

## CD-DA evidence

With `SATRECOMP_CD_LOG=1` and `SATRECOMP_MUSIC_LOG=1` a run reaches:

```
cd cmd 10 1000 0200 0000 0200
cd 10 play start=000200 end=000200 mode=00 -> FAD 2330..8226 (CDDA)
music: PlaySectors FAD 2330..8226 (exclusive), repeats=0
```

The command is `track:index` form (`0x000200` = track 2, index 0), not a frame address. The
toolkit routes it to the music player, which requests 2352-byte raw sectors and consumes exactly
588 stereo samples per sector. After 78.6 s the track ends and the drive is paused (`music:
Pause`), which is the movie player stopping. No further CD-DA play is requested.

The game's own **SOUND TEST** (title -> hold Down + Start -> OPTION -> SOUND TEST)
lists BGM 00-18 and SE 00-62. Selecting BGM 01 ("ULTIMATE DESTROYER") and pressing A
produces a second CD-DA request:

```
cd 10 play start=000300 end=000300 mode=00 -> FAD 8376..20936 (CDDA)
music: PlaySectors FAD 8376..20936 (exclusive), repeats=0
```

so the toolchain also handles the later CD tracks, not just the opening. The BGM
timer in the sound-test screen advances while the track plays.

`SATRECOMP_SOUND_LOG=1` during the opening reports:

```
cd music 3513310 ... s16 key 1 act 0 send 6 pan 31 ... s17 key 0 act 0 send 6 pan 15 ...
mixed 7018510 cd_input 7018510 cd_send 7018510 last_send 6
```

so the CD samples reach the chip's CD input and the game's SCSP program routes them (send level 6)
to the output. The WAV dump is non-silent across the opening.

A direct check with `SATRECOMP_AUDIO_DUMP` and `SATRECOMP_CD_SOURCE_DUMP` over the first five
seconds of the opening gives **correlation 0.774** at a 256-sample lag between the output mix and
the CD source (peak output 14423, source 28846; the difference is the game's SCSP gain). A
near-zero correlation would mean the CD samples were not reaching the output.

## SCSP evidence

Stage/attract music has strong harmonic and rhythmic structure in a spectrogram while the CD
music player reports `state 0` (stopped). The same periods report six active/keyed SCSP voices and
a master volume of 15, and the audio dump is continuous. That is the sequenced soundtrack, not
CD-DA.

The title screen itself produced no audio in the tested run (no CD-DA command and no keyed
voices). That is recorded as an open question for gameplay validation, not as a confirmed
regression: the game may be silent at the title by design, and the attract/stage music that
follows is present.

## What was changed

No audio code was changed for Blast Wind. The toolkit copy already contains the Hyper Duel CD-DA
fixes:

- `b0e19d1` CD buffer commands for a game's own file system;
- `391b26d` route `track:index` play requests to the port's music player;
- `a0f490d` play raw audio sectors on the 44.1 kHz clock;
- `7460350` stop track ranges at the track's last sector, not the next pregap.

They apply unchanged because Blast Wind uses the same Technosoft CD loader and the same
track:index play form. They are kept in the shared toolkit, not in this game's sources.

## Diagnostics used

| Variable | What it shows |
| --- | --- |
| `SATRECOMP_CD_LOG=1` | every CD command, its parameters, track ranges, caller PC |
| `SATRECOMP_MUSIC_LOG=1` | play/pause/resume/stop, sector ranges, delivered/silent samples |
| `SATRECOMP_SOUND_LOG=1` | CD input, SCSP routing/gain, active voices, output |
| `SATRECOMP_AUDIO_DUMP=path` | every output sample, 16-bit stereo 44.1 kHz (headerless) |
| `SATRECOMP_CD_SOURCE_DUMP=path` | the CD-DA source samples as consumed |
| `SATRECOMP_CD_DIRECT=1` | diagnostic only: add CD input straight to the output |

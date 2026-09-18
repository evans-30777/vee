#!/usr/bin/env python3
"""Build the home hero videos from the sources in `pinterest/`.

The sources are reference clips the owner supplied. They are other people's
footage, so this script does two jobs: it re-frames each clip for the hero, and
it removes everything in them that belongs to another brand. Both matter — the
second one is not optional polish. Re-run it after replacing a source:

    python3 tools/build_hero_video.py

Outputs land in `static/video/` as an MP4 and a WebM at two sizes each, plus a
poster per size. Nothing here runs at request time; the outputs are committed.

`main.js` asks for the MP4 first and only falls back to the WebM when the
browser cannot decode H.264. VP9 was measured against x264 on all three clips
at matched quality and came out 20-90% *larger* every time — these are short,
near-black, low-colour clips, which is where x264 is still strong — so every
mainstream browser should and does take the smaller file. The WebM is there for
the browsers that ship without H.264 (Chromium builds without proprietary
codecs, some Linux distributions), which no visitor pays for and which is also
the only way this pipeline can be checked in a real browser from CI.

Per-clip edits, and why each one is there
-----------------------------------------
vortex  (`vid hero.mp4`) — an abstract particle vortex. Carries no text and no
    branding, so it passes through untouched apart from re-framing.

words   (`vid hero digital growth.mp4`) — a rotating wheel of single words. The
    only foreign mark is the "RANK YOU UP" logo in the top-right corner: three
    ascending bars and an up arrow, ending at y=113. Both crops start below it,
    so it is framed out rather than painted over. Painting was tried first and
    was wrong: the blurred words sweep through that corner, so a filled box
    left a black notch visible during playback.

clock   (`vid hero 2.mp4`) — an analog clock hand sweeping past service icons.
    Two edits:

    1. Cut at 22.0s. The clip runs 24.87s and hands over to a
       "GET IN TOUCH / MarketingBeast360" card at 22.6s. 22.0s leaves 0.6s of
       margin and still lands after every icon has appeared.
    2. Black out the nine text elements. The headline reads "Full-Spectrum
       Digital Marketing" and the eight labels name that agency's service list
       — four of them (Brand Strategy, Social Media Management, Influencer
       Marketing, Content Creation) are services VEE does not offer, and a hero
       that names them is a claim VEE cannot support. The icons stay: a laptop
       or a magnifier claims nothing. Every box was measured against the
       clock hand's sweep (max reach 192px from the hub at 360,640) so that
       masking the text never clips the hand.

    The clip is then played at 2x. At its native length one hero slide would
    hold the stage for 22 seconds and most visitors would never reach the
    other two.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "pinterest"
OUT = ROOT / "static" / "video"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Text to erase from `vid hero 2.mp4`, as x:y:w:h in source pixels.
# Measured from the rendered frames; see the module docstring for why.
CLOCK_TEXT_BOXES = [
    (150, 155, 425, 60),   # "Full-Spectrum Digital Marketing"
    (250, 345, 215, 57),   # Website Design
    (0, 476, 250, 50),     # Performance Marketing
    (530, 480, 125, 55),   # SEO
    (0, 679, 190, 45),     # Content Creation
    (519, 680, 201, 48),   # Brand Strategy
    (0, 893, 305, 107),    # Influencer Marketing
    (410, 890, 305, 110),  # Analytics & Reporting
    (190, 992, 340, 80),   # Social Media Management
]

def boxes(specs, colour="black"):
    return ",".join(
        f"drawbox=x={x}:y={y}:w={w}:h={h}:color={colour}:t=fill" for x, y, w, h in specs
    )


# Two renditions. `tall` is what phones get — a 2:3 frame that fills a portrait
# hero without the browser having to throw most of it away. `wide` is 16:9 for
# tablets up. Both are modest: the video sits behind a scrim with the headline
# over it, so sharpness matters far less than how fast it arrives.
TALL = "540:810"
WIDE = "1152:648"
FPS = 24

CLIPS = {
    "vortex": {
        "src": "vid hero.mp4",
        "input_args": [],
        "prefix": "",
        # A full-frame field of moving high-contrast dots is the worst case for
        # any codec, so this one takes the loosest quality. It is abstract —
        # compression artifacts in a dot field are invisible.
        "crf": "34",
        # The hole drifts over y 312-575; this band keeps it in frame throughout.
        "wide": f"crop=720:405:0:238,scale={WIDE}",
        "tall": f"scale=810:810,crop=540:810:135:0",
    },
    "words": {
        "src": "vid hero digital growth.mp4",
        "input_args": [],
        "prefix": "",
        # Large type: this is the one clip where softness would show.
        "crf": "28",
        # A 16:9 crop of a 9:16 source can take at most a 405px band, and that
        # blew the words up until they fought the headline for the page. So the
        # landscape rendition keeps the word column at a readable size and lets
        # the rest be black — but the words run to the source's own edges, so a
        # plain black bar would slice them mid-stroke. The luma ramp fades the
        # column's outer 80px towards black instead, and since the background
        # already is black the words simply dissolve out of frame.
        #
        # A blurred copy of the footage was tried in the bars first. The two
        # scales did not line up, so the words looked broken rather than
        # continued, and the join between sharp and blurred read as a seam.
        #
        # The column sits at 82% across rather than centred: the hero's copy
        # owns the left half, and a word column behind the lead paragraph made
        # both harder to read.
        "wide": (
            "crop=720:780:0:250,scale=-2:648,"
            "geq=lum='p(X\\,Y)*clip(min(X\\,W-X)/80\\,0\\,1)'"
            ":cb='p(X\\,Y)':cr='p(X\\,Y)',"
            "pad=1152:648:(ow-iw)*0.82:0:black"
        ),
        # The word in focus sits at y=640. Both crops start below the corner
        # logo at y=113 and still keep that word in the upper-middle of frame.
        #
        # The same edge fade, narrower. The longest words run past the source's
        # own edges, which on a phone is fine — they read as words scrolling by
        # — but on a tablet, where this cut is scaled up by half again, a word
        # as recognisable as "Content" sliced flat at the frame edge reads as a
        # broken video rather than a deliberate crop.
        "tall": (
            f"crop=720:1080:0:150,scale={TALL},"
            "geq=lum='p(X\\,Y)*clip(min(X\\,W-X)/90\\,0\\,1)'"
            ":cb='p(X\\,Y)':cr='p(X\\,Y)'"
        ),
    },
    "clock": {
        "src": "vid hero 2.mp4",
        "input_args": ["-t", "22"],
        "prefix": boxes(CLOCK_TEXT_BOXES) + ",setpts=0.5*PTS",
        "crf": "27",
        # The dial spans y 285-1030. Crop to it, then pad out in black — the
        # background is pure #000000, so the padding is invisible. Off-centre
        # for the same reason as the words clip: the copy owns the left half.
        "wide": f"crop=720:940:0:190,scale=-2:648,pad=1152:648:(ow-iw)*0.78:0:black",
        "tall": f"crop=720:940:0:190,scale=540:-2,pad=540:810:0:(oh-ih)/2:black",
    },
}


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed: {' '.join(args[:6])} ...")


def chain(clip, size):
    parts = [p for p in (clip["prefix"], clip[size], f"fps={FPS}") if p]
    return ",".join(parts)


def build(name, clip):
    source = SRC / clip["src"]
    if not source.exists():
        raise SystemExit(f"missing source: {source}")

    for size in ("wide", "tall"):
        common = [FFMPEG, "-y", "-v", "error", *clip["input_args"], "-i", str(source),
                  "-vf", chain(clip, size), "-an"]

        run(common + [
            "-c:v", "libx264", "-preset", "slower", "-crf", clip["crf"],
            "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-g", "48", "-movflags", "+faststart",
            str(OUT / f"hero-{name}-{size}.mp4"),
        ])
        # Roughly matched to the H.264 quality above; VP9's scale sits higher.
        run(common + [
            "-c:v", "libvpx-vp9", "-crf", str(int(clip["crf"]) + 10), "-b:v", "0",
            "-row-mt", "1", "-pix_fmt", "yuv420p", "-deadline", "good",
            str(OUT / f"hero-{name}-{size}.webm"),
        ])

    # A poster per size, not one for both. The two renditions are framed
    # differently, so a single poster meant a phone showed the landscape crop
    # until the video painted over it — and showed it permanently on any
    # browser that could not play the clip at all.
    #
    # The moment is chosen per clip: it has to be a frame where the composition
    # has already formed, not the black first frame of a fade-in.
    poster_at = {"vortex": "2.0", "words": "3.0", "clock": "9.0"}[name]
    for size in ("wide", "tall"):
        run([FFMPEG, "-y", "-v", "error", *clip["input_args"], "-ss", poster_at,
             "-i", str(source), "-vf", chain(clip, size), "-frames:v", "1",
             "-q:v", "6", str(OUT / f"hero-{name}-poster-{size}.jpg")])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, clip in CLIPS.items():
        print(f"building {name} from {clip['src']} ...")
        build(name, clip)

    print("\n  file                          size")
    total = 0
    for path in sorted(OUT.glob("hero-*")):
        kb = path.stat().st_size / 1024
        total += kb
        print(f"  {path.name:30s} {kb:7.1f} KB")
    print(f"  {'total':30s} {total:7.1f} KB")


if __name__ == "__main__":
    main()

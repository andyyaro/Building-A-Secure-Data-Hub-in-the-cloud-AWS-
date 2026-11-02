"""Cut "RnB" (Arulo, Mixkit 224, Mixkit free licence: assets/audio/SOURCE.md) to the Secure Data Hub film.

    python3 -I sound/music.py     # -> assets/audio/music.wav, sound/grid.json

Andy, 2026-11-01: "use calm tracks from now on, calm but not too calm".
RnB is relaxed, serious contemporary R&B at exactly 100 BPM with a half-time feel (kick on 1, snare on 3).
A bar is 2.4 s, and track bar n starts at 0.45 + 2.4 n s.
- Bars 0-4 are the quiet intro. The groove enters on bar 5 (12.45 s) and runs to bar 15.
- Then a breakdown (16-17) and a softer middle (18-31).
- The fullest section is bars 32-37 (77.25 s), then the outro (38-42, from 91.65 s) and the fade.

The edit (joins on bar lines, 12 ms crossfades):
  film  0.00-12.45  track  0.00-12.45  the intro under the hook
  film 12.45-38.85  track 12.45-38.85  the groove enters on the drop (the title)
  film 38.85-53.25  track 77.25-91.65  breakdown and middle skipped: the fullest section under decisions 3-4 and the tests
  film 53.25-62.50  track 91.65-...    the outro under the end card, faded at the end
"""
import json, subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TRACK = ROOT / "sound/track.mp3"
SR, B0, BAR = 48000, 0.45, 2.4
tb = lambda n: B0 + n * BAR
SEGMENTS = [(0.0, 0.0), (tb(5), tb(5)), (tb(16), tb(32)), (tb(22), tb(38))]   # (film start, track start)
DROP, JUMP, END_CARD = tb(5), tb(16), tb(22)
FILM_END = 62.5
XF = 0.012


def main():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(TRACK), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    track = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
    n = int(FILM_END * SR)
    out = np.zeros((2, n))
    x = int(XF * SR); ramp = np.linspace(0, 1, x)
    for k, (f0s, t0s) in enumerate(SEGMENTS):
        f0 = int(round(f0s * SR)); f1 = int(round(SEGMENTS[k + 1][0] * SR)) if k + 1 < len(SEGMENTS) else n
        t0 = int(round(t0s * SR))
        seg = track[:, t0: t0 + (f1 - f0)]
        seg = np.pad(seg, ((0, 0), (0, (f1 - f0) - seg.shape[1])))
        if k > 0:
            out[:, f0 - x: f0] = out[:, f0 - x: f0] * (1 - ramp) + track[:, t0 - x: t0] * ramp
        out[:, f0:f1] = seg
    fi = int(0.3 * SR); out[:, :fi] *= np.linspace(0, 1, fi)
    fo = int(2.5 * SR); out[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    import soundfile as sf
    (ROOT / "assets/audio").mkdir(parents=True, exist_ok=True)
    sf.write(ROOT / "assets/audio/music.wav", out.T.astype(np.float32), SR)
    grid = {"track": "RnB (Arulo, Mixkit 224)", "bpm": 100, "bar": BAR, "drop": round(DROP, 3), "jump": round(JUMP, 3),
            "end_card": round(END_CARD, 3), "track_ending": round(END_CARD, 3), "duration": FILM_END, "segments": SEGMENTS}
    (ROOT / "sound/grid.json").write_text(json.dumps(grid, indent=1))
    print(f"music.wav {FILM_END} s; drop {DROP:.2f}, jump {JUMP:.2f}, end card {END_CARD:.2f}")


if __name__ == "__main__":
    main()

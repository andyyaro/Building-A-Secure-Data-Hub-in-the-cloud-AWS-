"""Write the film's English captions from the narration: renders/secure-data-hub-v1.en.vtt.

    python3 -I narration/vtt.py [out.vtt]

The film has no subtitles in the picture, so this file is the only captions it has; the watch page plays it as a
track. The text is the script as written (narration/lines.json); each cue's time comes from the voice's own word
times (assets/vo.js, made by sound/mix.py), so a re-voiced or re-slotted line re-times its captions here.
A cue is at most two rows of 42 characters; a line too long for that is cut at a comma into two cues.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINES = json.loads((ROOT / "narration/lines.json").read_text())
s = (ROOT / "assets/vo.js").read_text()
VO = json.loads(s[s.index("{"): s.rindex("}") + 1])

# (line, cue text). Each cue must be the next words of its line; together a line's cues must be the whole line.
CUES = [
    ("v01", "One stolen credential."),
    ("v02", "In most apps,\nthat opens every client's record."),
    ("v03", "Here, breaking into the app\ndoesn't expose the data."),
    ("v04", "This is Secure Data Hub."),
    ("v05", "A multi-account AWS architecture\nfor sensitive client data."),
    ("v06", "The app account holds no data access."),
    ("v07", "To read one record, it assumes a role\nin a separate data account,"),
    ("v07", "with temporary credentials."),
    ("v08", "The tenant ID never comes from the caller."),
    ("v09", "The gateway takes it\nfrom a verified token,"),
    ("v09", "before any code runs."),
    ("v10", "Each record is encrypted\nwith a customer-managed key,"),
    ("v10", "used only as the data account."),
    ("v11", "And the admin's broad permission\nnever touches the sensitive table."),
    ("v12", "Fifty-one tests pin\nthese boundaries in place."),
    ("v13", "Secure Data Hub."),
]
LEAD, TAIL, GAP = 0.08, 0.30, 0.04


def norm(text):
    text = text.lower().replace("fifty-one", "51")      # the voice's words were transcribed as "51"
    return "".join(c for c in text if c.isalnum())


def ts(t):
    h, r = divmod(t, 3600); m, r = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{r:06.3f}"


cues, pos = [], {}
for key, text in CUES:
    for row in text.split("\n"):
        assert len(row) <= 42, f"{key}: caption row over 42 characters: {row!r}"
    words, i = VO[key]["words"], pos.get(key, 0)
    want, got, j = norm(text), "", i
    while len(got) < len(want) and j < len(words):
        got += norm(words[j]["w"]); j += 1
    assert got == want, f"{key}: caption {text!r} does not match the voiced words from word {i}"
    pos[key] = j
    cues.append([words[i]["t0"] - LEAD, words[j - 1]["t1"] + TAIL, text])
for key, text in LINES.items():
    joined = " ".join(t.replace("\n", " ") for k, t in CUES if k == key)
    assert joined == text, f"{key}: the cues do not add up to the line: {joined!r}"
for a, b in zip(cues, cues[1:]):
    a[1] = min(a[1], b[0] - GAP)

out = ["WEBVTT", ""]
for n, (t0, t1, text) in enumerate(cues, 1):
    out += [str(n), f"{ts(t0)} --> {ts(t1)}", text, ""]
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "renders/secure-data-hub-v1.en.vtt"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("\n".join(out))
print(f"{path.name}: {len(cues)} cues from {len(LINES)} lines")

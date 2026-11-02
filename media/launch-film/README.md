# Secure Data Hub launch film

The 63-second film at the top of the [repository README](../../README.md), published at
https://andyyaro.github.io/Building-A-Secure-Data-Hub-in-the-cloud-AWS-/film.html. It is for a
cloud or security engineer: in one minute, why breaking into this app does not expose the data.
It shows the project's four design decisions, each on its real AWS parts (separate accounts, the
tenant ID taken from the verified token, a customer-managed key used only as the data account,
and an admin Scan that never reaches the sensitive table), then the 51 tests that pin them. The
parts are drawn, not recorded, and every name and figure on screen comes from this repository.

[STORYBOARD.md](STORYBOARD.md) has the scenes, the look, the sound and every build step.
[FACTS.md](FACTS.md) has every claim in the film and where it comes from, and
[SPEC.md](SPEC.md) is the brief the film was built to.

## What is here

| Path | What it is |
|---|---|
| `index.html`, `compositions/` | The composition (HyperFrames 0.8.173, GSAP): the ground, the travelling light and the scene hosts in `index.html`, and one file per scene |
| `build.py` | Writes the scene windows from `sound/timing.json` into `index.html` |
| `assets/vo.js`, `assets/timing.js` | What the scenes read: every narrated word's film time (`window.VO`) and the scene windows (`window.TM`), as the film was rendered |
| `narration/` | The script (`lines.json`), the script as voiced (`lines-tts.json`), `pick.py`, which chooses the best take of each line and times its words (`words.json`), and `vtt.py`, which writes the captions file |
| `sound/` | The music edit (`music.py`, `grid.json`) and the mix (`mix.py`, `timing.json`): narration, music and 69 effects, each placed on its picture |
| `FACTS.md` | Every line of narration and every on-screen claim, with its source in this repository |
| `SPEC.md` | The brief: goal, sound, look, motion, shots and what is banned |
| `package.json` | The HyperFrames commands at the pinned version |
| `tools/fetch_vendor.sh` | Fetches GSAP at the pinned version and checks the file's SHA-256 |
| `deploy/film.html`, `deploy/index.html`, `deploy/logo.svg` | The watch page, a redirect to it from the site's root, and the page's logo (the mark and the wordmark side by side, from [docs/assets/brand/](../../docs/assets/brand/)) |
| `assets/audio/SOURCE.md` | Every third-party sound and font in the film, with its licence and where it goes |

## What is not here, and why

The working folder for the film is about 47 MB. This folder keeps the source and leaves out
everything that is generated or that its licence does not let us hand on by itself:

- **Generated:** the narration takes and the chosen takes, the music edit, the voice and the mix
  (`assets/audio/`), HyperFrames' snapshots and check files (`.hyperframes/`) and the renders, the
  captions file included. The build steps make them again.
- **Screen recordings:** there are none. The film draws every part in HTML and SVG.
- **Third-party media:** the music ("RnB" by Arulo, Mixkit) and seven Mixkit sound effects.
  [assets/audio/SOURCE.md](assets/audio/SOURCE.md) lists each one with its licence and the path
  it goes to.
- **Libraries and fonts:** GSAP 3.14.2 is fetched by `tools/fetch_vendor.sh`. The Geist, Chakra
  Petch and Montserrat fonts (SIL OFL 1.1) go in `assets/fonts/`. `node_modules/` is made by
  HyperFrames.
- **Logo files:** the film draws the mark in its own SVG, so it needs none; the logo files are in
  [docs/assets/brand/](../../docs/assets/brand/).

## Publishing

The MP4, its captions and its poster are assets of the
[`film-v1` release](https://github.com/andyyaro/Building-A-Secure-Data-Hub-in-the-cloud-AWS-/releases/tag/film-v1),
so the 9.0 MB film is not in the repository's history. The
[film page workflow](../../.github/workflows/film.yml) puts them on GitHub Pages with
`deploy/film.html`, `deploy/index.html`, `deploy/logo.svg` and the favicon. It runs when anything
in `deploy/` changes on `main`. After replacing a release asset, run it by hand:

```sh
gh release upload film-v1 secure-data-hub-launch.mp4 --clobber
gh workflow run film.yml
```

The film has no subtitles in the picture. Its captions are the WebVTT file, written from the
narration's word times by `narration/vtt.py`; the watch page plays them as a track, on by default.

## Credits

Narration: Kokoro-82M (Apache-2.0), voice af_heart. Music: "RnB" by Arulo (Mixkit). Sound
effects: Mixkit. Type: Geist, Chakra Petch and Montserrat (SIL OFL 1.1); the wordmark is Chakra
Petch Bold, outlined in the logo files. Look: after the Outbreak Detective intro and the EV-SIENT
film, in Secure Data Hub's own colours.

# Third-party sounds and type in the film

These are in the film but not in this repository. Their licences cover using them inside a film,
not handing the files on by themselves, so they are listed here instead. Download each one again
to the path shown to rebuild.

## Music

| Used as | Track | Licence | Put it at |
|---|---|---|---|
| The bed under the whole film, cut on its bar lines by `sound/music.py` | "RnB" by Arulo, [Mixkit 224](https://assets.mixkit.co/music/224/224.mp3) | [Mixkit Stock Music Free License](https://mixkit.co/license/): free in any project, no credit required, not for use in a music-only track | `sound/track.mp3` |

## Sound effects

All from Mixkit, under the [Mixkit Sound Effects Free License](https://mixkit.co/license/).
The names are the ones `sound/mix.py` uses (`SFX`); each file goes in `sound/sfx-src/` as
`mixkit-<id>.mp3`.

| Name in `mix.py` | Mixkit id | What it marks |
|---|---|---|
| `pop` | 2357 | A part arriving; pitched down (0.8), always a denial |
| `tick` | 1120 | A step or a row: the records turning red, the six boundaries, the end card's squares |
| `whoosh_air` | 1492 | Something that travels: the stolen credential, the role being assumed, the token's claim, the admin's Scan |
| `whoosh_wind` | 1465 | The records gliding to the centre before the title; the move to the admin frame |
| `sweep` | 3115 | A new frame: "Here", decision 1, the turn to the Lambda's own role |
| `pop_hard` | 3005 | The app turning red, the credential breaking in, the title drop, the one record lighting green, the 51, the end card's key |
| `riser` | 2408 | The swell into the title drop |

`mix.py` also names `typing` (Mixkit 2538), but no cue in the film uses it, so it is not needed.

## Voice

Kokoro-82M ([Apache-2.0](https://huggingface.co/hexgrad/Kokoro-82M)), voice af_heart, run
locally. The lines are `narration/lines-tts.json`; the audio is generated, so it is not kept.

## Type

All under the [SIL Open Font License 1.1](https://openfontlicense.org/), as `.woff2` files in
`assets/fonts/` with the names `index.html` and the scenes load:

| Family | Weights | Files |
|---|---|---|
| [Geist](https://fonts.google.com/specimen/Geist) | Regular, Medium, SemiBold, Bold | `Geist-Regular.woff2`, `Geist-Medium.woff2`, `Geist-SemiBold.woff2`, `Geist-Bold.woff2` |
| [Chakra Petch](https://fonts.google.com/specimen/Chakra+Petch) | SemiBold, Bold | `ChakraPetch-600.woff2`, `ChakraPetch-700.woff2` |
| [Montserrat](https://fonts.google.com/specimen/Montserrat) | SemiBold | `Montserrat-SemiBold.woff2` |

Chakra Petch Bold is the Secure Data Hub wordmark's face; the film uses it only for the wordmark
and the big 51.

## Pictures

There are none from outside: every shape in the film, the mark included, is drawn in the
composition's own HTML and SVG.

# Secure Data Hub launch film: storyboard and build

62.5 s (1,875 frames), 1920 × 1080, 30 fps. H.264 with AAC at 256 kb/s; measured on the MP4:
-16.1 LUFS integrated, true peak -1.4 dBTP, loudness range 8.2 LU. Every claim in it and its
source is in [FACTS.md](FACTS.md); the brief it was built to is [SPEC.md](SPEC.md).

## What is real and what is drawn

- **Real:** every name, path, value and number on screen. The two Lambda functions, the four IAM
  policies and their grants, the API Gateway mapping template and its 400, the test event's
  `client_id` (25xwe2) and path, the Scan's three fields and its limit of 20, and the test suite:
  51 passed and 1 xfailed with `pytest -q` at `c197b22`.
- **Drawn:** the accounts, functions, tables, keys and paths. There is no screen recording; the
  film is a diagram that moves, timed on the narration's own words.
- **Stand-ins:** the nine client records are the logo's nine squares. The caller's `9ab3f1` stands
  for any ID a caller might send. The decrypted item (Ada Lovelace) puts the tests' sample name on
  the test event's ID. The "9 of 9 exposed" count is the single-account case, shown to be avoided.
- **Left out:** the nine-account organisation in the architecture deck. It is a design, not code
  in this repository.

## The film

| Time (s) | Scene | Narration | What you see |
|---|---|---|---|
| 0–6.0 | Open: one account | "One stolen credential. In most apps, that opens every client's record." | "In most apps · one account holds it all". One AWS account holds the client app and nine records. A red key slides in on "stolen"; on "opens" the app turns red and a red line reaches the records; on "every" they turn red column by column and "9 of 9 client records exposed" counts up. |
| 6.0–10.7 | Open: two accounts | "Here, breaking into the app doesn't expose the data." | "Here · the data lives in its own account". The box splits into the app account and the data account, and the records go back to outline. The credential breaks into the app, which turns red; red dashes stop at the gap between the accounts, a red cross, "0 of 9 client records exposed". |
| 10.7–19.65 | Title | "This is Secure Data Hub. A multi-account AWS architecture for sensitive client data." | Everything clears but the records, which glide to the centre. On the music's drop (12.45 s) the centre record becomes the green keyhole: the mark. SECURE DATA HUB, the tagline, then "API Gateway · Cognito · Lambda · STS · DynamoDB · KMS · Terraform". |
| 19.65–29.25 | Decision 1 · Separate accounts | "The app account holds no data access. To read one record, it assumes a role in a separate data account, with temporary credentials." | The Client Lambda in the app account, ClientsBase in the data account. A direct read runs as red dashes and is refused at the boundary: "No direct read". The one record it wants lights; a green dot goes down and across as "sts:AssumeRole · on one role ARN" to the data role; "Temporary credentials: AccessKeyId, SecretAccessKey, SessionToken · no long-lived keys"; then up to the table with "GetItem, DescribeTable · on one table", and the one record turns green. |
| 29.25–38.85 | Decision 2 · The tenant comes from the token | "The tenant ID never comes from the caller. The gateway takes it from a verified token, before any code runs." | The caller's request (`GET /client/profile`, a bearer token, `client_id: 9ab3f1`): its own `client_id` is struck out, "ignored". The verified Cognito token: `sub`, `email`, `custom:client_id` 25xwe2. The claim travels into API Gateway (Cognito authorizer), "client_id ← claims['custom:client_id']"; only then does the Client Lambda get the request, "event client_id: 25xwe2". Then the claim goes missing: "400 · Missing Client Id." at the gateway, and the Lambda is "never invoked". |
| 38.85–44.9 | Decision 3 · A customer-managed key | "Each record is encrypted with a customer-managed key, used only as the data account." | One ClientsBase item: `id` 25xwe2, its `firstName`, `lastName` and `signature` locked. The KMS key ("customer managed, by alias"). The assumed data role reaches the key and the item decrypts (Ada, Lovelace, verified), "Decrypted in the Lambda, as the data role". The Lambda's own role, "the SDK's silent default", is refused. |
| 44.9–49.1 | Decision 4 · Least privilege for admins | "And the admin's broad permission never touches the sensitive table." | "The broad Scan never touches the PII table." The Admin Lambda (its own data role) sends `dynamodb:Scan`: it reaches ClientsSummary (id, firstName, lastName), "Scan · limit 20"; the branch to ClientsBase (encrypted PII, GetItem only) is refused, "no grant on this table". |
| 49.1–54.0 | Proof · the test suite | "Fifty-one tests pin these boundaries in place." | 51 counts up and lands on "tests"; "tests pin these boundaries in place."; six of the boundaries tick in; "1 known export defect, pinned as xfail. Terraform for both accounts, validated in CI." |
| 53.25–62.5 | End card | "Secure Data Hub." | The mark's eight squares arrive clockwise, then the green keyhole; SECURE DATA HUB; "Breaking into the app doesn't expose the data."; github.com/andyyaro/Building-A-Secure-Data-Hub-in-the-cloud-AWS-. |

## Look

- **References:** the Outbreak Detective intro (light, clean frames; a small coloured kicker over
  a bold sentence-case headline at the top left; a story told in dots; an end card of logo, one
  line and the URL) and the EV-SIENT film (parts that light up one by one, a counter that counts
  up), both moved onto Secure Data Hub's own brand.
- **Brand:** the logo's own colours (`docs/assets/brand/`): ground #E6ECEF with a faint 40 px
  blueprint dot grid and one soft white light that travels behind whatever the frame is about;
  navy #0E2433 for type, outlines and parts; green #0F9D74 for the allowed path, the key and the
  kicker (#0B8562 for small green text); red #D64545 only for the breach and the denials.
- **Shapes:** accounts are thick-outlined rounded boxes, and records are the mark's own squares,
  so on the drop the nine records become the logo.
- **Type:** Geist SemiBold headlines, Geist for body, chips and code words, Montserrat SemiBold
  capitals for the small labels, and Chakra Petch Bold (the wordmark's face) only for the
  wordmark and the big 51. No monospace and no em dashes on screen; no shadows.
- **Motion:** calm. Headlines rise 22 px out of a 5 px blur on the voice's own word times; parts
  pop in from 86 %; paths draw and a green dot travels them; denials are red dashes and a red
  cross. Exits blur out in about half the entrance time.

## Sound

- **Voice:** Kokoro-82M, voice af_heart, 13 lines, each take the closest match to the script.
  "AWS" is voiced as "A W S" and "tenant ID" as "tenant I D" (`narration/lines-tts.json`).
- **Music:** "RnB" by Arulo (Mixkit 224), relaxed R&B at 100 BPM, a bar every 2.4 s, cut on its
  bar lines by `sound/music.py` with 12 ms crossfades:

  | Film (s) | Track (s) | Under |
  |---|---|---|
  | 0–12.45 | 0–12.45 | The quiet intro, under the hook |
  | 12.45–38.85 | 12.45–38.85 | The groove enters on the drop, on "Secure", under the title and decisions 1 and 2 |
  | 38.85–53.25 | 77.25–91.65 | The breakdown and the softer middle are skipped: the fullest section under decisions 3 and 4 and the tests |
  | 53.25–62.5 | from 91.65 | The track's own outro under the end card, faded over the last 2.5 s |

- **Effects:** 69 soft Mixkit sounds with one vocabulary: a low pop is always a denial, a soft pop
  a part arriving, a tick a step or a row, whooshes for things that travel. Each peaks one frame
  after its picture. The list is in [assets/audio/SOURCE.md](assets/audio/SOURCE.md).
- **Levels:** speech at -16 LUFS, the bed 9 dB under it and ducked 4.5 dB more while she speaks;
  the mix at -16 LUFS. On the MP4: -16.1 LUFS, true peak -1.4 dBTP.

## Build

Get the inputs first: `tools/fetch_vendor.sh` for GSAP, then the fonts, music and effects listed
in [assets/audio/SOURCE.md](assets/audio/SOURCE.md). The Python steps need numpy, soundfile,
librosa and mlx-whisper, and ffmpeg on the path.

```sh
tools/fetch_vendor.sh
# Voice each line of narration/lines-tts.json with Kokoro-82M (af_heart) at speeds 1.0 and 1.06,
# as narration/takes/<id>.<k>.wav
python3 narration/pick.py takes            # best take per line: narration/chosen/, words.json
python3 -I sound/music.py                  # assets/audio/music.wav, sound/grid.json
python3 -I sound/mix.py                    # assets/audio/mix.wav, assets/vo.js, assets/timing.js
python3 -I build.py                        # scene windows into index.html
python3 -I narration/vtt.py                # renders/secure-data-hub-v1.en.vtt
npx --yes hyperframes@0.8.173 lint && npx --yes hyperframes@0.8.173 check
npx --yes hyperframes@0.8.173 render -o renders/raw.mp4 --fps 30
ffmpeg -y -i renders/raw.mp4 -i assets/audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
  -shortest -movflags +faststart renders/secure-data-hub-v1.mp4
```

The last step puts the exact mix back on the picture, because the renderer's own audio comes out
about 1 dB quieter. The scenes find their cue words by text in `window.VO`, so a re-voiced or
re-slotted line re-times the picture by itself, and `vtt.py` re-times the captions the same way.
`assets/vo.js`, `assets/timing.js` and the timing JSON are kept as the film was rendered, so the
picture and the captions can be rebuilt without voicing the lines again.

## Captions

The film has no subtitles in the picture. `narration/vtt.py` writes the WebVTT file: 16 cues from
the 13 lines, at most two rows of 42 characters, each timed from its first word to its last
(0.08 s before, 0.3 s after). The watch page plays it as a track.

## The README preview

`docs/assets/readme/secure-data-hub-in-action.webp` is the request path, 22.0–38.0 s of the film:
decision 1 from the refused direct read to the one record, then all of decision 2, ending on the
400 and the Lambda that is never invoked. It is 1200 × 676 at 15 fps, lossy WebP at quality 90,
2.1 MB. A keyframe every 2 to 4 frames matters here: with img2webp's default, the frames that only
patch what changed left faint blocks of the last scene's boxes on the light ground, and the
moving light behind them banded. Measured against the source frames, this encode is as clean as
one with every frame a keyframe (6.0 MB), at a third of the size.

```sh
mkdir -p preview
ffmpeg -ss 22.0 -i renders/secure-data-hub-v1.mp4 -t 16 \
  -vf "fps=15,scale=1200:676:flags=lanczos" preview/f%03d.png
img2webp -loop 0 -lossy -q 90 -m 6 -kmin 2 -kmax 4 -d 67 preview/f*.png \
  -o ../../docs/assets/readme/secure-data-hub-in-action.webp
```

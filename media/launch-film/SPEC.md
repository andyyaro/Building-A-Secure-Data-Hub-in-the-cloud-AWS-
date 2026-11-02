# Secure Data Hub launch film: SPEC

```text
GOAL:    a cloud or security engineer understands, in one minute, why breaking into this app does not expose the
         data: four design decisions, each shown on its real AWS parts, and 51 tests that pin them.
OUTPUT:  HyperFrames 0.8.173, 1920 x 1080, 30 fps, 62.5 s = 1875 frames.
SOUND:   "RnB" (Arulo, Mixkit 224), relaxed R&B at 100 BPM (bar 2.4 s): calm but not too calm (Andy, 2026-11-01).
         Quiet intro under the hook; the groove enters on the drop (12.45 s) on "Secure"; the breakdown is cut and
         the fullest section starts on decision 3 (38.85 s); the track's own outro under the end card (53.25 s).
         Voice Kokoro af_heart, speech -16 LUFS, the bed 9 dB under it and ducked 4.5 dB more while she speaks.
         69 soft effects with one vocabulary: a low pop is always a denial, a soft pop a part arriving, a tick a
         step, whooshes for things that travel. Mix -16 LUFS, true peak -1.7 dBTP.
LOOK:    References: the Outbreak Detective intro (outbreak.andyyaro.com): light, Apple-clean frames, a small
         coloured kicker over a bold sentence-case headline at the top left, a data story told in dots ("One boy
         falls ill." -> 298), and an end card of logo, one line and the URL. From the EV-SIENT film: parts that
         light up one by one, and a counter that counts up. Both moved onto Secure Data Hub's own brand:
           ground   #E6ECEF (the brand ground), a faint 40 px blueprint dot grid, one soft white light that travels
           ink      #0E2433 navy: type, outlines, nodes
           green    #0F9D74: the allowed path, the key, the kicker (#0B8562 for small green text, for contrast)
           red      #D64545: only the breach and the denials
           type     Geist SemiBold for headlines (72-96 px, -0.032em); Geist for body, chips and code words;
                    Montserrat SemiBold caps for the small labels (Andy's approved label face); Chakra Petch Bold
                    for the wordmark and the big numeral only. NO MONOSPACE anywhere.
           shapes   accounts are thick-outlined rounded boxes and records are the mark's own squares: the film's
                    nine client records ARE the mark, and on the drop the centre one becomes the green keyhole.
MOTION:  calm: headlines rise 22 px with blur 5 -> 0 on the voice's own word times (window.VO); parts pop in
         (scale 0.86 -> 1, back.out); paths draw and a green dot travels them; denials are red dashes and a red
         cross. Exits blur out at about half the entrance.
SHOTS:   s1 open      0-19.65   "One stolen credential." -> nine records in one account turn red -> the wall: app
                                account and data account; the credential breaks into the app and is stopped
                                at the boundary -> the records travel to the centre and become the mark on the
                                drop; SECURE DATA HUB; the tagline; the stack.
         s2 accounts  19.65-29.25  decision 1: the direct read is denied; the Lambda goes down, across as
                                sts:AssumeRole, to the data role; temporary credentials; GetItem on one record.
         s3 token     29.25-38.85  decision 2: the caller's own client_id is struck out; the verified token's
                                custom:client_id travels into the gateway's mapping; only then does the Lambda
                                run; with no claim, 400 · Missing Client Id. and the Lambda is never invoked.
         s4 key       38.85-49.1   decision 3: the item's fields are encrypted; the assumed data role reaches the
                                KMS key and the item decrypts; the Lambda's own role (the SDK's silent default)
                                is denied. Decision 4: the admin's Scan reaches ClientsSummary (3 fields, limit
                                20); ClientsBase has no grant.
         s5 tests     49.1-54.0    51 counts up; "tests pin these boundaries in place."; six of the boundaries;
                                1 known export defect pinned as xfail; Terraform for both accounts, in CI.
         s6 end       53.25-62.5   the mark builds clockwise, then the key; SECURE DATA HUB; the line; the repo.
OBJECTS: real code only: LambdaFunctionForBaseTable_Client.py (assume_role, the botocore_session fix,
         EncryptedTable.get_item); LambdaFunctionForSummaryTable_Admin.py (Scan, AttributesToGet id/firstName/
         lastName, Limit 20); the four IAM policies; apigw/ClientApp/mapping_template.vtl (custom:client_id, 400
         "Missing Client Id."); the test event (client_id 25xwe2, GET /client/profile); the test item (Ada
         Lovelace); 51 passed + 1 xfailed (pytest, main @c197b22). The caller's "9ab3f1" stands for any
         caller-supplied ID. The nine-account organisation in the deck is a design only, so it is not shown.
BANNED:  monospace fonts; em dashes on screen; the Huly look; the Linear look of Orkestra v2; Provalume's
         Biennale paper; shadows; three feature cards; the logo docked in a corner.
QA:      1.6, 4.7, 8.9, 12.9, 17.2, 21.9, 28.5, 31.9, 35.2, 37.9, 41.5, 44.4, 47.8, 51.9, 54.6, 60.5.
```

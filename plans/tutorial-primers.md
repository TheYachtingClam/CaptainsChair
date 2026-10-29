# Plan: Captain primers

A primer is a small tutorial for a Captain who mostly plays by the general rules but has one or two twists. See [tutorials-roadmap.md](tutorials-roadmap.md).

## Format

- **Cadet Training**, the Captain's own deck, Basic side.
- **One guided turn**, about 8–12 steps, stacked to show the Captain's main twist.
- **Then free play with 4–6 tips** about the deck's key cards and its mission.
- **Assumes the Picard tutorial;** the lobby says so.
- The framework already supports it: a short script with tips. Each primer is one YAML file and its replay test.

## Order

From the Captains' complexity, and how far each departs from the general rules. Each primer's twist is confirmed from the deck's specs when its script is written.

| Order | Captain | Complexity | The twist to show |
|---|---|---|---|
| 1 | Freeman | 7 | SUPPORT chains from hand on your own turn (REQ-EXP-30 to -37), Lower Decker cards. Also teaches SUPPORT for every Second Contact deck |
| 2 | Archer | 6 | 2 Away Teams to start, 4 set aside; cards that add them, and cards that put cards back on the Reserve (REQ-CD-ARC-01, -02) |
| 3 | Riker | 6 | Strong Military; getting Research via Utilize; Gluonic Distortion turning your deck face up |
| 4 | Pike | 5 | Playing a skilled card climbs a track; Starbase One's Away Team; the Time Crystal's early Developments |
| 5 | Sela | 5 | Decided when written, from her deck's specs |
| 6 | Kirk, Sisko | 4 | Probably no primer: the general rules cover them. A short tip set might do |
| — | Georgiou, Shran, Soval, Koloth | 2–3 | None planned |

## Steps

✅ Freeman, Archer, Riker, Pike and Sela are written (`server/content/tutorials/<captain>-primer.yaml`), each with a replay test, for your review. Kirk and Sisko have none, as planned.

Each primer: script (for your review), check, deploy on your word. Freeman's primer may need the coach to point at SUPPORT answers offered from the hand; that is settled when its script is written.

# Raw scans

Source scans of game components. These files are **not** copied into the Docker image. Run the processing script to make the web images the server uses:

```bash
scripts/process_scans.py                              # everything
scripts/process_scans.py to_boldly_go/cards second_contact   # only these folders and their subfolders
```

The script writes `server/content/images/<same folders>/<id>.webp` and updates `server/content/images/manifest.json`. Commit both.

## Folders

Scans are grouped by product, then by kind:

```
resources/scans/<set>/<kind>/...
```

`<set>` is the product: `base_game` (the Core Box), `to_boldly_go`, `second_contact`, `promo1` or `promo2`. The `<kind>` folder decides how an image is sized. Below it, organise scans however you like, at any depth, for example `to_boldly_go/cards/captains/soval/`.

| Kind folder | What goes in it | Output |
|---|---|---|
| `cards/` | Every card: Market, Crew, Locations, Incidents, Encounters, Stardates, card backs | Exact card proportions, 630 × 880 |
| `boards/` | Crew boards, one scan per side | Scan's own proportions, 1800 px on the long side |
| `command/` | The Bot's Automated Command cards, one image or PDF page per side | Scan's own proportions, 1400 px on the long side |
| `ships/` | Ship tokens, front (ship art) and back (name), as cut-out PNGs | Own proportions, 400 px on the long side, transparency kept |
| `tokens/` | Other tokens: Away Teams (`away-team-p1`, `-p2`) and Khan's trait tokens (`tokens/khan/`) | Own proportions, 400 px on the long side, transparency kept |
| `manual/`, `solo/` | Rulebook pages | Not processed; for people to read |

Any other kind folder keeps its proportions at 1200 px on the long side.

Card and board specs (`.md` files beside each scan) must sit in the folder of the set they declare; `scripts/build_content.py` checks this.

Images and PDFs both work. Each PDF page becomes its own image.

## Ids

Each image is named by an id that must be unique across all folders. The script stops and lists any duplicates. An id comes from, in order:

1. a `mapping.csv` in the same folder as the scan, which applies only to files in that folder:

   ```csv
   file,id,rotate
   IMG_4411.jpg,2GEO01,
   cc-soval.pdf#3,cc-soval-traits,
   ```

   For a PDF page, write the file as `name.pdf#page`, with pages counted from 1. `rotate` is optional and turns the finished image clockwise by 0, 90, 180 or 270 degrees.
2. the file name, if it starts with the card id printed on the card, such as `2GEO01.jpg`, or if the whole name is a lower-case id with hyphens, such as `cb-soval-basic.jpg` or `back-standard.jpg`;
3. for a PDF page without a mapping, the PDF's name plus the page number, such as `cc-soval-p3`.

Current naming conventions:

| Item | Id |
|---|---|
| Card | Printed id, e.g. `2SOV01`, `SD09` |
| Card back | `card-back`, in `to_boldly_go/cards/`. The client draws every facedown deck and hidden hand with it |
| Crew board side | `cb-<captain>-basic`, `cb-<captain>-advanced` |
| Command card side | `cc-<captain>-traits`, `cc-<captain>-upgrades`, `cc-<captain>-suits-no-duty-officer`, `cc-<captain>-suits-duty-officer` |
| Ship token | `ship-<card id in lower case>` (front, shown on the board), `ship-<card id>-back` (the name side). Set in `ships/mapping.csv` |
| Away Team token | `away-team-p1` (first player, blue), `away-team-p2` (second player or the Bot, pink) |
| Khan's trait token | `khan-<trait>`, and `khan-<trait>-marked` for the crossed-out side with the tick |

## Cropping

Scans should already be cropped to the item, as flatbed or scanning-app scans are. The script then only resizes them.

For photos that still show the table around the item, run with `--detect` on just those folders. The script then finds the item's outline and straightens it. Never use `--detect` on cropped scans: it can lock onto the artwork inside a card and crop to that.

## Keeping images tidy

A full run, with no folders named:

- moves an image when its scan moves to another folder;
- removes the image of a deleted or renamed scan;
- ignores hidden files and folders, whose names start with a dot.

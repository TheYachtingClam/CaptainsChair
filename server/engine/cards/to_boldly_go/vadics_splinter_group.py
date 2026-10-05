"""2ALL15 Vadic's Splinter Group (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL15.md
The PLAY duplicates, which arrives in Step 6."""

from engine.cards import trait_modifier
from engine.ops import card, table_cards


@trait_modifier("2ALL15", staging=True)
def changeling(state, owner, inst, target):
    """SPECIAL: While this card is in your Staging Area and you have a Borg in play, this card is additionally treated
    as Wildcard. Note: the engine has no Wildcard rules yet (REQ-TR-05), so this has no further effect."""
    if target is not inst:
        return set()
    in_play = [*table_cards(owner), *owner.staging]
    return {"Wildcard"} if any("Borg" in card(i).traits for i in in_play) else set()

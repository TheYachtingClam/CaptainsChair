"""1CAR01 Biobed (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("1CAR01", 0, uses=[A.JUNK, A.FREE_PLAY, A.FIND])
def treatment(ctx, actions):
    """PLAY: Junk a card from the Market. Free play an Incident OR find a Doctor."""
    yield from actions.junk()
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    options = ([("play", "Free play an Incident")] if incidents else []) + [("find", "Find a Doctor")]
    choice = yield from actions.choose("Biobed: free play an Incident, or find a Doctor?", options)
    if choice == "play":
        incident = yield from actions.pick_card("Free play which Incident?", incidents)
        yield from actions.free_play(incident)
    else:
        yield from actions.find(lambda i: has_trait(i, "Doctor"), "a Doctor")

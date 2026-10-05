"""2LOC13 Kelvas Docks (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC13.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import no_effect
from ._util import is_suit, ships

operation("2LOC13", 0, uses=[])(no_effect)


@operation("2LOC13", 1, uses=[A.SPEND, A.FREE_PLAY, A.REFRESH])
def drydock(ctx, actions):
    """ACTIVATION: You may spend 3 [Dilithium] to free play a Ship. You may refresh a Ship."""
    playable = actions.free_play_candidates(lambda i: is_suit(i, "Ship"))
    if playable and actions.can_spend(dilithium=3):
        ship = yield from actions.pick_card("Spend 3 Dilithium to free play a Ship?", playable, optional=True,
                                            none_label="No")
        if ship:
            yield from actions.spend(dilithium=3)
            yield from actions.free_play(ship)
    tired = [s for s in ships(ctx) if s.exhausted]
    ship = yield from actions.pick_card("Refresh a Ship?", tired, optional=True, none_label="No")
    if ship:
        yield from actions.refresh(ship)

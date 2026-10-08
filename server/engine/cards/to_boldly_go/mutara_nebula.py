"""2KHA14 Mutara Nebula (Location). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA14.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import ships


def _ships_here(ctx):
    return [s for s in ships(ctx) if s.at == ctx.this_card.uid]


@operation("2KHA14", 0, uses=[A.JUNK, A.GAIN_CARD, A.DISCARD, A.TAKE_CONTROL])
def hide(ctx, actions):
    """PLAY: Junk a card from the Market. If you have 7+ traits marked, gain a Ship from the Junk, otherwise discard 2
    cards. Take control of this location."""
    yield from actions.junk()
    if ctx.traits_marked() >= 7:
        yield from actions.gain_card(["Ship"], label="a Ship from the Junk", only_junk=True)
    else:
        yield from actions.discard(2)
    yield from actions.take_control(ctx.this_card)


@operation("2KHA14", 1)
def static(ctx, actions):
    """CONTROL: No effect."""
    return
    yield  # pragma: no cover


@operation("2KHA14", 2, uses=[A.WARP, A.SEND_AWAY_TEAM], cost=[Spend(dilithium=1)],
           requires=lambda ctx: bool(_ships_here(ctx)))
def emerge(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to warp a Ship from here, then send an [Away Team] to the Location you warped
    to."""
    ship = yield from actions.pick_card("Warp which Ship from here?", _ships_here(ctx))
    dest = yield from actions.warp(ship)
    if dest is not None:
        yield from actions.send_away_team(1, target=dest)

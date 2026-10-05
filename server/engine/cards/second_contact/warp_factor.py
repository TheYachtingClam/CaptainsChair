"""3RIK21 Warp in the Factor of 5, 6, 7, 8! (Directive). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK21.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, ships


def _starfleet_ships(ctx):
    return [s for s in ships(ctx) if has_trait(s, "Starfleet")]


@operation("3RIK21", 0, uses=[A.DRAW, A.DISCARD, A.WARP])
def engage(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. You may warp up to 3 Ship with Starfleet."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(2)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")
    warped: set[str] = set()
    for n in (1, 2, 3):
        left = [s for s in _starfleet_ships(ctx) if s.uid not in warped]
        ship = yield from actions.pick_card(f"Warp a Starfleet Ship ({n} of up to 3)?", left, optional=True,
                                            none_label="Stop")
        if not ship:
            break
        warped.add(ship.uid)
        yield from actions.warp(ship)


@operation("3RIK21", 1, uses=[A.SEND_AWAY_TEAM])
def landing_parties(ctx, actions):
    """PLAY: For each deployed Ship with Starfleet you have, send an [Away Team] to its Location."""
    for ship in _starfleet_ships(ctx):
        loc = ctx.location_of(ship)
        if loc is not None:
            yield from actions.send_away_team(1, target=loc)

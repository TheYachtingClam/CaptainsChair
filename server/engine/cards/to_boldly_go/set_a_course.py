"""Set a Course (Directive): 2GEO10, and identical copies 2KIRK20, 3FRE17.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO10.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, ships

IDS = ("2GEO10", "2KIRK20", "3FRE17")


@operation(IDS, 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))
def discard_persons_send_teams(ctx, actions):
    """PLAY: Discard up to 3 Person to send the same number of Away Teams to the same Location."""
    persons = [i for i in ctx.me.hand if is_suit(i, "Person")]
    chosen = yield from actions.pick_cards("Discard Persons (up to 3)", persons, maximum=3, minimum=1)
    for inst in chosen:
        actions._discard(inst)
    yield from actions.send_away_team(len(chosen), same_location=True)


@operation(IDS, 1, uses=[A.DRAW, A.DISCARD, A.WARP])
def draw_discard_warp(ctx, actions):
    """PLAY: Draw a card, then discard a card. Warp up to 2 of your Ship."""
    yield from actions.draw(1)
    yield from actions.discard(1)
    remaining = ships(ctx)
    for _ in range(2):
        ship = yield from actions.pick_card("Warp which Ship?", remaining, optional=True, none_label="Stop warping")
        if not ship:
            break
        remaining.remove(ship)
        yield from actions.warp(ship)

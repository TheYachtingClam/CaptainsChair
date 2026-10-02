"""2GEO21 Lt. Detmer (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO21.md"""

from engine.cards import operation, skill_icons
from engine.ops import A

from ._util import ships


@operation("2GEO21", 0, uses=[A.DISCARD, A.WARP, A.SEND_AWAY_TEAM])
def pilot(ctx, actions):
    """PLAY: Discard the top card of your deck. You may discard a card to warp a Ship and send an Away Team
    to the Location you warped to."""
    yield from actions.discard_top()
    your_ships = ships(ctx)
    if your_ships and ctx.me.hand and (yield from actions.may("Discard a card to warp a Ship and send an Away Team there?")):
        yield from actions.discard(1)
        ship = yield from actions.pick_card("Warp which Ship?", your_ships)
        dest = yield from actions.warp(ship)
        if dest is not None:
            yield from actions.send_away_team(1, target=dest)


@operation("2GEO21", 1, uses=[A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "warp" and ev["seat"] == ctx.me.seat)
def draw_on_warp(ctx, actions):
    """REACTION: After warping a Ship, draw a card."""
    yield from actions.draw(1)


@skill_icons("2GEO21")
def any_skill(state, owner, inst):
    """PASSIVE: This card has 1 Any Skill (only while on duty)."""
    return ["Any"]

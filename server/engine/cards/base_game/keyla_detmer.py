"""1BUR20 Keyla Detmer (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR20.md  Not Lt. Detmer (2GEO21)."""

from engine.cards import operation, skill_icons
from engine.ops import A

from ._util import others_in_hand, ships


@operation("1BUR20", 0, uses=[A.DISCARD, A.WARP, A.SEND_AWAY_TEAM])
def helm(ctx, actions):
    """PLAY: Discard the top card of your deck. You may discard a card to warp a Ship and send an [Away Team] to the
    Location you warped to."""
    yield from actions.discard_from_deck()
    fleet = [s for s in ships(ctx) if actions.can_warp(s)]
    if not fleet or not others_in_hand(ctx) or not (
            yield from actions.may("Discard a card to warp a Ship and send an Away Team there?")):
        return
    yield from actions.discard(1)
    ship = yield from actions.pick_card("Warp which Ship?", fleet)
    yield from actions.warp(ship)
    ship = next((s for s in ctx.me.fleet if s.uid == ship.uid), None)
    loc = ctx.location_of(ship) if ship is not None else None
    if loc is not None and any(t.uid == loc.uid for t in actions.away_targets()):
        yield from actions.send_away_team(1, target=loc)


@skill_icons("1BUR20")
def any_skills(state, owner, inst):
    """PASSIVE: This card has 2 [Any Skill]."""
    return ["Any", "Any"]

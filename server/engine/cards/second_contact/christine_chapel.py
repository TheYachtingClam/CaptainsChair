"""3PIK12 Christine Chapel (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK12.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, ships

registry.CANNOT_PROMOTE.add("3PIK12")  # SPECIAL: This card cannot be promoted.


@operation("3PIK12", 0, uses=[A.FREE_PLAY, A.BEAM, A.SEND_AWAY_TEAM])
def triage(ctx, actions):
    """PLAY: Free play an Incident. If you do, you may beam this card to a deployed Ship to send an [Away Team] to its
    Location."""
    incident = yield from actions.pick_card("Free play which Incident?",
                                            actions.free_play_candidates(lambda i: is_suit(i, "Incident")))
    if not incident:
        return
    yield from actions.free_play(incident)
    me = ctx.this_card
    placed = [s for s in ships(ctx) if ctx.location_of(s) is not None]
    if me is None or me not in ctx.me.staging or not placed:
        return
    ship = yield from actions.pick_card("Beam Christine Chapel to a Ship to send an Away Team to its Location?", placed,
                                        optional=True, none_label="No")
    if ship:
        yield from actions.beam(me, ship)
        yield from actions.send_away_team(1, target=ctx.location_of(ship))


@operation("3PIK12", 1, uses=[A.SCAN_FOR, A.DRAW], requires=lambda ctx: ctx.track("research") >= 6)
def nurse(ctx, actions):
    """PLAY: Requires [Research] 6. Scan for a Doctor. Draw a card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Doctor"), "a Doctor")
    yield from actions.draw(1)

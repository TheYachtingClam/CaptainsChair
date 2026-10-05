"""2KIRK04 What Have I Done (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import ships

development_cost("2KIRK04", Spend(latinum=3))


def _ships_at_locations(ctx):
    return [s for s in ships(ctx) if ctx.location_of(s) is not None]


@operation("2KIRK04", 0, uses=[A.LOG, A.SEND_AWAY_TEAM, A.TAKE_CONTROL, A.ATTACK, A.TAKE_INCIDENT, A.FORCE, A.DISMISS],
           requires=lambda ctx: bool(_ships_at_locations(ctx)))
def self_destruct(ctx, actions):
    """ATTACK PLAY: Log a deployed Ship to send up to 3 [Away Team] to the same Location. If that Location is neutral and
    now secured, take control of it. Your opponent takes an Incident. Force your opponent to dismiss (one of) their
    Duty Officer(s). Log this card. Ruling: the Ship's Location is noted before logging removes its token."""
    ship = yield from actions.pick_card("Log which deployed Ship?", _ships_at_locations(ctx))
    loc = ctx.location_of(ship)
    yield from actions.log(ship)
    for n in (1, 2, 3):
        if not (yield from actions.may(f"Send an Away Team to {ctx.name(loc)} ({n} of up to 3)?")):
            break
        yield from actions.send_away_team(1, target=loc)
    if loc in ctx.state.neutral and ctx.secured_by(loc):
        yield from actions.take_control(loc)
    opp = ctx.opponent
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
        if opp is not None and opp.duty:
            officer = yield from actions.pick_card("Dismiss one of your Duty Officers.", list(opp.duty), seat=opp.seat)
            yield from actions.dismiss(officer)
    yield from actions.log(ctx.this_card)

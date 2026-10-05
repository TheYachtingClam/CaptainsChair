"""3FRE13 Samanthan Rutherford (Person). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE13.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import count_traits, is_suit


@operation("3FRE13", 0, uses=[A.TAKE_INCIDENT, A.ENLIST_DEVELOPMENT], cost=[TakeIncidentCost()])
def upgrades(ctx, actions):
    """PLAY: Take an Incident to enlist a Development."""
    yield from actions.enlist_development()


def _own_ship_exhausted(ctx, ev):
    ship = ctx.event_card
    return (ev["kind"] == "exhaust" and ev["seat"] == ctx.me.seat and ship is not None and ship in ctx.me.fleet
            and is_suit(ship, "Ship"))


@operation("3FRE13", 1, uses=[A.REFRESH, A.BEAM, A.GAIN_RESOURCE], trigger=_own_ship_exhausted)
def implant(ctx, actions):
    """SUPPORT: After exhausting a Ship, refresh it and you may beam this card to it. If you have another Synthetic in
    play, gain 1 [Glory]."""
    ship = ctx.event_card
    yield from actions.refresh(ship)
    me = ctx.this_card
    if me in ctx.me.staging and (yield from actions.may(f"Beam Rutherford to {ctx.name(ship)}?")):
        yield from actions.beam(me, ship)
    if count_traits(ctx, "Synthetic", exclude=me):
        yield from actions.gain_resource("glory", 1)


@operation("3FRE13", 2, uses=[A.GAIN_RESOURCE, A.DISCARD, A.GAIN_ACTION])
def engineering(ctx, actions):
    """ACTIVATION: Gain 1 [Dilithium], and 2 [Dilithium] for each controlled Location you have in play. If you have
    another Engineer in play, you may discard a card to gain an [Action]."""
    yield from actions.gain_resource("dilithium", 1 + 2 * len(ctx.me.locations))
    if count_traits(ctx, "Engineer", exclude=ctx.this_card) and ctx.me.hand:
        if (yield from actions.discard(1, label="a card to gain an Action", optional=True)):
            yield from actions.gain_action(1)



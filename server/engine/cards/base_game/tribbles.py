"""1CAR14 Tribbles (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR14.md"""

from engine.cards import operation
from engine.ops import A


@operation("1CAR14", 0, uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.JUNK, A.ATTACK, A.TAKE_INCIDENT, A.DISMISS, A.FORCE,
                             A.DISCARD])
def trouble(ctx, actions):
    """ATTACK PLAY: Gain 1 [Influence]. Gain 1 [Latinum]. Junk a card from the Market. Your opponent takes an Incident.
    Dismiss all of their Klingon Duty Officers. If any were dismissed, force them to discard a card."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_resource("latinum", 1)
    yield from actions.junk()
    if not (yield from actions.attack()):
        return
    yield from actions.take_incident(opponent=True)
    opp = ctx.opponent
    if opp is None:
        return
    klingons = [i for i in opp.duty if "Klingon" in ctx.traits(i)]
    for officer in klingons:
        yield from actions.dismiss(officer)
    if klingons:
        yield from actions.discard(1, player=opp)

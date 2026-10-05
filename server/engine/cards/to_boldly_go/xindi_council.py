"""2ARC09 Xindi Council (Ally, Development). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition

from ._util import has_trait, is_suit, opponent_has

development_cost("2ARC09", Condition(
    lambda ctx: ctx.count_in_play(lambda i: is_suit(i, "Incident")) > 0
    and ctx.count_in_play(lambda i: is_suit(i, "Encounter")) > 0, "an Incident and an Encounter in play"))


@operation("2ARC09", 0, uses=[A.GAIN_SPECIALTY, A.SCAN_FOR])
def council(ctx, actions):
    """PLAY: Gain 2 [Influence]. Scan for Xindi, including from the Junk."""
    yield from actions.gain_specialty("influence", 2)
    yield from actions.scan_for(lambda i: has_trait(i, "Xindi"), "a Xindi", include_junk=True)


@operation("2ARC09", 1, uses=[A.TAKE_INCIDENT, A.ATTACK, A.EXHAUST, A.TAKE_ENCOUNTER, A.LOG],
           requires=lambda ctx: ctx.track("influence") >= 6)
def weapon_test(ctx, actions):
    """ATTACK PLAY: Requires [Influence] 6. If your opponent has Xindi in play, you both take an Incident. Exhaust an
    opponent controlled Location (of your choice). Take the top Encounter. Log this card."""
    opp = ctx.opponent
    xindi = opponent_has(ctx, lambda i: has_trait(i, "Xindi"))
    if xindi:
        yield from actions.take_incident()
    if (yield from actions.attack()):
        if xindi:
            yield from actions.take_incident(opponent=True)
        if opp is not None:
            loc = yield from actions.pick_card("Exhaust which opponent Location?",
                                               [l for l in opp.locations if not l.exhausted])
            if loc:
                yield from actions.exhaust(loc)
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)

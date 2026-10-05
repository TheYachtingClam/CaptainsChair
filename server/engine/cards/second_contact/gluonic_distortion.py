"""3RIK09 Gluonic Distortion (Status, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK09.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, Condition, Spend

from ._util import is_suit

development_cost("3RIK09", Spend(dilithium=3), Condition(
    lambda ctx: ctx.count_in_play(lambda i: is_suit(i, "Encounter")) > 0, "have an Encounter in play"))
# PASSIVE: Your Draw deck is face-up. When interacting with your deck you can choose any of its cards.
registry.DECK_FACE_UP.add("3RIK09")


@operation("3RIK09", 0, uses=[A.EXHAUST, A.TAKE_INCIDENT])
def unstable(ctx, actions):
    """RESUPPLY: Exhaust this card and take an Incident."""
    yield from actions.exhaust(ctx.this_card)
    yield from actions.take_incident()


@operation("3RIK09", 1, uses=[A.SHUFFLE_INTO, A.LOG])
def collapse(ctx, actions):
    """CLEAN-UP: If this card is exhausted, shuffle your deck and log this card."""
    if ctx.this_card.exhausted:
        yield from actions.shuffle_deck()
        yield from actions.log(ctx.this_card)


@operation("3RIK09", 3, uses=[A.PUT],
           trigger=lambda ctx, ev: ev["kind"] == "enlist" and ev.get("uid") == ctx.ref.uid and ev["seat"] == ctx.me.seat)
def materialise(ctx, actions):
    """SPECIAL: When this card is enlisted, put it into play immediately."""
    yield from actions.put_into_status(ctx.this_card)

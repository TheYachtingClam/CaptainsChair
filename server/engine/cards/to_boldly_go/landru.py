"""2PER09 Landru (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER09.md
Landru has no PLAY: he reaches the Duty Officer slot only by a promote effect."""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, others_in_hand


@operation("2PER09", 0, uses=[A.BEAM], requires=lambda ctx: bool(others_in_hand(ctx, lambda i: is_suit(i, "Person"))))
def absorb(ctx, actions):
    """ACTIVATION: Beam a Person here."""
    person = yield from actions.pick_card("Beam which Person to Landru?",
                                          others_in_hand(ctx, lambda i: is_suit(i, "Person")))
    yield from actions.beam(person, ctx.this_card)


def _beamed_people(ctx):
    return [b for b in ctx.this_card.beamed if is_suit(b, "Person")]


@operation("2PER09", 1, uses=[A.LOG, A.TAKE_CONTROL, A.JUNK, A.RECALL],
           requires=lambda ctx: ctx.track("influence") >= 2 and len(_beamed_people(ctx)) >= 2
           and bool(ctx.state.location_deck))
def the_body(ctx, actions):
    """ACTIVATION: Requires [Influence] 2. Log 2 Person beamed here to draw the top Location and take control of it.
    Junk a card from the Market and recall this card."""
    for n in (1, 2):
        person = yield from actions.pick_card(f"Log which Person beamed to Landru ({n} of 2)?", _beamed_people(ctx))
        yield from actions.log(person)
    yield from actions.take_control(ctx.state.location_deck[0])
    yield from actions.junk()
    yield from actions.recall(ctx.this_card)

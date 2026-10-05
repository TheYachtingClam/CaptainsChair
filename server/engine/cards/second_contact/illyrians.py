"""3ALL02 Illyrians (Ally). Spec: resources/scans/second_contact/cards/ally/3ALL02.md
The SPECIAL (two extra Duty Officers) arrives in Step 5."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, has_trait, is_suit


@operation("3ALL02", 0, uses=[A.PROMOTE],
           requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand + ctx.me.staging if i is not ctx.this_card))
def enhance(ctx, actions):
    """PLAY: Promote a Person from your hand or the Staging Area to Duty Officer."""
    people = [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person") and i is not ctx.this_card]
    person = yield from actions.pick_card("Promote which Person?", people)
    yield from actions.promote(person)


@operation("3ALL02", 1, uses=[A.DISCARD, A.SCAN, A.PROMOTE],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Starfleet"), "a Starfleet")])
def recruit(ctx, actions):
    """PLAY: Discard a Starfleet to scan 2 of Person. Promote the gained card to Duty Officer."""
    person = yield from actions.scan(2, ["Person"])
    if person:
        yield from actions.promote(person)


@operation("3ALL02", 2, uses=[A.GAIN_SPECIALTY, A.LOG])
def colony(ctx, actions):
    """CLEAN-UP: Gain 1 [Research] for each Duty Officer you have in play. If you have no other Augment in play, log
    this card."""
    if ctx.me.duty:
        yield from actions.gain_specialty("research", len(ctx.me.duty))
    if not count_traits(ctx, "Augment", exclude=ctx.this_card):
        yield from actions.log(ctx.this_card)

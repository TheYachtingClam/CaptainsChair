"""2ARC23 Faith of the Heart (Directive). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC23.md"""

from engine.cards import operation
from engine.ops import A, ExhaustCaptain

from ._util import has_trait, is_suit


@operation("2ARC23", 0, uses=[A.EXHAUST, A.SCAN_FOR, A.PUT], cost=[ExhaustCaptain()])
def legacy(ctx, actions):
    """PLAY: Exhaust your Captain to scan for NX-01. Put the gained card on top of your Reserve deck."""
    gained = yield from actions.scan_for(lambda i: has_trait(i, "NX-01"), "an NX-01")
    if gained:
        yield from actions.put_on_reserve(gained)


@operation("2ARC23", 1, uses=[A.PEEK, A.REORDER, A.PROMOTE])
def plan_ahead(ctx, actions):
    """PLAY: Look at the top 2 cards of your Reserve deck. Put them on the top and/or bottom in any order. You may
    promote a Person with Starfleet from your hand or Staging Area to Duty Officer."""
    yield from actions.peek_and_reorder(2)
    people = [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person") and has_trait(i, "Starfleet")]
    person = yield from actions.pick_card("Promote a Starfleet Person?", people, optional=True, none_label="No")
    if person:
        yield from actions.promote(person)

"""2KIRK10 Time Warp (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK10.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import has_trait

development_cost("2KIRK10", Spend(dilithium=2), TakeIncidentCost())


@operation("2KIRK10", 0, uses=[A.FIND])
def slingshot(ctx, actions):
    """PLAY: Find any card."""
    yield from actions.find(lambda i: True, "any card")


@operation("2KIRK10", 1, uses=[A.RECALL])
def back_in_time(ctx, actions):
    """PLAY: Recall a non-Time Travel card from your Staging Area."""
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]
    card = yield from actions.pick_card("Recall which card?", cards)
    if card:
        yield from actions.recall(card)

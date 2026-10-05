"""2KIRK15 Needs of the Many (Directive). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK15.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, ships


@operation("2KIRK15", 0, uses=[A.DISMISS, A.LOG, A.ENLIST_DEVELOPMENT],
           requires=lambda ctx: bool(ships(ctx) or ctx.me.duty))
def sacrifice(ctx, actions):
    """PLAY: Dismiss a deployed Ship or a Duty Officer, then log the dismissed card to enlist a Person from your
    Development pile. Log this card."""
    card = yield from actions.pick_card("Dismiss which deployed Ship or Duty Officer?", [*ships(ctx), *ctx.me.duty])
    yield from actions.dismiss(card)
    dismissed = next((i for i in ctx.me.discard if i.uid == card.uid), None)
    if dismissed is not None:
        yield from actions.log(dismissed)
        yield from actions.enlist_development(pred=lambda i: is_suit(i, "Person"))
    yield from actions.log(ctx.this_card)

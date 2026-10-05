"""2ALL07 Letheans (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL07.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("2ALL07", 0, uses=[A.ATTACK, A.DISMISS, A.SCAN_FOR, A.DRAW_FROM_DISCARD, A.LOG])
def telepathic_assault(ctx, actions):
    """ATTACK PLAY: Dismiss an opponent Duty Officer. You may scan for a Shady. You may draw a Cargo from your Discard
    pile. Log this card."""
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None and opp.duty:
        officer = yield from actions.pick_card("Dismiss which opponent Duty Officer?", list(opp.duty))
        yield from actions.dismiss(officer)
    if (yield from actions.may("Scan for a Shady?")):
        yield from actions.scan_for(lambda i: has_trait(i, "Shady"), "a Shady")
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Cargo"), "a Cargo", optional=True)
    yield from actions.log(ctx.this_card)

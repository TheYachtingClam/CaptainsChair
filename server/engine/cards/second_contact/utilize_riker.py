"""3RIK08 Utilize: Riker's copy is a Development. Its PLAYs are registered with the other copies in
engine/cards/to_boldly_go/utilize.py. Spec: resources/scans/second_contact/cards/captains/william riker/3RIK08.md"""

from engine.cards import development_cost
from engine.ops import A, EffectCost, Spend

SWOOPING_IN = "3RIK23"


def _where(ctx):
    """'find' when Swooping In is in your hand, deck, Discard pile or Reserve; 'recall' when it is in play."""
    me = ctx.me
    if any(i.card == SWOOPING_IN for i in me.hand + me.draw + me.discard + me.reserve):
        return "find"
    if ctx.count_in_play(lambda i: i.card == SWOOPING_IN):
        return "recall"
    return None


def _log_swooping_in(ctx, actions):
    """Find or recall Swooping In, then log it."""
    if _where(ctx) == "recall":
        card = next(i for i in ctx.in_play() if i.card == SWOOPING_IN)
        yield from actions.recall(card)
    else:
        card, _ = yield from actions.find(lambda i: i.card == SWOOPING_IN, "Swooping In")
    if card is not None:
        yield from actions.log(card)


development_cost("3RIK08", Spend(dilithium=1, latinum=1), EffectCost(
    lambda ctx: _where(ctx) is not None, _log_swooping_in, (A.FIND, A.RECALL, A.LOG), "find/recall and log Swooping In"))

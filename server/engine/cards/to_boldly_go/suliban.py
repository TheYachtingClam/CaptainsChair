"""2ALL12 Suliban (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL12.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


@operation("2ALL12", 0, uses=[A.DISCARD, A.RECALL, A.DUPLICATE])
def temporal_agents(ctx, actions):
    """PLAY: You may discard a card to recall a non-Time Travel card from your Staging Area. You may duplicate a play
    operation of an Ally from the Market."""
    recallable = [i for i in ctx.me.staging if not has_trait(i, "Time Travel") and i is not ctx.this_card]
    if recallable and others_in_hand(ctx) and (
            yield from actions.may("Discard a card to recall a non-Time Travel card from your Staging Area?")):
        yield from actions.discard(1)
        card = yield from actions.pick_card("Recall which card?", recallable)
        yield from actions.recall(card)
    ally = ctx.state.market.get("Ally")
    if ally is not None:
        yield from actions.duplicate([ally], label=f"the Market Ally ({ctx.name(ally)})")

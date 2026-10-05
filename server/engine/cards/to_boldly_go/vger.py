"""2ENC08 V'Ger (Encounter). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC08.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ENC08", 0, uses=[A.LOG])
def join_the_creator(ctx, actions):
    """PLAY: Log up to 2 cards from your hand or Discard pile."""
    for n in (1, 2):
        cards = [i for i in ctx.me.hand + ctx.me.discard if i is not ctx.this_card]
        card = yield from actions.pick_card(f"Log a card from your hand or Discard pile ({n} of up to 2)?", cards,
                                            optional=True, none_label="Stop")
        if not card:
            break
        yield from actions.log(card)

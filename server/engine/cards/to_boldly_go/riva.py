"""2PER16 Riva (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER16.md
The Reaction that ignores attacks arrives in Step 4."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("2PER16", 0, uses=[A.DRAW, A.LOG, A.GAIN_RESOURCE])
def mediate(ctx, actions):
    """PLAY: Draw a card. You may log an Attack from your hand or Discard pile to gain 1 [Glory]."""
    yield from actions.draw(1)
    attacks = [i for i in ctx.me.hand + ctx.me.discard if has_trait(i, "Attack") and i is not ctx.this_card]
    card = yield from actions.pick_card("Log an Attack from your hand or Discard pile to gain 1 Glory?", attacks,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)
        yield from actions.gain_resource("glory", 1)

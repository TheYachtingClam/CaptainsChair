"""2ALL06 Kelpiens (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2ALL06", 0, uses=[A.RETURN_INCIDENT, A.LOG])
def return_incidents(ctx, actions):
    """PLAY: Return up to 2 Incident from your hand or Discard pile. Log this card."""
    for n in (1, 2):
        cards = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Incident")]
        card = yield from actions.pick_card(f"Return an Incident ({n} of up to 2)?", cards, optional=True, none_label="Stop")
        if not card:
            break
        yield from actions.return_incident(card)
    yield from actions.log(ctx.this_card)

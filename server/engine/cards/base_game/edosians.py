"""1ALL05 Edosians (Ally). Spec: resources/scans/base_game/cards/ally/1ALL05.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck

from ._util import draw_two_discard_one

operation("1ALL05", 0, uses=[A.DRAW, A.DISCARD])(draw_two_discard_one)


@operation("1ALL05", 1, uses=[A.PUT, A.TAKE_ENCOUNTER, A.LOG], cost=[PutOnDeck(3)],
           requires=lambda ctx: ctx.track("influence") >= 5)
def archive(ctx, actions):
    """PLAY: Requires [Influence] 5. Put 3 cards on the top of your deck to look at the top 2 Encounter. Take one of
    them and return the other to the bottom of its deck. Log this card."""
    yield from actions.take_encounter(look=2)
    yield from actions.log(ctx.this_card)

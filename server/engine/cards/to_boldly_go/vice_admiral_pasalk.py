"""2PER26 Vice Admiral Pasalk (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER26.md
The attack PLAY and the SPECIAL that blocks the opponent's Reactions arrive in Step 4."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


@operation("2PER26", 1, uses=[A.DISCARD, A.DRAW])
def refit(ctx, actions):
    """RESUPPLY: You may discard a card to draw a card. Repeat this for each Ongoing you have in play.
    Rulebook example: with 1 Ongoing in play it may happen up to 2 times."""
    times = 1 + ctx.count_in_play(lambda i: has_trait(i, "Ongoing"))
    for n in range(1, times + 1):
        if not others_in_hand(ctx) or not (yield from actions.may(f"Discard a card to draw a card ({n} of {times})?")):
            break
        yield from actions.discard(1)
        yield from actions.draw(1)

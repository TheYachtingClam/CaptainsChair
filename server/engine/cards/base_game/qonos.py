"""1KOL20 Qo'noS (Location). Spec: resources/scans/base_game/cards/captains/koloth/1KOL20.md"""

from engine.cards import operation
from engine.ops import A

from ._util import others_in_hand, take_control_of_this

operation("1KOL20", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1KOL20", 1, uses=[A.GAIN_SPECIALTY])
def high_council(ctx, actions):
    """CONTROL: Gain 1 [Influence]."""
    yield from actions.gain_specialty("influence", 1)


@operation("1KOL20", 2, uses=[A.DRAW, A.SPEND, A.DISCARD])
def great_hall(ctx, actions):
    """ACTIVATION: If you have an [Away Team] here, draw a card. If you have 3+ total [Away Team] on 1 or more
    controlled Location, draw a card. You may pay 2 [Dilithium] and discard a card to draw a card."""
    n = int(ctx.away_at(ctx.this_card) > 0) + int(sum(ctx.away_at(loc) for loc in ctx.controlled_locations()) >= 3)
    if n:
        yield from actions.draw(n)
    if actions.can_spend(dilithium=2) and others_in_hand(ctx) and (
            yield from actions.may("Pay 2 Dilithium and discard a card to draw a card?")):
        yield from actions.spend(dilithium=2)
        yield from actions.discard(1)
        yield from actions.draw(1)

"""2REB01 Rebner (Captain). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB01.md"""

from engine.cards import endgame, hand_size_modifier, operation
from engine.ops import A, Spend, card

from ._util import is_helmet, owned_cards


@hand_size_modifier("2REB01")
def hand_size_is_three(state, owner, size):
    """PASSIVE: Your hand size is 3 (REQ-CD-REB-01)."""
    return 3


@operation("2REB01", 1, uses=[A.DRAW], requires=lambda ctx: not ctx.me.hand)
def empty_handed(ctx, actions):
    """ACTIVATION: If your hand is empty, draw 2 cards."""
    yield from actions.draw(2)


@operation("2REB01", 2, uses=[A.DRAW], cost=[Spend(latinum=1)])
def buy_cards(ctx, actions):
    """ACTIVATION: Spend 1 [Latinum] to draw 2 cards."""
    yield from actions.draw(2)


@endgame("2REB01")
def collector(state, player):
    """ENDGAME: Score 1 [VP] for every 2 of your Cargo cards, excluding cards with Helmet."""
    return sum(1 for i in owned_cards(player) if card(i).suit == "Cargo" and not is_helmet(i)) // 2

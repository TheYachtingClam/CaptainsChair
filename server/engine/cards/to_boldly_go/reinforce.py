"""2DIR02 Reinforce (Directive, solo campaign only). Spec: resources/scans/to_boldly_go/cards/2DIR02.md"""

from engine.cards import operation
from engine.ops import A


@operation("2DIR02", 0, uses=[A.TAKE_FROM_REINFORCEMENT], requires=lambda ctx: bool(ctx.me.reinforcement))
def reinforce(ctx, actions):
    """PLAY: Take a card from your Reinforcement pile."""
    yield from actions.take_from_reinforcement()


@operation("2DIR02", 1, uses=[A.DRAW, A.LOG], requires=lambda ctx: not ctx.me.reinforcement)
def stand_by(ctx, actions):
    """PLAY: If your Reinforcement pile is empty, draw a card, then log this card."""
    yield from actions.draw(1)
    yield from actions.log(ctx.this_card)

"""1SEL19 Remus (Location). Spec: resources/scans/base_game/cards/captains/sela/1SEL19.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


@operation("1SEL19", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this card."""
    yield from actions.take_control(ctx.this_card)


@operation("1SEL19", 1, uses=[A.ATTACK, A.FORCE, A.DISCARD])
def dilithium_mines(ctx, actions):
    """ATTACK CONTROL: Force your opponent to discard a card."""
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(1, player=ctx.opponent)


@operation("1SEL19", 2, uses=[A.GAIN_RESOURCE, A.DISCARD])
def slave_labour(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]. You may discard a Reman to gain an additional 2 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)
    reman = lambda i: has_trait(i, "Reman")  # noqa: E731
    if others_in_hand(ctx, reman) and (yield from actions.may("Discard a Reman to gain 2 more Dilithium?")):
        yield from actions.discard(1, pred=reman, label="a Reman")
        yield from actions.gain_resource("dilithium", 2)

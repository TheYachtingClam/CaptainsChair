"""1PIC16 Diplomacy (Directive). Spec: resources/scans/base_game/cards/captains/picard/1PIC16.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import draw_two_discard_one


@operation("1PIC16", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_SPECIALTY], cost=[Spend(dilithium=1)])
def negotiate(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to draw 2 cards and discard one of them, and gain 1 [Influence]."""
    yield from draw_two_discard_one(ctx, actions)
    yield from actions.gain_specialty("influence", 1)


@operation("1PIC16", 1, uses=[A.GAIN_CARD, A.LOG])
def treaty(ctx, actions):
    """PLAY: Gain an Ally and log this card."""
    yield from actions.gain_card(["Ally"], label="an Ally")
    yield from actions.log(ctx.this_card)

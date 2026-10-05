"""3FRE19 Douglas Station (Location). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE19.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("3FRE19", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("3FRE19", 1, uses=[A.GAIN_CARD, A.LOG])
def recruitment(ctx, actions):
    """CONTROL: You may gain a Person. You may log a card from your hand or Discard pile."""
    if (yield from actions.may("Gain a Person?")):
        yield from actions.gain_card(["Person"], label="a Person")
    card = yield from actions.pick_card("Log a card from your hand or Discard pile?", ctx.me.hand + ctx.me.discard,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)


@operation("3FRE19", 2, uses=[A.DRAW, A.GAIN_RESOURCE])
def shore_leave(ctx, actions):
    """ACTIVATION: If you have an [Away Team] here, draw a card. If you have 4+ Lower Decker in play, draw a card and
    gain 1 [Dilithium]."""
    if ctx.away_at(ctx.this_card):
        yield from actions.draw(1)
    if count_traits(ctx, "Lower Decker") >= 4:
        yield from actions.draw(1)
        yield from actions.gain_resource("dilithium", 1)

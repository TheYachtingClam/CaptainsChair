"""3PIK07 Rigel VII (Location, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

development_cost("3PIK07", Spend(dilithium=2, latinum=2))


@operation("3PIK07", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("3PIK07", 1, uses=[A.DRAW, A.BEAM])
def fortress(ctx, actions):
    """CONTROL: Draw a card. You may beam a card here from your hand or Discard pile."""
    yield from actions.draw(1)
    card = yield from actions.pick_card("Beam a card to Rigel VII?", ctx.me.hand + ctx.me.discard, optional=True,
                                        none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)


@operation("3PIK07", 2, uses=[A.BEAM, A.GAIN_RESOURCE])
def trade_post(ctx, actions):
    """CLEAN-UP: You may beam a card here from your hand or Staging Area. Gain 1 [Dilithium] for each card beamed
    here."""
    card = yield from actions.pick_card("Beam a card to Rigel VII?", ctx.me.hand + ctx.me.staging, optional=True,
                                        none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)
    if ctx.this_card.beamed:
        yield from actions.gain_resource("dilithium", len(ctx.this_card.beamed))


@operation("3PIK07", 3, uses=[A.DRAW, A.LOG, A.GAIN_RESOURCE])
def archive(ctx, actions):
    """ACTIVATION: Draw a card. Log all cards beamed here. For every 2 cards logged this way, gain 1 [Glory]."""
    yield from actions.draw(1)
    logged = 0
    for card in list(ctx.this_card.beamed):
        yield from actions.log(card)
        logged += 1
    if logged // 2:
        yield from actions.gain_resource("glory", logged // 2)

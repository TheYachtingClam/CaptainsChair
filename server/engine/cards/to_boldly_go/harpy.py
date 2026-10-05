"""2REB07 Harpy (Ship, Development). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import is_helmet, warp_this_ship

development_cost("2REB07", Spend(latinum=2))


@operation("2REB07", 0, uses=[A.DEPLOY, A.GAIN_SPECIALTY])
def launch(ctx, actions):
    """PLAY: Deploy this ship. Gain 1 [Military] for each [Military] you have in play (excluding beamed cards)."""
    yield from actions.deploy(ctx.this_card)
    n = sum(ctx.skills(i).count("Military") for i in ctx.in_play(beamed=False))
    if n:
        yield from actions.gain_specialty("military", n)


operation("2REB07", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)


@operation("2REB07", 2, uses=[A.DISCARD, A.DISMISS, A.PUT],
           cost=[DiscardFromHand(1, lambda ctx, i: is_helmet(i), "a Helmet")])
def refit(ctx, actions):
    """ACTIVATION: Discard a Helmet to dismiss this ship, then put this card on the top of your deck."""
    yield from actions.dismiss(ctx.this_card)
    if ctx.this_card in ctx.me.discard:
        yield from actions.put_on_deck(ctx.this_card)

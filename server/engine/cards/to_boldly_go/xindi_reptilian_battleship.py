"""2SHI13 Xindi-Reptillian Battleship (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, count_traits, has_trait, warp_this_ship


@operation("2SHI13", 0, uses=[A.DEPLOY, A.GAIN_CARD, A.BEAM, A.GAIN_RESOURCE])
def deploy_and_arm(ctx, actions):
    """PLAY: Deploy this ship. You may gain a Cargo. If the gained card is Weapon, beam it here and gain 1 [Glory]."""
    yield from actions.deploy(ctx.this_card)
    cargo = yield from actions.gain_card(["Cargo"], label="a Cargo", optional=True)
    if cargo and has_trait(cargo, "Weapon"):
        yield from actions.beam(cargo, ctx.this_card)
        yield from actions.gain_resource("glory", 1)


@operation("2SHI13", 1, uses=[A.DEPLOY, A.GAIN_RESOURCE])
def deploy_for_time_travel(ctx, actions):
    """PLAY: Deploy this ship. Gain 1 [Glory] per Time Travel you have in play (max 3)."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.gain_resource("glory", min(3, count_traits(ctx, "Time Travel")))


@operation("2SHI13", 2, uses=[A.DRAW])
def anomalies(ctx, actions):
    """RESUPPLY: Draw a card for every 2 Anomaly you have in play (max 4 cards)."""
    n = min(4, count_traits(ctx, "Anomaly") // 2)
    if n:
        yield from actions.draw(n)


operation("2SHI13", 3, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI13", 4, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

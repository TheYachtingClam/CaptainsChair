"""2SHI06 Kazon Raider (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI06.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, others_in_hand, warp_this_ship

operation("2SHI06", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI06", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("2SHI06", 3, uses=[A.DRAW, A.REFRESH], cost=[Spend(latinum=1)],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat and ev.get("to") == "top")
def raid(ctx, actions):
    """REACTION: After gaining a card to the top of your deck, spend 1 [Latinum] to draw a card and refresh this
    card."""
    yield from actions.draw(1)
    yield from actions.refresh(ctx.this_card)


@operation("2SHI06", 0, uses=[A.DEPLOY, A.ATTACK, A.FORCE, A.DISCARD, A.GAIN_RESOURCE])
def pillage(ctx, actions):
    """ATTACK PLAY: Deploy this ship. Force your opponent to discard a card. You may discard a card to gain 1
    [Latinum]."""
    yield from actions.deploy(ctx.this_card)
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(1, player=ctx.opponent)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to gain 1 Latinum?")):
        yield from actions.discard(1)
        yield from actions.gain_resource("latinum", 1)

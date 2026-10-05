"""2SHI06 Kazon Raider (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI06.md
The attack PLAY arrives in Step 4."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship

operation("2SHI06", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI06", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("2SHI06", 3, uses=[A.DRAW, A.REFRESH], cost=[Spend(latinum=1)],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat and ev.get("to") == "top")
def raid(ctx, actions):
    """REACTION: After gaining a card to the top of your deck, spend 1 [Latinum] to draw a card and refresh this
    card."""
    yield from actions.draw(1)
    yield from actions.refresh(ctx.this_card)

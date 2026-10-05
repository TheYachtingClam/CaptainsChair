"""2REB02 Mondor (Ship). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB02.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, is_suit, warp_this_ship
from .uss_shenzhou import promote


@operation("2REB02", 0, uses=[A.DEPLOY, A.GAIN_CARD, A.GAIN_SPECIALTY])
def launch(ctx, actions):
    """PLAY: Deploy this ship. You may gain a Cargo from the Junk. If the gained card is Weapon / Anomaly, gain 1
    [Military]."""
    yield from actions.deploy(ctx.this_card)
    gained = yield from actions.gain_card(["Cargo"], label="a Cargo from the Junk", only_junk=True, optional=True)
    if gained is not None and has_trait(gained, "Weapon", "Anomaly"):
        yield from actions.gain_specialty("military", 1)


operation("2REB02", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2REB02", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("2REB02", 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)

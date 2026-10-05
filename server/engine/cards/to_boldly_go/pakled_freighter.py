"""2SHI08 Pakled Freighter (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI08.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, warp_this_ship


@operation("2SHI08", 0, uses=[A.DEPLOY, A.GAIN_CARD, A.GAIN_SPECIALTY])
def deploy_and_salvage(ctx, actions):
    """PLAY: Deploy this ship. You may gain a Cargo from the Junk. If the gained card is Weapon/Anomaly, gain 1
    [Military]."""
    yield from actions.deploy(ctx.this_card)
    cargo = yield from actions.gain_card(["Cargo"], label="a Cargo from the Junk", only_junk=True, optional=True)
    if cargo and has_trait(cargo, "Weapon", "Anomaly"):
        yield from actions.gain_specialty("military", 1)


operation("2SHI08", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI08", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

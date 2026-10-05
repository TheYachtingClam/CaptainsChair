"""2SHI10 U.S.S. Pasteur (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI10.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, warp_this_ship


@operation("2SHI10", 0, uses=[A.DEPLOY, A.FREE_PLAY])
def deploy_and_play(ctx, actions):
    """PLAY: Deploy this ship. You may free play a Communication/Doctor."""
    yield from actions.deploy(ctx.this_card)
    cards = actions.free_play_candidates(lambda i: has_trait(i, "Communication", "Doctor"))
    card = yield from actions.pick_card("Free play a Communication or Doctor?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("2SHI10", 1, uses=[A.SCAN_FOR], cost=[Spend(dilithium=2)])
def scan_specialist(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to scan for either Communication, Doctor, Engineer, or Scientist."""
    trait = yield from actions.choose("Scan for which trait?", [(t, t) for t in ("Communication", "Doctor", "Engineer", "Scientist")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")


operation("2SHI10", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI10", 3, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

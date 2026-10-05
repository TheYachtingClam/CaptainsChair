"""2SHI12 Xindi-Aquatic Cruiser (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI12.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, others_in_hand


@operation("2SHI12", 0, uses=[A.DEPLOY, A.DISCARD, A.BEAM])
def deploy_and_beam(ctx, actions):
    """PLAY: Deploy this ship. You may discard a card to beam a card here."""
    yield from actions.deploy(ctx.this_card)
    if len(others_in_hand(ctx)) >= 2 and (yield from actions.may("Discard a card to beam a card here?")):
        yield from actions.discard(1)
        yield from beam_a_card_here(ctx, actions)


@operation("2SHI12", 1, uses=[A.WARP, A.FREE_PLAY], cost=[Spend(dilithium=2)])
def warp_and_play(ctx, actions):
    """ACTIVATION: Spend 2 [Dilithium] to warp this ship. You may free play a card beamed here."""
    ship = ctx.this_card
    yield from actions.warp(ship)
    cards = actions.free_play_candidates(lambda i: True, cards=list(ship.beamed))
    card = yield from actions.pick_card("Free play a card beamed here?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


operation("2SHI12", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

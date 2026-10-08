"""1SHI08 Son'a Battlecruiser (Ship). Spec: resources/scans/base_game/cards/ships/1SHI08.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship


@operation("1SHI08", 0, uses=[A.DEPLOY, A.ATTACK, A.STEAL])
def harvest(ctx, actions):
    """ATTACK PLAY: Deploy this ship. Steal 1 [Dilithium]."""
    yield from actions.deploy(ctx.this_card)
    if (yield from actions.attack()):
        yield from actions.steal("dilithium", 1)


@operation("1SHI08", 1, uses=[A.DEPLOY, A.ATTACK, A.STEAL, A.FORCE, A.DISCARD],
           requires=lambda ctx: ctx.track("military") >= 6)
def subjugate(ctx, actions):
    """ATTACK PLAY: Requires [Military] 6. Deploy this ship. Steal 2 [Dilithium]. Your opponent discards a card."""
    yield from actions.deploy(ctx.this_card)
    if (yield from actions.attack()):
        yield from actions.steal("dilithium", 2)
        if ctx.opponent is not None:
            yield from actions.discard(1, player=ctx.opponent)


operation("1SHI08", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SHI08", 3, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

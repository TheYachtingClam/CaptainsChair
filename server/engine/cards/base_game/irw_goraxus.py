"""1SEL02 I.R.W. Goraxus (Ship), and Sela's other Warbirds with the same operations: I.R.W. Khazara (1SEL17) and
I.R.W. Terix (1SEL23); I.R.W. Valdore (1SEL03) shares the PLAY. Spec: resources/scans/base_game/cards/captains/sela/1SEL02.md"""

from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, people_in_hand, warp_this_ship

WARBIRDS = ("1SEL02", "1SEL17", "1SEL23")


@operation((*WARBIRDS, "1SEL03"), 0, uses=[A.DEPLOY, A.SEND_AWAY_TEAM])
def decloak(ctx, actions):
    """PLAY: Deploy this ship. You may send an [Away Team] to a Location, ignoring any opponent Ship."""
    yield from actions.deploy(ctx.this_card)
    if actions.away_targets(ignore_ships=True) and (
            yield from actions.may("Send an Away Team to a Location, ignoring any opponent Ship?")):
        yield from actions.send_away_team(1, ignore_ships=True)


operation(WARBIRDS, 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation(WARBIRDS, 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("1SEL02", 3, uses=[A.PROMOTE], requires=lambda ctx: bool(people_in_hand(ctx)))(promote)

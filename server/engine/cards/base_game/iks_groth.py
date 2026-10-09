"""1KOL02 I.K.S. Gr'oth (Ship), and I.K.S. Klothos (1KOL24), which prints the same first four operations.
Spec: resources/scans/base_game/cards/captains/koloth/1KOL02.md, 1KOL24.md"""

from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, people_in_hand, send_team_here, warp_this_ship

IDS = ("1KOL02", "1KOL24")


@operation(IDS, 0, uses=[A.DEPLOY])
def launch(ctx, actions):
    """PLAY: Deploy this ship."""
    yield from actions.deploy(ctx.this_card)


operation(IDS, 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation(IDS, 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation(IDS, 3, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.location_of(ctx.this_card) is not None)(send_team_here)
operation("1KOL02", 4, uses=[A.PROMOTE], requires=lambda ctx: bool(people_in_hand(ctx)))(promote)

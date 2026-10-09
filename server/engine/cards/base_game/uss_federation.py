"""1BUR04 U.S.S. Federation (Ship, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR04.md"""

from engine.cards import development_cost, endgame, operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, Spend, SpendUnless, card

from ._util import owned_cards, people_in_hand

VANCE = "1BUR05"

development_cost("1BUR04", SpendUnless(Spend(dilithium=6), lambda ctx: any(i.card == VANCE for i in ctx.me.duty)))


@operation("1BUR04", 0, uses=[A.DEPLOY, A.SPEND, A.WARP])
def headquarters(ctx, actions):
    """PLAY: Deploy this ship. You may spend 1 [Dilithium] to warp this ship."""
    yield from actions.deploy(ctx.this_card)
    if actions.can_spend(dilithium=1) and actions.can_warp(ctx.this_card) and (
            yield from actions.may("Spend 1 Dilithium to warp this ship?")):
        yield from actions.spend(dilithium=1)
        yield from actions.warp(ctx.this_card)


operation("1BUR04", 1, uses=[A.PROMOTE], requires=lambda ctx: bool(people_in_hand(ctx)))(promote)


@endgame("1BUR04")
def member_worlds(state, player):
    """ENDGAME: Score 1 [VP] for each of your cards with [Influence Focus]/[Military Focus]."""
    return sum(1 for i in owned_cards(player) if card(i).focus in ("Influence", "Military"))

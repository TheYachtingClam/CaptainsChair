"""1SIS15 U.S.S. Defiant (Ship). Spec: resources/scans/base_game/cards/captains/sisko/1SIS15.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship


@operation("1SIS15", 0, uses=[A.DEPLOY, A.WARP, A.ATTACK, A.FORCE, A.DISCARD])
def ambush(ctx, actions):
    """ATTACK PLAY: Deploy and warp this ship. If the opponent has at least one Ship at the U.S.S. Defiant's Location,
    force them to discard 2 cards."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    if ship in ctx.me.fleet:
        yield from actions.warp(ship)
    opp = ctx.opponent
    loc = ctx.location_of(ctx.this_card)
    if opp is None or loc is None or not ctx.ships_at(loc, opp):
        return
    if (yield from actions.attack()):
        yield from actions.discard(2, player=opp)


@operation("1SIS15", 1, uses=[A.DEPLOY, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("influence") >= 5)
def cloaked_insertion(ctx, actions):
    """PLAY: Requires [Influence] 5. Deploy this ship. You may send an [Away Team] to a Location, ignoring any
    opponent Ship."""
    yield from actions.deploy(ctx.this_card)
    if actions.away_targets(ignore_ships=True) and (
            yield from actions.may("Send an Away Team to a Location, ignoring any opponent Ship?")):
        yield from actions.send_away_team(1, ignore_ships=True)


operation("1SIS15", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SIS15", 3, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

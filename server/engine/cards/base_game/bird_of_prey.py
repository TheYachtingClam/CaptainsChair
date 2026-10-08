"""1SHI01 Bird-of-Prey (Ship). Spec: resources/scans/base_game/cards/ships/1SHI01.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, opponent_ships, others_in_hand


@operation("1SHI01", 0, uses=[A.DEPLOY, A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def decloak(ctx, actions):
    """PLAY: Deploy this ship. You may discard a card to send an [Away Team] to a Location, ignoring any opponent
    Ship. If the discarded card is Imperial, gain 1 [Glory]."""
    yield from actions.deploy(ctx.this_card)
    if others_in_hand(ctx) and actions.away_targets(ignore_ships=True) and (
            yield from actions.may("Discard a card to send an Away Team, ignoring any opponent Ship?")):
        discarded = yield from actions.discard(1)
        yield from actions.send_away_team(1, ignore_ships=True)
        if discarded and has_trait(discarded[0], "Imperial"):
            yield from actions.gain_resource("glory", 1)


@operation("1SHI01", 1, uses=[A.WARP, A.SPEND, A.ATTACK, A.FORCE, A.RECALL])
def strike(ctx, actions):
    """ATTACK ACTIVATION: Warp this ship. You may spend 1 [Dilithium] to force your opponent to recall a Ship."""
    yield from actions.warp(ctx.this_card)
    opp = ctx.opponent
    if not actions.can_spend(dilithium=1) or not (yield from actions.may("Spend 1 Dilithium to make your opponent "
                                                                         "recall a Ship?")):
        return
    yield from actions.spend(dilithium=1)
    if not (yield from actions.attack()) or opp is None:
        return
    theirs = opponent_ships(ctx)
    ship = yield from actions.pick_card("Bird-of-Prey: recall one of your Ships.", theirs, seat=opp.seat)
    if ship:
        yield from actions.recall(ship)


operation("1SHI01", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

"""2REB06 Jackabog's Clumpship (Ship, Development) and its identical copy 2REB11 The Clumpship Pakled.
Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, is_suit, warp_this_ship

IDS = ("2REB06", "2REB11")
development_cost("2REB06", Spend(dilithium=3, latinum=1))


def _opponent_ships(ctx):
    opp = ctx.opponent
    if opp is None:
        return 1 if ctx.virtual_opponent else 0  # the virtual opponent has one of everything (REQ-CTM-12)
    return ctx.count_in_play(lambda i: is_suit(i, "Ship"), opp)


@operation(IDS, 0, uses=[A.DEPLOY, A.DRAW, A.REVEAL, A.LOG, A.ATTACK, A.FORCE])
def ram(ctx, actions):
    """ATTACK PLAY: Deploy this ship. For each Ship your opponent has in play, draw and reveal a card. You may log a
    drawn card with Weapon to force your opponent to log a Ship from their hand, Discard pile, or in play."""
    yield from actions.deploy(ctx.this_card)
    n = _opponent_ships(ctx)
    if not n:
        return
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(n)
    drawn = [i for i in ctx.me.hand if i.uid not in before]
    if drawn:
        yield from actions.reveal(drawn)
    weapons = [i for i in drawn if has_trait(i, "Weapon")]
    weapon = yield from actions.pick_card("Log a drawn Weapon to make your opponent log a Ship?", weapons,
                                          optional=True, none_label="No")
    if not weapon:
        return
    yield from actions.log(weapon)
    opp = ctx.opponent
    if opp is not None and (yield from actions.attack()):
        ships = [i for i in ([] if opp.bot is not None else opp.hand + opp.discard) + ctx.in_play(opp)
                 if is_suit(i, "Ship")]  # the Bot never chooses from its Discard pile (REQ-SOLO-190)
        ship = yield from actions.pick_card("Log one of your Ships (Clumpship).", ships, seat=opp.seat)
        if ship:
            yield from actions.log(ship)


operation(IDS, 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation(IDS, 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)

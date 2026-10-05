"""2KIRK06 U.S.S. Excelsior (Ship, Development). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend, SpendUnless

from ._util import beam_a_card_here, can_discard_then_beam, opponent_ships, warp_this_ship

development_cost("2KIRK06", SpendUnless(Spend(dilithium=6), lambda ctx: any(i.card == "2KIRK07" for i in ctx.me.duty)))


@operation("2KIRK06", 0, uses=[A.DEPLOY, A.ATTACK, A.TAKE_INCIDENT, A.FIND])
def great_experiment(ctx, actions):
    """ATTACK PLAY: Deploy this ship. If the opponent has at least one Ship at a neutral Location, they take an
    Incident. You may find Set a Course."""
    yield from actions.deploy(ctx.this_card)
    neutral = {loc.uid for loc in ctx.state.neutral}
    if any(s.at in neutral for s in opponent_ships(ctx)) and (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    if (yield from actions.may("Find Set a Course?")):
        yield from actions.find(lambda i: ctx.name(i) == "Set a Course", "Set a Course", optional=True)


operation("2KIRK06", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2KIRK06", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("2KIRK06", 3, uses=[A.RECALL], cost=[Spend(dilithium=1)])
def return_to_spacedock(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to recall this ship (with its beamed cards), so its attack can be played
    again."""
    yield from actions.recall(ctx.this_card)

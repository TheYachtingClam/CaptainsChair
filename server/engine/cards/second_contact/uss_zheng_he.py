"""3RIK06 U.S.S. Zheng He (Ship, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship

development_cost("3RIK06", Spend(dilithium=5))


def _opponent_at_neutral(ctx):
    opp = ctx.opponent
    return opp is not None and any(s.at in {loc.uid for loc in ctx.state.neutral} for s in opp.fleet)


@operation("3RIK06", 0, uses=[A.DEPLOY, A.ATTACK, A.TAKE_INCIDENT, A.REFRESH])
def time_ship(ctx, actions):
    """ATTACK PLAY: Deploy this ship. If the opponent has at least one Ship at a neutral Location, they take an
    Incident. Refresh your Captain. Cadet: the virtual opponent has no Ships at neutral Locations (REQ-CTM-12)."""
    yield from actions.deploy(ctx.this_card)
    if _opponent_at_neutral(ctx) and (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    if ctx.me.captain.exhausted:
        yield from actions.refresh(ctx.me.captain)


operation("3RIK06", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("3RIK06", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("3RIK06", 3, uses=[A.RECALL], cost=[Spend(dilithium=1)])
def return_to_future(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to recall this ship."""
    yield from actions.recall(ctx.this_card)

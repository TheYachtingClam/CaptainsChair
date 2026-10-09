"""0SHI01 U.S.S. Enterprise-B (Ship, promo). Spec: resources/scans/promo1/cards/ships/0SHI01.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, EffectCost, Spend

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, warp_this_ship

TUESDAY = 1


@operation("0SHI01", 0, uses=[A.DISCARD, A.DEPLOY, A.GAIN_RESOURCE, A.SEND_AWAY_TEAM], cost=[DiscardFromHand(1)])
def maiden_voyage(ctx, actions):
    """PLAY: Discard a card to deploy this ship and gain 1 [Glory]. If it is a Tuesday, you may send an [Away Team] to
    a Location. Ruling: the real weekday when this PLAY was chosen (REQ-CORE-53)."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.gain_resource("glory", 1)
    if ctx.weekday() == TUESDAY and actions.away_targets() and (
            yield from actions.may("It is Tuesday. Send an Away Team to a Location?")):
        yield from actions.send_away_team(1)


operation("0SHI01", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("0SHI01", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


def _people(ctx):
    return [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person")]


def _log_a_person(ctx, actions):
    person = yield from actions.pick_card("Log which Person from your hand or Staging Area (cost)?", _people(ctx))
    yield from actions.log(person)


@operation("0SHI01", 3, uses=[A.LOG, A.DRAW, A.GAIN_ACTION],
           cost=[EffectCost(lambda ctx: bool(_people(ctx)), _log_a_person, (A.LOG,),
                            "log a Person from your hand or Staging Area")])
def nexus(ctx, actions):
    """ACTIVATION: Log a Person from your hand or your Staging Area to draw a card and gain an [Action]."""
    yield from actions.draw(1)
    yield from actions.gain_action(1)

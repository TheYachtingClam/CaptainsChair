"""1SHI12 Voth Research Vessel (Ship). Spec: resources/scans/base_game/cards/ships/1SHI12.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, EffectCost

from ._util import beam_a_card_here, can_discard_then_beam, deploy_and_warp_this, has_trait, is_suit, warp_this_ship

operation("1SHI12", 0, uses=[A.DISCARD, A.DEPLOY, A.WARP], cost=[DiscardFromHand(1)])(deploy_and_warp_this)
operation("1SHI12", 1, uses=[A.WARP])(warp_this_ship)
operation("1SHI12", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


def _humans_here(ctx):
    return [b for b in ctx.this_card.beamed if is_suit(b, "Person") and has_trait(b, "Human")]


def _dismiss_a_human(ctx, actions):
    human = yield from actions.pick_card("Dismiss which Human beamed here (cost)?", _humans_here(ctx))
    yield from actions.dismiss(human)


@operation("1SHI12", 3, uses=[A.DISMISS, A.TAKE_ENCOUNTER, A.LOG],
           cost=[EffectCost(lambda ctx: bool(_humans_here(ctx)), _dismiss_a_human, (A.DISMISS,),
                            "dismiss a Human Person beamed here")])
def distant_origin(ctx, actions):
    """ACTIVATION: Dismiss a Person with Human that is beamed here to take the top Encounter card. Log this card."""
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)

"""1LOC07 Deep Space K-7 (Location). Spec: resources/scans/base_game/cards/location/1LOC07.md"""

from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import has_trait, is_suit, no_effect, others_in_hand

operation("1LOC07", 0, uses=[])(no_effect)


def _orders(ctx):
    return others_in_hand(ctx, lambda i: is_suit(i, "Directive") or has_trait(i, "Security"))


def _file_orders(ctx, actions):
    card = yield from actions.pick_card("Put which Directive or Security on top of your deck (cost)?", _orders(ctx))
    yield from actions.put_on_deck(card)


@operation("1LOC07", 1, uses=[A.PUT, A.GAIN_ACTION],
           cost=[EffectCost(lambda ctx: bool(_orders(ctx)), _file_orders, (A.PUT,),
                            "put a Directive or a Security on top of your deck")])
def station_business(ctx, actions):
    """ACTIVATION: Put a Directive or a Security on the top of your deck to gain an [Action]."""
    yield from actions.gain_action(1)

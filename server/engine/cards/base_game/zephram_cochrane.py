"""1PER25 Zephram Cochrane (Person). Spec: resources/scans/base_game/cards/person/1PER25.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, Spend

from ._util import is_suit, others_in_hand


def _ships_in_hand(ctx):
    return others_in_hand(ctx, lambda i: is_suit(i, "Ship"))


def _stage_a_ship(ctx, actions):
    ship = yield from actions.pick_card("Put which Ship into your Staging Area (its PLAY does not resolve)?",
                                        _ships_in_hand(ctx))
    yield from actions.put_into_staging(ship)


@operation("1PER25", 0, uses=[A.DRAW])
def inspiration(ctx, actions):
    """PLAY: Draw 3 cards."""
    yield from actions.draw(3)


@operation("1PER25", 1, uses=[A.PUT, A.TAKE_ENCOUNTER, A.LOG],
           cost=[EffectCost(lambda ctx: bool(_ships_in_hand(ctx)), _stage_a_ship, (A.PUT,),
                            "put a Ship into your Staging Area"), Spend(dilithium=3)])
def first_flight(ctx, actions):
    """ACTIVATION: Put a Ship in your Staging Area (without triggering its play operation) and spend 3 [Dilithium] to
    take the top Encounter and log this card."""
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)

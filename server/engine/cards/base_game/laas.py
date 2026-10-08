"""1PER10 Laas (Person). Spec: resources/scans/base_game/cards/person/1PER10.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, Spend

from ._util import is_suit, people_in_hand


def _stage_a_person(ctx, actions):
    person = yield from actions.pick_card("Put which Person into your Staging Area (its PLAY does not resolve)?",
                                          people_in_hand(ctx))
    yield from actions.put_into_staging(person)


@operation("1PER10", 0, uses=[A.PUT, A.DUPLICATE],
           cost=[EffectCost(lambda ctx: bool(people_in_hand(ctx)), _stage_a_person, (A.PUT,),
                            "put a Person into your Staging Area")])
def mimic(ctx, actions):
    """PLAY: Put a Person into your Staging Area (without triggering their play operation) to duplicate a play
    operation of a Person or Cargo from the Market or your Discard pile."""
    market = [i for i in ctx.state.market.values() if i is not None]
    cards = [i for i in market + ctx.me.discard if is_suit(i, "Person", "Cargo")]
    yield from actions.duplicate(cards, label="a Person or Cargo in the Market or your Discard pile", optional=False)


@operation("1PER10", 1, uses=[A.FIND], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(ctx.me.draw))
def seek(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to find a card in your Draw deck."""
    yield from actions.find(lambda i: True, "a card in your Draw deck", zones_=("draw",))

"""1PIC05 Phasing Cloak (Cargo, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC05.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, EffectCost, Spend

from ._util import is_suit


def _people(ctx):
    me = ctx.me
    return [i for i in me.hand + me.draw + me.discard + me.reserve if is_suit(i, "Person")]


def _find_and_log_a_person(ctx, actions):
    person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person, to log it")
    if person is not None:
        yield from actions.log(person)


development_cost("1PIC05", Spend(dilithium=2), EffectCost(lambda ctx: bool(_people(ctx)), _find_and_log_a_person,
                                                          (A.FIND, A.LOG), "find a Person and log it"))
# PASSIVE: You ignore all opponent Ship when sending [Away Team] to a neutral Location.
registry.IGNORE_OPPONENT_SHIPS.add("1PIC05")


@operation("1PIC05", 0, uses=[A.DEPLOY, A.JUNK])
def install(ctx, actions):
    """PLAY: Deploy this card. Junk a card from the Market."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.junk()


@operation("1PIC05", 1, uses=[A.FREE_PLAY],
           requires=lambda ctx: any(is_suit(i, "Ship") for i in ctx.me.hand))
def phase(ctx, actions):
    """ACTIVATION: Free play a Ship."""
    ship = yield from actions.pick_card("Free play which Ship?", actions.free_play_candidates(lambda i: is_suit(i, "Ship")))
    if ship:
        yield from actions.free_play(ship)

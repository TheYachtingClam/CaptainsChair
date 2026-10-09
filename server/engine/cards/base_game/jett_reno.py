"""1BUR07 Jett Reno (Person, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DismissFromPlay, TakeIncidentCost

from ._util import is_suit

development_cost("1BUR07", DismissFromPlay(lambda ctx, i: i in ctx.me.fleet and is_suit(i, "Ship"), "a deployed Ship"))


@operation("1BUR07", 0, uses=[A.GAIN_RESOURCE])
def salvage(ctx, actions):
    """PLAY: Gain 3 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 3)


@operation("1BUR07", 1, uses=[A.MOVE_RESOURCES])
def refine(ctx, actions):
    """PLAY: Recrystallize 2 [Dilithium]."""
    yield from actions.recrystallize(2)


@operation("1BUR07", 2, uses=[A.TAKE_INCIDENT, A.GAIN_CARD, A.DISCARD], cost=[TakeIncidentCost()])
def duct_tape(ctx, actions):
    """ACTIVATION: Take an Incident to gain a Cargo or a Ship and discard the gained card."""
    gained = yield from actions.gain_card(["Cargo", "Ship"], label="a Cargo or a Ship")
    if gained is not None and any(i.uid == gained.uid for i in ctx.me.draw):
        yield from actions.discard_from_deck(gained)

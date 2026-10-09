"""1BUR17 Recover (Directive). Spec: resources/scans/base_game/cards/captains/burnham/1BUR17.md"""

from engine.cards import operation
from engine.ops import A, Spend, TakeIncidentCost


@operation("1BUR17", 0, uses=[A.TAKE_INCIDENT, A.GAIN_CARD], cost=[TakeIncidentCost()])
def salvage_a_ship(ctx, actions):
    """PLAY: Take an Incident to gain a Ship from the Junk."""
    yield from actions.gain_card(["Ship"], label="a Ship from the Junk", only_junk=True)


@operation("1BUR17", 1, uses=[A.GAIN_CARD], cost=[Spend(latinum=1)])
def buy_cargo(ctx, actions):
    """PLAY: Spend 1 [Latinum] to gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")

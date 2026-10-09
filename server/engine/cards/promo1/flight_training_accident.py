"""0INC01 Flight Training Accident (Incident, promo). Spec: resources/scans/promo1/cards/incident/0INC01.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import count_traits, is_suit

registry.REPLACES_AN_INCIDENT.add("0INC01")  # SPECIAL: during setup, replace a random Incident with this card


def _ships(ctx):
    me = ctx.me
    return [i for i in me.hand + me.draw + me.discard + me.reserve if is_suit(i, "Ship")]


def _find_and_log_a_ship(ctx, actions):
    ship, _ = yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship, to log it")
    if ship is not None:
        yield from actions.log(ship)


@operation("0INC01", 0, uses=[A.FIND, A.LOG, A.RETURN_INCIDENT, A.GAIN_ACTION],
           cost=[EffectCost(lambda ctx: bool(_ships(ctx)), _find_and_log_a_ship, (A.FIND, A.LOG),
                            "find a Ship and log it")])
def inquiry(ctx, actions):
    """PLAY: Find and log a Ship to return this card. If you have 1+ Person on duty, gain an [Action]."""
    yield from actions.return_incident(ctx.this_card)
    if ctx.me.duty:
        yield from actions.gain_action(1)


@operation("0INC01", 1, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE], requires=lambda ctx: count_traits(ctx, "Pilot") > 0)
def ace(ctx, actions):
    """PLAY: If you have a Pilot in play, return this card and gain 1 [Glory]."""
    yield from actions.return_incident(ctx.this_card)
    yield from actions.gain_resource("glory", 1)


@operation("0INC01", 2, uses=[A.GAIN_RESOURCE, A.RESOLVE_CARD, A.RETURN_INCIDENT])
def surprise(ctx, actions):
    """SURPRISE (Bot only): Gain 1 [Glory], then resolve the top card of the Bot deck. Return this card.
    Runs with the Bot as "me" (REQ-SOLO-87)."""
    yield from actions.gain_resource("glory", 1)
    yield from actions.resolve_bot_top()
    yield from actions.return_incident(ctx.this_card)

"""0INC02 Whale Probe Incursion (Incident, promo). Spec: resources/scans/promo1/cards/incident/0INC02.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import count_traits, opponent_ships, ships

registry.REPLACES_AN_INCIDENT.add("0INC02")  # SPECIAL: during setup, replace a random Incident with this card


@operation("0INC02", 0, uses=[A.RECALL, A.ATTACK, A.FORCE, A.RETURN_INCIDENT])
def probe(ctx, actions):
    """ATTACK PLAY: Recall a deployed Ship, if able. Force your opponent to recall a deployed Ship. If you have a
    Creature in play, return this card."""
    mine = yield from actions.pick_card("Recall which of your Ships?", ships(ctx))
    if mine:
        yield from actions.recall(mine)
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        theirs = yield from actions.pick_card("Whale Probe Incursion: recall one of your Ships.", opponent_ships(ctx),
                                              seat=opp.seat)
        if theirs:
            yield from actions.recall(theirs)
    if count_traits(ctx, "Creature"):
        yield from actions.return_incident(ctx.this_card)


@operation("0INC02", 1, uses=[A.ATTACK, A.FORCE, A.RECALL, A.RETURN_INCIDENT])
def surprise(ctx, actions):
    """SURPRISE (Bot only): You must recall a Ship, if able. Return this card. Runs with the Bot as "me"
    (REQ-SOLO-87); "you" is the human."""
    human = ctx.opponent
    if (yield from actions.attack()) and human is not None:
        ship = yield from actions.pick_card("Whale Probe Incursion: recall one of your Ships.", opponent_ships(ctx),
                                            seat=human.seat)
        if ship:
            yield from actions.recall(ship)
    yield from actions.return_incident(ctx.this_card)

"""2GEO01 Philippa Georgiou (Captain). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO01.md"""

from engine.cards import endgame, operation
from engine.ops import A, RemoveOwnAwayTeam

from ._util import table_of


@operation("2GEO01", 0, uses=[A.RETURN_INCIDENT], cost=[RemoveOwnAwayTeam()],
           requires=lambda ctx: bool(ctx.hand_incidents()))
def return_an_incident(ctx, actions):
    """ACTIVATION: Remove an Away Team from a Location to return an Incident."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents())
    yield from actions.return_incident(incident)


@endgame("2GEO01")
def one_per_three_in_play(state, player):
    """ENDGAME: Score 1 VP for every 3 cards you have in play."""
    from engine.ops import _all_beamed

    cards = table_of(player)
    return (len(cards) + sum(len(_all_beamed(i)) for i in cards)) // 3

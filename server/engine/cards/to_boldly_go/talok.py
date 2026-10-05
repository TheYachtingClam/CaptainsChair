"""2PER21 Talok (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER21.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A, RemoveOwnAwayTeam

from ._util import count_traits


@hand_size_modifier("2PER21")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1


@operation("2PER21", 0, uses=[A.REMOVE_AWAY_TEAM, A.SCAN, A.ATTACK, A.TAKE_INCIDENT, A.GAIN_RESOURCE],
           cost=[RemoveOwnAwayTeam()])
def tal_shiar(ctx, actions):
    """ATTACK PLAY: Remove one of your [Away Team] from a Location to scan 1 of Person. Your opponent takes an
    Incident. If you have 2 or more Imperial in play, gain 2 [Glory]."""
    yield from actions.scan(1, ["Person"])
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    if count_traits(ctx, "Imperial") >= 2:
        yield from actions.gain_resource("glory", 2)

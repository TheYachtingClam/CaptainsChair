"""1BUR02 Inert Dilithium (Status). Spec: resources/scans/base_game/cards/captains/burnham/1BUR02.md"""

from engine import cards as registry
from engine.cards import hand_size_modifier


@hand_size_modifier("1BUR02")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1


# PASSIVE: Any [Dilithium] you gain, except from the Market must be placed on this card, unavailable to be spent. If an
# effect allows you to recrystallize [Dilithium], move it from here to your supply (actions.recrystallize).
registry.HOLDS_GAINS["1BUR02"] = "dilithium"
# PASSIVE: You cannot spend [Glory] as [Dilithium].
registry.NO_GLORY_AS_DILITHIUM.add("1BUR02")

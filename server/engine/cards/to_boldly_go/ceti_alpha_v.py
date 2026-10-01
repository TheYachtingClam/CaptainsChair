"""2KHA02A Ceti Alpha V (Location). PASSIVE: Increase your hand size by 1. Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA02A.md"""

from engine.cards import hand_size_modifier


@hand_size_modifier("2KHA02A")
def plus_one(state, owner, size):
    return size + 1

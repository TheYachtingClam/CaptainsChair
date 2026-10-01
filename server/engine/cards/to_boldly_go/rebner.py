"""2REB01 Rebner (Captain). PASSIVE: Your hand size is 3. Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB01.md"""

from engine.cards import hand_size_modifier


@hand_size_modifier("2REB01")
def hand_size_is_three(state, owner, size):
    return 3

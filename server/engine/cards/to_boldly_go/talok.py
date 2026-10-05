"""2PER21 Talok (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER21.md
The attack PLAY arrives in Step 4."""

from engine.cards import hand_size_modifier


@hand_size_modifier("2PER21")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1

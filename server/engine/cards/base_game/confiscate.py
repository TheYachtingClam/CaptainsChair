"""1SHR17 Confiscate (Directive), and the copies in Koloth's and Sela's decks (1KOL15, 1SEL09). Spec: resources/scans/base_game/cards/captains/shran/1SHR17.md"""

from engine.cards import operation
from engine.ops import A, Spend


@operation("1SHR17", 0, uses=[A.GAIN_CARD], cost=[Spend(dilithium=4)])
def seize_a_ship(ctx, actions):
    """PLAY: Spend 4 [Dilithium] to gain a Ship."""
    yield from actions.gain_card(["Ship"], label="a Ship")


@operation("1SHR17", 1, uses=[A.GAIN_CARD], cost=[Spend(dilithium=2)])
def seize_cargo(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")


@operation("1SHR17", 2, uses=[A.GAIN_RESOURCE])
def levy(ctx, actions):
    """PLAY: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)

"""Archer's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/archer.md"""

from engine.ops import A, Spend
from engine.upgrades import boost, own, reinforce

CREW = "archer"


@boost(CREW, "win", 0, moment="after_hand", uses=[A.ENLIST_RESERVE])
def enlist_a_reserve(ctx, actions):
    """BOOST: After drawing the starting hand, enlist a Reserve."""
    yield from actions.enlist_reserve()


@boost(CREW, "win", 1, moment="after_hand", uses=[A.SCAN_FOR], cost=[Spend(dilithium=1)])
def scan_nx01_dilithium(ctx, actions):
    """BOOST: After drawing the starting hand, spend 1 [Dilithium] to scan for NX-01."""
    yield from actions.scan_for(lambda i: ctx.has(i, "NX-01"), "an NX-01 card")


@boost(CREW, "loss", 0, moment="after_hand", uses=[A.SCAN_FOR], cost=[Spend(glory=1)])
def scan_nx01_glory(ctx, actions):
    """BOOST: After drawing the starting hand, spend 1 [Glory] to scan for NX-01."""
    yield from actions.scan_for(lambda i: ctx.has(i, "NX-01"), "an NX-01 card")


@reinforce(CREW, "loss", 1)
def a_reserve_card(cards):
    """REINFORCE: A non-Incident card from your Reserve deck."""
    return [own(cards, "Reserve", pred=lambda c: c.suit != "Incident")]

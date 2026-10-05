"""2SOV03 Vulcan (Location). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV03.md"""

from engine.cards import duty_slots, operation
from engine.ops import A

from .vulcan_science_academy import draw

operation("2SOV03", 0, uses=[A.DRAW])(draw)  # same printed Activation as the Vulcan Science Academy


@duty_slots("2SOV03")
def vulcan_officer(state, owner, inst):
    """PASSIVE: You may have an additional Person with Vulcan on duty."""
    return ["Vulcan"]

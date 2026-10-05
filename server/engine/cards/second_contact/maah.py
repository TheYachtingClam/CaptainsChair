"""3PER12 Ma'ah (Person). Spec: resources/scans/second_contact/cards/person/3PER12.md
The SUPPORT arrives in Step 7."""

from engine.cards import operation
from engine.ops import A, DismissDutyOfficer, LogFromHand

from ._util import has_trait


@operation("3PER12", 0, uses=[A.DISMISS, A.GAIN_SPECIALTY, A.GAIN_RESOURCE], cost=[DismissDutyOfficer()])
def challenge(ctx, actions):
    """PLAY: Dismiss a Duty Officer to gain 1 [Influence], 1 [Military], and 1 [Glory]."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_resource("glory", 1)


@operation("3PER12", 2, uses=[A.LOG, A.GAIN_SPECIALTY, A.DRAW],
           cost=[LogFromHand(lambda ctx, i: has_trait(i, "Klingon", "Shady", "Lower Decker"),
                             "a Klingon, Shady or Lower Decker", ("hand", "discard"))])
def honour(ctx, actions):
    """ACTIVATION: Log a Klingon / Shady / Lower Decker from your hand or Discard pile to gain 1 [Influence] and draw
    2 cards."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.draw(2)

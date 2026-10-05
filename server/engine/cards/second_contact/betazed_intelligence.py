"""3ALL01 Betazed Intelligence (Ally). Spec: resources/scans/second_contact/cards/ally/3ALL01.md
The CLEAN-UP (temporary hand size) arrives in Step 5."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("3ALL01", 0, uses=[A.FIND])
def intelligence(ctx, actions):
    """PLAY: Find a Beverage/Ambassador/Telepath, except in your Reserve deck."""
    yield from actions.find(lambda i: has_trait(i, "Beverage", "Ambassador", "Telepath"),
                            "a Beverage, Ambassador or Telepath", exclude_reserve=True)

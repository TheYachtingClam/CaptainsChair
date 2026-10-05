"""3ALL01 Betazed Intelligence (Ally). Spec: resources/scans/second_contact/cards/ally/3ALL01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import distinct_traits, has_trait


@operation("3ALL01", 0, uses=[A.FIND])
def intelligence(ctx, actions):
    """PLAY: Find a Beverage/Ambassador/Telepath, except in your Reserve deck."""
    yield from actions.find(lambda i: has_trait(i, "Beverage", "Ambassador", "Telepath"),
                            "a Beverage, Ambassador or Telepath", exclude_reserve=True)


@operation("3ALL01", 1, uses=[A.ADJUST_HAND_SIZE, A.LOG])
def briefing(ctx, actions):
    """CLEAN-UP: Temporarily increase your hand size by 1 for each different one of Starfleet / Beverage / Ambassador
    you have in play. If this increased your hand size by 2 or 3, log this card.
    Ruling: Clean-up operations run before Discard & Draw, so it applies to this turn's draw."""
    n = distinct_traits(ctx.in_play(), ("Starfleet", "Beverage", "Ambassador"))
    if n:
        yield from actions.adjust_hand_size(n)
    if n >= 2:
        yield from actions.log(ctx.this_card)

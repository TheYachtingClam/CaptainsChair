"""3FRE06 Strange New Worlds: Freeman's copy is a Development. Its PLAY is registered with the other copies in
engine/cards/to_boldly_go/strange_new_worlds.py. Spec: resources/scans/second_contact/cards/captains/freeman/3FRE06.md"""

from engine.cards import development_cost
from engine.ops import A, EffectCost

from ._util import has_trait


def _findable(ctx):
    me = ctx.me
    return [i for i in me.hand + me.draw + me.discard + me.reserve if has_trait(i, "Starfleet")]


def _log_two_starfleet(ctx, actions):
    """Find 2 Starfleet and log both."""
    for n in (1, 2):
        card, _ = yield from actions.find(lambda i: has_trait(i, "Starfleet"), f"a Starfleet ({n} of 2)")
        if card is not None:
            yield from actions.log(card)


development_cost("3FRE06", EffectCost(lambda ctx: len(_findable(ctx)) >= 2, _log_two_starfleet, (A.FIND, A.LOG),
                                      "find 2 Starfleet and log both"))

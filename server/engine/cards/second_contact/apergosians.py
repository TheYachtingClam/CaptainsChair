"""3FRE04 Apergosians (Ally, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit

development_cost("3FRE04", Spend(latinum=3))


@operation("3FRE04", 0, uses=[A.FIND, A.DUPLICATE, A.LOG, A.GAIN_RESOURCE])
def energy_beings(ctx, actions):
    """PLAY: Find a Person/Cargo. Duplicate one of the found card's play operations up to two times, ignoring any
    effect that would log this card. Then, log the found card. Gain 2 [Glory]. Log this card."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Person", "Cargo"), "a Person or Cargo")
    if found is not None:
        for n in (1, 2):
            if n == 2 and not (yield from actions.may(f"Duplicate a PLAY of {ctx.name(found)} again?")):
                break
            done = yield from actions.duplicate([found], label=ctx.name(found), skip_log_self=True)
            if done is None:
                break
        yield from actions.log(found)
    yield from actions.gain_resource("glory", 2)
    yield from actions.log(ctx.this_card)

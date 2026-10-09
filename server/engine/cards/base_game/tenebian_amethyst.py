"""1SHR06 Tenebian Amethyst (Cargo, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit

development_cost("1SHR06", Spend(dilithium=1, latinum=1))


@operation("1SHR06", 0, uses=[A.GAIN_RESOURCE, A.LOG])
def gift(ctx, actions):
    """PLAY: Gain 2 [Latinum]. You may log a Person from your hand or Discard pile to log this card."""
    yield from actions.gain_resource("latinum", 2)
    this = ctx.this_card
    people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person") and i.uid != this.uid]
    person = yield from actions.pick_card("Log a Person from your hand or Discard pile to log this card?", people,
                                          optional=True, none_label="No")
    if person:
        yield from actions.log(person)
        yield from actions.log(this)


@operation("1SHR06", 1, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("uid") == ctx.ref.uid)
def treasured(ctx, actions):
    """SPECIAL: When you log this card (via any effect), gain 3 [Glory]."""
    yield from actions.gain_resource("glory", 3)

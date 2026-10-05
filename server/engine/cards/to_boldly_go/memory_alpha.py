"""2LOC15 Memory Alpha (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC15.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2LOC15", 0, uses=[A.LOG, A.DUPLICATE])
def archive(ctx, actions):
    """CONTROL: You may log a card. You may duplicate a play operation of a Person / Cargo / Ally / Directive from your
    Log."""
    card = yield from actions.pick_card("Log a card from your hand?", list(ctx.me.hand), optional=True, none_label="No")
    if card:
        yield from actions.log(card)
    logged = [i for i in ctx.me.log if is_suit(i, "Person", "Cargo", "Ally", "Directive")]
    if logged:
        yield from actions.duplicate(logged, label="a Person, Cargo, Ally or Directive in your Log")


@operation("2LOC15", 1, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("by") == ctx.me.seat)
def records(ctx, actions):
    """REACTION: After logging a card, gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)

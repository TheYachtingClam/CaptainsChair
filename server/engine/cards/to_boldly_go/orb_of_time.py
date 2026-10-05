"""2CAR13 Orb of Time (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("2CAR13", 0, uses=[A.TAKE_INCIDENT, A.DUPLICATE, A.RECALL])
def vision(ctx, actions):
    """PLAY: You may take an Incident to duplicate a play operation of a Person/Cargo/Ally from your Log. You may
    recall a non-Time Travel card from your Staging Area.
    Rulings: duplicating a self-logging card logs the Orb (KW-DUP-04); when itself duplicated, only the recall
    happens (KW-DUP-05)."""
    logged = [i for i in ctx.me.log if is_suit(i, "Person", "Cargo", "Ally")]
    if logged and ctx.state.incident and not actions.in_duplicate and (
            yield from actions.may("Take an Incident to duplicate a PLAY operation from your Log?")):
        yield from actions.take_incident()
        yield from actions.duplicate(logged, label="a Person, Cargo or Ally in your Log", optional=False)
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel") and i is not ctx.this_card]
    card = yield from actions.pick_card("Recall a non-Time Travel card from your Staging Area?", cards,
                                        optional=True, none_label="No")
    if card:
        yield from actions.recall(card)

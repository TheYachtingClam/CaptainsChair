"""2LOC20 Xahea (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC20.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import no_effect
from ._util import is_suit

operation("2LOC20", 0, uses=[])(no_effect)


@operation("2LOC20", 1, uses=[A.GAIN_RESOURCE])
def dilithium(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@operation("2LOC20", 2, uses=[A.PUT, A.DUPLICATE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev.get("played") and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.name(ctx.event_card) == "Utilize"
           and any(is_suit(i, "Person") for i in ctx.me.hand))
def queen(ctx, actions):
    """REACTION: After playing Utilize, you may put a Person on the top of your deck to duplicate Utilize's other play
    operation."""
    utilize = ctx.event_card
    person = yield from actions.pick_card("Put which Person on top of your deck?",
                                          [i for i in ctx.me.hand if is_suit(i, "Person")])
    yield from actions.put_on_deck(person)
    played = ctx.event.get("index")
    others = [i for i, op in enumerate(ctx.card(utilize).operations) if op.kind == "PLAY" and i != played]
    yield from actions.duplicate([utilize], label="Utilize", optional=False, indexes=others)

"""2LOC09 Risa (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC09.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import beamed_here
from ._util import is_suit


@operation("2LOC09", 0, uses=[A.FIND, A.BEAM])
def shore_leave(ctx, actions):
    """CONTROL: Find up to 3 Person, except in your Reserve deck, and beam them here."""
    for n in (1, 2, 3):
        person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), f"a Person ({n} of up to 3)",
                                            exclude_reserve=True, optional=True)
        if not person:
            break
        yield from actions.beam(person, ctx.this_card)


@operation("2LOC09", 1, uses=[A.BEAM], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))
def vacation(ctx, actions):
    """ACTIVATION: Beam a Person here."""
    person = yield from actions.pick_card("Beam which Person to Risa?", [i for i in ctx.me.hand if is_suit(i, "Person")])
    yield from actions.beam(person, ctx.this_card)


@operation("2LOC09", 2, uses=[A.RECALL, A.GAIN_RESOURCE], requires=lambda ctx: bool(beamed_here(ctx)))
def return_home(ctx, actions):
    """ACTIVATION: Recall a card beamed here to gain 1 [Latinum]."""
    card = yield from actions.pick_card("Recall which card from Risa?", beamed_here(ctx))
    yield from actions.recall(card)
    yield from actions.gain_resource("latinum", 1)

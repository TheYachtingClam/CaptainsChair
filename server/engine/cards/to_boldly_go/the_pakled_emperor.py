"""2REB08 The Pakled Emperor (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit, wearing

development_cost("2REB08", Spend(latinum=2))


@operation("2REB08", 0, uses=[A.FIND, A.FREE_PLAY])
def decree(ctx, actions):
    """PLAY: Find any card. You may free play an Incident."""
    yield from actions.find(lambda i: True, "any card")
    card = yield from actions.pick_card("Free play an Incident?",
                                        actions.free_play_candidates(lambda i: is_suit(i, "Incident")),
                                        optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("2REB08", 1, uses=[A.TAKE_ENCOUNTER, A.LOG], cost=[Spend(dilithium=4)],
           requires=lambda ctx: wearing(ctx.this_card, "2REB03"))
def coronation(ctx, actions):
    """ACTIVATION: If The Pakled Emperor is wearing the Big Enough Helmet, spend 4 [Dilithium] to take the top
    Encounter. Log this card (along with the Helmet)."""
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)

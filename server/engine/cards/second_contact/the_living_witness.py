"""3PER08 The Living Witness (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER08.md"""

from engine.cards import endgame, operation
from engine.ops import A

from ._util import count_traits, is_suit, table_of


@operation("3PER08", 0, uses=[A.DRAW, A.FREE_PLAY, A.LOG, A.FIND, A.RETURN_INCIDENT])
def testimony(ctx, actions):
    """PLAY: Draw a card. You may free play an Incident. If you have an Ancient in play, log this card and you may
    (additionally) find and return an Incident."""
    yield from actions.draw(1)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
    if count_traits(ctx, "Ancient"):
        yield from actions.log(ctx.this_card)
        if (yield from actions.may("Find an Incident and return it?")):
            found, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident", optional=True)
            if found:
                yield from actions.return_incident(found)


@endgame("3PER08")
def witness(state, player):
    """ENDGAME: Score 4 [VP] (only while in play at game end)."""
    return 4 if any(i.card == "3PER08" for i in table_of(player)) else 0

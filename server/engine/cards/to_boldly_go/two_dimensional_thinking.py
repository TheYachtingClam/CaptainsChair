"""2KHA22 Two Dimensional Thinking (Incident, in the common Incident deck). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA22.md
Its SURPRISE operation (index 1) is for the Bot and waits for the Khan Bot."""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, is_suit, opponent_ships


@operation("2KHA22", 0, uses=[A.DRAW_FROM_DISCARD, A.WARP, A.FREE_PLAY, A.RETURN_INCIDENT, A.FORCE])
def pattern(ctx, actions):
    """PLAY: Draw a card from your Discard pile. Your opponent may warp a Ship. If you have no Augment in play, you
    may free play an Incident. Return this card."""
    yield from actions.draw_from_discard()
    opp = ctx.opponent
    theirs = [s for s in opponent_ships(ctx) if actions.can_warp(s)]
    if opp is not None and theirs:
        ship = yield from actions.pick_card("Two Dimensional Thinking: warp one of your Ships?", theirs, optional=True,
                                            seat=opp.seat, none_label="No")
        if ship is not None:
            yield from actions.warp(ship, by=opp)
    if not count_traits(ctx, "Augment"):
        this = ctx.this_card
        incidents = [i for i in actions.free_play_candidates(lambda i: is_suit(i, "Incident")) if i.uid != this.uid]
        incident = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
        if incident is not None:
            yield from actions.free_play(incident)
    yield from actions.return_incident(ctx.this_card)

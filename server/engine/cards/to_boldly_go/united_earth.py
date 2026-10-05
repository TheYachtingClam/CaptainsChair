"""2SOV22 United Earth (Ally). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV22.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import has_trait


@operation("2SOV22", 0, uses=[A.SCAN_FOR, A.LOG])
def embassy(ctx, actions):
    """PLAY: Scan for a Human. Log this card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Human"), "a Human")
    yield from actions.log(ctx.this_card)


@operation("2SOV22", 1, uses=[A.TAKE_INCIDENT, A.SCAN, A.FREE_PLAY, A.LOG], cost=[TakeIncidentCost()])
def coalition(ctx, actions):
    """PLAY: Take an Incident to scan 2 of Ally. You may free play the gained card. If you do, log this card.
    Ruling (spec): the gained card is free played from wherever it landed."""
    ally = yield from actions.scan(2, ["Ally"])
    if ally and actions.free_play_candidates(lambda i: i is ally, cards=[ally]) and (
            yield from actions.may(f"Free play {ctx.name(ally)}?")):
        yield from actions.free_play(ally)
        yield from actions.log(ctx.this_card)

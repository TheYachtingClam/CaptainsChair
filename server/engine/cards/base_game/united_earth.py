"""1SHR13 United Earth (Ally). Spec: resources/scans/base_game/cards/captains/shran/1SHR13.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import has_trait


@operation("1SHR13", 0, uses=[A.SCAN_FOR, A.LOG])
def envoy(ctx, actions):
    """PLAY: Scan for a Human. Log this card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Human"), "a Human")
    yield from actions.log(ctx.this_card)


@operation("1SHR13", 1, uses=[A.TAKE_INCIDENT, A.SCAN, A.FREE_PLAY, A.LOG], cost=[TakeIncidentCost()])
def coalition(ctx, actions):
    """PLAY: Take an Incident to scan 2 of Ally. You may free play the gained card. If you do, log this card."""
    gained = yield from actions.scan(2, ["Ally"])
    if gained is not None and actions.free_play_candidates(lambda i: i.uid == gained.uid, cards=[gained]) and (
            yield from actions.may(f"Free play {ctx.name(gained)}?")):
        yield from actions.free_play(gained)
        yield from actions.log(ctx.this_card)

"""1BUR25 Saru (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR25.md  Not Lt. Saru (Georgiou's deck)."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("1BUR25", 0, uses=[A.TAKE_INCIDENT, A.SCAN_FOR, A.FIND, A.FREE_PLAY])
def diplomacy(ctx, actions):
    """PLAY: You may take an Incident to scan for a Kelpien. Find a Directive. You may free play the found card."""
    if (yield from actions.may("Take an Incident to scan for a Kelpien?")):
        yield from actions.take_incident()
        yield from actions.scan_for(lambda i: has_trait(i, "Kelpien"), "a Kelpien")
    found, _ = yield from actions.find(lambda i: is_suit(i, "Directive"), "a Directive")
    if found and actions.free_play_candidates(lambda i: i.uid == found.uid) and (
            yield from actions.may(f"Free play {ctx.name(found)}?")):
        yield from actions.free_play(found)


@operation("1BUR25", 1, uses=[A.REVEAL, A.GAIN_ACTION], requires=lambda ctx: ctx.track("influence") >= 2)
def counsel(ctx, actions):
    """RESUPPLY: Requires [Influence] 2. Reveal your hand. If you have at least 2 Person in your hand, gain an
    [Action]."""
    yield from actions.reveal(list(ctx.me.hand))
    if sum(1 for i in ctx.me.hand if is_suit(i, "Person")) >= 2:
        yield from actions.gain_action(1)

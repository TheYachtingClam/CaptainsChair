"""2GEO12 Lt. Saru (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO12.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("2GEO12", 0, uses=[A.TAKE_INCIDENT, A.SCAN_FOR, A.FIND, A.FREE_PLAY])
def scan_find_play(ctx, actions):
    """PLAY: You may take an Incident to scan for a Kelpien. Find a Directive. If the card was found in your
    Reserve deck, take an Incident. You may free play the found card."""
    if ctx.state.incident and (yield from actions.may("Take an Incident to scan for a Kelpien?")):
        yield from actions.take_incident()
        yield from actions.scan_for(lambda i: has_trait(i, "Kelpien"), "a Kelpien")
    found, zone = yield from actions.find(lambda i: is_suit(i, "Directive"), "a Directive")
    if found and zone == "reserve":
        yield from actions.take_incident()
    if found and found in actions.free_play_candidates(lambda i: i is found) and (
            yield from actions.may(f"Free play {ctx.name(found)}?")):
        yield from actions.free_play(found)


@operation("2GEO12", 1, uses=[A.REVEAL, A.GAIN_ACTION], requires=lambda ctx: ctx.track("research") >= 3)
def reveal_for_action(ctx, actions):
    """RESUPPLY: Requires Research 3. Reveal your hand. If you have at least 2 Person in your hand, gain an Action."""
    if ctx.track("research") < 3:
        return
    yield from actions.reveal(list(ctx.me.hand))
    if sum(1 for i in ctx.me.hand if is_suit(i, "Person")) >= 2:
        yield from actions.gain_action(1)

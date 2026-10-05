"""2ARC17 Porthos (Cargo). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC17.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, is_suit


@operation("2ARC17", 0, uses=[A.FIND, A.DISCARD, A.REFRESH, A.GAIN_RESOURCE, A.TAKE_INCIDENT])
def good_boy(ctx, actions):
    """PLAY: Find a Person. If the card was found in your Reserve deck, discard it. You may refresh your Captain. If
    you have an Alien in play, you gain 1 [Glory] and both players take an Incident. This is not an Attack."""
    person, zone = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person")
    if person and zone == "reserve":
        yield from actions.discard(1, pred=lambda i: i is person, label=ctx.name(person))
    if ctx.me.captain.exhausted and (yield from actions.may("Refresh your Captain?")):
        yield from actions.refresh(ctx.me.captain)
    if count_traits(ctx, "Alien"):
        yield from actions.gain_resource("glory", 1)
        yield from actions.take_incident()
        yield from actions.take_incident(opponent=True)

"""2CAR18 Universal Translator (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit, ships


@operation("2CAR18", 0, uses=[A.SCAN_FOR],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Starfleet"), "a Starfleet")])
def translate(ctx, actions):
    """PLAY: Discard a Starfleet to scan for an Alien."""
    yield from actions.scan_for(lambda i: has_trait(i, "Alien"), "an Alien")


@operation("2CAR18", 1, uses=[A.TAKE_ENCOUNTER, A.DISCARD, A.DISMISS, A.LOG])
def first_words(ctx, actions):
    """PLAY: If you have 3 non-Encounter cards with Alien in play, take the top Encounter card and discard it.
    Dismiss every Ship with Alien and every beamed Alien. Log this card.
    Rulings: only your own Ships are dismissed; the Encounter goes into your hand, then your Discard pile."""
    aliens = ctx.count_in_play(lambda i: has_trait(i, "Alien") and not is_suit(i, "Encounter"))
    if aliens >= 3:
        encounter = yield from actions.take_encounter()
        if encounter:
            yield from actions.discard(1, pred=lambda i: i is encounter, label=ctx.name(encounter))
        for ship in [s for s in ships(ctx) if has_trait(s, "Alien")]:
            yield from actions.dismiss(ship)
        beamed = [b for host in ctx.in_play(beamed=False) for b in host.beamed if has_trait(b, "Alien")]
        for card in beamed:
            yield from actions.dismiss(card)
    yield from actions.log(ctx.this_card)

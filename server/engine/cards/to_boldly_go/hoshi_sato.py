"""2PER07 Hoshi Sato (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER07.md"""

from engine.cards import operation
from engine.ops import SPECIES, A, DiscardFromHand

from ._util import count_traits, has_trait


@operation("2PER07", 0, uses=[A.FIND])
def linguist(ctx, actions):
    """PLAY: Find a card with [Research]/[Research Focus]."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "research"), "a card with Research")


@operation("2PER07", 1, uses=[A.SCAN_FOR], requires=lambda ctx: ctx.track("research") >= 5,
           cost=[DiscardFromHand(1, lambda ctx, i: ctx.has_specialty_icon(i, "research"), "a card with Research")])
def first_contact(ctx, actions):
    """PLAY: Requires [Research] 5. Discard a card with [Research]/[Research Focus] to scan for Any Species of your
    choice."""
    species = yield from actions.choose("Scan for which Species?", [(s, s) for s in sorted(SPECIES)])
    yield from actions.scan_for(lambda i: has_trait(i, species), f"a {species}")


@operation("2PER07", 2, uses=[A.DRAW, A.FIND, A.PUT])
def translation_matrix(ctx, actions):
    """ACTIVATION: Draw a card for each Alien you have in play (max 3 cards). You may find a card in your Reserve deck
    and put the found card in your Staging Area (without triggering its play operation)."""
    aliens = min(3, count_traits(ctx, "Alien"))
    if aliens:
        yield from actions.draw(aliens)
    if ctx.me.reserve and (yield from actions.may("Find a card in your Reserve deck and put it in your Staging Area?")):
        card, _ = yield from actions.find(lambda i: True, "a card in your Reserve deck", zones_=("reserve",))
        if card:
            yield from actions.put_into_staging(card)

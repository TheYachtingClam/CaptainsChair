"""3PER03 Chancellor Gowron (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER03.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, minus_unless_logged

registry.VP_SPECIAL["3PER03"] = minus_unless_logged(2)  # SPECIAL: If not logged, this card scores -2.


@operation("3PER03", 0, uses=[A.FIND, A.GAIN_RESOURCE, A.SPEND, A.SCAN_FOR])
def high_council(ctx, actions):
    """PLAY: Find a Klingon or a Ship. If the found card is a Ship with Klingon, gain 1 [Glory]. You may spend 3
    [Dilithium] to scan for [Military Focus]."""
    found, _ = yield from actions.find(lambda i: has_trait(i, "Klingon") or is_suit(i, "Ship"), "a Klingon or a Ship")
    if found and is_suit(found, "Ship") and has_trait(found, "Klingon"):
        yield from actions.gain_resource("glory", 1)
    if actions.can_spend(dilithium=3) and (yield from actions.may("Spend 3 Dilithium to scan for a Military Focus card?")):
        yield from actions.spend(dilithium=3)
        yield from actions.scan_for(lambda i: ctx.card(i).focus == "Military", "a card with a Military Focus")


@operation("3PER03", 1, uses=[A.DRAW, A.JUNK, A.DISCARD, A.GAIN_RESOURCE],
           requires=lambda ctx: ctx.track("military") >= 5,
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] == ctx.me.seat
           and ctx.track("military") >= 5)
def conquest(ctx, actions):
    """REACTION: Requires [Military] 5. After taking control of a Location, choose 2 of the following: draw a card OR
    junk a card from the Market OR discard a card to gain 1 [Glory]."""
    remaining = [("draw", "Draw a card"), ("junk", "Junk a card from the Market")] + \
        ([("glory", "Discard a card to gain 1 Glory")] if ctx.me.hand else [])
    for n in (1, 2):
        choice = yield from actions.choose(f"Gowron: choose an option ({n} of 2).", remaining)
        remaining = [o for o in remaining if o[0] != choice]
        if choice == "draw":
            yield from actions.draw(1)
        elif choice == "junk":
            yield from actions.junk()
        else:
            yield from actions.discard(1)
            yield from actions.gain_resource("glory", 1)

"""3PIK21 Lt. Spock (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK21.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, LogFromHand

TRACKS = ("research", "influence", "military")


@operation("3PIK21", 0, uses=[A.LOG, A.GAIN_RESOURCE, A.GAIN_SPECIALTY], cost=[LogFromHand()])
def logic(ctx, actions):
    """PLAY: Log a card from your hand to gain 3 [Dilithium] and gain 1 [Research]/[Influence]/[Military]. If the
    logged card has [Military]/[Military Focus] gain 1 (additional) [Influence]."""
    yield from actions.gain_resource("dilithium", 3)
    track = yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in TRACKS])
    yield from actions.gain_specialty(track, 1)
    if ctx.has_specialty_icon(actions.paid[0], "military"):
        yield from actions.gain_specialty("influence", 1)


@operation("3PIK21", 1, uses=[A.EXHAUST, A.GAIN_RESOURCE, A.DRAW])
def science_officer(ctx, actions):
    """RESUPPLY: If you have more [Research] than [Influence], exhaust this card to either: gain 1 [Glory] OR draw a
    card."""
    if ctx.track("research") <= ctx.track("influence") or ctx.this_card.exhausted:
        return
    choice = yield from actions.choose("Exhaust Lt. Spock to:", [("glory", "Gain 1 Glory"), ("draw", "Draw a card"),
                                                                 ("none", "Don't exhaust him")])
    if choice == "none":
        return
    yield from actions.exhaust(ctx.this_card)
    if choice == "glory":
        yield from actions.gain_resource("glory", 1)
    else:
        yield from actions.draw(1)


@operation("3PIK21", 2, uses=[A.DISCARD, A.FIND],
           cost=[DiscardFromHand(1, lambda ctx, i: ctx.has_specialty_icon(i, "research"), "a card with Research")])
def research(ctx, actions):
    """ACTIVATION: Discard a [Research]/[Research Focus] to find any card, except in your Reserve deck."""
    yield from actions.find(lambda i: True, "any card", exclude_reserve=True)

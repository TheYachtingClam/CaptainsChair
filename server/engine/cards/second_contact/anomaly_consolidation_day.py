"""3FRE21 Anomaly Consolidation Day (Directive). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE21.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("3FRE21", 0, uses=[A.JUNK, A.TAKE_INCIDENT, A.DISCARD, A.GAIN_CARD])
def consolidate(ctx, actions):
    """PLAY: Junk a card from the Market. You may take an Incident. You may discard an Incident to gain a Cargo."""
    yield from actions.junk()
    if ctx.state.incident and (yield from actions.may("Take an Incident?")):
        yield from actions.take_incident()
    if any(is_suit(i, "Incident") for i in ctx.me.hand):
        if (yield from actions.discard(1, pred=lambda i: is_suit(i, "Incident"), label="an Incident to gain a Cargo",
                                       optional=True)):
            yield from actions.gain_card(["Cargo"], label="a Cargo")


@operation("3FRE21", 1, uses=[A.GAIN_RESOURCE, A.DRAW, A.DISCARD],
           trigger=lambda ctx, ev: ev["kind"] == "support_resolved" and ev["seat"] == ctx.me.seat
           and ctx.this_card in ctx.me.staging)
def bonus(ctx, actions):
    """SPECIAL: While this card is in your Staging Area, after resolving a support operation you may either: gain 2
    [Dilithium] OR draw a card and discard a card."""
    choice = yield from actions.choose("Anomaly Consolidation Day: a SUPPORT was resolved.",
                                       [("dilithium", "Gain 2 Dilithium"), ("draw", "Draw a card, then discard a card"),
                                        ("none", "Neither")])
    if choice == "dilithium":
        yield from actions.gain_resource("dilithium", 2)
    elif choice == "draw":
        yield from actions.draw(1)
        yield from actions.discard(1)

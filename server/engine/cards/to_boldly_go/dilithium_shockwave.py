"""2INC01 Dilithium Shockwave (Incident). Spec: resources/scans/to_boldly_go/cards/incident/2INC01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("2INC01", 0, uses=[A.SPEND, A.GAIN_RESOURCE, A.RETURN_INCIDENT])
def shockwave(ctx, actions):
    """PLAY: Spend all your [Dilithium]. Your opponent gains 2 [Dilithium]. Return this card.
    Ruling: "spend all" can be zero and never forces Glory (KW-SPEND-03)."""
    if ctx.me.dilithium:
        yield from actions.spend(dilithium=ctx.me.dilithium)
    if ctx.opponent is not None:
        yield from actions.gain_resource("dilithium", 2, player=ctx.opponent)
    yield from actions.return_incident(ctx.this_card)


@operation("2INC01", 1, uses=[A.RETURN_INCIDENT, A.SPEND, A.GAIN_RESOURCE],
           requires=lambda ctx: count_traits(ctx, "Kelpien") > 0)
def kelpien_calm(ctx, actions):
    """PLAY: If you have a Kelpien in play, return this card, and you may spend 3 [Dilithium] to gain 1 [Glory]."""
    yield from actions.return_incident(ctx.this_card)
    if actions.can_spend(dilithium=3) and (yield from actions.may("Spend 3 Dilithium to gain 1 Glory?")):
        yield from actions.spend(dilithium=3)
        yield from actions.gain_resource("glory", 1)


@operation("2INC01", 2, uses=[A.GAIN_RESOURCE, A.DISCARD, A.RETURN_INCIDENT])
def surprise(ctx, actions):
    """SURPRISE (Bot only): Gain 1 [Glory] and discard the top card of the Bot deck. You gain 2 [Dilithium]. Return
    this card. Runs with the Bot as "me" (REQ-SOLO-87); "you" is the human."""
    yield from actions.gain_resource("glory", 1)
    yield from actions.discard_from_deck()
    if ctx.opponent is not None:
        yield from actions.gain_resource("dilithium", 2, player=ctx.opponent)
    yield from actions.return_incident(ctx.this_card)

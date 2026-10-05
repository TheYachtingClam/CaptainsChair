"""3FRE22 Jack Ransom (Person). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE22.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck

from ._util import has_trait


@operation("3FRE22", 0, uses=[A.DRAW_FROM_DISCARD, A.SPEND, A.SEND_AWAY_TEAM, A.DISCARD, A.TRIGGER_CONTROL])
def first_officer(ctx, actions):
    """PLAY: You may draw a non-Lower Decker card from your Discard pile. Spend 1 [Dilithium] to send an [Away Team] to
    a controlled Location. You may discard a Lower Decker to trigger that card's control operation."""
    yield from actions.draw_from_discard(lambda i: not has_trait(i, "Lower Decker"), "a non-Lower Decker card",
                                         optional=True)
    if not ctx.me.locations or not actions.can_spend(dilithium=1):
        return  # the Dilithium is spent mid-effect; without it the rest is skipped
    yield from actions.spend(dilithium=1)
    loc = yield from actions.send_away_team(1, where=lambda loc: loc in ctx.me.locations)
    if loc is not None and (yield from actions.discard(1, pred=lambda i: has_trait(i, "Lower Decker"),
                                                       label="a Lower Decker to trigger its CONTROL", optional=True)):
        yield from actions.trigger_control(loc)


@operation("3FRE22", 1, uses=[A.PUT, A.GAIN_CARD], cost=[PutOnDeck()])
def scout_talent(ctx, actions):
    """ACTIVATION: Put a card on the top of your deck to gain a Person to your Discard pile."""
    yield from actions.gain_card(["Person"], label="a Person")

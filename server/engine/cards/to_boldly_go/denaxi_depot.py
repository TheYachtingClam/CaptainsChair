"""2LOC06 Denaxi Depot (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC06.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, RemoveOwnAwayTeam, Spend

from ._util import has_trait, is_suit


@operation("2LOC06", 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def dock(ctx, actions):
    """CONTROL: You may discard a card to send an [Away Team] here. If the discarded card is Business, gain 2
    [Latinum]."""
    if ctx.me.hand and (yield from actions.may("Discard a card to send an Away Team to Denaxi Depot?")):
        discarded = yield from actions.discard(1)
        yield from actions.send_away_team(1, target=ctx.this_card)
        if discarded and has_trait(discarded[0], "Business"):
            yield from actions.gain_resource("latinum", 2)


@operation("2LOC06", 1, uses=[A.REMOVE_AWAY_TEAM, A.GAIN_CARD], cost=[RemoveOwnAwayTeam(here=True)])
def shipyard(ctx, actions):
    """ACTIVATION: Remove an [Away Team] from here to gain a Ship."""
    yield from actions.gain_card(["Ship"], label="a Ship")


@operation("2LOC06", 2, uses=[A.DISCARD, A.FIND], cost=[Spend(latinum=1), DiscardFromHand(1)])
def salvage(ctx, actions):
    """ACTIVATION: Spend 1 [Latinum] and discard a card to find a Ship, except in your Reserve deck."""
    yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship", exclude_reserve=True)

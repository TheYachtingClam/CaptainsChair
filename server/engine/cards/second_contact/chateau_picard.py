"""3RIK10 Chateau Picard (Cargo). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK10.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, is_suit


@operation("3RIK10", 0, uses=[A.GAIN_CARD, A.JUNK],
           cost=[Spend(latinum=1), DiscardFromHand(1, lambda ctx, i: is_suit(i, "Directive"), "a Directive")])
def vintage(ctx, actions):
    """PLAY: Spend 1 [Latinum] and discard a Directive to gain an Ally, including from the Junk. Junk a card from the
    Market."""
    yield from actions.gain_card(["Ally"], label="an Ally", from_junk=True)
    yield from actions.junk()


@operation("3RIK10", 1, uses=[A.DISCARD, A.RETURN_INCIDENT],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Starfleet"), "a Starfleet")],
           requires=lambda ctx: bool(ctx.hand_incidents("discard")))
def toast(ctx, actions):
    """PLAY: Discard a Starfleet to return an Incident from your hand or Discard pile."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    if incident:
        yield from actions.return_incident(incident)


@operation("3RIK10", 2, uses=[A.GAIN_RESOURCE])
def a_fine_year(ctx, actions):
    """CLEAN-UP: Gain 1 [Glory] from the supply for each Beverage you have in play (max 3, excluding this card). Then,
    your opponent does the same for each Beverage they have in play (max 5). Cadet: the virtual opponent's Glory does
    not matter, so only you gain."""
    mine = min(3, ctx.count_in_play(lambda i: i is not ctx.this_card and has_trait(i, "Beverage")))
    if mine:
        yield from actions.gain_resource("glory", mine, supply=True)
    opp = ctx.opponent
    if opp is not None:
        theirs = min(5, ctx.count_in_play(lambda i: has_trait(i, "Beverage"), opp))
        if theirs:
            yield from actions.gain_resource("glory", theirs, player=opp, supply=True)

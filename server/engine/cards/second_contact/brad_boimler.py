"""3RIK14 Brad Boimler, Lt. jg (Person). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK14.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

from ._util import is_suit

BOIMLERS = ("3RIK14", "3FRE23")  # Freeman's Bradward Boimler prints the same PLAY and SUPPORT


@operation(BOIMLERS, 0, uses=[A.SPEND, A.DRAW, A.FREE_PLAY])
def overachiever(ctx, actions):
    """PLAY: Spend all your remaining [Action] (possibly none). For each [Action] spent this way, draw a card; then
    draw one additional card. Free play one of the drawn cards."""
    spent = ctx.me.actions
    if spent:
        yield from actions.spend(actions=spent)
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(spent + 1)
    drawn = [i for i in ctx.me.hand if i.uid not in before]
    card = yield from actions.pick_card("Free play which drawn card?", actions.free_play_candidates(lambda i: True,
                                                                                                    cards=drawn))
    if card:
        yield from actions.free_play(card)


@operation(BOIMLERS, 1, uses=[A.DUPLICATE],
           trigger=lambda ctx, ev: ev["kind"] == "promote" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def by_the_book(ctx, actions):
    """SUPPORT: After promoting a Person, duplicate a play operation of that card."""
    yield from actions.duplicate([ctx.event_card], label=ctx.name(ctx.event_card), optional=False)


@operation("3RIK14", 2, uses=[A.DISCARD, A.TAKE_INCIDENT, A.ENLIST_DEVELOPMENT],
           cost=[DiscardFromHand(1, lambda ctx, i: "Research" in ctx.skills(i), "a card with Research"),
                 TakeIncidentCost()])
def study(ctx, actions):
    """ACTIVATION: Discard a card with [Research] and take an Incident to enlist a Development."""
    yield from actions.enlist_development()

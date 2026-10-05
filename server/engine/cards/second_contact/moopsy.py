"""3CAR02 Moopsy (Cargo). Spec: resources/scans/second_contact/cards/cargo/3CAR02.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit


@operation("3CAR02", 1, uses=[A.REFRESH, A.LOG])
def feed(ctx, actions):
    """RESUPPLY: Refresh this card. You may log a Person from play. Refresh this card."""
    yield from actions.refresh(ctx.this_card)
    people = [i for i in ctx.in_play() if is_suit(i, "Person") and i is not ctx.me.captain]
    person = yield from actions.pick_card("Log one of your Persons in play?", people, optional=True, none_label="No")
    if person:
        yield from actions.log(person)
    yield from actions.refresh(ctx.this_card)


@operation("3CAR02", 2, uses=[A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def snack(ctx, actions):
    """REACTION: After you or your opponent logs a Person, draw a card."""
    yield from actions.draw(1)


@operation("3CAR02", 0, uses=[A.DEPLOY, A.ATTACK, A.FORCE, A.LOG], cost=[Spend(latinum=1)])
def hungry(ctx, actions):
    """ATTACK PLAY: Spend 1 [Latinum] to deploy this card. Force your opponent to log a Person from their hand,
    Discard pile, or in play."""
    yield from actions.deploy(ctx.this_card)
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        people = [i for i in ([] if opp.bot is not None else opp.hand + opp.discard) + ctx.in_play(opp)
                 if is_suit(i, "Person")]  # the Bot never chooses from its Discard pile (REQ-SOLO-190)
        person = yield from actions.pick_card("Moopsy: log one of your Persons (hand, Discard pile or play).", people,
                                              seat=opp.seat)
        if person:
            yield from actions.log(person)

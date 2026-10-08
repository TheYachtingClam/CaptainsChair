"""1PER14 Lwaxana Troi (Person). Spec: resources/scans/base_game/cards/person/1PER14.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit


@operation("1PER14", 0, uses=[A.REFRESH])
def encourage(ctx, actions):
    """PLAY: Refresh your Captain or your Duty Officer."""
    cards = [i for i in [ctx.me.captain, *ctx.me.duty] if i.exhausted]
    card = yield from actions.pick_card("Refresh your Captain or a Duty Officer?", cards)
    if card:
        yield from actions.refresh(card)


@operation("1PER14", 1, uses=[A.GAIN_SPECIALTY], cost=[Spend(latinum=1)])
def reception(ctx, actions):
    """PLAY: Spend 1 [Latinum] to gain 2 [Influence]."""
    yield from actions.gain_specialty("influence", 2)


@operation("1PER14", 2, uses=[A.DRAW], requires=lambda ctx: ctx.track("influence") >= 6,
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.track("influence") >= 6 and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def daughter_of_the_fifth_house(ctx, actions):
    """REACTION: Requires [Influence] 6. After putting a Person into play, draw a card."""
    yield from actions.draw(1)

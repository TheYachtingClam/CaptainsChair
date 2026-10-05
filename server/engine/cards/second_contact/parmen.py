"""3PER13 Parmen (Person). Spec: resources/scans/second_contact/cards/person/3PER13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


@operation("3PER13", 1, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_SPECIALTY], cost=[DiscardFromHand(1)])
def platonian(ctx, actions):
    """PLAY: Discard a card to gain 1 [Latinum] and 1 [Influence]."""
    yield from actions.gain_resource("latinum", 1)
    yield from actions.gain_specialty("influence", 1)


@operation("3PER13", 2, uses=[A.DISCARD, A.FREE_PLAY], cost=[DiscardFromHand(1)],
           requires=lambda ctx: ctx.track("influence") >= 6,
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat and ctx.state.step != "resupply"
           and ctx.event_card is not None and is_suit(ctx.event_card, "Person") and ctx.track("influence") >= 6)
def compel(ctx, actions):
    """REACTION: Requires [Influence] 6. After gaining a Person, except during your Resupply Step, discard a card to
    free play the gained card."""
    gained = ctx.event_card
    if gained is not None and actions.free_play_candidates(lambda i: i is gained, cards=[gained]):
        yield from actions.free_play(gained)


@operation("3PER13", 0, uses=[A.FIND, A.ATTACK, A.EXHAUST])
def mind_control(ctx, actions):
    """ATTACK PLAY: Find any card in your Draw deck. Exhaust an opponent Duty Officer and their Captain."""
    yield from actions.find(lambda i: True, "any card in your Draw deck", zones_=("draw",))
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        officer = yield from actions.pick_card("Exhaust which opponent Duty Officer?",
                                               [i for i in opp.duty if not i.exhausted])
        if officer:
            yield from actions.exhaust(officer)
        if not opp.captain.exhausted:
            yield from actions.exhaust(opp.captain)

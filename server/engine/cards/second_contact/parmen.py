"""3PER13 Parmen (Person). Spec: resources/scans/second_contact/cards/person/3PER13.md
The attack PLAY arrives in Step 4."""

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

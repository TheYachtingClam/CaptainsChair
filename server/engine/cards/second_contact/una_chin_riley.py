"""3PIK13 Una "Number One" Chin-Riley (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, has_trait, is_suit


@operation("3PIK13", 0, uses=[A.DISCARD, A.GAIN_CARD, A.FREE_PLAY, A.TAKE_INCIDENT],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Starfleet"), "a Starfleet")])
def first_officer(ctx, actions):
    """PLAY: Discard a Starfleet to gain a Ship. You may discard a card to free play the gained card. Then, if you
    have no other Augment in play, take an Incident."""
    ship = yield from actions.gain_card(["Ship"], label="a Ship")
    if ship and ship in actions.free_play_candidates(lambda i: i.uid == ship.uid, ("hand", "discard", "draw"))             and [i for i in ctx.me.hand if i is not ship]             and (yield from actions.may(f"Discard a card to free play {ctx.name(ship)}?")):
        yield from actions.discard(1, pred=lambda i: i is not ship)
        yield from actions.free_play(ship)
    if not count_traits(ctx, "Augment", exclude=ctx.this_card):
        yield from actions.take_incident()


@operation("3PIK13", 1, uses=[A.DUPLICATE])
def number_one(ctx, actions):
    """RESUPPLY: If able, duplicate a resupply operation of a Person in your Discard pile."""
    people = [i for i in ctx.me.discard if is_suit(i, "Person")]
    yield from actions.duplicate(people, label="a Person in your Discard pile", optional=False, kind="RESUPPLY")


@operation("3PIK13", 2, uses=[A.DISCARD, A.SEND_AWAY_TEAM], cost=[DiscardFromHand(1)])
def landing_party(ctx, actions):
    """ACTIVATION: Discard a card to send an [Away Team] to a Location."""
    yield from actions.send_away_team(1)

"""2PER11 Malcolm Reed (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER11.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, distinct_traits, has_trait, is_suit, others_in_hand


@operation("2PER11", 0, uses=[A.GAIN_SPECIALTY, A.DISCARD])
def tactical(ctx, actions):
    """PLAY: Gain 1 [Military]. Discard a card from your hand or the top of your deck. Gain 1 [Military] for each
    different one of Augment / Xindi / Romulan you have in your Discard pile."""
    yield from actions.gain_specialty("military", 1)
    options = ([("hand", "Discard a card from your hand")] if others_in_hand(ctx) else []) + \
        [("top", "Discard the top card of your deck")]
    choice = yield from actions.choose("Discard from where?", options)
    if choice == "hand":
        yield from actions.discard(1)
    else:
        yield from actions.discard_top()
    kinds = distinct_traits(ctx.me.discard, ("Augment", "Xindi", "Romulan"))
    if kinds:
        yield from actions.gain_specialty("military", kinds)


@operation("2PER11", 1, uses=[A.GAIN_RESOURCE])
def engineering_support(ctx, actions):
    """RESUPPLY: If you have an Engineer in play, gain 2 [Dilithium]."""
    if count_traits(ctx, "Engineer"):
        yield from actions.gain_resource("dilithium", 2)


@operation("2PER11", 2, uses=[A.FIND, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] != ctx.me.seat
           and ctx.event_card is not None and (is_suit(ctx.event_card, "Ship") or ctx.card(ctx.event_card).ship_token))
def armory(ctx, actions):
    """REACTION: After your opponent deploys a Ship, either find a Weapon OR send an [Away Team] to a Location where
    you have an [Away Team]."""
    choice = yield from actions.choose("Malcolm Reed: find a Weapon, or send an Away Team?",
                                       [("find", "Find a Weapon"),
                                        ("send", "Send an Away Team to a Location where you have one")])
    if choice == "find":
        yield from actions.find(lambda i: has_trait(i, "Weapon"), "a Weapon")
    else:
        yield from actions.send_away_team(1, where=lambda loc: ctx.away_at(loc) > 0)

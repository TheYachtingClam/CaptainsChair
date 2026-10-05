"""2PER13 Petra Aberdeen (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER13.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, others_in_hand


@operation("2PER13", 0, uses=[A.REVEAL, A.PUT, A.GAIN_CARD, A.LOG, A.GAIN_RESOURCE, A.DRAW],
           requires=lambda ctx: bool(others_in_hand(ctx)))
def archaeology(ctx, actions):
    """PLAY: Reveal a card from your hand and put it on the top of your deck to gain a card of the same suit from
    the Junk. Log the gained card and gain 1 [Glory]. If the gained card is Ancient, draw 2 cards."""
    card = yield from actions.pick_card("Reveal which card and put it on top of your deck?", others_in_hand(ctx))
    suit = ctx.suit(card)
    yield from actions.reveal([card])
    yield from actions.put_on_deck(card)
    gained = yield from actions.gain_card([suit], label=f"a {suit} from the Junk", only_junk=True)
    if gained:
        yield from actions.log(gained)
        yield from actions.gain_resource("glory", 1)
        if has_trait(gained, "Ancient"):
            yield from actions.draw(2)


@operation("2PER13", 1, uses=[A.GAIN_RESOURCE, A.DISCARD])
def appraisal(ctx, actions):
    """ACTIVATION: Gain 1 [Latinum]. You may discard a Starfleet to gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)
    starfleet = others_in_hand(ctx, lambda i: has_trait(i, "Starfleet"))
    if starfleet and (yield from actions.may("Discard a Starfleet to gain 1 more Latinum?")):
        yield from actions.discard(1, pred=lambda i: has_trait(i, "Starfleet"), label="a Starfleet")
        yield from actions.gain_resource("latinum", 1)


@operation("2PER13", 2, uses=[A.GAIN_SPECIALTY], cost=[Spend(latinum=1)],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None
           and (is_suit(ctx.event_card, "Cargo") or has_trait(ctx.event_card, "Alien", "Ancient")))
def study(ctx, actions):
    """REACTION: After putting a Cargo/Alien/Ancient into play, spend 1 [Latinum] to gain 2 [Research]."""
    yield from actions.gain_specialty("research", 2)



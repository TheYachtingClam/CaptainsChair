"""3CAR01 Gift Box (Cargo). Spec: resources/scans/second_contact/cards/cargo/3CAR01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, others_in_hand


@operation("3CAR01", 0, uses=[A.DEPLOY, A.DISCARD, A.GAIN_CARD])
def wrap(ctx, actions):
    """PLAY: Deploy this card. You may discard a card to gain a Cargo."""
    yield from actions.deploy(ctx.this_card)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to gain a Cargo?")):
        yield from actions.discard(1)
        yield from actions.gain_card(["Cargo"], label="a Cargo")


@operation("3CAR01", 1, uses=[A.RECALL])
def unwrap(ctx, actions):
    """RESUPPLY: You may recall a card beamed here."""
    card = yield from actions.pick_card("Recall a card beamed to Gift Box?", list(ctx.this_card.beamed),
                                        optional=True, none_label="No")
    if card:
        yield from actions.recall(card)


@operation("3CAR01", 2, uses=[A.BEAM, A.DRAW], requires=lambda ctx: any(is_suit(i, "Cargo") for i in ctx.me.discard))
def regift(ctx, actions):
    """ACTIVATION: Beam a Cargo from your Discard pile here. Your opponent may draw a card."""
    cargo = yield from actions.pick_card("Beam which Cargo from your Discard pile?",
                                         [i for i in ctx.me.discard if is_suit(i, "Cargo")])
    yield from actions.beam(cargo, ctx.this_card)
    opp = ctx.opponent
    if opp is not None and (yield from actions.may("Gift Box: do you want to draw a card?", seat=opp.seat)):
        yield from actions.draw(1, player=opp)


@operation("3CAR01", 3, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Betazoid"))
def betazoid_thanks(ctx, actions):
    """REACTION: After putting a Betazoid into play (including this card), gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)

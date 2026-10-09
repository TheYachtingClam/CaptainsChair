"""1DIR01 Conspiracy (Directive, solo Ticking Clock challenge). Spec: resources/scans/base_game/cards/1DIR01.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


@operation("1DIR01", 0, uses=[A.DISCARD, A.PUT, A.DRAW],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")])
def expose(ctx, actions):
    """PLAY: Discard a Person from your hand to discard this card and draw a card."""
    yield from actions.put_in_discard(ctx.this_card, ctx.me)
    yield from actions.draw(1)


# SPECIAL: This card cannot be beamed or discarded by any effect except its own play operation.
registry.CANNOT_BE_DISCARDED.add("1DIR01")


@operation("1DIR01", 2, uses=[A.DESTROY])
def unravel(ctx, actions):
    """SPECIAL: Before scoring, if this card is owned by the bot or logged, destroy it."""
    this = ctx.this_card
    if ctx.me.bot is not None or any(i.uid == this.uid for i in ctx.me.log):
        yield from actions.destroy(this)


registry.BEFORE_SCORING.add("1DIR01")
registry.VP_SPECIAL["1DIR01"] = lambda state, player, inst: -4  # -4*: for whoever still owns it at final scoring


@operation("1DIR01", 3, uses=[A.FORCE, A.TAKE_INCIDENT, A.PUT, A.GAIN_RESOURCE, A.DISCARD])
def surprise(ctx, actions):
    """SURPRISE (Bot only): You must choose: take an Incident and put it and this card to the bottom of your draw deck
    OR the bot gains 2 [Glory] and discards the top card of its Supplement deck. Runs with the Bot as "me"
    (REQ-SOLO-87, -132)."""
    human = ctx.opponent
    choice = "glory"
    if human is not None:
        choice = yield from actions.choose(
            "Conspiracy: you must choose.",
            [("incident", "Take an Incident; it and Conspiracy go on the bottom of your Draw deck"),
             ("glory", "The Bot gains 2 Glory and discards the top card of its Supplement deck")], seat=human.seat)
    if choice == "incident":
        yield from actions.take_incident(human, to="deck_bottom")
        yield from actions.put_on_deck(ctx.this_card, bottom=True, player=human)
    else:
        yield from actions.gain_resource("glory", 2)
        yield from actions.discard_from_reserve()

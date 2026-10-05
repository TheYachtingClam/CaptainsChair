"""3RIK11 Holodeck (Cargo). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK11.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, is_suit


@operation("3RIK11", 0, uses=[A.RECALL, A.DRAW, A.PUT, A.JUNK])
def simulation(ctx, actions):
    """PLAY: You may recall a Duty Officer. You may draw a card. Put a card on the top of your deck and junk a card
    from the Market."""
    officer = yield from actions.pick_card("Recall a Duty Officer?", list(ctx.me.duty), optional=True, none_label="No")
    if officer:
        yield from actions.recall(officer)
    if (yield from actions.may("Draw a card?")):
        yield from actions.draw(1)
    card = yield from actions.pick_card("Put which card on top of your deck?",
                                        [i for i in ctx.me.hand if i is not ctx.this_card])
    if card:
        yield from actions.put_on_deck(card)
    yield from actions.junk()


@operation("3RIK11", 1, uses=[A.DUPLICATE, A.GAIN_SPECIALTY, A.GAIN_RESOURCE], cost=[Spend(dilithium=1)])
def program(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to duplicate a play operation of a Person/Cargo/Ally from your hand or Discard pile.
    If you have an NX-01 in play, gain 1 [Research]/[Influence]/[Military]/[Glory]."""
    cards = [i for i in ctx.me.hand + ctx.me.discard if i is not ctx.this_card and is_suit(i, "Person", "Cargo", "Ally")]
    yield from actions.duplicate(cards, label="a Person, Cargo or Ally in your hand or Discard pile", optional=False)
    if count_traits(ctx, "NX-01"):
        choice = yield from actions.choose("Gain 1 of which?", [("research", "Research"), ("influence", "Influence"),
                                                                 ("military", "Military"), ("glory", "Glory")])
        if choice == "glory":
            yield from actions.gain_resource("glory", 1)
        else:
            yield from actions.gain_specialty(choice, 1)

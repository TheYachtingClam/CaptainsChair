"""3PIK09 James Kirk (United Earth Fleet) (Person, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition, DiscardFromHand, Spend, TakeIncidentCost

from ._util import is_suit

development_cost("3PIK09", Spend(dilithium=2), Condition(
    lambda ctx: sum(1 for i in ctx.me.log if is_suit(i, "Incident")) >= 2, "have 2 Incident logged"))


@operation("3PIK09", 0, uses=[A.DRAW_FROM_DISCARD, A.FREE_PLAY])
def temporal_officer(ctx, actions):
    """PLAY: You may draw a Directive from your Discard pile. You may free play a Directive."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Directive"), "a Directive", optional=True)
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Directive"))
    card = yield from actions.pick_card("Free play a Directive?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("3PIK09", 1, uses=[A.TAKE_INCIDENT, A.SCAN, A.DRAW], cost=[TakeIncidentCost()])
def recruit(ctx, actions):
    """PLAY: Take an Incident to scan 3 of Person and draw a card."""
    yield from actions.scan(3, ["Person"])
    yield from actions.draw(1)


@operation("3PIK09", 2, uses=[A.DISCARD, A.GAIN_CARD, A.DRAW, A.DISMISS],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")])
def reassign(ctx, actions):
    """ACTIVATION: Discard a Person to gain a Person/Ship. Draw a card. Dismiss this card."""
    yield from actions.gain_card(["Person", "Ship"], label="a Person or Ship")
    yield from actions.draw(1)
    yield from actions.dismiss(ctx.this_card)

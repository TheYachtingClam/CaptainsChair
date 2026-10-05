"""3PIK15 Time Crystal (Cargo). Spec: resources/scans/second_contact/cards/captains/pike/3PIK15.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

from ._util import has_trait, is_suit


@operation("3PIK15", 0, uses=[A.DISCARD, A.RECALL, A.LOG], cost=[DiscardFromHand(1)])
def rewind(ctx, actions):
    """PLAY: Discard a card to recall a non-Time Travel card from your Staging Area. Log a Time Travel from in play
    (can be this card)."""
    card = yield from actions.pick_card("Recall which card?",
                                        [i for i in ctx.me.staging if not has_trait(i, "Time Travel")])
    if card:
        yield from actions.recall(card)
    tt = [i for i in ctx.in_play() if has_trait(i, "Time Travel")]
    card = yield from actions.pick_card("Log which Time Travel card?", tt)
    if card:
        yield from actions.log(card)


@operation("3PIK15", 1, uses=[A.TAKE_INCIDENT, A.DUPLICATE], cost=[TakeIncidentCost()])
def glimpse(ctx, actions):
    """PLAY: Take an Incident to duplicate a play operation of a Person or Ally from your Development pile."""
    cards = [i for i in ctx.me.development if is_suit(i, "Person", "Ally")]
    yield from actions.duplicate(cards, label="a Person or Ally in your Development pile", optional=False)

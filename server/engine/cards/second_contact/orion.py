"""3LOC02 Orion (Location). Spec: resources/scans/second_contact/cards/location/3LOC02.md"""

from engine.cards import endgame, operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit, owned_cards


@operation("3LOC02", 0, uses=[A.SPEND, A.GAIN_CARD, A.FREE_PLAY])
def black_market(ctx, actions):
    """CONTROL: You may spend 1 [Latinum] to gain a Ship from the top of the deck, and free play it, if able."""
    if ctx.state.market_decks.get("Ship") and actions.can_spend(latinum=1) and (
            yield from actions.may("Spend 1 Latinum to gain the top card of the Ship deck?")):
        yield from actions.spend(latinum=1)
        ship = yield from actions.gain_card(["Ship"], label="the top Ship", deck_only=True)
        if ship and actions.free_play_candidates(lambda i: i is ship, cards=[ship]):
            yield from actions.free_play(ship)


@operation("3LOC02", 1, uses=[A.LOG, A.GAIN_ACTION, A.GAIN_RESOURCE],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Ship"), "a Ship", ("hand", "discard"))])
def smugglers(ctx, actions):
    """ACTIVATION: Log a Ship from your hand or Discard pile to gain an [Action] and 1 [Dilithium]/[Latinum]."""
    yield from actions.gain_action(1)
    kind = yield from actions.choose("Gain 1 Dilithium or 1 Latinum?", [("dilithium", "Dilithium"), ("latinum", "Latinum")])
    yield from actions.gain_resource(kind, 1)


@endgame("3LOC02")
def orions(state, player):
    """ENDGAME: Score 1 [VP] for each of your Orion cards."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Orion"))

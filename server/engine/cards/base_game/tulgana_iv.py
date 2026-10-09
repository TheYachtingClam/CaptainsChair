"""1LOC18 Tulgana IV (Location). Spec: resources/scans/base_game/cards/location/1LOC18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import is_suit, locations_with_your_ship


@operation("1LOC18", 0, uses=[A.JUNK])
def embassy(ctx, actions):
    """CONTROL: You may junk up to 2 cards from the Market."""
    for n in (1, 2):
        if not (yield from actions.may(f"Junk a card from the Market ({n} of up to 2)?")):
            break
        yield from actions.junk()


@operation("1LOC18", 1, uses=[A.SEND_AWAY_TEAM], cost=[Spend(latinum=1)],
           requires=lambda ctx: bool(locations_with_your_ship(ctx)))
def escort(ctx, actions):
    """ACTIVATION: Spend 1 [Latinum] to send an [Away Team] to a Location where you have a Ship."""
    yield from actions.send_away_team(1, lambda loc: bool(ctx.ships_at(loc)))


@operation("1LOC18", 2, uses=[A.DISCARD, A.DRAW, A.DRAW_FROM_DISCARD],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Cargo"), "a Cargo")])
def trade_mission(ctx, actions):
    """ACTIVATION: Discard a Cargo to draw a card from your deck or Discard pile."""
    choice = yield from actions.choose("Draw from where?", [("deck", "Your Draw deck"), ("discard", "Your Discard pile")])
    if choice == "deck":
        yield from actions.draw(1)
    else:
        yield from actions.draw_from_discard()

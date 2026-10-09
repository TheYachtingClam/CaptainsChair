"""1KOL16 Conquer (Directive), and the copy in Sela's deck (1SEL10). Spec: resources/scans/base_game/cards/captains/koloth/1KOL16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, locations_with_your_ship, others_in_hand, ships


@operation("1KOL16", 0, uses=[A.DISCARD, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM, A.DISMISS, A.GAIN_CARD])
def invade(ctx, actions):
    """PLAY: You may discard a Person and take an Incident to send 2 [Away Team] to a Location where you have a Ship.
    You may dismiss a Ship to gain a Person/Ship/Ally."""
    person = lambda i: is_suit(i, "Person")  # noqa: E731
    if others_in_hand(ctx, person) and ctx.state.incident and locations_with_your_ship(ctx) and (
            yield from actions.may("Discard a Person and take an Incident to send 2 Away Teams where you have a Ship?")):
        yield from actions.discard(1, pred=person, label="a Person")
        yield from actions.take_incident()
        yield from actions.send_away_team(2, lambda loc: bool(ctx.ships_at(loc)), same_location=True)
    ship = yield from actions.pick_card("Dismiss a Ship to gain a Person, Ship or Ally?", ships(ctx), optional=True,
                                        none_label="No")
    if ship:
        yield from actions.dismiss(ship)
        yield from actions.gain_card(["Person", "Ship", "Ally"], label="a Person, Ship or Ally")

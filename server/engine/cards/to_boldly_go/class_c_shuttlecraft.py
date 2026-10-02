"""Class C Shuttlecraft (Ship): 2GEO14, and the identical Type 6A Shuttlecraft 3FRE18.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO14.md"""

from engine.cards import operation
from engine.ops import A

from ._util import locations_with_your_ship, ships

IDS = ("2GEO14", "3FRE18")


@operation(IDS, 0, uses=[A.SEND_AWAY_TEAM, A.PUT], requires=lambda ctx: bool(locations_with_your_ship(ctx)))
def send_team(ctx, actions):
    """PLAY: Send an Away Team to a Location where you have a Ship. You may put this card on the top of your deck."""
    yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))
    if (yield from actions.may(f"Put {ctx.name(ctx.this_card)} on top of your deck?")):
        yield from actions.put_on_deck(ctx.this_card)


@operation(IDS, 1, uses=[A.GAIN_RESOURCE, A.BEAM, A.RECALL])
def dilithium_and_beam(ctx, actions):
    """PLAY: Gain 1 Dilithium. Then you may either: beam a card to a Ship OR recall a card beamed to a Ship."""
    yield from actions.gain_resource("dilithium", 1)
    your_ships = ships(ctx)
    options = []
    if your_ships and ctx.me.hand:
        options.append(("beam", "Beam a card to a Ship"))
    if any(s.beamed for s in your_ships):
        options.append(("recall", "Recall a card beamed to a Ship"))
    if not options:
        return
    choice = yield from actions.choose("Then?", options + [("none", "Neither")])
    if choice == "beam":
        card = yield from actions.pick_card("Beam which card?", list(ctx.me.hand))
        ship = yield from actions.pick_card("To which Ship?", your_ships)
        yield from actions.beam(card, ship)
    elif choice == "recall":
        beamed = [b for s in your_ships for b in s.beamed]
        card = yield from actions.pick_card("Recall which beamed card?", beamed)
        yield from actions.recall(card)

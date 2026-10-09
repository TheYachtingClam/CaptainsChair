"""1PIC14 Type 7 Shuttlecraft (Ship). Spec: resources/scans/base_game/cards/captains/picard/1PIC14.md"""

from engine.cards import operation
from engine.ops import A

from ._util import locations_with_your_ship, others_in_hand, ships


def ferry(ctx, actions):
    """Gain 1 [Dilithium]. Then you may either: beam a card to a Ship OR recall a card beamed to a Ship."""
    yield from actions.gain_resource("dilithium", 1)
    fleet = ships(ctx)
    beamed = [b for s in fleet for b in s.beamed]
    options = ([("beam", "Beam a card to a Ship")] if fleet and others_in_hand(ctx) else []) + \
        ([("recall", "Recall a card beamed to a Ship")] if beamed else [])
    if not options:
        return
    choice = yield from actions.choose("Beam a card to a Ship, or recall one?", options + [("none", "Neither")])
    if choice == "beam":
        card = yield from actions.pick_card("Beam which card?", others_in_hand(ctx))
        ship = yield from actions.pick_card(f"Beam {ctx.name(card)} to which Ship?", fleet)
        yield from actions.beam(card, ship)
    elif choice == "recall":
        card = yield from actions.pick_card("Recall which card?", beamed)
        yield from actions.recall(card)


@operation("1PIC14", 0, uses=[A.SEND_AWAY_TEAM, A.PUT])
def shuttle(ctx, actions):
    """PLAY: Send an [Away Team] to a Location where you have a Ship. You may put this card on the top of your deck."""
    if locations_with_your_ship(ctx):
        yield from actions.send_away_team(1, lambda loc: bool(ctx.ships_at(loc)))
    if (yield from actions.may("Put the Shuttlecraft on top of your deck?")):
        yield from actions.put_on_deck(ctx.this_card)


operation("1PIC14", 1, uses=[A.GAIN_RESOURCE, A.BEAM, A.RECALL])(ferry)

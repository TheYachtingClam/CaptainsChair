"""2ARC18 Shuttlepod 1 (Ship). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC18.md"""

from engine.cards import operation
from engine.ops import A

from ._util import locations_with_your_ship, others_in_hand, ships


@operation("2ARC18", 0, uses=[A.SEND_AWAY_TEAM, A.BEAM, A.RECALL], requires=lambda ctx: bool(locations_with_your_ship(ctx)))
def shuttle(ctx, actions):
    """PLAY: Send an [Away Team] to a Location where you have a Ship. You may either: beam a card to a Ship OR recall a
    card beamed to a Ship."""
    yield from actions.send_away_team(1, where=lambda l: bool(ctx.ships_at(l)))
    options = ([("beam", "Beam a card to a Ship")] if ships(ctx) and others_in_hand(ctx) else []) + \
        ([("recall", "Recall a card beamed to a Ship")] if any(s.beamed for s in ships(ctx)) else [])
    if not options:
        return
    choice = yield from actions.choose("Then?", options + [("none", "Neither")])
    if choice == "beam":
        card = yield from actions.pick_card("Beam which card?", others_in_hand(ctx))
        ship = yield from actions.pick_card("To which Ship?", ships(ctx))
        yield from actions.beam(card, ship)
    elif choice == "recall":
        card = yield from actions.pick_card("Recall which beamed card?", [b for s in ships(ctx) for b in s.beamed])
        yield from actions.recall(card)

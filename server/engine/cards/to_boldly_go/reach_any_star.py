"""2ARC16 Reach Any Star (Directive). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC16.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import ships


@operation("2ARC16", 0, uses=[A.DRAW, A.WARP, A.EXHAUST, A.SPEND, A.SEND_AWAY_TEAM])
def explore(ctx, actions):
    """PLAY: Draw a card OR warp a Ship OR exhaust your Captain to do both. You may spend 1 [Dilithium] to send an [Away
    Team] to a Location where you have a Ship."""
    options = [("draw", "Draw a card")] + ([("warp", "Warp a Ship")] if ships(ctx) else [])
    if ships(ctx) and not ctx.me.captain.exhausted:
        options.append(("both", "Exhaust your Captain to do both"))
    choice = yield from actions.choose("Reach Any Star: choose one.", options)
    if choice == "both":
        yield from actions.exhaust(ctx.me.captain)
    if choice in ("draw", "both"):
        yield from actions.draw(1)
    if choice in ("warp", "both"):
        ship = yield from actions.pick_card("Warp which Ship?", ships(ctx))
        yield from actions.warp(ship)
    if actions.can_spend(dilithium=1) and any(ctx.ships_at(l) for l in ctx.all_locations()) and (
            yield from actions.may("Spend 1 Dilithium to send an Away Team where you have a Ship?")):
        yield from actions.spend(dilithium=1)
        yield from actions.send_away_team(1, where=lambda l: bool(ctx.ships_at(l)))


@operation("2ARC16", 1, uses=[A.TAKE_INCIDENT, A.TAKE_CONTROL, A.LOG], cost=[TakeIncidentCost()],
           requires=lambda ctx: bool(ctx.state.location_deck))
def new_world(ctx, actions):
    """PLAY: Take an Incident to draw the top Location and take control of it. Log this card."""
    yield from actions.take_control(ctx.state.location_deck[0])
    yield from actions.log(ctx.this_card)

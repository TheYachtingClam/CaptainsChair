"""2KHA06 Cpt. Terrell (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import locations_with_your_ship

development_cost("2KHA06", TakeIncidentCost())


@operation("2KHA06", 0, uses=[A.DRAW, A.DISCARD])
def report(ctx, actions):
    """PLAY: Draw 2 cards and discard 1 of them."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(2)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")


@operation("2KHA06", 1, uses=[A.ENLIST_DEVELOPMENT, A.LOG])
def controlled(ctx, actions):
    """PLAY: Enlist a Development, at no [Dilithium]/[Latinum]/Incident cost. Log this card. Other conditions of the
    development cost still apply."""
    yield from actions.enlist_development(no_resources=True)
    yield from actions.log(ctx.this_card)


@operation("2KHA06", 2, uses=[A.GAIN_RESOURCE])
def supplies(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@operation("2KHA06", 3, uses=[A.SEND_AWAY_TEAM], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat
           and bool(locations_with_your_ship(ctx)))
def landing_party(ctx, actions):
    """REACTION: After taking an Incident, spend 1 [Dilithium] to send an [Away Team] to a Location where you have a
    Ship."""
    here = {loc.uid for loc in locations_with_your_ship(ctx)}
    yield from actions.send_away_team(1, where=lambda loc: loc.uid in here)

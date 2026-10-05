"""2ENC05 New Federation Applicants (Encounter). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC05.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import has_trait, is_suit, ships


def _beamed_incidents(ctx):
    return [b for host in ctx.in_play(beamed=False) for b in host.beamed if is_suit(b, "Incident")]


@operation("2ENC05", 0, uses=[A.TAKE_INCIDENT, A.DRAW, A.BEAM, A.GAIN_RESOURCE], cost=[TakeIncidentCost()])
def application(ctx, actions):
    """PLAY: Take an Incident to draw 2 cards. You may beam an Incident to a deployed Ship with Starfleet to gain 1
    [Glory]."""
    yield from actions.draw(2)
    starfleet_ships = [s for s in ships(ctx) if has_trait(s, "Starfleet")]
    incidents = [i for i in ctx.me.hand if is_suit(i, "Incident")]
    if starfleet_ships and incidents and (
            yield from actions.may("Beam an Incident to a Starfleet Ship to gain 1 Glory?")):
        incident = yield from actions.pick_card("Beam which Incident?", incidents)
        ship = yield from actions.pick_card("To which Starfleet Ship?", starfleet_ships)
        yield from actions.beam(incident, ship)
        yield from actions.gain_resource("glory", 1)


@operation("2ENC05", 1, uses=[A.RETURN_INCIDENT, A.REFRESH],
           requires=lambda ctx: bool(_beamed_incidents(ctx)) and bool(ctx.me.locations))
def accepted(ctx, actions):
    """PLAY: Return a beamed Incident to refresh a Location."""
    incident = yield from actions.pick_card("Return which beamed Incident?", _beamed_incidents(ctx))
    yield from actions.return_incident(incident)
    loc = yield from actions.pick_card("Refresh which of your Locations?", list(ctx.me.locations))
    if loc:
        yield from actions.refresh(loc)

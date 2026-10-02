"""Strange New Worlds (Directive): 2GEO17 and identical copies 2ARC13, 2KIRK21, 3PIK18, 3RIK17, 3FRE06.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO17.md"""

from engine.cards import operation
from engine.ops import A

IDS = ("2GEO17", "2ARC13", "2KIRK21", "3PIK18", "3RIK17", "3FRE06")


@operation(IDS, 0, uses=[A.TAKE_ENCOUNTER, A.LOG, A.GAIN_SPECIALTY], requires=lambda ctx: bool(ctx.me.locations))
def explore(ctx, actions):
    """PLAY: Select a controlled Location. If there is 1+ Away Team and 1+ Ship there, look at the top 2
    Encounter. Take one of them and return the other to the bottom of its deck. Log the selected Location
    to gain 1 Research. Ruling: logging is required; the card needs a controlled Location to be played."""
    loc = yield from actions.pick_card("Select one of your controlled Locations.", list(ctx.me.locations))
    if ctx.away_at(loc) > 0 and ctx.ships_at(loc):
        yield from actions.take_encounter(look=2)
    yield from actions.log(loc)
    yield from actions.gain_specialty("research", 1)

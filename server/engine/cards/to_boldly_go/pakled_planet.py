"""2REB20 Pakled Planet (Location). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB20.md"""

from engine.cards import operation
from engine.ops import A

from ._util import bareheaded_officers, helmets_in_hand, is_helmet
from .pakled_decree import HELMET_HERE


@operation("2REB20", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2REB20", 1, uses=[A.FIND])
def helmet_shop(ctx, actions):
    """CONTROL: Find a Helmet, except in your Reserve deck."""
    yield from actions.find(is_helmet, "a Helmet", exclude_reserve=True)


@operation("2REB20", 2, uses=[A.BEAM, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], cost=[HELMET_HERE])
def muster(ctx, actions):
    """ACTIVATION: Beam a Helmet here to send an [Away Team] to a Location. If you have a Ship at that Location, gain
    1 [Glory]."""
    loc = yield from actions.send_away_team(1)
    if loc is not None and ctx.ships_at(loc):
        yield from actions.gain_resource("glory", 1)


@operation("2REB20", 3, uses=[A.BEAM], requires=lambda ctx: bool(helmets_in_hand(ctx) and bareheaded_officers(ctx)))
def fitting(ctx, actions):
    """ACTIVATION: Beam a Helmet to your Duty Officer. A Duty Officer can wear only one Helmet (KW-HELM-02)."""
    helmet = yield from actions.pick_card("Beam which Helmet?", helmets_in_hand(ctx))
    officer = yield from actions.pick_card("To which Duty Officer?", bareheaded_officers(ctx))
    yield from actions.beam(helmet, officer)

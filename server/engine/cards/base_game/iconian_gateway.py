"""1ENC04 Iconian Gateway (Encounter). Spec: resources/scans/base_game/cards/encounter/1ENC04.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("1ENC04", 0, uses=[A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def gateway(ctx, actions):
    """PLAY: Send up to 3 [Away Team] to the same Location, ignoring any opponent Ship. For each Imperial you have in
    play (excluding this card) gain 1 [Military]."""
    targets = actions.away_targets(ignore_ships=True)
    if targets:
        n = yield from actions.choose("Send how many Away Teams through the Gateway?",
                                      [("3", "3"), ("2", "2"), ("1", "1"), ("0", "None")])
        if int(n):
            yield from actions.send_away_team(int(n), same_location=True, ignore_ships=True)
    imperial = count_traits(ctx, "Imperial", exclude=ctx.this_card)
    if imperial:
        yield from actions.gain_specialty("military", imperial)

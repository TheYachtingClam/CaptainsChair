"""1BUR05 Admiral Vance (Person, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import incidents_in_hand, is_suit

development_cost("1BUR05", Spend(dilithium=2))


@operation("1BUR05", 0, uses=[A.GAIN_CARD, A.DRAW])
def command(ctx, actions):
    """PLAY: Gain an Ally. Draw a card."""
    yield from actions.gain_card(["Ally"], label="an Ally")
    yield from actions.draw(1)


@operation("1BUR05", 1, uses=[A.DRAW, A.DISCARD, A.GAIN_ACTION])
def briefing(ctx, actions):
    """ACTIVATION: If you have an [Away Team] on a controlled Location, draw a card. If you have 3+ total [Away Team]
    on 1 or more controlled Location, draw a card. You may discard an Incident to gain an [Action]."""
    teams = sum(ctx.away_at(loc) for loc in ctx.controlled_locations())
    n = int(teams >= 1) + int(teams >= 3)
    if n:
        yield from actions.draw(n)
    if incidents_in_hand(ctx):
        discarded = yield from actions.discard(1, lambda i: is_suit(i, "Incident"), "an Incident to gain an Action",
                                               optional=True)
        if discarded:
            yield from actions.gain_action(1)

"""3LOC01 Krulmuth-B (Location). Spec: resources/scans/second_contact/cards/location/3LOC01.md"""

from engine.cards import operation
from engine.ops import A, RemoveOwnAwayTeam

from ._util import has_trait


@operation("3LOC01", 0, uses=[A.TAKE_INCIDENT, A.SCAN_FOR])
def contact(ctx, actions):
    """CONTROL: You may take an Incident to scan for an Orion."""
    if ctx.state.incident and (yield from actions.may("Take an Incident to scan for an Orion?")):
        yield from actions.take_incident()
        yield from actions.scan_for(lambda i: has_trait(i, "Orion"), "an Orion")


@operation("3LOC01", 1, uses=[A.REMOVE_AWAY_TEAM, A.TAKE_FROM_REWARD_PILE, A.DESTROY],
           cost=[RemoveOwnAwayTeam(here=True)], requires=lambda ctx: bool(ctx.state.rewards))
def crossover(ctx, actions):
    """ACTIVATION: Remove an [Away Team] from here to look at 2 random Crossover from the Reward pile. Take one of them
    and destroy the other. Ruling: "take" puts it into hand, so "when you gain" Reactions do not trigger."""
    _, others = yield from actions.take_from_reward_pile(2)
    for other in others:
        yield from actions.destroy(other)


@operation("3LOC01", 2, uses=[A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Scientist", "Orion"))
def survey_team(ctx, actions):
    """REACTION: After putting a Scientist or an Orion into play, send an [Away Team] here."""
    yield from actions.send_away_team(1, target=ctx.this_card)

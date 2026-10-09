"""1SHR24 Plasma Rifles (Cargo). Spec: resources/scans/base_game/cards/captains/shran/1SHR24.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait


@operation("1SHR24", 0, uses=[A.GAIN_SPECIALTY, A.JUNK, A.DEPLOY], cost=[Spend(dilithium=1)])
def issue(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to gain 1 [Military]. Junk a card from the Market. Deploy this card."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)


@operation("1SHR24", 1, uses=[A.DISCARD, A.ATTACK, A.REMOVE_AWAY_TEAM, A.TAKE_INCIDENT, A.DISMISS],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Andorian"), "an Andorian")])
def volley(ctx, actions):
    """ATTACK ACTIVATION: Discard an Andorian to remove 1 opponent [Away Team] from a Location. If an [Away Team] was
    removed this way from a Location controlled by your opponent, they take an Incident. Dismiss this card."""
    opp = ctx.opponent
    if opp is not None and (yield from actions.attack(removes_away_teams=True)):
        targets = [loc for loc in ctx.all_locations() if ctx.away_at(loc, opp) > 0]
        loc = yield from actions.pick_card("Remove an opponent Away Team from which Location?", targets)
        if loc:
            theirs = any(c.uid == loc.uid for c in opp.locations)
            yield from actions.remove_away_team(loc, opp)
            if theirs:
                yield from actions.take_incident(opponent=True)
    yield from actions.dismiss(ctx.this_card)

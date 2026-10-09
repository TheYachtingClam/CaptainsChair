"""1SHR16 Imperial Pride (Directive), and the copy in Sela's deck (1SEL11). Spec: resources/scans/base_game/cards/captains/shran/1SHR16.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, Spend


def _garrisons(ctx):
    return [loc for loc in ctx.controlled_locations() if ctx.away_at(loc) > 0]


def _withdraw_three(ctx, actions):
    chosen: list[str] = []
    for n in (1, 2, 3):
        left = [loc for loc in _garrisons(ctx) if loc.uid not in chosen]
        loc = yield from actions.pick_card(f"Remove an Away Team from which controlled Location ({n} of 3, cost)?", left)
        chosen.append(loc.uid)
        yield from actions.remove_away_team(loc, ctx.me)


@operation("1SHR16", 0, uses=[A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER],
           cost=[EffectCost(lambda ctx: len(_garrisons(ctx)) >= 3, _withdraw_three, (A.REMOVE_AWAY_TEAM,),
                            "remove an Away Team from 3 different controlled Locations")])
def tribute(ctx, actions):
    """PLAY: Remove an [Away Team] from 3 different controlled Location to look at the top 2 Encounter. Take one of
    them and return the other to the bottom of its deck."""
    yield from actions.take_encounter(look=2)


def _log_a_location(ctx, actions):
    loc = yield from actions.pick_card("Log which controlled Location (cost)?", ctx.controlled_locations())
    shares = bool(ctx.traits(loc) & ctx.traits(ctx.me.captain))
    yield from actions.log(loc)
    actions.paid.append(loc)
    actions.emit(f"{ctx.name(loc)} {'shares a trait' if shares else 'shares no trait'} with your Captain.")


@operation("1SHR16", 1, uses=[A.LOG, A.TAKE_ENCOUNTER, A.GAIN_SPECIALTY],
           cost=[Spend(dilithium=10), EffectCost(lambda ctx: bool(ctx.controlled_locations()), _log_a_location,
                                                 (A.LOG,), "log a controlled Location")])
def annex(ctx, actions):
    """PLAY: Spend 10 [Dilithium] and log a controlled Location to take the top Encounter. If the logged card shares
    no traits with your Captain, gain 1 [Influence]."""
    yield from actions.take_encounter()
    logged = actions.paid[-1] if actions.paid else None
    if logged is not None and not (ctx.traits(logged) & ctx.traits(ctx.me.captain)):
        yield from actions.gain_specialty("influence", 1)

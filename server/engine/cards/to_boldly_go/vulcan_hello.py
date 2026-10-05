"""2SOV05 Vulcan Hello (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, opponent_has, opponent_ships

development_cost("2SOV05", Spend(dilithium=4))


@operation("2SOV05", 0, uses=[A.ATTACK, A.DISMISS, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def hello(ctx, actions):
    """ATTACK PLAY: Dismiss an opponent Ship at a neutral Location and you may send an [Away Team] to the same
    Location. If your opponent has Klingon in play, gain 1 [Glory].
    Ruling: playable with no opponent Ship at a neutral Location; the dismissal is then skipped."""
    neutral = {loc.uid for loc in ctx.state.neutral}
    targets = [s for s in opponent_ships(ctx) if s.at in neutral]
    loc = None
    if (yield from actions.attack()) and targets:
        ship = yield from actions.pick_card("Dismiss which opponent Ship?", targets)
        loc = next(l for l in ctx.state.neutral if l.uid == ship.at)
        yield from actions.dismiss(ship)
    options = [loc] if loc is not None else []
    if not options:
        options = actions.away_targets(lambda l: l in ctx.state.neutral)
    if options and (yield from actions.may("Send an Away Team there?" if loc else "Send an Away Team to a neutral Location?")):
        yield from actions.send_away_team(1, where=lambda l: l in options)
    if opponent_has(ctx, lambda i: has_trait(i, "Klingon")):
        yield from actions.gain_resource("glory", 1)


@operation("2SOV05", 1, uses=[A.TAKE_CONTROL, A.LOG], requires=lambda ctx: ctx.track("military") >= 9)
def annexation(ctx, actions):
    """PLAY: Requires [Military] 9. Select a neutral Location not secured by your opponent. Take control of it and log
    this card."""
    choices = [loc for loc in ctx.state.neutral if not (ctx.opponent and ctx.secured_by(loc, ctx.opponent))]
    loc = yield from actions.pick_card("Take control of which neutral Location?", choices)
    if loc:
        yield from actions.take_control(loc)
    yield from actions.log(ctx.this_card)

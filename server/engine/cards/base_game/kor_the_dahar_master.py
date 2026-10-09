"""1KOL08 Kor, the Dahar Master (Person, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition, Spend

from ._util import ships

development_cost("1KOL08", Spend(dilithium=2, latinum=1), Condition(lambda ctx: ctx.me.glory >= 10, "have 10+ Glory"))


@operation("1KOL08", 0, uses=[A.SEND_AWAY_TEAM, A.SPEND, A.TAKE_CONTROL, A.LOG])
def conquest(ctx, actions):
    """PLAY: Send an [Away Team] to a neutral Location. If that Location is now secured, you may spend an [Action] to
    take control of it. If you do, log this card."""
    loc = yield from actions.send_away_team(1, lambda loc: loc in ctx.state.neutral)
    if loc is None or not ctx.secured_by(loc) or not actions.can_spend(actions=1):
        return
    if (yield from actions.may(f"Spend an Action to take control of {ctx.name(loc)}?")):
        yield from actions.spend(actions=1)
        yield from actions.take_control(loc)
        yield from actions.log(ctx.this_card)


@operation("1KOL08", 1, uses=[A.GAIN_SPECIALTY, A.WARP],
           trigger=lambda ctx, ev: ev["kind"] == "gain_specialty" and ev["seat"] == ctx.me.seat
           and ev.get("track") == "influence" and (ev.get("amount") or 0) >= 1)
def old_warrior(ctx, actions):
    """REACTION: After gaining at least 1 [Influence], gain 1 [Military] and you may warp a Ship."""
    yield from actions.gain_specialty("military", 1)
    movable = [s for s in ships(ctx) if actions.can_warp(s)]
    ship = yield from actions.pick_card("Warp a Ship?", movable, optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)

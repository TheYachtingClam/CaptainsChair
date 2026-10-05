"""2REB05 Varuvian Bomb (Cargo, Development). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, SpendUnless

from ._util import has_trait

development_cost("2REB05", SpendUnless(Spend(dilithium=5), lambda ctx: any(
    loc.card == "2REB04" and ctx.away_at(loc) for loc in ctx.me.locations)))


@operation("2REB05", 0, uses=[A.ATTACK, A.TAKE_INCIDENT, A.LOG, A.GAIN_SPECIALTY, A.DISCARD])
def detonate(ctx, actions):
    """ATTACK PLAY: Your opponent takes an Incident. Log a controlled Location you have in play. Gain 1 [Military], and
    2 [Military] for each [Research]/[Influence]/[Military]/[Any Skill] the logged card has. Then, either: discard a
    Shady OR log this card."""
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    loc = yield from actions.pick_card("Log which controlled Location?", list(ctx.me.locations))
    icons = 0
    if loc is not None:
        icons = sum(1 for s in ctx.skills(loc) if s in ("Research", "Influence", "Military", "Any"))
        yield from actions.log(loc)
    yield from actions.gain_specialty("military", 1 + 2 * icons)
    shady = [i for i in ctx.me.hand if has_trait(i, "Shady")]
    choice = "log" if not shady else (yield from actions.choose("Then?", [("discard", "Discard a Shady"),
                                                                          ("log", "Log Varuvian Bomb")]))
    if choice == "discard":
        yield from actions.discard(1, pred=lambda i: has_trait(i, "Shady"), label="a Shady")
    else:
        yield from actions.log(ctx.this_card)

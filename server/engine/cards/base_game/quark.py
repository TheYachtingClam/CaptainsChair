"""1SIS24 Quark (Person). Spec: resources/scans/base_game/cards/captains/sisko/1SIS24.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, has_trait


@operation("1SIS24", 0, uses=[A.SCAN, A.DRAW, A.TAKE_INCIDENT], cost=[Spend(latinum=1)])
def broker(ctx, actions):
    """PLAY: Spend 1 [Latinum] to scan 1 of Person. If the gained card is Business, draw a card. If the gained card is
    Shady, take an Incident."""
    gained = yield from actions.scan(1, ["Person"])
    if gained is None:
        return
    if has_trait(gained, "Business"):
        yield from actions.draw(1)
    if has_trait(gained, "Shady"):
        yield from actions.take_incident()


@operation("1SIS24", 1, uses=[A.GAIN_RESOURCE])
def bar(ctx, actions):
    """RESUPPLY: Gain 1 [Latinum]. If you have 2+ Ferengi in play, gain 1 additional [Latinum]."""
    yield from actions.gain_resource("latinum", 2 if count_traits(ctx, "Ferengi") >= 2 else 1)


@operation("1SIS24", 2, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "spend" and ev["seat"] == ctx.me.seat
           and (ev.get("cost_latinum") or 0) > 0)
def profit(ctx, actions):
    """REACTION: After resolving an operation with a [Latinum] cost, gain 1 [Glory]. Latinum the operation asks for
    counts, as its cost or as a "you may spend 1 [Latinum] to …" in its effect (decision, 2026-10-09)."""
    yield from actions.gain_resource("glory", 1)

"""3PER07 Lieutenant Dax (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER07.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import has_trait, minus_unless_logged

registry.VP_SPECIAL["3PER07"] = minus_unless_logged(1)  # SPECIAL: If not logged, this card scores -1.

TRACKS = [(t, t.capitalize()) for t in ("research", "influence", "military")]


@operation("3PER07", 0, uses=[A.GAIN_SPECIALTY, A.SPEND, A.PROMOTE])
def symbiont(ctx, actions):
    """PLAY: Gain 1 [Research]/[Influence]/[Military]. You may spend 1 [Latinum] to gain 1 more. If you have a Vulcan on
    duty, gain 1 more. You may promote this card to Duty Officer."""
    yield from actions.gain_specialty((yield from actions.choose("Gain 1 on which track?", TRACKS)), 1)
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to gain 1 more?")):
        yield from actions.spend(latinum=1)
        yield from actions.gain_specialty((yield from actions.choose("Gain 1 on which track?", TRACKS)), 1)
    if any(has_trait(i, "Vulcan") for i in ctx.me.duty):
        yield from actions.gain_specialty((yield from actions.choose("Vulcan on duty: gain 1 on which track?", TRACKS)), 1)
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Lieutenant Dax to Duty Officer?")):
        yield from actions.promote(ctx.this_card)


@operation("3PER07", 1, uses=[A.SCAN, A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "would_gain_market" and ev["seat"] == ctx.me.seat)
def nine_lives(ctx, actions):
    """REACTION: When you would gain a card, scan 2 of the same suit instead, then draw a card."""
    suits = ctx.event.get("suits") or []
    if not suits:
        return False
    yield from actions.scan(2, suits)
    yield from actions.draw(1)
    return True

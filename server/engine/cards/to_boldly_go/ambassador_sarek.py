"""2GEO04 Ambassador Sarek (Person), and 2KIRK08 Sarek with the same operations.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO04.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit

IDS = ("2GEO04", "2KIRK08")
development_cost(IDS, Spend(dilithium=1, latinum=1))
for cid in IDS:
    registry.DUTY_LIMIT[cid] = 2  # PASSIVE: You may have up to two additional Person on duty.


@operation(IDS, 0, uses=[A.GAIN_SPECIALTY, A.PROMOTE])
def influence_and_promote(ctx, actions):
    """PLAY: Gain 1 Influence for each Vulcan you have in play (including this card). You may promote Sarek
    and optionally another Person from your Staging Area to Duty Officer(s)."""
    vulcans = ctx.count_in_play(lambda i: has_trait(i, "Vulcan"))
    yield from actions.gain_specialty("influence", vulcans)
    sarek = ctx.this_card
    if sarek in ctx.me.staging and (yield from actions.may(f"Promote {ctx.name(sarek)} to Duty Officer?")):
        yield from actions.promote(sarek)
        others = [i for i in ctx.me.staging if is_suit(i, "Person")]
        other = yield from actions.pick_card("Also promote another Person from your Staging Area?", others,
                                             optional=True, none_label="No")
        if other:
            yield from actions.promote(other)

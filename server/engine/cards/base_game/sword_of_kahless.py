"""1KOL04 Sword of Kahless (Cargo, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, SpendUnless

from ._util import in_play_ids

# "[Dilithium] x5, OR free if the I.K.S. Devisor is in play."
development_cost("1KOL04", SpendUnless(Spend(dilithium=5), lambda ctx: "1KOL09" in in_play_ids(ctx)))


@operation("1KOL04", 0, uses=[A.JUNK, A.DISMISS, A.GAIN_RESOURCE, A.LOG], requires=lambda ctx: ctx.track("military") >= 9)
def unite(ctx, actions):
    """PLAY: Requires [Military] 9. Junk a card from the Market. Dismiss a Klingon Duty Officer to gain 4 [Glory]. Log
    this card."""
    yield from actions.junk()
    klingons = [i for i in ctx.me.duty if ctx.has(i, "Klingon")]
    officer = yield from actions.pick_card("Dismiss a Klingon Duty Officer to gain 4 Glory?", klingons, optional=True,
                                           none_label="No")
    if officer:
        yield from actions.dismiss(officer)
        yield from actions.gain_resource("glory", 4)
    yield from actions.log(ctx.this_card)

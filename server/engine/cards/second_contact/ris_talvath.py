"""3SHI02 R.I.S. Talvath (Ship). Spec: resources/scans/second_contact/cards/ships/3SHI02.md"""

from engine.cards import dismiss_rewards, operation
from engine.ops import A

from ._util import has_trait


@operation("3SHI02", 0, uses=[A.DEPLOY, A.WARP])
def deploy(ctx, actions):
    """PLAY: Deploy this ship. You may warp this ship."""
    yield from actions.deploy(ctx.this_card)
    if ctx.this_card in ctx.me.fleet and (yield from actions.may("Warp the R.I.S. Talvath?")):
        yield from actions.warp(ctx.this_card)


@operation("3SHI02", 1, uses=[A.PLACE_RESOURCES, A.WARP],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ctx.event_card is not None
           and has_trait(ctx.event_card, "Anomaly", "Communication", "Time Travel"))
def scan_anomaly(ctx, actions):
    """REACTION: After you or your opponent puts an Anomaly/Communication/Time Travel into play, place 1 [Dilithium]
    on this card and you may warp this ship."""
    yield from actions.place_resources(ctx.this_card, "dilithium", 1)
    if (yield from actions.may("Warp the R.I.S. Talvath?")):
        yield from actions.warp(ctx.this_card)


@dismiss_rewards("3SHI02")
def evacuate(state, owner, inst):
    """PASSIVE: When this ship is dismissed during your Control Step, gain 1 [Glory] and gain all resources from this
    card (overriding REQ-EXP-50)."""
    if state.step != "control" or state.active != owner.seat:
        return {}
    reward = {kind: n for kind, n in inst.res.items() if n}
    reward["glory"] = reward.get("glory", 0) + 1
    return reward

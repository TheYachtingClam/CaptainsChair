"""2ALL03 Bynars (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL03.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ALL03", 0, uses=[A.GAIN_CARD, A.LOG])
def gain_cargo(ctx, actions):
    """PLAY: Gain a Cargo. Log this card."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")
    yield from actions.log(ctx.this_card)


@operation("2ALL03", 1, uses=[A.SCAN, A.LOG], requires=lambda ctx: ctx.track("research") >= 3)
def scan_cargo(ctx, actions):
    """PLAY: Requires [Research] 3. Scan 3 of Cargo. Log this card."""
    yield from actions.scan(3, ["Cargo"])
    yield from actions.log(ctx.this_card)

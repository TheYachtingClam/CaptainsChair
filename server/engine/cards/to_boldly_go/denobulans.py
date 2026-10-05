"""2ALL04 Denobulans (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL04.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ALL04", 0, uses=[A.GAIN_CARD, A.LOG])
def gain_person(ctx, actions):
    """PLAY: Gain a Person. Log this card."""
    yield from actions.gain_card(["Person"], label="a Person")
    yield from actions.log(ctx.this_card)


@operation("2ALL04", 1, uses=[A.SCAN, A.LOG], requires=lambda ctx: ctx.track("influence") >= 3)
def scan_people(ctx, actions):
    """PLAY: Requires [Influence] 3. Scan 3 of Person. Log this card."""
    yield from actions.scan(3, ["Person"])
    yield from actions.log(ctx.this_card)

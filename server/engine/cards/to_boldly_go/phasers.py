"""2CAR14 Phasers (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR14.md
The Reaction against attacks arrives in Step 4."""

from engine.cards import operation
from engine.ops import A, Spend


@operation("2CAR14", 0, uses=[A.DRAW, A.JUNK, A.DEPLOY])
def arm(ctx, actions):
    """PLAY: Draw two cards. Junk a card from the Market. Deploy this card."""
    yield from actions.draw(2)
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)


@operation("2CAR14", 1, uses=[A.GAIN_ACTION, A.JUNK, A.DEPLOY], cost=[Spend(dilithium=1)],
           requires=lambda ctx: ctx.track("military") >= 4)
def ready(ctx, actions):
    """PLAY: Requires [Military] 4. Spend 1 [Dilithium] to gain an [Action]. Junk a card from the Market. Deploy
    this card."""
    yield from actions.gain_action(1)
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)

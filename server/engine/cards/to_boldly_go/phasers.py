"""2CAR14 Phasers (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR14.md"""

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


@operation("2CAR14", 2, uses=[A.DISMISS],
           trigger=lambda ctx, ev: ev["kind"] == "would_attack" and ev["seat"] == ctx.me.seat
           and ev.get("removes_away_teams"))
def stun(ctx, actions):
    """REACTION: When you would be forced by an attack to remove 1 or more [Away Team], dismiss this card to ignore
    the negative effect."""
    yield from actions.dismiss(ctx.this_card)
    return True

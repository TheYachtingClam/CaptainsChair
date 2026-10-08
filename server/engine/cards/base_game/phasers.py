"""1CAR11 Phasers (Cargo), the older Core Box version. Spec: resources/scans/base_game/cards/cargo/1CAR11.md
Unlike To Boldly Go's version (2CAR14), its first PLAY costs an action. Its second PLAY is registered with that card."""

from engine.cards import operation
from engine.ops import A


@operation("1CAR11", 0, uses=[A.DRAW, A.JUNK, A.DEPLOY])
def arm(ctx, actions):
    """PLAY: Draw 2 cards. Junk a card from the Market. Deploy this card."""
    yield from actions.draw(2)
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)


@operation("1CAR11", 2, uses=[A.DISMISS],
           trigger=lambda ctx, ev: ev["kind"] == "would_attack" and ev["seat"] == ctx.me.seat
           and ev.get("removes_away_teams"))
def stun(ctx, actions):
    """REACTION: When you would be forced by an attack to remove an [Away Team], dismiss this card to ignore the
    effect."""
    yield from actions.dismiss(ctx.this_card)
    return True

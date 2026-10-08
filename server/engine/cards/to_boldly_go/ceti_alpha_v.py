"""2KHA02A Ceti Alpha V and 2KHA02B Devastated Ceti Alpha V (Location, the two sides of one card).
Specs: resources/scans/to_boldly_go/cards/captains/kahn/2KHA02A.md and 2KHA02B.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import has_trait


@hand_size_modifier("2KHA02A")
def plus_one(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1


@operation("2KHA02B", 0, uses=[A.ATTACK, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def devastation(ctx, actions):
    """ATTACK CONTROL: Your opponent takes an Incident. Send all of your [Away Team] here."""
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    yield from actions.send_all_away_teams(ctx.this_card)  # from the Captain and from every other Location


@operation("2KHA02B", 1, uses=[A.DRAW])
def scavenge(ctx, actions):
    """ACTIVATION: If you have no [Away Team] here, draw a card."""
    if ctx.away_at(ctx.this_card) == 0:
        yield from actions.draw(1)
    else:
        actions.emit(f"{ctx.me.name} has an Away Team at {ctx.name(ctx.this_card)}, so no card is drawn.")


@operation("2KHA02B", 2, uses=[A.DRAW, A.ENLIST_DEVELOPMENT],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Augment"))
def followers(ctx, actions):
    """REACTION: After putting an Augment into play, draw a card and you may enlist a Development."""
    yield from actions.draw(1)
    if ctx.me.development and (yield from actions.may("Enlist a Development?")):
        yield from actions.enlist_development()


@operation("2KHA02B", 3, uses=[A.REFRESH],
           trigger=lambda ctx, ev: ev["kind"] == "return_incident" and ev["seat"] == ctx.me.seat)
def endure(ctx, actions):
    """PASSIVE: After returning an Incident, refresh this card."""
    yield from actions.refresh(ctx.this_card)

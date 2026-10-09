"""1BUR22 Sylvia Tilly (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR22.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, LogFromHand

from ._util import count_traits, is_suit


def _tired(ctx):
    return [i for i in ctx.in_play() if i.exhausted and (i is ctx.me.captain or is_suit(i, "Captain", "Cargo", "Ship"))]


@operation("1BUR22", 0, uses=[A.DRAW, A.REFRESH])
def enthusiasm(ctx, actions):
    """PLAY: For each Scientist you have in play (excluding your Captain), draw a card. For each Engineer in play,
    refresh a Captain/Cargo/Ship."""
    scientists = count_traits(ctx, "Scientist", exclude=ctx.me.captain)
    if scientists:
        yield from actions.draw(scientists)
    for _ in range(count_traits(ctx, "Engineer")):
        if not _tired(ctx):
            break
        card = yield from actions.pick_card("Refresh which Captain, Cargo or Ship?", _tired(ctx))
        yield from actions.refresh(card)


@operation("1BUR22", 1, uses=[A.LOG, A.MOVE_RESOURCES], cost=[LogFromHand(zones=("hand", "discard"))])
def bright_idea(ctx, actions):
    """PLAY: Log a card from your hand or Discard pile to recrystallize 1 [Dilithium]."""
    yield from actions.recrystallize(1)


@operation("1BUR22", 2, uses=[A.DISCARD, A.SEND_AWAY_TEAM],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Incident"), "an Incident")],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def welcome_aboard(ctx, actions):
    """REACTION: After gaining a Person, discard an Incident to send an [Away Team] to a Location."""
    yield from actions.send_away_team(1)

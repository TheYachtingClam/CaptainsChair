"""1SEL24 Remans (Ally). Spec: resources/scans/base_game/cards/captains/sela/1SEL24.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck


@operation("1SEL24", 0, uses=[A.PUT, A.SEND_AWAY_TEAM, A.LOG, A.DRAW, A.FORCE], cost=[PutOnDeck(1)])
def shock_troops(ctx, actions):
    """PLAY: Put a card on the top of your deck to send an [Away Team] to a Location. Then either: log this card OR
    your opponent may draw a card."""
    yield from actions.send_away_team(1)
    opp = ctx.opponent
    choice = yield from actions.choose("Remans:", [("log", "Log this card"), ("draw", "Your opponent may draw a card")])
    if choice == "log":
        yield from actions.log(ctx.this_card)
    elif opp is not None and (yield from actions.may("Draw a card?", seat=opp.seat)):
        yield from actions.draw(1, player=opp)

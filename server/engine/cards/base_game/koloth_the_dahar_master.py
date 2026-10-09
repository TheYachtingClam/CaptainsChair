"""1KOL01 Koloth, the Dahar Master (Captain). Spec: resources/scans/base_game/cards/captains/koloth/1KOL01.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck


@operation("1KOL01", 0, uses=[A.PUT, A.SEND_AWAY_TEAM, A.DRAW, A.FORCE], cost=[PutOnDeck(1)])
def campaign(ctx, actions):
    """ACTIVATION: Put a card on the top of your deck to send an [Away Team] to a Location. Your opponent may draw a
    card."""
    yield from actions.send_away_team(1)
    opp = ctx.opponent
    if opp is not None and (yield from actions.may("Draw a card?", seat=opp.seat)):
        yield from actions.draw(1, player=opp)

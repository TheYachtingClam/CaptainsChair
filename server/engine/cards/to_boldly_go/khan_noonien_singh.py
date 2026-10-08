"""2KHA01A Khan Noonien Singh and 2KHA01B Wrathful Khan (Captain, the two sides of one card).
Specs: resources/scans/to_boldly_go/cards/captains/kahn/2KHA01A.md and 2KHA01B.md"""

from engine.cards import IGNORE_SPECIALTY_REQUIREMENTS, NO_ENLIST_ON_CYCLE, endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit, others_in_hand, owned_cards

# PASSIVE (both sides): You do not enlist when you cycle your deck.
NO_ENLIST_ON_CYCLE.update({"2KHA01A", "2KHA01B"})
# PASSIVE (Wrathful): Ignore all [Research]/[Influence]/[Military] requirements.
IGNORE_SPECIALTY_REQUIREMENTS.add("2KHA01B")


def _opponent_returned_an_incident(ctx, ev):
    return ev["kind"] == "return_incident" and ev["seat"] != ctx.me.seat


def _gain_one(ctx, actions):
    kind = yield from actions.choose("Gain which resource?", [("dilithium", "1 Dilithium"), ("latinum", "1 Latinum")])
    yield from actions.gain_resource(kind, 1)


@operation("2KHA01A", 0, uses=[A.DISCARD, A.DRAW],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Incident"), "an Incident")])
def brood(ctx, actions):
    """ACTIVATION: Discard an Incident to draw 2 cards and discard one of them."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(2)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")


@operation("2KHA01A", 1, uses=[A.DISCARD, A.GAIN_RESOURCE], trigger=_opponent_returned_an_incident)
def exile(ctx, actions):
    """PASSIVE: After your opponent returns an Incident discard a card to gain 1 [Dilithium]/[Latinum].
    Ruling: mandatory, every time; with no card in hand it does nothing."""
    if not others_in_hand(ctx):
        return
    yield from actions.discard(1)
    yield from _gain_one(ctx, actions)


@operation("2KHA01B", 0, uses=[A.DISCARD, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)],
           trigger=_opponent_returned_an_incident)
def wrath(ctx, actions):
    """REACTION: After your opponent returns an Incident, discard a card to gain 1 [Dilithium]/[Latinum]."""
    yield from _gain_one(ctx, actions)


@endgame("2KHA01B")
def scores_to_settle(state, player):
    """ENDGAME: Score 1 [VP] for each of your [Research Focus]/[Influence Focus]/[Military Focus]. If you have all 12
    traits marked, score 3 [VP] for each instead. A Best Focus icon is one of them."""
    from engine.ops import card, trait_board

    icons = sum(1 for inst in owned_cards(player) if card(inst).focus)
    each = 3 if len(player.marks) >= len(trait_board(player)) > 0 else 1
    return icons * each

"""Khan's three Incidents with the same text: 2KHA19 To the Last, I Will Grapple with Thee!, 2KHA20 From Hell's Heart,
I Stab at Thee! and 2KHA21 I Spit My Last Breath at Thee! Specs: resources/scans/to_boldly_go/cards/captains/kahn/2KHA19.md to 2KHA21.md
Their SURPRISE operation (index 1) is for the Bot and waits for the Khan Bot."""

from engine.cards import operation
from engine.ops import A, PutOnDeck

from ._util import has_trait, virtual

IDS = ("2KHA19", "2KHA20", "2KHA21")


@operation(IDS, 0, uses=[A.REVEAL, A.PUT, A.ATTACK, A.GAIN_RESOURCE, A.DRAW, A.FORCE, A.RETURN_INCIDENT],
           cost=[PutOnDeck(1)])
def curse(ctx, actions):
    """ATTACK PLAY: Reveal a card and put it on the top of your deck to put this card in your opponent's Discard pile.
    If the revealed card shares a non-Human trait with your opponent's Captain, gain 1 [Glory] and they may draw a
    card. Cadet Training ruling: against the virtual opponent this card is returned and you gain 1 Glory, as when an
    Incident is given to it (REQ-CTM-13)."""
    revealed = actions.paid[0]
    yield from actions.reveal([revealed])
    opp = ctx.opponent
    if (yield from actions.attack()):
        if opp is not None:
            yield from actions.put_in_discard(ctx.this_card, opp)
        elif virtual(ctx):
            yield from actions.return_incident(ctx.this_card)
            yield from actions.gain_resource("glory", 1)
    shared = [t for t in ctx.opponent_captain_traits() if t != "Human"]
    if shared and has_trait(revealed, *shared):
        yield from actions.gain_resource("glory", 1)
        if opp is not None and (yield from actions.may("Draw a card?", seat=opp.seat)):
            yield from actions.draw(1, player=opp)

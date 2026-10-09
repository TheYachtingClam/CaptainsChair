"""1PIC01 Jean-Luc Picard (Captain). Spec: resources/scans/base_game/cards/captains/picard/1PIC01.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit, owned_cards, ships


@operation("1PIC01", 0, uses=[A.DISCARD, A.GAIN_RESOURCE, A.BEAM], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ally"))
def diplomat(ctx, actions):
    """REACTION: After gaining an Ally, discard a card to gain 1 [Glory] and you may beam the gained card to a Ship."""
    yield from actions.gain_resource("glory", 1)
    ally = ctx.event_card
    if ally is None or not ships(ctx):
        return
    ship = yield from actions.pick_card(f"Beam {ctx.name(ally)} to a Ship?", ships(ctx), optional=True,
                                        none_label="No")
    if ship:
        yield from actions.beam(ally, ship)


@endgame("1PIC01")
def allies(state, player):
    """ENDGAME: Score 1 [VP] for each of your Ally cards."""
    return sum(1 for i in owned_cards(player) if is_suit(i, "Ally"))

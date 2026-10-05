"""3PIK05 Talosians (Ally, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import count_traits, is_suit

development_cost("3PIK05", Spend(dilithium=3, latinum=1))
SUITS = ("Person", "Cargo", "Ship", "Ally")


@operation("3PIK05", 0, uses=[A.SWAP_JUNK_WITH_MARKET, A.DRAW_FROM_DISCARD])
def illusion(ctx, actions):
    """PLAY: Select one of Person / Cargo / Ship / Ally. You may swap a card of the selected suit between the Market
    and the Junk. You may draw a card of the selected suit from your Discard pile."""
    suit = yield from actions.choose("Select a suit.", [(s, s) for s in SUITS])
    current = ctx.state.market.get(suit)
    junk = [i for i in ctx.state.junk if is_suit(i, suit)] if current is None or not current.res else []
    card = yield from actions.pick_card(f"Swap a {suit} from the Junk into the Market?", junk, optional=True,
                                        none_label="No")
    if card:
        yield from actions.swap_junk_with_market(card)
    yield from actions.draw_from_discard(lambda i: is_suit(i, suit), f"a {suit}", optional=True)


@operation("3PIK05", 1, uses=[A.DRAW, A.PUT])
def telepathic_vision(ctx, actions):
    """PLAY: Draw 2 cards for each Telepath you have in play (max 6 cards), then put 1 card on the top of your deck for
    each Telepath you have in play."""
    n = count_traits(ctx, "Telepath")
    if n:
        yield from actions.draw(min(6, 2 * n))
    for k in range(1, n + 1):
        card = yield from actions.pick_card(f"Put a card on top of your deck ({k} of {n}).",
                                            [i for i in ctx.me.hand if i is not ctx.this_card])
        if not card:
            break
        yield from actions.put_on_deck(card)

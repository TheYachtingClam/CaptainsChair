"""1BUR14 Grudge (Cargo). Spec: resources/scans/base_game/cards/captains/burnham/1BUR14.md"""

from engine.cards import operation
from engine.ops import A

from ._util import others_in_hand

BOOKER, BOOKS_SHIP = "1BUR23", "1BUR15"


@operation("1BUR14", 0, uses=[A.FREE_PLAY, A.BEAM, A.JUNK])
def she_is_a_queen(ctx, actions):
    """PLAY: You may free play Cleveland Booker or Book's ship. You may beam this card and another card to Book's
    ship. Junk a card from the Market."""
    friend = yield from actions.pick_card("Free play Cleveland Booker or Book's Ship?",
                                          actions.free_play_candidates(lambda i: i.card in (BOOKER, BOOKS_SHIP)),
                                          optional=True, none_label="No")
    if friend:
        yield from actions.free_play(friend)
    ship = next((s for s in ctx.me.fleet if s.card == BOOKS_SHIP), None)
    if ship is not None and others_in_hand(ctx) and (
            yield from actions.may("Beam Grudge and another card to Book's Ship?")):
        other = yield from actions.pick_card("Beam which other card to Book's Ship?", others_in_hand(ctx))
        yield from actions.beam(ctx.this_card, ship)
        yield from actions.beam(other, ship)
    yield from actions.junk()

"""1SHR12 Weytahn (Location). Spec: resources/scans/base_game/cards/captains/shran/1SHR12.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit, location_of_player, take_control_of_this

operation("1SHR12", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1SHR12", 1, uses=[A.FREE_PLAY])
def staging_ground(ctx, actions):
    """CONTROL: You may free play a Cargo or a Ship."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Cargo", "Ship"))
    card = yield from actions.pick_card("Free play a Cargo or a Ship?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("1SHR12", 2, uses=[A.DISMISS])
def abandoned(ctx, actions):
    """CLEAN-UP: If there are no [Away Team] here, dismiss this card. Ruling: your own Away Teams."""
    if ctx.away_at(ctx.this_card) == 0 and ctx.this_card in ctx.me.locations:
        yield from actions.dismiss(ctx.this_card)


def _martial(ctx, i):
    return has_trait(i, "Weapon") or ctx.has_specialty_icon(i, "military")


@operation("1SHR12", 3, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY],
           cost=[DiscardFromHand(1, _martial, "a Weapon or a card with a Military icon")])
def reinforce(ctx, actions):
    """ACTIVATION: Discard a card with at least one of Weapon/[Military]/[Military Focus] to send an [Away Team] here
    and gain 1 [Influence]."""
    yield from actions.send_away_team(1, target=ctx.this_card)
    yield from actions.gain_specialty("influence", 1)


@endgame("1SHR12")
def held(state, player):
    """ENDGAME: Score 4 [VP] if 2 or more [Away Team] are here."""
    loc = location_of_player(player, "1SHR12")
    return 4 if loc is not None and loc.away.get(player.seat, 0) >= 2 else 0

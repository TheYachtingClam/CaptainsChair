"""2SOV11 Paan Mokar (Location). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV11.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit


@operation("2SOV11", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2SOV11", 1, uses=[A.FREE_PLAY])
def supply_depot(ctx, actions):
    """CONTROL: You may free play a Cargo/Ship."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Cargo", "Ship"))
    card = yield from actions.pick_card("Free play a Cargo or Ship?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("2SOV11", 2, uses=[A.DISMISS])
def abandoned(ctx, actions):
    """CLEAN-UP: If there are no [Away Team] here, dismiss this card. Its own text allows dismissing a Location."""
    if ctx.this_card in ctx.me.locations and not ctx.away_at(ctx.this_card):
        yield from actions.dismiss(ctx.this_card)


def _military(ctx, i) -> bool:
    return has_trait(i, "Weapon") or ctx.has_specialty_icon(i, "military")


@operation("2SOV11", 3, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY],
           cost=[DiscardFromHand(1, _military, "a Weapon or a card with Military")])
def garrison(ctx, actions):
    """ACTIVATION: Discard a card with at least one of Weapon/[Military]/[Military Focus] to send an [Away Team] here
    and gain 1 [Influence]."""
    yield from actions.send_away_team(1, target=ctx.this_card)
    yield from actions.gain_specialty("influence", 1)


@endgame("2SOV11")
def held(state, player):
    """ENDGAME: Score 4 [VP] if 2 or more [Away Team] are here."""
    loc = next((i for i in player.locations if i.card == "2SOV11"), None)
    return 4 if loc is not None and loc.away.get(player.seat, 0) >= 2 else 0

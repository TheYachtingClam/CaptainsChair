"""Helpers shared with the base set. Registers nothing."""

from engine.cards.to_boldly_go._util import *  # noqa: F401,F403


def minus_unless_logged(points: int):
    """SPECIAL "If not logged, this card scores -N" for a Reward card's asterisk VP."""

    def score(state, player, inst):
        return 0 if any(i.uid == inst.uid for i in player.log) else -points

    return score


def status_of(player, card_id: str):
    """A player's Status card with this id, if they have it (Pike's Improbable, Unstoppable, Sensational)."""
    return next((i for i in player.status if i.card == card_id), None)

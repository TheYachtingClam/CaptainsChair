"""Helpers shared with the base set. Registers nothing."""

from engine.cards.to_boldly_go._util import *  # noqa: F401,F403


def minus_unless_logged(points: int):
    """SPECIAL "If not logged, this card scores -N" for a Reward card's asterisk VP."""

    def score(state, player, inst):
        return 0 if any(i.uid == inst.uid for i in player.log) else -points

    return score

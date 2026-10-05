"""Five-Year Mission, the solo campaign: the rules that need no database (requirements/22-solo-mode.md §14).

The server keeps the campaign record (app/campaigns.py); this module decides ranks, the Bot's difficulty, which cards
can be reinforced, and the final evaluation.
"""

from __future__ import annotations

import re

from engine.content import MARKET_SUITS, content
from engine.state import GameState, Player

RANKS = ("ensign", "lieutenant", "commander", "captain", "commodore", "admiral")  # REQ-CAMP-07
MODES = ("set_phasers_to_stun", "yellow_alert", "gates_of_sto_vo_kor", "kobayashi_maru")  # REQ-CAMP-03, easiest first
MODE_NAMES = {
    "set_phasers_to_stun": "Set Phasers to Stun",
    "yellow_alert": "Yellow Alert",
    "gates_of_sto_vo_kor": "Gates of Sto'Vo'Kor",
    "kobayashi_maru": "The Kobayashi Maru",
}
ASSIGNMENTS = 10  # REQ-CAMP-01

# REQ-CAMP-10: the Bot's difficulty by the human's rank (rows) and campaign mode (columns).
DIFFICULTY = {
    "ensign": ("ensign", "lieutenant", "commander", "admiral"),
    "lieutenant": ("lieutenant", "commander", "captain", "admiral"),
    "commander": ("commander", "captain", "admiral", "admiral"),
    "captain": ("captain", "captain", "admiral", "admiral"),
    "commodore": ("captain", "admiral", "admiral", "admiral"),
}


def difficulty(rank: str, mode: str) -> str:
    return DIFFICULTY[rank][MODES.index(mode)]


def promoted(rank: str) -> str:
    """The next rank after a success (REQ-CAMP-07)."""
    return RANKS[min(RANKS.index(rank) + 1, len(RANKS) - 1)]


def finished(rank: str, assignments: int) -> bool:
    """The campaign ends at Admiral, or after 10 assignments (REQ-CAMP-01)."""
    return rank == "admiral" or assignments >= ASSIGNMENTS


def evaluation(rank: str, assignments: int) -> str:
    """The performance review for the final rank (§14.5)."""
    if rank == "admiral":
        if assignments <= 6:
            return "The Legends: Archer, Kirk, Picard, you…"
        if assignments <= 8:
            return "Section 31 will be in touch…"
        return "Welcome to Starfleet Command!"
    return {
        "ensign": "You are like an eternal Harry Kim.",
        "lieutenant": "You are like Picard, but in a blue shirt.",
        "commander": "You are far from the bones of your ancestors.",
        "captain": "The California-class needs captains, too…",
        "commodore": "You'll be leading a backwater sector…",
    }[rank]


# =========================================================================== upgrades (REQ-CAMP-24 to -26)


def restriction(bot_crew: str, won: bool) -> str | None:
    """The common card types option A allows after facing this Bot: its upgrade card's WIN or LOSS line."""
    crew = content().command.get(bot_crew)
    if crew is None:
        return None
    return (crew.upgrades.win if won else crew.upgrades.loss).reinforce


def matches_restriction(card_id: str, text: str) -> bool:
    """Whether a card fits an upgrade line such as "Telepath / [Research]" or "Cargo (except Helmet)"."""
    from engine.bot.actions import card_matches
    from engine.state import Inst

    inst = Inst(uid="probe", card=card_id)
    excluded = re.findall(r"\(except ([^)]+)\)", text)
    text = re.sub(r"\s*\(except [^)]+\)", "", text)
    if any(card_matches(inst, term.strip()) for group in excluded for term in group.split("/")):
        return False
    return any(card_matches(inst, term.strip()) for term in text.split("/") if term.strip())


def can_be_reinforced(card_id: str) -> bool:
    """Only common Market cards; never an Encounter, an Incident or a common Location (REQ-CAMP-24)."""
    card = content().cards[card_id]
    return card.is_common and card.suit in MARKET_SUITS


def option_a_cards(state: GameState, player: Player, bot_crew: str, won: bool) -> list[str]:
    """Option A (REQ-CAMP-25): the Market cards the human had in that game that match the Bot's restriction. One
    entry per card id, in a stable order."""
    from engine.scoring import owned_cards

    line = restriction(bot_crew, won)
    if not line:
        return []
    seen: dict[str, None] = {}
    for inst in owned_cards(player):
        if can_be_reinforced(inst.card) and matches_restriction(inst.card, line):
            seen.setdefault(inst.card, None)
    return sorted(seen)

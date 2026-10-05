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


def option_b(bot_crew: str, won: bool, challenges=()) -> list[str]:
    """Option B (REQ-CAMP-25): the alternative bonuses of the Bot just faced, as bonus keys. Rules of Acquisition
    takes them away after a success. Only bonuses with code are offered (Khan's wait with his deck)."""
    from engine import upgrades

    if won and "rules_of_acquisition" in challenges:
        return []
    crew = content().command.get(bot_crew)
    if crew is None:
        return []
    upgrades.load()
    side = "win" if won else "loss"
    keys = [upgrades.key(bot_crew, side, i) for i in range(len((crew.upgrades.win if won else crew.upgrades.loss).bonuses))]
    return [k for k in keys if k in upgrades.BOOSTS or k in upgrades.REINFORCES]


def reinforce_pools(bonus_key: str, deck_id: str, reinforcement=()) -> list[list[str]]:
    """The cards a REINFORCE bonus offers: the human's own crew cards, by pool, not already in the Reinforcement
    pile, and never an Encounter or an Incident (REQ-CAMP-24)."""
    from engine import upgrades

    upgrades.load()
    cards = [c for c in content().crew_deck(deck_id) if not c.id.endswith("B")]
    pools = upgrades.REINFORCES[bonus_key].fn(cards)
    return [[c.id for c in pool if c.id not in reinforcement and c.suit not in ("Encounter", "Incident")]
            for pool in pools]


# =========================================================================== challenges (§14.4)

CHALLENGES = {
    "live_long_and_prosper": "Live Long and Prosper",
    "not_a_weakness": "That Is Not a Weakness; That Is Life",
    "two_weeks": "Two Weeks to the Closest Outpost",
    "baby_gazelle": "Running Like a Baby Gazelle",
    "rules_of_acquisition": "Rules of Acquisition",
    "only_ship": "Only Ship in the Quadrant",
    "arrive_on_tuesday": "They Will Arrive on Tuesday",
}
CHALLENGE_RULES = {
    "live_long_and_prosper": "After a success, start the next game with no Dilithium or no Latinum (your choice); after "
                             "another, with neither. A failure resets it.",
    "not_a_weakness": "From Lieutenant on: your Reserve deck is dealt at random from your Reserve and Available cards.",
    "two_weeks": "After a success, Reinforce is shuffled into your Reserve deck instead of your starting deck.",
    "baby_gazelle": "After two successes in a row, an Incident is shuffled into your starting deck, until a failure.",
    "rules_of_acquisition": "After a success, option B is not available. With no matching card there is no upgrade.",
    "only_ship": "If your starting Ship is ever dismissed or recalled, you fail the assignment at once.",
    "arrive_on_tuesday": "One Away Team (two after a success) is set aside until your Reserve deck empties.",
}


def available_challenges(deck_id: str) -> list[str]:
    """REQ-CAMP-41: Only Ship in the Quadrant needs a starting deployed Ship; They Will Arrive on Tuesday a Reserve
    deck."""
    cards = content().crew_deck(deck_id)
    out = list(CHALLENGES)
    if not any(c.position == "Deployed" and c.suit == "Ship" for c in cards):
        out.remove("only_ship")
    if not any(c.position == "Reserve" for c in cards):
        out.remove("arrive_on_tuesday")
    return out


def win_streak(outcomes) -> int:
    """Successes in a row at the end of the campaign so far."""
    n = 0
    for outcome in reversed(list(outcomes)):
        if outcome != "win":
            break
        n += 1
    return n


def needs_resource_choice(outcomes, challenges) -> bool:
    """Live Long and Prosper after exactly one success: the human picks which resource to start without."""
    return "live_long_and_prosper" in challenges and win_streak(outcomes) == 1


def game_setup(rank: str, outcomes, challenges, boosts, drop: str | None = None):
    """The next game's CampaignSetup: Boosts and what each chosen challenge does to it (REQ-CAMP-40)."""
    from engine.setup import CampaignSetup

    streak = win_streak(outcomes)
    after_success = streak > 0
    live_long = "live_long_and_prosper" in challenges
    return CampaignSetup(
        boosts=tuple(boosts),
        no_dilithium=live_long and (streak >= 2 or (streak == 1 and drop != "latinum")),
        no_latinum=live_long and (streak >= 2 or (streak == 1 and drop == "latinum")),
        mixed_reserve="not_a_weakness" in challenges and rank != "ensign",
        reinforce_in_reserve="two_weeks" in challenges and after_success,
        extra_incident="baby_gazelle" in challenges and streak >= 2,
        only_ship="only_ship" in challenges,
        teams_aside=(2 if after_success else 1) if "arrive_on_tuesday" in challenges else 0,
    )


def setup_notes(setup) -> list[str]:
    """What the challenges do to the next game, for the campaign screen."""
    notes = []
    if setup.no_dilithium and setup.no_latinum:
        notes.append("You start with no Dilithium and no Latinum.")
    elif setup.no_dilithium or setup.no_latinum:
        notes.append("You start without Dilithium or without Latinum (you choose).")
    if setup.mixed_reserve:
        notes.append("Your Reserve deck is dealt at random from your Reserve and Available cards.")
    if setup.reinforce_in_reserve:
        notes.append("Reinforce goes into your Reserve deck.")
    if setup.extra_incident:
        notes.append("An Incident is shuffled into your starting deck.")
    if setup.only_ship:
        notes.append("Losing your starting Ship fails the assignment.")
    if setup.teams_aside:
        notes.append(f"{setup.teams_aside} Away Team(s) are set aside until your Reserve deck empties.")
    return notes

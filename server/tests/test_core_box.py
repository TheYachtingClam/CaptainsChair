"""Choosing a box and combining boxes (requirements/23-core-box.md §2, §3; plans/base-game.md Step 4)."""

from collections import Counter

import pytest

from engine.content import content
from engine.setup import BOXES, SeatSetup, SetupError, common_cards, new_game

CARDS = content().cards


def game(box, decks=("picard", "sisko"), expansions=(), promos=False, seed=4):
    return new_game(seed, "two_player", [SeatSetup(d.capitalize(), d, "basic") for d in decks], list(expansions), promos,
                    box=box)


def market(s):
    return [i for deck in s.market_decks.values() for i in deck] + [i for i in s.market.values() if i] + s.junk


def common_ids(s):
    """Every common card in the game's shared decks."""
    return {i.card for i in [*market(s), *s.location_deck, *s.neutral, *s.encounter, *s.incident] if CARDS[i.card].is_common}


def test_the_default_box_is_to_boldly_go():
    a = new_game(9, "two_player", [SeatSetup("Kirk", "kirk", "basic"), SeatSetup("Soval", "soval", "basic")])
    b = game("to_boldly_go", ("kirk", "soval"), seed=9)
    assert a.box == "to_boldly_go" and a.model_dump() == b.model_dump()
    assert {CARDS[c].set for c in common_ids(a)} == {"to_boldly_go"} and a.junk == []


def test_an_unknown_box_is_refused():
    with pytest.raises(SetupError):
        game("deluxe")


def test_core_box_uses_only_core_common_cards_and_the_old_versions():
    """REQ-CORE-11, -21, -27: all Core Box common cards, the Junk empty, 6 Incidents."""
    s = game("core")
    assert {CARDS[c].set for c in common_ids(s)} == {"base_game"}
    assert Counter(CARDS[i.card].suit for i in market(s)) == {"Ally": 13, "Cargo": 16, "Person": 25, "Ship": 13}
    assert len(s.encounter) == 8 and len(s.incident) == 6 and s.junk == []
    assert "1CAR11" in common_ids(s) and "2CAR14" not in common_ids(s)  # CORE-AS-2: the old Phasers
    assert s.stardates and all(CARDS[i.card].set == "to_boldly_go" for i in s.stardates)  # REQ-CORE-03


def test_combined_setup_counts():
    """CORE-AS-1 (REQ-CORE-20 to -24)."""
    s = game("both", ("picard", "kirk"))
    assert Counter(CARDS[i.card].suit for i in market(s)) == {"Ally": 21, "Cargo": 24, "Person": 42, "Ship": 18}
    assert len(s.junk) == 4 and len({CARDS[i.card].suit for i in s.junk}) == 4
    assert len(s.location_deck) == 16 and len(s.neutral) == 3  # 15 Advanced and 4 of the 14 Starting Locations
    assert len(s.encounter) == 13
    assert len([i for i in s.incident if CARDS[i.card].is_common]) == 6


def test_combined_keeps_one_copy_of_a_reprint_and_only_the_new_version():
    """REQ-CORE-20, -21 and CORE-AS-2."""
    cards = [c for c in common_cards(content(), "both", [], False) if c.suit != "Stardate"]
    ids = {c.id for c in cards}
    names = Counter(c.name for c in cards)
    assert max(names.values()) == 1, [n for n, k in names.items() if k > 1]
    assert "2CAR14" in ids and "1CAR11" not in ids  # Phasers: the To Boldly Go version
    assert "2PER16" in ids and "1PER19" not in ids  # Riva: the To Boldly Go printing
    assert {"1INC01", "1INC04"} <= ids  # Energy Drain and Red Alert have twins only in Crew decks, so they stay
    assert len(cards) == 105 + 29 + 13 + 8


def test_combined_incidents_are_cut_at_random():
    kept = {frozenset(i.card for i in game("both", seed=seed).incident if CARDS[i.card].is_common) for seed in range(12)}
    assert all(len(k) == 6 for k in kept) and len(kept) > 1


def test_second_contact_seeds_the_junk_again_and_crew_cards_are_never_removed():
    """REQ-CORE-24, -26."""
    s = game("both", ("picard", "burnham"), ["second_contact"])
    assert len(s.junk) == 8
    burnham = s.players[1]
    owned = [*burnham.draw, *burnham.hand, *burnham.reserve, *burnham.development, *burnham.fleet, *burnham.status]
    assert len(owned) + 1 + 1 == 26  # her Captain, and Subspace Phenomenon in the Incident deck
    assert any(i.card == "1BUR26" for i in s.incident)


def test_boxes_name_the_sets_of_their_crew_decks():
    assert BOXES == {"core": ("base_game",), "to_boldly_go": ("to_boldly_go",), "both": ("base_game", "to_boldly_go")}

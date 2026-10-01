"""Checks the generated card and board data against the rulebooks and CLAUDE.md."""

import re
from collections import Counter
from pathlib import Path

import pytest

from engine.content import MARKET_SUITS, load_content

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def data():
    return load_content()


def test_card_counts(data):
    by_set = Counter(c.set for c in data.cards.values())
    assert by_set == {"to_boldly_go": 170, "second_contact": 20, "promo2": 5}


def test_crew_deck_sizes_match_rulebook(data):
    # To Boldly Go rulebook p. 2
    assert len(data.crew_deck("georgiou")) == 23
    assert len(data.crew_deck("soval")) == 24


def test_each_crew_deck_has_one_captain(data):
    for deck in ("georgiou", "soval"):
        assert [c.suit for c in data.crew_deck(deck)].count("Captain") == 1


def test_common_counts_in_to_boldly_go(data):
    common = Counter(c.suit for c in data.by_set("to_boldly_go") if c.is_common)
    assert common["Cargo"] == 18
    assert common["Person"] == 26
    assert common["Ship"] == 13
    assert common["Encounter"] == 8
    assert common["Incident"] == 6
    assert common["Location"] == 20
    assert common["Stardate"] == 32


def test_box_markers_match_set_codes(data):
    for card in data.cards.values():
        marker = {"•": "duplicate", "†": "replacement"}.get(card.set_code[-1])
        assert card.box_marker == marker, card.id
    assert Counter(c.box_marker for c in data.cards.values())["replacement"] == 9


def test_crew_cards_have_a_start_position(data):
    for card in data.cards.values():
        if not card.is_common and card.suit not in ("Captain", "Status"):
            assert card.position, card.id


def test_common_locations_are_starting_or_advanced(data):
    for card in data.cards.values():
        if card.is_common and card.suit == "Location":
            assert card.position in ("Starting Location", "Advanced Location"), card.id


def test_stardate_piles(data):
    for mode, size in [("2-Player", 5), ("Solo Cadet Practice", 2), ("Solo vs Ensign Bot", 5), ("Solo vs Admiral Bot", 5)]:
        pile = data.stardates(mode)
        assert [c.sequence for c in pile] == list(range(1, size + 1)), mode
        assert all(c.starting_glory for c in pile)


def test_operations_only_use_listed_actions(data):
    claude = (ROOT / "CLAUDE.md").read_text()
    allowed = set(re.findall(r"`(?:A\.)?([A-Z_]+)`", claude))
    for card in data.cards.values():
        for op in card.operations:
            assert set(op.uses) <= allowed, (card.id, op.kind, set(op.uses) - allowed)


def test_every_card_has_an_image(data):
    import json

    manifest = json.loads((ROOT / "server/content/images/manifest.json").read_text())["images"]
    missing = [c.id for c in data.cards.values() if c.image not in manifest]
    assert missing == []


def test_boards(data):
    assert set(data.boards) == {"cb-soval-basic", "cb-soval-advanced", "cb-georgiou-basic", "cb-georgiou-advanced"}
    basic = data.board("georgiou", "basic")
    assert basic.control_max == 1 and basic.actions == 3
    assert basic.mission_completion_tokens == 1
    assert data.board("soval", "advanced").mission_completion_tokens == 3
    assert [m.vp for m in data.board("soval", "advanced").missions] == [2, 4, 3]


def test_track_multipliers(data):
    basic = data.board("georgiou", "basic")
    assert basic.multiplier("influence", 0) == 1
    assert basic.multiplier("influence", 12) == 5
    assert basic.multiplier("military", 15) == 5
    advanced = data.board("soval", "advanced")
    assert advanced.multiplier("research", 1) == 0  # Advanced sides start at x0
    assert advanced.multiplier("influence", 9) == 3


def test_market_suits_known(data):
    assert set(MARKET_SUITS) <= {c.suit for c in data.cards.values()} | {"Ally"}

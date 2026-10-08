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
    assert by_set == {"to_boldly_go": 282, "second_contact": 99, "promo2": 6, "base_game": 250, "promo1": 5}


def test_crew_deck_sizes_match_rulebook(data):
    # To Boldly Go rulebook p. 2 and Second Contact p. 2. Khan's two double-sided cards count once each.
    sizes = {"georgiou": 23, "soval": 24, "archer": 23, "kirk": 25, "rebner": 22, "khan": 22,
             "pike": 26, "riker": 25, "freeman": 25}
    for deck, size in sizes.items():
        cards = [c for c in data.crew_deck(deck) if not c.id.endswith("B")]
        assert len(cards) == size, deck


def test_each_crew_deck_has_one_captain(data):
    for deck in ("georgiou", "soval", "archer", "kirk", "rebner", "pike", "riker", "freeman"):
        assert [c.suit for c in data.crew_deck(deck)].count("Captain") == 1, deck
    assert [c.id for c in data.crew_deck("khan") if c.suit == "Captain"] == ["2KHA01A", "2KHA01B"]


def test_common_counts_in_to_boldly_go(data):
    common = Counter(c.suit for c in data.by_set("to_boldly_go") if c.is_common)
    assert common["Ally"] == 16
    assert common["Cargo"] == 18
    assert common["Person"] == 26
    assert common["Ship"] == 13
    assert common["Encounter"] == 8
    assert common["Incident"] == 6
    assert common["Location"] == 20
    assert common["Stardate"] == 32


def test_box_markers_match_set_codes(data):
    for card in data.cards.values():
        if card.set == "base_game":
            continue  # the marks are on the To Boldly Go cards; Mirok's printed dagger (1PER15) replaces nothing here
        marker = {"•": "duplicate", "†": "replacement"}.get(card.set_code[-1])
        assert card.box_marker == marker, card.id
    assert Counter(c.box_marker for c in data.cards.values())["replacement"] == 9


def test_crew_cards_have_a_start_position(data):
    for card in data.cards.values():
        if not card.is_common and card.suit not in ("Captain", "Status") and not card.id.endswith("B"):
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
    assert len(data.boards) == 29  # 17, and two sides for each of the six Core Box Crews
    assert data.board("khan", "advanced").trait_slots == 12
    assert data.board("khan", "advanced").tracks == {}
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


def test_rebner_has_no_research_or_influence_multipliers(data):
    for side in ("basic", "advanced"):
        board = data.board("rebner", side)
        assert board.multiplier("research", 15) == 0
        assert board.multiplier("influence", 15) == 0


def test_market_suits_known(data):
    assert set(MARKET_SUITS) <= {c.suit for c in data.cards.values()} | {"Ally"}


def test_core_box_reprints_and_old_versions_point_at_their_to_boldly_go_cards(data):
    """REQ-CS-31: To Boldly Go reprints 45 Core Box cards and replaces 9."""
    core = [c for c in data.cards.values() if c.set == "base_game" and c.is_common]
    reprints = {c.same_as for c in core if c.same_as and data.cards[c.same_as].box_marker == "duplicate"}
    replaced = {c.replaced_by for c in core if c.replaced_by}
    assert reprints == {c.id for c in data.cards.values() if c.box_marker == "duplicate"} and len(reprints) == 45
    assert replaced == {c.id for c in data.cards.values() if c.box_marker == "replacement"} and len(replaced) == 9
    assert Counter(c.suit for c in core) == {"Ally": 13, "Cargo": 16, "Person": 25, "Ship": 13, "Location": 20,
                                             "Encounter": 8, "Incident": 6, "Directive": 2}


def test_core_box_crew_deck_sizes(data):
    sizes = {"burnham": 26, "sisko": 25, "picard": 24, "shran": 24, "koloth": 24, "sela": 24}
    for deck, size in sizes.items():
        cards = data.crew_deck(deck)
        assert len(cards) == size, deck
        assert [c.suit for c in cards].count("Captain") == 1, deck
        assert sorted(int(c.id[-2:]) for c in cards) == list(range(1, size + 1)), deck


def test_core_box_boards_and_command_cards(data):
    for crew in ("burnham", "koloth", "picard", "sela", "shran", "sisko"):
        basic, advanced = data.board(crew, "basic"), data.board(crew, "advanced")
        assert len(basic.missions) == 1 and len(advanced.missions) == 3, crew
        assert advanced.missions[0].id == basic.missions[0].id and advanced.missions[0].reward == basic.missions[0].reward, crew
        for track in ("research", "influence", "military"):  # the Advanced side is one multiplier lower, from its first step
            assert {k: v + 1 for k, v in advanced.tracks[track].items()} == {k: v for k, v in basic.tracks[track].items() if k}, (crew, track)
        command = data.command[crew]
        assert [len(command.side(s).rows) for s in ("no_duty_officer", "with_duty_officer")] == [8, 8], crew
        assert len(command.upgrades.win.bonuses) == 2 and len(command.upgrades.loss.bonuses) == 2, crew
    assert [m.vp for m in data.board("burnham", "advanced").missions] == [4, 3, 6]

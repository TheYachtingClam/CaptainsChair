"""The strict registry test (plans/card-implementation.md Step 19): every printed operation and every Crew board
mission has code, except what waits on purpose.

Waiting on purpose:
- solo-only cards and SURPRISE operations, which need the Bot (requirements/22-solo-mode.md) and are covered by the
  Bot tests;
- Stardate WHEN EMPTIED and STARDATE RESOLUTION, which the engine runs itself;
- the Core Box Crew decks (`WAITING_SETS`), until plans/base-game.md writes their code."""

from engine import cards as registry
from engine.content import content

ENGINE_KINDS = {"WHEN EMPTIED", "STARDATE RESOLUTION"}


WAITING_SETS = {"base_game"}  # the Core Box Crew decks: specs are written, code comes in plans/base-game.md Steps 7 to 12
WAITING_BOTS = {"burnham", "koloth", "picard", "sela", "shran", "sisko"}  # Bot rows: Step 13
WAITING_CREWS = WAITING_BOTS - {"picard"}  # Crew cards and missions: Steps 7 to 12, one Crew at a time


def _waits(card) -> bool:
    return (card.position or "").startswith("Solo") or (card.set in WAITING_SETS and card.deck in WAITING_CREWS)


def test_every_printed_operation_has_code():
    missing = []
    for card in content().cards.values():
        if _waits(card):
            continue
        for index, op in enumerate(card.operations):
            if op.kind in ENGINE_KINDS or op.kind == "SURPRISE":
                continue
            if not registry.has_code(card.id, index, op.kind):
                missing.append(f"{card.id} {card.name}: {index} {op.kind}")
    assert not missing, missing


def test_every_mission_has_a_goal_and_a_reward():
    missing = []
    for board in content().boards.values():
        if board.captain in WAITING_CREWS:
            continue
        for mission in board.missions:
            impl = registry.MISSIONS.get(mission.id)
            if impl is None or impl.goal is None or impl.reward is None:
                missing.append(f"{board.id}: {mission.id}")
    assert not missing, missing


def test_only_waiting_cards_lack_code():
    """Every PLAY outside the solo-only cards has code, so nothing reaches the 'not implemented yet' note."""
    from engine.ops import legal
    from tests.scenario import given

    s = given(deck="georgiou")
    player = s.players[0]
    for card in content().cards.values():
        if _waits(card):
            continue
        inst = s.new_inst(card.id)
        for index, op in enumerate(card.operations):
            if op.kind == "PLAY":
                assert registry.OPS.get((card.id, index)) is not None, (card.id, index)
                legal(s, player, inst, index)  # never the placeholder path


def test_every_bot_row_has_code():
    """Every Automated Command row of every Bot Crew has a function, except the SURPRISE reminder rows, which resolve
    the card's own SURPRISE operation (requirements/22-solo-mode.md §6)."""
    from engine import bot as bot_rules

    missing = []
    for crew, data in content().command.items():
        if crew in WAITING_BOTS:
            continue
        for side in data.sides:
            for r in side.rows:
                if "Surprise" not in r.matches and (crew, side.side, r.number) not in bot_rules.ROWS:
                    missing.append(f"{crew} {side.side} {r.number}")
    assert not missing, missing

"""Central setup (requirements/03-central-setup.md) and player setup (04-player-setup.md)."""

from __future__ import annotations

from dataclasses import dataclass

from engine.content import MARKET_SUITS, Card, content
from engine.state import GameState, Inst, Player

BASE_SET = "to_boldly_go"
STARDATE_MODE = {"two_player": "2-Player", "cadet": "Solo Cadet Practice"}
SOLO_ONLY = {"Solo Challenge", "Solo Campaign"}  # Reinforce, Time Is Running Out
SUBSPACE_RHAPSODY = "0INC03"


@dataclass(frozen=True)
class SeatSetup:
    name: str
    deck: str
    board_side: str


class SetupError(ValueError):
    pass


def new_game(seed: int, mode: str, seats: list[SeatSetup], expansions: list[str] | None = None, promos: bool = False) -> GameState:
    if mode not in STARDATE_MODE:
        raise SetupError(f"Mode {mode!r} is not supported by the engine yet")
    expected = 2 if mode == "two_player" else 1
    if len(seats) != expected:
        raise SetupError(f"Mode {mode} needs {expected} player(s)")
    expansions = list(expansions or [])
    data = content()
    sets = {BASE_SET, *expansions} | ({"promo2"} if promos else set())

    # Players are created first so their captains exist; central setup follows the rulebook order.
    state = GameState(seed=seed, mode=mode, expansions=expansions, promos=promos, players=[], first_seat=0, active=0)
    common = [c for c in data.cards.values() if c.is_common and c.set in sets and c.position not in SOLO_ONLY]

    _central_setup(state, common, data)
    for seat, choice in enumerate(seats):
        state.players.append(_player_setup(state, seat, choice, data))
    state.shuffle(state.incident)  # after Crew cards marked Incident Deck were added (REQ-PS-11)

    state.first_seat = state.rng().randrange(len(state.players))  # REQ-CS-17
    state.active = state.first_seat
    for player in state.players:
        from engine.game import draw, hand_size  # local import: game imports setup

        draw(state, player, hand_size(state, player), announce=False)
    state.emit(f"{state.players[state.first_seat].name} takes the Starting Player token.")
    return state


# --------------------------------------------------------------------------- central


def _insts(state: GameState, cards: list[Card]) -> list[Inst]:
    return [state.new_inst(c.id) for c in sorted(cards, key=lambda c: c.id)]


def _central_setup(state: GameState, common: list[Card], data) -> None:
    by_suit = lambda suit: [c for c in common if c.suit == suit and c.position != "Rewards"]  # noqa: E731

    # Market decks and slots (REQ-CS-02, -03, -07)
    for suit in MARKET_SUITS:
        deck = _insts(state, by_suit(suit))
        state.shuffle(deck)
        state.market_decks[suit] = deck
    state.encounter = _insts(state, by_suit("Encounter"))
    state.shuffle(state.encounter)

    incidents = by_suit("Incident")
    if any(c.id == SUBSPACE_RHAPSODY for c in incidents):
        # Its SPECIAL replaces a random Incident (REQ-CS-22).
        others = [c for c in incidents if c.id != SUBSPACE_RHAPSODY]
        removed = others[state.rng().randrange(len(others))]
        incidents = [c for c in incidents if c.id != removed.id]
    state.incident = _insts(state, incidents)

    for suit in MARKET_SUITS:
        refill_market(state, suit, announce=False)

    # Second Contact seeds the Junk with one card per Market deck (REQ-EXP-12).
    if "second_contact" in state.expansions:
        for suit in MARKET_SUITS:
            if state.market_decks[suit]:
                state.junk.append(state.market_decks[suit].pop(0))
        state.rewards = _insts(state, [c for c in common if c.position == "Rewards"])

    # Locations (REQ-CS-08 to REQ-CS-10)
    starting = _insts(state, [c for c in common if c.suit == "Location" and c.position == "Starting Location"])
    advanced = _insts(state, [c for c in common if c.suit == "Location" and c.position == "Advanced Location"])
    state.shuffle(starting)
    state.shuffle(advanced)
    state.location_deck = [starting.pop(0)] + advanced if starting else advanced
    state.neutral = starting[:3]

    # Stardates (REQ-CS-11, REQ-CS-13)
    pile = data.stardates(STARDATE_MODE[state.mode])
    state.stardates = [state.new_inst(c.id) for c in pile]
    state.stardate_glory = pile[0].starting_glory or 0 if pile else 0


def refill_market(state: GameState, suit: str, *, announce: bool = True) -> None:
    if state.market.get(suit) is None and state.market_decks.get(suit):
        card = state.market_decks[suit].pop(0)
        state.market[suit] = card
        if announce:
            state.emit(f"{content().cards[card.card].name} is revealed in the Market.", irreversible=True)
    else:
        state.market.setdefault(suit, None)


# --------------------------------------------------------------------------- player


def _player_setup(state: GameState, seat: int, choice: SeatSetup, data) -> Player:
    cards = [c for c in data.crew_deck(choice.deck) if not c.id.endswith("B")]  # B sides of double-sided cards
    if not cards:
        raise SetupError(f"Unknown Crew deck {choice.deck!r}")
    board = data.board(choice.deck, choice.board_side)
    captain_card = next(c for c in cards if c.suit == "Captain")
    player = Player(seat=seat, name=choice.name, deck=choice.deck, board=board.id, captain=state.new_inst(captain_card.id))
    player.mission_tokens = board.mission_completion_tokens
    player.actions = board.actions

    by_position: dict[str | None, list[Card]] = {}
    for card in cards:
        if card.suit == "Captain":
            continue
        by_position.setdefault(card.position, []).append(card)

    player.status = _insts(state, [c for c in by_position.pop(None, []) if c.suit == "Status"])  # REQ-PS-05
    player.draw = _insts(state, by_position.pop("Available", []))
    state.shuffle(player.draw)  # REQ-PS-06
    player.development = _insts(state, by_position.pop("Development", []))
    player.reserve = _insts(state, by_position.pop("Reserve", []))
    state.shuffle(player.reserve)  # REQ-PS-08
    player.locations = _insts(state, by_position.pop("Controlled Location", []))
    player.fleet = _insts(state, by_position.pop("Deployed", []))
    state.incident.extend(_insts(state, by_position.pop("Incident Deck", [])))
    player.discard = _insts(state, by_position.pop("Discard", []))
    if by_position:
        raise SetupError(f"{choice.deck}: cards with unexpected positions {sorted(map(str, by_position))}")

    player.dilithium = player.latinum = player.glory = 1  # REQ-PS-13, from the supply

    teams = captain_card.away_teams
    count = int(str(teams).rstrip("+")) if teams is not None else 0
    player.away_pool = count  # REQ-PS-14
    if choice.deck == "archer":
        player.away_aside = 4  # REQ-CD-ARC-01
    if choice.deck == "pike":
        starbase = next(i for i in player.locations if i.card == "3PIK03")
        starbase.away[seat] = 1  # REQ-EXP-PIK-01
    return player

"""Central setup (requirements/03-central-setup.md) and player setup (04-player-setup.md)."""

from __future__ import annotations

from dataclasses import dataclass

from engine.content import MARKET_SUITS, Card, content
from engine.state import GameState, Inst, Player

BASE_SET = "to_boldly_go"
CORE_SET = "base_game"
# The box a game is played with (REQ-CORE-10, -11): its common cards, and the sets its Crew decks may come from.
BOXES = {"core": (CORE_SET,), "to_boldly_go": (BASE_SET,), "both": (CORE_SET, BASE_SET)}
DEFAULT_BOX = "to_boldly_go"
COMBINED_INCIDENTS = 6  # REQ-CORE-23
STARDATE_MODE = {"two_player": "2-Player", "cadet": "Solo Cadet Practice", "solo": "Solo vs {difficulty} Bot"}
DIFFICULTIES = ("ensign", "lieutenant", "commander", "captain", "admiral")  # REQ-SOLO-10, easiest first
# Crews whose Bot is not written yet: the Core Box Crews, until plans/base-game.md Step 13.
BOT_UNAVAILABLE: set[str] = {"burnham", "koloth", "picard", "sela", "shran", "sisko"}
TIME_IS_RUNNING_OUT = "2DIR01"
REINFORCE = "2DIR02"
SOLO_ONLY = {"Solo Challenge", "Solo Campaign"}  # Reinforce, Time Is Running Out
SUBSPACE_RHAPSODY = "0INC03"


@dataclass(frozen=True)
class SeatSetup:
    name: str
    deck: str
    board_side: str
    reinforcement: tuple[str, ...] = ()  # Five-Year Mission: card ids in the Reinforcement pile (REQ-CAMP-20)
    campaign: CampaignSetup | None = None


@dataclass(frozen=True)
class CampaignSetup:
    """A Five-Year Mission game's extras for the human (requirements/22-solo-mode.md §14), worked out by
    engine/campaign.py from the campaign record: Boosts and the challenges' effects on this game."""

    boosts: tuple[str, ...] = ()  # bonus keys, e.g. "pike:win:1" (REQ-CAMP-30)
    no_dilithium: bool = False  # Live Long and Prosper
    no_latinum: bool = False
    mixed_reserve: bool = False  # That Is Not a Weakness; That Is Life
    reinforce_in_reserve: bool = False  # Two Weeks to the Closest Outpost
    extra_incident: bool = False  # Running Like a Baby Gazelle
    only_ship: bool = False  # Only Ship in the Quadrant
    teams_aside: int = 0  # They Will Arrive on Tuesday


@dataclass(frozen=True)
class BotSetup:
    """Solo mode: the Bot's Crew, difficulty and the optional Ticking Clock challenge (REQ-SRV-18)."""

    deck: str
    difficulty: str = "ensign"
    ticking_clock: bool = False


class SetupError(ValueError):
    pass


def common_cards(data, box: str, expansions: list[str], promos: bool) -> list[Card]:
    """The common cards of a game (REQ-CORE-11, -20, -21). With both boxes, a Core Box card that To Boldly Go reprints
    or replaces is left out, so one copy and only the new version remain."""
    sets = {*BOXES[box], *expansions} | ({"promo2"} if promos else set())
    cards = [c for c in data.cards.values() if c.is_common and c.set in sets and c.position not in SOLO_ONLY]
    if box == "both":
        def superseded(c: Card) -> bool:
            twin = data.cards.get(c.same_as or c.replaced_by or "")
            return c.set == CORE_SET and twin is not None and twin.is_common and twin.set in sets

        cards = [c for c in cards if not superseded(c)]
    return cards


def new_game(seed: int, mode: str, seats: list[SeatSetup], expansions: list[str] | None = None, promos: bool = False,
             bot: BotSetup | None = None, box: str = DEFAULT_BOX) -> GameState:
    if box not in BOXES:
        raise SetupError(f"Unknown box {box!r}")
    if mode not in STARDATE_MODE:
        raise SetupError(f"Mode {mode!r} is not supported by the engine yet")
    expected = 2 if mode == "two_player" else 1
    if len(seats) != expected:
        raise SetupError(f"Mode {mode} needs {expected} player(s)")
    if mode == "solo":
        if bot is None:
            raise SetupError("Solo mode needs a Bot")
        if bot.difficulty not in DIFFICULTIES:
            raise SetupError(f"Unknown difficulty {bot.difficulty!r}")
        if bot.deck in BOT_UNAVAILABLE or bot.deck not in content().command:
            raise SetupError(f"There is no {bot.deck!r} Bot yet")
    expansions = list(expansions or [])
    data = content()
    sets = {*BOXES[box], *expansions} | ({"promo2"} if promos else set())

    # Players are created first so their captains exist; central setup follows the rulebook order.
    state = GameState(seed=seed, mode=mode, expansions=expansions, promos=promos, players=[], first_seat=0, active=0,
                      difficulty=bot.difficulty if bot else None, box=box)
    common = common_cards(data, box, expansions, promos)

    _central_setup(state, common, data)
    for seat, choice in enumerate(seats):
        state.players.append(_player_setup(state, seat, choice, data))
    if mode == "solo":
        state.players.append(_bot_setup(state, len(state.players), bot, data))
    if mode == "cadet":
        for player in state.players:
            if data.boards[player.board].trait_order:
                # Khan in Cadet Training: a random other Captain sets his two opponent entries (REQ-CD-KHN-10).
                captains = sorted(c.id for c in data.cards.values()
                                  if c.suit == "Captain" and c.set in sets and c.deck != player.deck)
                player.rival_captain = captains[state.rng().randrange(len(captains))]
                state.emit(f"{player.name}'s two Opponent's Captain entries use the traits of "
                           f"{data.cards[player.rival_captain].name}.", seat=player.seat)
    state.shuffle(state.incident)  # after Crew cards marked Incident Deck were added (REQ-PS-11)
    for seat, choice in enumerate(seats):
        if choice.campaign and choice.campaign.extra_incident and state.incident:
            # Running Like a Baby Gazelle: one Incident from the Incident deck goes into the starting deck.
            player = state.players[seat]
            player.draw.append(state.incident.pop(0))
            state.shuffle(player.draw)

    # REQ-CS-17; in solo mode the human takes the Starting Player token (REQ-SOLO-21).
    state.first_seat = 0 if mode == "solo" else state.rng().randrange(len(state.players))
    state.active = state.first_seat
    for player in state.players:
        from engine.game import draw, hand_size  # local import: game imports setup

        if player.bot is None and not player.boosts:  # the Bot has no hand (REQ-SOLO-34)
            draw(state, player, hand_size(state, player), announce=False)
    if any(p.boosts for p in state.players):
        state.step = "setup"  # Boosts run around drawing the starting hand (game.step_setup)
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
    if state.box == "both":
        # Combined boxes: random Incidents go back to the box until 6 remain (REQ-CORE-23).
        incidents = sorted(incidents, key=lambda c: c.id)
        while len(incidents) > COMBINED_INCIDENTS:
            incidents.pop(state.rng().randrange(len(incidents)))
    if any(c.id == SUBSPACE_RHAPSODY for c in incidents):
        # Its SPECIAL replaces a random Incident (REQ-CS-22).
        others = [c for c in incidents if c.id != SUBSPACE_RHAPSODY]
        removed = others[state.rng().randrange(len(others))]
        incidents = [c for c in incidents if c.id != removed.id]
    state.incident = _insts(state, incidents)

    for suit in MARKET_SUITS:
        refill_market(state, suit, announce=False)

    # Combined boxes seed the Junk with one card per Market deck (REQ-CORE-24).
    if state.box == "both":
        for suit in MARKET_SUITS:
            if state.market_decks[suit]:
                state.junk.append(state.market_decks[suit].pop(0))

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
    pile = data.stardates(STARDATE_MODE[state.mode].format(difficulty=(state.difficulty or "").capitalize()))
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
    if choice.campaign:
        _campaign_setup(state, player, choice.campaign)
    if choice.reinforcement:
        # REQ-CAMP-29: the human's own cards in the Reinforcement pile start there instead of in their deck.
        for card_id in choice.reinforcement:
            for zone in (player.draw, player.reserve):
                own = next((i for i in zone if i.card == card_id), None)
                if own is not None:
                    zone.remove(own)
                    break
        # REQ-CAMP-21: with cards in the Reinforcement pile, Reinforce is shuffled into the starting deck.
        player.reinforcement = [state.new_inst(c) for c in choice.reinforcement]
        camp = choice.campaign
        deck = player.reserve if camp and camp.reinforce_in_reserve else player.draw  # Two Weeks to the Closest Outpost
        deck.append(state.new_inst(REINFORCE))
        state.shuffle(deck)
    return player


def _campaign_setup(state: GameState, player: Player, camp: CampaignSetup) -> None:
    """The challenges that change setup (requirements/22-solo-mode.md §14.4), and the Boosts to run."""
    player.boosts = list(camp.boosts)
    if camp.no_dilithium:
        player.dilithium = 0  # Live Long and Prosper
    if camp.no_latinum:
        player.latinum = 0
    if camp.mixed_reserve:
        # That Is Not a Weakness; That Is Life: a new Reserve deck of the same size, dealt from both piles.
        size = len(player.reserve)
        pool = player.reserve + player.draw
        state.shuffle(pool)
        player.reserve, player.draw = pool[:size], pool[size:]
    if camp.only_ship and player.fleet:
        player.only_ship = player.fleet[0].uid
    if camp.teams_aside:
        aside = min(camp.teams_aside, player.away_pool)
        player.away_pool -= aside
        player.teams_until_reserve_empty = aside


# --------------------------------------------------------------------------- the Bot (requirements/22-solo-mode.md §2)


def _bot_setup(state: GameState, seat: int, choice: BotSetup, data) -> Player:
    """REQ-SOLO-24 to -33: Basic board, no resources, actions or mission tokens; the Supplement deck (Reserves on top
    of Developments) and the Bot deck (Deployed and Controlled Location cards on top of the Available cards)."""
    from engine import bot as rules
    from engine.state import BotState

    removed = rules.SETUP_REMOVES.get(choice.deck, ())  # Khan: Ceti Alpha V and VI (REQ-CD-KHN-11)
    cards = [c for c in data.crew_deck(choice.deck) if not c.id.endswith("B") and c.id not in removed]
    board = data.board(choice.deck, "basic")
    captain_card = next(c for c in cards if c.suit == "Captain")
    player = Player(seat=seat, name=f"{captain_card.name} Bot", deck=choice.deck, board=board.id,
                    captain=state.new_inst(captain_card.id),
                    bot=BotState(crew=choice.deck, difficulty=choice.difficulty, ticking_clock=choice.ticking_clock,
                                 exile=data.command[choice.deck].side("exile_traits") is not None))
    player.actions = 0
    player.mission_tokens = 0

    by_position: dict[str | None, list[Card]] = {}
    for card in cards:
        if card.suit not in ("Captain", "Status"):  # Status cards go back to the box (REQ-SOLO-26)
            by_position.setdefault(card.position, []).append(card)
    state.incident.extend(_insts(state, by_position.pop("Incident Deck", [])))  # REQ-SOLO-25

    developments = _insts(state, by_position.pop("Development", []))
    reserves = _insts(state, by_position.pop("Reserve", []))
    if choice.ticking_clock:  # REQ-SOLO-130
        reserves.append(state.new_inst(TIME_IS_RUNNING_OUT))
    last = rules.SUPPLEMENT_BOTTOM.get(choice.deck, ())  # Khan: Genesis Device goes on the bottom (REQ-CD-KHN-11)
    bottom = [i for i in developments if i.card in last]
    developments = [i for i in developments if i.card not in last]
    state.shuffle(developments)
    state.shuffle(reserves)
    player.reserve = reserves + developments + bottom  # REQ-SOLO-27: the Supplement deck

    available = _insts(state, by_position.pop("Available", []))
    state.shuffle(available)
    on_top = _insts(state, by_position.pop("Deployed", []) + by_position.pop("Controlled Location", []))
    state.shuffle(on_top)
    player.draw = on_top + available  # REQ-SOLO-28: the Bot deck
    player.discard = _insts(state, by_position.pop("Discard", []))  # REQ-SOLO-29
    if by_position:
        raise SetupError(f"{choice.deck} Bot: cards with unexpected positions {sorted(map(str, by_position))}")

    teams = captain_card.away_teams
    player.away_pool = int(str(teams).rstrip("+")) if teams is not None else 0  # REQ-SOLO-31
    return player  # no resources at all, not even Glory (REQ-SOLO-33)

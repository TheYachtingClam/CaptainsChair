"""The turn loop and the shared rules every card relies on.

Public interface:
    advance(state)               run until a player decision is needed or the game is over
    choose(state, seat, option)  apply a player's answer to the pending decision, then advance

Card operations are placeholders in this skeleton: playing a card moves it to the Staging Area
and spends its action, using an Activation exhausts the card, and the effect itself is logged
as not yet implemented. Everything else follows requirements/05 to 07 and 13.
"""

from __future__ import annotations

import copy

from engine import cards as card_code
from engine.content import MARKET_SUITS, content
from engine.setup import refill_market
from engine.state import SPECIALTIES, Decision, GameState, Inst, Option, Player

BASE_HAND_SIZE = 5
FLEET_SHIP_WEIGHT = {"3FRE03": 2}  # A Fleet of 30 California-Class Ships (REQ-EXP-FRE-01)
KHAN_CAPTAINS = {"2KHA01A", "2KHA01B"}


class IllegalCommand(ValueError):
    pass


def card(inst: Inst):
    return content().cards[inst.card]


def name(inst: Inst) -> str:
    return card(inst).name


# =========================================================================== public


def choose(state: GameState, seat: int, option_id: str) -> None:
    decision = state.decision
    if decision is None:
        raise IllegalCommand("Nothing to decide")
    if decision.seat != seat:
        raise IllegalCommand("It is not your decision")
    if option_id not in {o.id for o in decision.options}:
        raise IllegalCommand(f"Unknown option {option_id!r}")
    state.decision = None
    HANDLERS[decision.kind](state, state.player(seat), option_id)
    advance(state)


def advance(state: GameState, *, flag_irreversible: bool = True) -> None:
    while state.decision is None and state.step != "over":
        STEPS[state.step](state)
    if state.decision is not None and flag_irreversible:
        _flag_irreversible(state)


def _flag_irreversible(state: GameState) -> None:
    """Mark each option that would reach an irreversible event before the next decision (REQ-UNDO-11).

    The engine is deterministic, so each option is simply tried on a copy of the state.
    """
    decision = state.decision
    for option in decision.options:
        trial = copy.deepcopy(state)
        before = len(trial.log)
        trial.decision = None
        HANDLERS[decision.kind](trial, trial.player(decision.seat), option.id)
        _advance_untracked(trial)
        hits = [e for e in trial.log[before:] if e.irreversible]
        option.irreversible = bool(hits)
        option.reason = hits[0].text if hits else None


def _advance_untracked(state: GameState) -> None:
    while state.decision is None and state.step != "over":
        STEPS[state.step](state)


def ask(state: GameState, seat: int, kind: str, prompt: str, options: list[tuple[str, str]]) -> None:
    state.decision = Decision(seat=seat, kind=kind, prompt=prompt, options=[Option(id=i, label=l) for i, l in options])


# =========================================================================== shared rules


def hand_size(state: GameState, player: Player) -> int:
    size = BASE_HAND_SIZE
    for inst in table_cards(player):
        modifier = card_code.HAND_SIZE.get(inst.card)
        if modifier:
            size = modifier(state, player, size)
    return size


def table_cards(player: Player) -> list[Inst]:
    """Cards in a table position: where PASSIVE and REACTION operations work (REQ-AS-21, REQ-AS-22)."""
    return [player.captain, *player.status, *player.fleet, *player.locations, *player.duty]


def is_khan(player: Player) -> bool:
    return player.captain.card in KHAN_CAPTAINS


def draw(state: GameState, player: Player, count: int, *, announce: bool = True) -> int:
    drawn = 0
    for _ in range(count):
        if not player.draw and not cycle_deck(state, player):
            break
        player.hand.append(player.draw.pop(0))
        drawn += 1
    if drawn and announce:
        state.emit(f"{player.name} draws {drawn} card(s).", seat=player.seat, irreversible=True)
    return drawn


def cycle_deck(state: GameState, player: Player) -> bool:
    """Shuffle the Discard pile into a new Draw deck and enlist a Reserve (REQ-DK-01, REQ-DK-02)."""
    if not player.discard:
        return False
    player.draw, player.discard = player.discard, []
    state.shuffle(player.draw)
    state.emit(f"{player.name} shuffles their Discard pile into a new deck.", seat=player.seat, irreversible=True)
    if is_khan(player):
        return True  # Khan does not enlist when cycling (REQ-CD-KHN-03)
    if player.reserve:
        player.draw.insert(0, player.reserve.pop(0))
        state.emit(f"{player.name} enlists a Reserve.", seat=player.seat)
    # Enlisting a Development when the Reserve is empty is optional and costs resources (REQ-DK-10).
    # It needs card-cost payment, which arrives with card code.
    return True


def gain_glory(state: GameState, player: Player, amount: int) -> None:
    for _ in range(amount):
        take_glory_from_stardate(state)
        player.glory += 1


def take_glory_from_stardate(state: GameState) -> None:
    """Take one Glory from the top Stardate card, or the supply after a Resolution (REQ-SD-01)."""
    if state.resolution or not state.stardates:
        return
    state.stardate_glory -= 1
    if state.stardate_glory <= 0:
        empty_stardate(state)


def empty_stardate(state: GameState) -> None:
    top = state.stardates[0]
    if len(state.stardates) == 1:
        trigger_resolution(state)
        return
    state.stardates.pop(0)
    emptied = next((op.text or "" for op in card(top).operations if op.kind == "WHEN EMPTIED"), "")
    if "inactive player" in emptied:
        receiver = state.opponent(state.active) or state.player(state.active)
        receiver.received_stardates.append(top)
        state.emit(f"The Stardate card empties and goes to {receiver.name}'s Staging Area.")
    elif "your Staging Area" in emptied:
        state.player(state.active).received_stardates.append(top)
        state.emit("The Stardate card empties and goes to the active player's Staging Area.")
    else:
        state.emit("The Stardate card empties and is destroyed.")
    state.stardate_glory = card(state.stardates[0]).starting_glory or 0


def trigger_resolution(state: GameState) -> None:
    """The last Stardate empties: finish the round, then each player takes one more turn (REQ-OV-22)."""
    state.resolution = True
    players = len(state.players)
    position = state.turn % players  # 0 = the first player's turn in this round
    round_end = state.turn + (players - 1 - position)
    state.last_turn = round_end + players
    state.emit("The final Stardate card is empty. Resolution: the game ends after the final turns.")


def take_incident(state: GameState, player: Player) -> Inst | None:
    if not state.incident:
        burn(state)
        return None
    inst = state.incident.pop(0)
    player.hand.append(inst)
    state.emit(f"{player.name} takes an Incident.", seat=player.seat, irreversible=True)
    if not state.incident:
        burn(state)
    return inst


def burn(state: GameState) -> None:
    """The Incident deck is empty: the game ends at once (REQ-OV-23)."""
    from engine.scoring import incidents_owned, score_game

    counts = {p.seat: incidents_owned(p) for p in state.players}
    state.emit("The Incident deck is empty. The Burn ends the game.")
    if len(state.players) == 1:
        state.result = {"reason": "burn", "winners": [], "incidents": counts}
    elif len(set(counts.values())) == 1:
        state.result = {"reason": "burn-tie", **score_game(state)}
    else:
        fewest = min(counts.values())
        state.result = {"reason": "burn", "winners": [s for s, n in counts.items() if n == fewest], "incidents": counts}
    state.step = "over"
    state.decision = None


def tokens_at(state: GameState, location: Inst, seat: int) -> int:
    """Away Teams plus Ship tokens, weighted, that a player has at a Location (REQ-CT-01)."""
    player = state.player(seat)
    ships = sum(FLEET_SHIP_WEIGHT.get(s.card, 1) for s in player.fleet if s.at == location.uid)
    return location.away.get(seat, 0) + ships


def secured_by(state: GameState, location: Inst, seat: int) -> bool:
    mine = tokens_at(state, location, seat)
    other = state.opponent(seat)
    theirs = tokens_at(state, location, other.seat) if other else 0
    return mine >= 3 and mine - theirs >= 2


def take_control(state: GameState, player: Player, location: Inst) -> None:
    """REQ-CT-03."""
    other = state.opponent(player.seat)
    if other:
        tokens = location.away.get(other.seat, 0) + sum(1 for s in other.fleet if s.at == location.uid)
        if tokens:
            gain_glory(state, other, tokens)
            state.emit(f"{other.name} gains {tokens} Glory for their tokens at {name(location)}.")
    for p in state.players:
        p.away_pool += location.away.pop(p.seat, 0)
        for ship in [s for s in p.fleet if s.at == location.uid]:
            dismiss(state, p, ship)
    state.neutral.remove(location)
    player.locations.append(location)
    player.controls_this_turn += 1
    state.emit(f"{player.name} takes control of {name(location)}. (Its CONTROL operation is not implemented yet.)")
    if state.location_deck:
        revealed = state.location_deck.pop(0)
        state.neutral.append(revealed)
        state.emit(f"{name(revealed)} is revealed in the Neutral Zone.", irreversible=True)


def dismiss(state: GameState, owner: Player, inst: Inst) -> None:
    for zone in (owner.fleet, owner.locations, owner.duty):
        if inst in zone:
            zone.remove(inst)
            break
    inst.at = None
    inst.exhausted = False
    inst.res.clear()
    owner.discard.extend(inst.beamed)
    inst.beamed = []
    owner.discard.append(inst)
    state.emit(f"{name(inst)} is dismissed.", seat=owner.seat)


def wipe_market(state: GameState) -> None:
    for suit in MARKET_SUITS:
        inst = state.market.get(suit)
        if inst is not None:
            inst.res.clear()
            state.junk.append(inst)
            state.market[suit] = None
        refill_market(state, suit)
    state.emit("The Market is wiped.")


def wipe_neutral_zone(state: GameState) -> None:
    keep = [loc for loc in state.neutral if any(tokens_at(state, loc, p.seat) for p in state.players)]
    removed = [loc for loc in state.neutral if loc not in keep]
    state.neutral = keep
    while len(state.neutral) < 3 and state.location_deck:
        revealed = state.location_deck.pop(0)
        state.neutral.append(revealed)
        state.emit(f"{name(revealed)} is revealed in the Neutral Zone.", irreversible=True)
    if removed:
        state.emit("Neutral Locations without tokens are removed: " + ", ".join(name(loc) for loc in removed) + ".")


# =========================================================================== turn steps


def step_start(state: GameState) -> None:
    player = state.player(state.active)
    player.controls_this_turn = 0
    state.emit(f"Turn {state.turn + 1}: {player.name}.", seat=player.seat)
    state.step = "resupply"


def step_resupply(state: GameState) -> None:
    player = state.player(state.active)
    ops = [inst for inst in table_cards(player) if any(op.kind == "RESUPPLY" for op in card(inst).operations)]
    if ops:
        state.emit("Resupply operations are not implemented yet: " + ", ".join(name(i) for i in ops) + ".", seat=player.seat)
    state.step = "control"


def step_control(state: GameState) -> None:
    player = state.player(state.active)
    limit = content().boards[player.board].control_max
    secured = [loc for loc in state.neutral if secured_by(state, loc, player.seat)] if player.controls_this_turn < limit else []
    if not secured:
        state.step = "action"
        return
    ask(state, player.seat, "control", "Take control of a secured Location?",
        [(f"take:{loc.uid}", f"Take control of {name(loc)}") for loc in secured] + [("skip", "Do not take control")])


def handle_control(state: GameState, player: Player, option: str) -> None:
    if option == "skip":
        state.step = "action"
        return
    location = next(loc for loc in state.neutral if loc.uid == option.split(":", 1)[1])
    take_control(state, player, location)
    # Stay in the Control Step: the limit may allow another (REQ-CT-05).


def step_action(state: GameState) -> None:
    player = state.player(state.active)
    options: list[tuple[str, str]] = []
    for inst in player.hand:
        for i, op in enumerate(card(inst).operations):
            if op.kind == "PLAY" and (player.actions > 0 or not op.action_cost):
                cost = " (action)" if op.action_cost else ""
                options.append((f"play:{inst.uid}:{i}", f"Play {name(inst)}{cost}: {op.text}"))
    for inst in table_cards(player):
        if inst.exhausted:
            continue
        for i, op in enumerate(card(inst).operations):
            if op.kind == "ACTIVATION" and (player.actions > 0 or not op.action_cost):
                options.append((f"activate:{inst.uid}:{i}", f"Activate {name(inst)}: {op.text}"))
    options.append(("end", "End the Action Step"))
    ask(state, player.seat, "action", f"Action Step. Actions left: {player.actions}.", options)


def handle_action(state: GameState, player: Player, option: str) -> None:
    if option == "end":
        state.step = "cleanup"
        state.substep = "ops"
        return
    verb, uid, index = option.split(":")
    op = None
    if verb == "play":
        inst = next(i for i in player.hand if i.uid == uid)
        op = card(inst).operations[int(index)]
        player.hand.remove(inst)
        player.staging.append(inst)
        state.emit(f"{player.name} plays {name(inst)}.", seat=player.seat)
    else:
        inst = next(i for i in table_cards(player) if i.uid == uid)
        op = card(inst).operations[int(index)]
        inst.exhausted = True
        state.emit(f"{player.name} activates {name(inst)}.", seat=player.seat)
    if op.action_cost:
        player.actions -= 1
    state.emit(f"(Card effect not implemented yet: {op.text})", seat=player.seat)


def step_cleanup(state: GameState) -> None:
    player = state.player(state.active)
    if state.substep == "ops":
        ops = [i for i in table_cards(player) + player.staging if any(op.kind == "CLEAN-UP" for op in card(i).operations)]
        if ops:
            state.emit("Clean-up operations are not implemented yet: " + ", ".join(name(i) for i in ops) + ".", seat=player.seat)
        state.substep = "stardate"
    elif state.substep == "stardate":
        for stardate in player.received_stardates:
            text = next((op.text or "" for op in card(stardate).operations if op.kind == "STARDATE RESOLUTION"), "")
            if text:
                wipe_market(state)
                if "neutral Location" in text:
                    wipe_neutral_zone(state)
        player.received_stardates = []
        state.substep = "glory"
    elif state.substep == "glory":
        slots = [(suit, inst) for suit, inst in state.market.items() if inst is not None]
        if not slots:
            state.substep = "discard"
            return
        ask(state, player.seat, "glory", "Place 1 Glory on a Market card.",
            [(f"glory:{suit}", f"{name(inst)} ({suit}, {inst.res.get('glory', 0)} Glory)") for suit, inst in slots])
    elif state.substep == "discard":
        player.discard.extend(player.staging)
        player.staging = []
        ask(state, player.seat, "discard", "Discard any cards from your hand, then draw up.",
            [(f"discard:{i.uid}", f"Discard {name(i)}") for i in player.hand] + [("done", "Done: draw up")])
    elif state.substep == "draw":
        missing = hand_size(state, player) - len(player.hand)
        if missing > 0:
            draw(state, player, missing)
        for inst in table_cards(player):
            inst.exhausted = False
        player.actions = content().boards[player.board].actions
        end_turn(state)


def handle_glory(state: GameState, player: Player, option: str) -> None:
    suit = option.split(":", 1)[1]
    take_glory_from_stardate(state)
    target = state.market[suit]
    target.res["glory"] = target.res.get("glory", 0) + 1
    state.emit(f"{player.name} places 1 Glory on {name(target)}.", seat=player.seat)
    state.substep = "discard"


def handle_discard(state: GameState, player: Player, option: str) -> None:
    if option == "done":
        state.substep = "draw"
        return
    inst = next(i for i in player.hand if i.uid == option.split(":", 1)[1])
    player.hand.remove(inst)
    player.discard.append(inst)
    state.emit(f"{player.name} discards {name(inst)}.", seat=player.seat)
    # The step handler asks again with the remaining hand.


def end_turn(state: GameState) -> None:
    state.emit(f"{state.player(state.active).name} ends their turn.", irreversible=True)
    if state.last_turn is not None and state.turn >= state.last_turn:
        from engine.scoring import score_game

        state.result = {"reason": "resolution", **score_game(state)}
        state.step = "over"
        state.emit("The game is over.")
        return
    state.turn += 1
    state.active = (state.active + 1) % len(state.players)
    state.step = "start"
    state.substep = ""


def step_over(state: GameState) -> None:  # pragma: no cover - advance() stops first
    pass


STEPS = {
    "start": step_start,
    "resupply": step_resupply,
    "control": step_control,
    "action": step_action,
    "cleanup": step_cleanup,
    "over": step_over,
}
HANDLERS = {
    "control": handle_control,
    "action": handle_action,
    "glory": handle_glory,
    "discard": handle_discard,
}

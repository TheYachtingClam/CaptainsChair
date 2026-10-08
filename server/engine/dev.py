"""Developer commands for testing cards by hand (plans/card-implementation.md, Step 1).

They are stored and replayed like any other command, so undo and rebuilds work. The server only
accepts new ones when DEV_TOOLS is on, but replay never checks that, so a game keeps its history.

A developer command is a dict:
  {"kind": "card", "card": "2PER01", "zone": "hand"}         a new copy of any card, placed in a zone
  {"kind": "resource", "resource": "dilithium", "amount": 3}  dilithium, latinum, glory or actions
  {"kind": "track", "track": "military", "amount": 2}          move a Specialty track (negative moves it back)
  {"kind": "mark", "amount": 3}                                mark that many trait slots on Khan's board, in board order

Placing a card does not count as putting it into play and triggers nothing: it sets up a position.
"""

from __future__ import annotations

from engine.content import content
from engine.state import SPECIALTIES, GameState

ZONES = {
    "hand": "hand",
    "staging": "Staging Area",
    "duty": "Duty Officer",
    "fleet": "Fleet Area",
    "locations": "Location Area",
    "discard": "Discard pile",
    "draw": "top of the Draw deck",
    "log": "Captain's Log",
}
RESOURCES = ("dilithium", "latinum", "glory", "actions")


class DevCommandError(ValueError):
    pass


def apply(state: GameState, seat: int, cmd: dict, *, flag_irreversible: bool = True) -> None:
    from engine.game import advance

    if state.step == "over":
        raise DevCommandError("The game is over")
    if state.running is not None or state.offer is not None or state.op_queue:
        raise DevCommandError("Finish the card effect in progress first")
    if not 0 <= seat < len(state.players):
        raise DevCommandError("Unknown seat")
    player = state.player(seat)
    kind = cmd.get("kind")

    if kind == "card":
        card_id, zone = cmd.get("card"), cmd.get("zone", "hand")
        card = content().cards.get(card_id)
        if card is None:
            raise DevCommandError(f"Unknown card {card_id!r}")
        if zone not in ZONES:
            raise DevCommandError(f"Unknown zone {zone!r}")
        inst = state.new_inst(card_id)
        if zone == "draw":
            player.draw.insert(0, inst)
        else:
            getattr(player, zone).append(inst)
        state.emit(f"[Dev] {player.name} puts a copy of {card.name} in their {ZONES[zone]}.", seat=seat)
    elif kind == "resource":
        resource, amount = cmd.get("resource"), int(cmd.get("amount", 0))
        if resource not in RESOURCES:
            raise DevCommandError(f"Unknown resource {resource!r}")
        setattr(player, resource, max(0, getattr(player, resource) + amount))
        state.emit(f"[Dev] {player.name}: {amount:+d} {resource.capitalize()}.", seat=seat)
    elif kind == "track":
        track, amount = cmd.get("track"), int(cmd.get("amount", 0))
        if track not in SPECIALTIES:
            raise DevCommandError(f"Unknown track {track!r}")
        player.tracks[track] = max(0, min(15, player.tracks[track] + amount))
        player.highest[track] = max(player.highest[track], player.tracks[track])
        state.emit(f"[Dev] {player.name}: {track.capitalize()} {amount:+d} (now {player.tracks[track]}).", seat=seat)
    elif kind == "mark":
        from engine.ops import mark_options
        from engine.state import Mark

        amount = int(cmd.get("amount", 0))
        marked = 0
        for _ in range(max(0, amount)):
            found = mark_options(state, player, None)  # any unmarked slot, in board order
            if not found:
                break
            slot, trait = found[0]
            player.marks.append(Mark(slot=slot, trait=trait))
            marked += 1
        state.emit(f"[Dev] {player.name} marks {marked} trait(s) (now {len(player.marks)}).", seat=seat)
    else:
        raise DevCommandError(f"Unknown developer command {kind!r}")

    # Ask the pending question again so its options reflect the new position.
    state.decision = None
    advance(state, flag_irreversible=flag_irreversible)

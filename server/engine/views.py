"""What each player may see (REQ-SRV-20, REQ-INF-01 to REQ-INF-03).

Hidden: the opponent's hand (count only), every facedown deck (count only), the seed and RNG.
Public: Market, Junk, Discard piles, Development piles, Captain's Logs (REQ-LOG-10), play areas.
"""

from __future__ import annotations

from engine.content import content
from engine.game import hand_size, secured_by
from engine.state import GameState, Inst, Player


def card_view(inst: Inst) -> dict:
    c = content().cards[inst.card]
    out = {"uid": inst.uid, "id": inst.card, "name": c.name, "suit": c.suit, "image": c.image, "exhausted": inst.exhausted}
    if inst.res:
        out["resources"] = dict(inst.res)
    if inst.beamed:
        out["beamed"] = [card_view(b) for b in inst.beamed]
    if inst.at is not None:
        out["at"] = inst.at
    if inst.away:
        out["away_teams"] = {str(k): v for k, v in inst.away.items()}
    return out


def player_view(state: GameState, player: Player, viewer: int | None) -> dict:
    mine = viewer == player.seat
    return {
        "seat": player.seat,
        "name": player.name,
        "deck": player.deck,
        "board": player.board,
        "captain": card_view(player.captain),
        "status": [card_view(i) for i in player.status],
        "hand": [card_view(i) for i in player.hand] if mine else None,
        "hand_count": len(player.hand),
        "hand_size": hand_size(state, player),
        "draw_count": len(player.draw),
        "reserve_count": len(player.reserve),
        "discard": [card_view(i) for i in player.discard],
        "development": [card_view(i) for i in player.development],
        "staging": [card_view(i) for i in player.staging + player.received_stardates],
        "fleet": [card_view(i) for i in player.fleet],
        "locations": [card_view(i) for i in player.locations],
        "duty": [card_view(i) for i in player.duty],
        "log": [card_view(i) for i in player.log],
        "resources": {"dilithium": player.dilithium, "latinum": player.latinum, "glory": player.glory},
        "actions": player.actions,
        "tracks": dict(player.tracks),
        "away_pool": player.away_pool,
        "mission_tokens": player.mission_tokens,
        "missions_completed": list(player.missions_completed),
    }


def game_view(state: GameState, viewer: int | None) -> dict:
    decision = None
    if state.decision is not None:
        d = state.decision
        decision = {"seat": d.seat, "kind": d.kind, "prompt": d.prompt}
        if d.seat == viewer:
            decision["options"] = [o.model_dump() for o in d.options]
    top = state.stardates[0] if state.stardates else None
    return {
        "mode": state.mode,
        "turn": state.turn + 1,
        "active": state.active,
        "first_seat": state.first_seat,
        "step": state.step,
        "substep": state.substep,
        "you": viewer,
        "players": [player_view(state, p, viewer) for p in state.players],
        "market": {suit: card_view(i) if i else None for suit, i in state.market.items()},
        "market_deck_counts": {suit: len(d) for suit, d in state.market_decks.items()},
        "neutral_zone": [
            {**card_view(loc), "secured_by": [p.seat for p in state.players if secured_by(state, loc, p.seat)]}
            for loc in state.neutral
        ],
        "location_deck_count": len(state.location_deck),
        "encounter_count": len(state.encounter),
        "incident_count": len(state.incident),
        "junk": [card_view(i) for i in state.junk],
        "reward_count": len(state.rewards),
        "stardate": {"top": card_view(top) if top else None, "glory": state.stardate_glory, "remaining": len(state.stardates)},
        "resolution": state.resolution,
        "last_turn": state.last_turn + 1 if state.last_turn is not None else None,
        "decision": decision,
        "log": [e.text for e in state.log[-60:] if e.private_to in (None, viewer)],
        "result": state.result,
    }

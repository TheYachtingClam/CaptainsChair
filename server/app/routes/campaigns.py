"""Five-Year Mission campaigns (requirements/22-solo-mode.md §14, REQ-CAMP-50 to -54).

A campaign is reached by its own secret link: the token goes in the X-Campaign-Token header. Each assignment is an
ordinary solo game against a Bot; the campaign reads its result when it is over and records the upgrade.
"""

from __future__ import annotations

import random
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app import content, play
from app.auth import hash_seat_token, new_seat_token, require_session
from app.db import get_db
from app.models import Campaign, Game
from app.routes.games import add_seat, validate_deck
from app.schemas import BoardSide, SeatChoice
from engine import campaign as rules
from engine.content import content as card_content

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"], dependencies=[Depends(require_session)])


class NewCampaign(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    deck_id: str
    mode: str = "set_phasers_to_stun"
    box: Literal["core", "to_boldly_go", "both"] = "to_boldly_go"
    expansions: list[str] = []
    promos: bool = False
    challenges: list[str] = []


class NewAssignment(BaseModel):
    bot_deck_id: str | None = None  # None: picked at random (REQ-CAMP-04)
    board_side: BoardSide = "basic"
    drop: Literal["dilithium", "latinum"] | None = None  # Live Long and Prosper after one success


class UpgradeChoice(BaseModel):
    """Option A: `card_id`, a Market card to reinforce. Option B: `bonus`, a bonus key, and for a REINFORCE bonus the
    own crew cards in `cards`. Neither: no upgrade, allowed only when nothing can be chosen."""

    card_id: str | None = None
    bonus: str | None = None
    cards: list[str] = []


def _load(db: Session, campaign_id: str, token: str | None) -> Campaign:
    found = db.get(Campaign, campaign_id)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
    if not token or hash_seat_token(token) != found.token_hash:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This campaign needs its link")
    return found


def _card(card_id: str) -> dict:
    c = card_content().cards[card_id]
    return {"id": c.id, "name": c.name, "suit": c.suit, "image": c.image}


def _captain(deck_id: str) -> str:
    return next((d["captain"] for d in content.decks() if d["id"] == deck_id), deck_id)


def _opponents(camp: Campaign) -> list[str]:
    """Bots you can face: not one you have already beaten in this campaign (REQ-CAMP-05)."""
    beaten = {a["bot"] for a in camp.assignments if a.get("outcome") == "win"}
    return sorted(d for d in content.bot_ids_for(camp.expansions, camp.box) if d not in beaten)


def _sync(db: Session, camp: Campaign) -> None:
    """Record the result of the current assignment once its game is over (REQ-CAMP-06, -07)."""
    if not camp.assignments:
        return
    current = dict(camp.assignments[-1])  # a copy: changing the stored JSON in place would not be saved
    if current.get("outcome") is not None or not current.get("game_id"):
        return
    game = db.get(Game, current["game_id"])
    if game is None:
        current["outcome"] = "loss"  # a deleted game counts as a failure
        current["upgrade_options"] = []
    else:
        state = play.build(game)
        if state.step != "over" or not state.result:
            return
        won = 0 in state.result.get("winners", [])  # a tie is a failure (REQ-CAMP-06)
        current["outcome"] = "win" if won else "loss"
        current["scores"] = {s["name"]: s["total"] for s in state.result.get("scores", [])}
        current["upgrade_options"] = rules.option_a_cards(state, state.players[0], current["bot"], won)
        if won:
            camp.rank = rules.promoted(camp.rank)
    if rules.finished(camp.rank, len(camp.assignments)):
        camp.status = "finished"  # no upgrade after the last assignment: there is no later game to use it
    camp.assignments = [*camp.assignments[:-1], current]
    flag_modified(camp, "assignments")
    db.commit()


def _outcomes(camp: Campaign) -> list[str]:
    return [a["outcome"] for a in camp.assignments if a.get("outcome")]


def _setup(camp: Campaign, drop: str | None = None):
    return rules.game_setup(camp.rank, _outcomes(camp), camp.challenges, camp.boosts, drop)


def _bonus_view(camp: Campaign, key: str) -> dict:
    from engine import upgrades

    out = {"key": key, "text": upgrades.text(key), "kind": "reinforce" if key in upgrades.REINFORCES else "boost"}
    if out["kind"] == "reinforce":
        out["each"] = upgrades.REINFORCES[key].each
        out["pools"] = [[_card(c) for c in pool] for pool in rules.reinforce_pools(key, camp.deck_id, camp.reinforcement)]
    return out


def _phase(camp: Campaign) -> str:
    if camp.status == "finished":
        return "finished"
    if not camp.assignments:
        return "start"
    current = camp.assignments[-1]
    if current.get("outcome") is None:
        return "playing"
    if current.get("upgrade") is None:
        return "upgrade"
    return "start"


def _view(camp: Campaign) -> dict:
    phase = _phase(camp)
    out = {
        "id": camp.id,
        "display_name": camp.display_name,
        "deck_id": camp.deck_id,
        "captain": _captain(camp.deck_id),
        "mode": camp.mode,
        "mode_name": rules.MODE_NAMES.get(camp.mode, camp.mode),
        "box": camp.box,
        "expansions": camp.expansions,
        "rank": camp.rank,
        "phase": phase,
        "assignments": [
            {k: v for k, v in a.items() if k != "upgrade_options"} | {"bot_captain": _captain(a["bot"])}
            for a in camp.assignments
        ],
        "assignments_left": rules.ASSIGNMENTS - len(camp.assignments),
        "reinforcement": [_card(c) for c in camp.reinforcement],
        "challenges": [{"id": c, "name": rules.CHALLENGES[c], "rule": rules.CHALLENGE_RULES[c]} for c in camp.challenges],
        "boosts": [_boost_text(k) for k in camp.boosts],
        "next_notes": rules.setup_notes(_setup(camp)),
        "choose_resource": rules.needs_resource_choice(_outcomes(camp), camp.challenges),
        "next_difficulty": rules.difficulty(camp.rank, camp.mode) if camp.rank != "admiral" else None,
        "opponents": [{"deck_id": d, "captain": _captain(d)} for d in _opponents(camp)],
    }
    if phase == "playing":
        out["game_id"] = camp.assignments[-1]["game_id"]
    if phase == "upgrade":
        current = camp.assignments[-1]
        won = current["outcome"] == "win"
        out["upgrade"] = {
            "won": won,
            "restriction": rules.restriction(current["bot"], won),
            "options": [_card(c) for c in current.get("upgrade_options", [])],
            "bonuses": [_bonus_view(camp, k) for k in rules.option_b(current["bot"], won, camp.challenges)],
        }
    if phase == "finished":
        out["evaluation"] = rules.evaluation(camp.rank, len(camp.assignments))
    return out


@router.post("", status_code=status.HTTP_201_CREATED)
def create_campaign(body: NewCampaign, db: Session = Depends(get_db)) -> dict:
    """REQ-CAMP-02: choose a Crew deck and a campaign mode; the rank starts at Ensign."""
    unknown = set(body.expansions) - set(content.EXPANSIONS)
    if unknown:
        raise HTTPException(422, f"Unknown expansion: {', '.join(sorted(unknown))}")
    validate_deck(body.deck_id, body.expansions, body.box)
    if not content.bot_ids_for(body.expansions, body.box):
        raise HTTPException(422, "No Bot is available for this box yet")
    if body.mode not in rules.MODES:
        raise HTTPException(422, "Unknown campaign mode")
    allowed = rules.available_challenges(body.deck_id)
    if set(body.challenges) - set(allowed):
        raise HTTPException(422, "A chosen challenge is not available for this Crew deck")
    token = new_seat_token()
    camp = Campaign(display_name=body.display_name.strip(), deck_id=body.deck_id, mode=body.mode,
                    box=body.box, expansions=body.expansions, promos=body.promos, token_hash=hash_seat_token(token),
                    challenges=[c for c in rules.CHALLENGES if c in body.challenges])
    db.add(camp)
    db.commit()
    return {"campaign": _view(camp), "token": token}


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, db: Session = Depends(get_db),
                 x_campaign_token: str | None = Header(default=None)) -> dict:
    camp = _load(db, campaign_id, x_campaign_token)
    _sync(db, camp)
    return _view(camp)


@router.post("/{campaign_id}/assignments", status_code=status.HTTP_201_CREATED)
def start_assignment(campaign_id: str, body: NewAssignment, db: Session = Depends(get_db),
                     x_campaign_token: str | None = Header(default=None)) -> dict:
    """The next assignment: a solo game against a Bot you have not beaten, at the difficulty the rank and mode give
    (REQ-CAMP-04, -05, -10). Returns the new game and your seat token."""
    camp = _load(db, campaign_id, x_campaign_token)
    _sync(db, camp)
    if _phase(camp) != "start":
        raise HTTPException(409, "Finish the current assignment first")
    opponents = _opponents(camp)
    bot = body.bot_deck_id or random.choice(opponents)
    if bot not in opponents:
        raise HTTPException(422, "You cannot face that Bot in this campaign")
    number = len(camp.assignments) + 1
    level = rules.difficulty(camp.rank, camp.mode)
    game = Game(mode="solo", box=camp.box, expansions=camp.expansions, promos=camp.promos,
                bot={"deck_id": bot, "difficulty": level, "ticking_clock": False},
                campaign={"id": camp.id, "assignment": number, "reinforcement": list(camp.reinforcement),
                          "setup": asdict(_setup(camp, body.drop))})
    db.add(game)
    seat, token = add_seat(db, game, SeatChoice(display_name=camp.display_name, deck_id=camp.deck_id,
                                                board_side=body.board_side))
    camp.assignments = [*camp.assignments, {
        "number": number, "game_id": game.id, "date": datetime.now(UTC).date().isoformat(), "rank": camp.rank,
        "bot": bot, "difficulty": level, "board_side": body.board_side, "outcome": None, "scores": None,
        "upgrade": None,
    }]
    db.commit()
    return {"game_id": game.id, "seat_index": seat.index, "seat_token": token, "campaign": _view(camp)}


@router.get("/challenges/{deck_id}")
def challenges_for(deck_id: str) -> list[dict]:
    """The challenges a Crew deck can take (REQ-CAMP-41)."""
    return [{"id": c, "name": rules.CHALLENGES[c], "rule": rules.CHALLENGE_RULES[c]}
            for c in rules.available_challenges(deck_id)]


def _boost_text(key: str) -> str:
    from engine import upgrades

    return upgrades.text(key)


@router.post("/{campaign_id}/upgrade")
def choose_upgrade(campaign_id: str, body: UpgradeChoice, db: Session = Depends(get_db),
                   x_campaign_token: str | None = Header(default=None)) -> dict:
    """One upgrade after each assignment (REQ-CAMP-25): option A adds an offered Market card to the Reinforcement
    pile; option B takes one of the Bot's bonuses: a Boost for every later game, or own cards to reinforce."""
    camp = _load(db, campaign_id, x_campaign_token)
    _sync(db, camp)
    if _phase(camp) != "upgrade":
        raise HTTPException(409, "There is no upgrade to choose now")
    current = dict(camp.assignments[-1])
    offered = current.get("upgrade_options", [])
    won = current["outcome"] == "win"
    bonuses = rules.option_b(current["bot"], won, camp.challenges)
    if body.card_id is not None:
        if body.card_id not in offered:
            raise HTTPException(422, "That card cannot be reinforced after this assignment")
        camp.reinforcement = [*camp.reinforcement, body.card_id]
        current["upgrade"] = {"option": "A", "card": body.card_id}
    elif body.bonus is not None:
        if body.bonus not in bonuses:
            raise HTTPException(422, "That bonus is not offered")
        view = _bonus_view(camp, body.bonus)
        if view["kind"] == "boost":
            camp.boosts = [*camp.boosts, body.bonus]
            current["upgrade"] = {"option": "B", "bonus": body.bonus, "text": view["text"]}
        else:
            pools = rules.reinforce_pools(body.bonus, camp.deck_id, camp.reinforcement)
            picked = list(dict.fromkeys(body.cards))
            per_pool = [sum(1 for c in picked if c in pool) for pool in pools]
            in_some = all(any(c in pool for pool in pools) for c in picked)
            limit_ok = all(n <= 1 for n in per_pool) if view["each"] else len(picked) == 1
            if not picked or not in_some or not limit_ok:
                raise HTTPException(422, "Choose the cards this bonus allows")
            camp.reinforcement = [*camp.reinforcement, *picked]
            current["upgrade"] = {"option": "B", "bonus": body.bonus, "text": view["text"], "cards": picked}
    else:
        if offered or any(_bonus_view(camp, k)["kind"] == "boost" or any(_bonus_view(camp, k)["pools"])
                          for k in bonuses):
            raise HTTPException(422, "Choose an upgrade")
        current["upgrade"] = {"option": "none"}
    camp.assignments = [*camp.assignments[:-1], current]
    flag_modified(camp, "assignments")
    db.commit()
    return _view(camp)

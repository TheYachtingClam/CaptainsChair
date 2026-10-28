"""The admin (requirements/19-technical-architecture.md §5.4, §5.6): accounts and invitations, every game and
campaign, and bug reports. Every endpoint here needs an admin account (REQ-USER-32)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import bugs, observe, play
from app.auth import require_admin, require_session, session_user, viewer_id
from app.db import get_db
from app.hub import hub
from app.models import BugReport, Campaign, Game
from app.schemas import BugStatus
from engine.views import game_view

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_session)])


@router.get("/status")
def admin_status(request: Request, db: Session = Depends(get_db)) -> dict:
    """Whether this account is an admin (REQ-USER-32)."""
    user = session_user(request.cookies, db)
    return {"admin": bool(user and user.is_admin)}


@router.get("/games", dependencies=[Depends(require_admin)])
def all_games(db: Session = Depends(get_db)) -> list[dict]:
    """Every game, newest first, in any state (REQ-ADMIN-03)."""
    games = db.scalars(select(Game).options(selectinload(Game.seats)).order_by(Game.created_at.desc())).all()
    return [{
        "id": g.id,
        "mode": g.mode,
        "status": g.status,
        "created_at": g.created_at.isoformat() if g.created_at else None,
        "players": [s.display_name for s in sorted(g.seats, key=lambda s: s.index)],
        "bot": (g.bot or {}).get("deck_id"),
        "campaign_id": (g.campaign or {}).get("id"),
        "moves": sum(1 for c in g.commands or [] if not c.get("undone")),
    } for g in games]


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_any_game(game_id: str, db: Session = Depends(get_db)) -> None:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Game not found")
    db.delete(game)
    db.commit()
    play.forget(game_id)
    await hub.broadcast(game_id, {"type": "game_deleted"})


@router.post("/games/{game_id}/seats/{seat_index}/take", dependencies=[Depends(require_admin)])
async def take_seat(game_id: str, seat_index: int, db: Session = Depends(get_db),
                    viewer: str = Depends(viewer_id)) -> dict:
    """The admin takes over a seat in a real game (REQ-ADMIN-06): the seat moves to the admin's account, so the player
    who held it is locked out. Their open pages are told and disconnected."""
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Game not found")
    seat = next((s for s in game.seats if s.index == seat_index), None)
    if seat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That seat is not taken")
    seat.user_id = viewer
    db.commit()
    await hub.broadcast(game_id, {"type": "seat_taken", "seat": seat_index})
    await hub.close_seat(game_id, seat_index, "The admin took over this seat")
    return {"game_id": game_id, "seat_index": seat_index, "display_name": seat.display_name}


# ------------------------------------------------------------------ watching a game (REQ-ADMIN-07 to -12)

def _started(db: Session, game_id: str) -> Game:
    from app.routes.games import load_game

    game = load_game(db, game_id)
    if game.seed is None:
        raise HTTPException(409, "The game has not started yet")
    return game


@router.get("/games/{game_id}/timeline", dependencies=[Depends(require_admin)])
def game_timeline(game_id: str, db: Session = Depends(get_db)) -> dict:
    """The game's positions: each move with its label and turn, and where each turn opens (REQ-ADMIN-09, -10)."""
    return observe.timeline(_started(db, game_id))


@router.get("/games/{game_id}/observe", dependencies=[Depends(require_admin)])
def observe_game(game_id: str, at: int | None = None, view_as: str = Query("all", alias="as"),
                 db: Session = Depends(get_db)) -> dict:
    """The game at position `at` (the last when left out), read-only (REQ-ADMIN-07): showing everything (`all`), as a
    seat sees it (`0`, `1`) or as a watcher without a seat sees it (`watcher`), REQ-ADMIN-08. Stores nothing."""
    game = _started(db, game_id)
    try:
        state = observe.state_at(game, at)
    except ValueError as err:
        raise HTTPException(422, str(err)) from err
    if view_as == "all":
        out = game_view(state, None, omniscient=True)
    elif view_as == "watcher":
        out = game_view(state, None)
    elif view_as.isdigit() and int(view_as) < len(state.players):
        out = game_view(state, int(view_as))
    else:
        raise HTTPException(422, "View as all, watcher or a seat number")
    last = observe.last(game)
    at = last if at is None else at
    out["can_undo"] = False
    out["dev_tools"] = False
    out["observe"] = {"at": at, "last": last, "live": at == last, "as": view_as}
    return out


class CopyRequest(BaseModel):
    moves: int  # the position to copy


@router.post("/games/{game_id}/copy", dependencies=[Depends(require_admin)])
def copy_game(game_id: str, body: CopyRequest, db: Session = Depends(get_db), viewer: str = Depends(viewer_id)) -> dict:
    """A playable copy of the game at a position, every seat the admin's (REQ-ADMIN-12). The game is not touched."""
    game = _started(db, game_id)
    try:
        commands = observe.cut(game, body.moves)
    except ValueError as err:
        raise HTTPException(422, str(err)) from err
    data = {"game": bugs.setup(game), "commands": [dict(c) for c in game.commands or []]}
    return {"game_id": _copy(db, data, commands, viewer).id}


def _copy(db: Session, data: dict, moves: int | None, owner: str) -> Game:
    """A new game from a setup and its commands (a bug report's bundle, or a game being watched), keeping only the
    first `moves` commands when given. Every seat is `owner`'s, and a copy never counts for a campaign (REQ-BUG-07)."""
    game = bugs.as_game(data, moves=moves, owner=owner)
    game.status = "active" if moves is not None else game.status
    if game.campaign:  # a copy must never count for the campaign it came from
        game.campaign = {k: v for k, v in game.campaign.items() if k in ("reinforcement", "setup")}
    db.add(game)
    db.commit()
    try:
        state = play.build(game)  # replays with today's rules; moves that no longer apply are dropped and noted
    except Exception as err:  # the setup itself no longer works: report it, and do not leave a broken game behind
        db.delete(game)
        db.commit()
        raise HTTPException(409, f"The game cannot be recreated with the current rules: {err}") from err
    if state.step == "over":
        game.status = "finished"
    elif game.status == "finished":
        game.status = "active"
    db.commit()
    return game


@router.get("/campaigns", dependencies=[Depends(require_admin)])
def all_campaigns(db: Session = Depends(get_db)) -> list[dict]:
    """Every Five-Year Mission campaign, newest first (REQ-ADMIN-04)."""
    camps = db.scalars(select(Campaign).order_by(Campaign.created_at.desc())).all()
    return [{
        "id": c.id,
        "display_name": c.display_name,
        "deck_id": c.deck_id,
        "rank": c.rank,
        "assignments": len(c.assignments or []),
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    } for c in camps]


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)) -> None:
    camp = db.get(Campaign, campaign_id)
    if camp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
    db.delete(camp)
    db.commit()


# ------------------------------------------------------------------ bug reports (REQ-BUG-05 to -08)

def _bug(db: Session, bug_id: str) -> BugReport:
    report = db.get(BugReport, bug_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bug report not found")
    return report


def _bug_summary(r: BugReport) -> dict:
    game = r.bundle.get("game", {})
    return {
        "id": r.id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "game_id": r.game_id,
        "reporter": r.reporter,
        "seat": r.seat,
        "description": r.description,
        "status": r.status,
        "kind": r.kind or "bug",
        "mode": game.get("mode"),
        "box": game.get("box"),
        "players": [f"{s['display_name']} ({s['deck_id']})" for s in game.get("seats", [])],
        "bot": (game.get("bot") or {}).get("deck_id"),
        "turn": r.bundle.get("turn"),
        "step": r.bundle.get("step"),
        "moves": len(r.bundle.get("commands", [])),
    }


@router.get("/bugs", dependencies=[Depends(require_admin)])
def all_bugs(db: Session = Depends(get_db)) -> list[dict]:
    """Every bug report, newest first."""
    reports = db.scalars(select(BugReport).order_by(BugReport.created_at.desc())).all()
    return [_bug_summary(r) for r in reports]


@router.get("/bugs/{bug_id}", dependencies=[Depends(require_admin)])
def one_bug(bug_id: str, db: Session = Depends(get_db)) -> dict:
    """The whole report with its bundle: the file `scripts/replay_bug.py` reads (REQ-BUG-06)."""
    report = _bug(db, bug_id)
    return {**_bug_summary(report), "bundle": report.bundle}


@router.get("/bugs/{bug_id}/download", dependencies=[Depends(require_admin)])
def download_bug(bug_id: str, db: Session = Depends(get_db)) -> Response:
    """The report as a JSON file, written by the server so that no number passes through the browser: a seed above
    2**53 would be rounded by JavaScript and the game would no longer replay (REQ-BUG-06)."""
    import json

    report = _bug(db, bug_id)
    body = json.dumps({**_bug_summary(report), "bundle": report.bundle}, indent=1)
    return Response(body, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="bug-{report.id[:8]}.json"'})


@router.post("/bugs/{bug_id}/status", dependencies=[Depends(require_admin)])
def set_bug_status(bug_id: str, body: BugStatus, db: Session = Depends(get_db)) -> dict:
    report = _bug(db, bug_id)
    report.status = body.status
    db.commit()
    return _bug_summary(report)


@router.delete("/bugs/{bug_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_bug(bug_id: str, db: Session = Depends(get_db)) -> None:
    db.delete(_bug(db, bug_id))
    db.commit()


class Recreate(BaseModel):
    # How many of the report's commands to keep; all of them when left out. Fewer goes back in time.
    moves: int | None = None


@router.post("/bugs/{bug_id}/recreate", dependencies=[Depends(require_admin)])
def recreate_bug(bug_id: str, body: Recreate | None = None, db: Session = Depends(get_db),
                 viewer: str = Depends(viewer_id)) -> dict:
    """Make a playable copy of the reported game, as it was at the report or `moves` commands in (REQ-BUG-07). Every
    seat of the copy is the admin's, so the admin can play either side; the original game is not touched."""
    report = _bug(db, bug_id)
    moves = body.moves if body else None
    if moves is not None and not 0 <= moves <= len(report.bundle["commands"]):
        raise HTTPException(422, "There are not that many moves in the report")
    game = _copy(db, report.bundle, moves, viewer)
    return {"game_id": game.id, "reporter_seat": report.seat}


# ------------------------------------------------------------------ accounts and invitations (REQ-USER-30, -31)

class InviteRequest(BaseModel):
    email: str
    admin: bool = False


def _user_row(u) -> dict:
    return {"id": u.id, "email": u.email, "display_name": u.display_name, "is_admin": u.is_admin,
            "disabled": u.disabled, "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_seen_at": u.last_seen_at.isoformat() if u.last_seen_at else None}


def _invite_row(i) -> dict:
    return {"id": i.id, "email": i.email, "is_admin": i.is_admin,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "expires_at": i.expires_at.isoformat() if i.expires_at else None}


@router.get("/users", dependencies=[Depends(require_admin)])
def all_users(db: Session = Depends(get_db)) -> list[dict]:
    from app.models import User

    return [_user_row(u) for u in db.scalars(select(User).order_by(User.created_at)).all()]


class UserChange(BaseModel):
    disabled: bool | None = None
    is_admin: bool | None = None


@router.patch("/users/{user_id}", dependencies=[Depends(require_admin)])
def change_user(user_id: str, body: UserChange, request: Request, db: Session = Depends(get_db)) -> dict:
    """Disable or enable an account, make it admin or not. An admin cannot do either to themselves, so there is
    always an admin (REQ-USER-31)."""
    from app.models import User

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such account")
    me = session_user(request.cookies, db)
    if me is not None and me.id == user.id and (body.disabled or body.is_admin is False):
        raise HTTPException(409, "You cannot disable yourself or remove your own admin rights")
    if body.disabled is not None:
        user.disabled = body.disabled
    if body.is_admin is not None:
        user.is_admin = body.is_admin
    db.commit()
    return _user_row(user)


@router.post("/users/{user_id}/reset", dependencies=[Depends(require_admin)])
def reset_user(user_id: str, db: Session = Depends(get_db)) -> dict:
    """Email the user a password-reset link, and show it to pass on another way (REQ-USER-22)."""
    from app import users
    from app.models import User

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such account")
    link, outcome = users.start_reset(db, user)
    db.commit()
    return {"link": link, "mail": outcome}


@router.get("/invites", dependencies=[Depends(require_admin)])
def all_invites(db: Session = Depends(get_db)) -> list[dict]:
    from app import users

    return [_invite_row(i) for i in users.open_invites(db)]


@router.post("/invites", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def invite(body: InviteRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    """Invite an email address: the invitation is emailed, and its link shown once, here (REQ-USER-30)."""
    from app import users

    try:
        row, code, outcome = users.create_invite(db, body.email, session_user(request.cookies, db), admin=body.admin)
    except users.UserError as err:
        raise HTTPException(422, str(err)) from err
    db.commit()
    return {**_invite_row(row), "link": users.invite_link(code), "mail": outcome}


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def cancel_invite(invite_id: str, db: Session = Depends(get_db)) -> None:
    from app.models import Invite

    row = db.get(Invite, invite_id)
    if row is None or row.used_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No open invitation")
    db.delete(row)
    db.commit()

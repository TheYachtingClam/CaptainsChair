"""Game state. One serialisable object holds everything (REQ-SRV-10).

The engine mutates a GameState in place; callers that need the previous state keep a copy.
Nothing here knows about the web, the database or card behaviour.
"""

from __future__ import annotations

import random
from typing import Literal

from pydantic import BaseModel, Field

Step = Literal["start", "resupply", "control", "action", "cleanup", "over"]
Resource = Literal["dilithium", "latinum", "glory"]
SPECIALTIES = ("research", "influence", "military")


class Inst(BaseModel):
    """One physical card on the table, identified by a uid unique within the game."""

    uid: str
    card: str  # card id, e.g. "2SOV01"
    exhausted: bool = False
    res: dict[str, int] = Field(default_factory=dict)  # resources placed on the card
    beamed: list[Inst] = Field(default_factory=list)
    at: str | None = None  # deployed Ships: uid of the Location the token is at; None = token on the card
    away: dict[int, int] = Field(default_factory=dict)  # Locations: Away Teams here, by seat


class Option(BaseModel):
    id: str
    label: str
    irreversible: bool = False
    reason: str | None = None  # shown in the can't-be-undone warning (REQ-UNDO-10)


class Decision(BaseModel):
    seat: int
    kind: str
    prompt: str
    options: list[Option]
    # Cards the question is about, shown to the deciding player only: e.g. a just-gained card, or cards
    # looked at from a deck. An option answers with a card when its id is the uid or ends with ":<uid>".
    cards: list[Inst] = Field(default_factory=list)


class Event(BaseModel):
    text: str
    seat: int | None = None  # who it concerns; None = the table
    private_to: int | None = None  # only this seat may see it
    irreversible: bool = False  # reveals information, uses randomness or ends a turn (REQ-UNDO-01)


class OpRef(BaseModel):
    """An operation waiting to run or running: a card's operation, or a system routine."""

    mode: str  # play | activate | trigger | auto | system
    seat: int  # whose operation it is
    uid: str | None = None  # the card
    index: int | None = None  # which printed operation
    system: str | None = None  # name of a system routine, e.g. "drawup"
    event: dict | None = None  # the trigger event, for REACTION and triggered PASSIVE operations


class Running(BaseModel):
    """The operation in progress. It is replayed from `snapshot` with `answers` after every answer."""

    ref: OpRef
    answers: list[str] = Field(default_factory=list)
    snapshot: dict


class Offer(BaseModel):
    """Optional triggered operations offered to one player (REQ-AS-28)."""

    seat: int
    refs: list[OpRef]


class Player(BaseModel):
    seat: int
    name: str
    deck: str
    board: str
    captain: Inst
    status: list[Inst] = Field(default_factory=list)
    hand: list[Inst] = Field(default_factory=list)
    draw: list[Inst] = Field(default_factory=list)  # index 0 is the top
    discard: list[Inst] = Field(default_factory=list)  # last item is the top
    reserve: list[Inst] = Field(default_factory=list)  # index 0 is the top
    development: list[Inst] = Field(default_factory=list)
    staging: list[Inst] = Field(default_factory=list)
    fleet: list[Inst] = Field(default_factory=list)
    locations: list[Inst] = Field(default_factory=list)
    duty: list[Inst] = Field(default_factory=list)
    log: list[Inst] = Field(default_factory=list)
    received_stardates: list[Inst] = Field(default_factory=list)  # held in the Staging Area until Clean-up
    dilithium: int = 0
    latinum: int = 0
    glory: int = 0
    actions: int = 3  # available Action tokens
    tracks: dict[str, int] = Field(default_factory=lambda: {s: 0 for s in SPECIALTIES})
    highest: dict[str, int] = Field(default_factory=lambda: {s: 0 for s in SPECIALTIES})
    away_pool: int = 0  # Away Teams on the Captain
    away_aside: int = 0  # Archer's set-aside Away Teams (REQ-CD-ARC-01)
    mission_tokens: int = 1
    missions_completed: list[str] = Field(default_factory=list)
    controls_this_turn: int = 0


class GameState(BaseModel):
    seed: int
    rng_calls: int = 0
    mode: str
    expansions: list[str] = Field(default_factory=list)
    promos: bool = False
    players: list[Player]
    first_seat: int  # holds the Starting Player token
    active: int
    turn: int = 0  # 0-based count of turns taken
    step: Step = "start"
    substep: str = ""
    market: dict[str, Inst | None] = Field(default_factory=dict)
    market_decks: dict[str, list[Inst]] = Field(default_factory=dict)
    encounter: list[Inst] = Field(default_factory=list)
    incident: list[Inst] = Field(default_factory=list)
    location_deck: list[Inst] = Field(default_factory=list)
    neutral: list[Inst] = Field(default_factory=list)
    junk: list[Inst] = Field(default_factory=list)
    rewards: list[Inst] = Field(default_factory=list)
    stardates: list[Inst] = Field(default_factory=list)  # index 0 is the top card
    stardate_glory: int = 0
    resolution: bool = False
    last_turn: int | None = None
    next_uid: int = 1
    decision: Decision | None = None
    log: list[Event] = Field(default_factory=list)
    result: dict | None = None
    op_queue: list[OpRef] = Field(default_factory=list)
    running: Running | None = None
    pending_events: list[dict] = Field(default_factory=list)  # trigger events waiting to be checked
    offer: Offer | None = None

    # ------------------------------------------------------------------ helpers

    def player(self, seat: int) -> Player:
        return self.players[seat]

    def opponent(self, seat: int) -> Player | None:
        return next((p for p in self.players if p.seat != seat), None)

    def new_inst(self, card: str) -> Inst:
        inst = Inst(uid=f"c{self.next_uid}", card=card)
        self.next_uid += 1
        return inst

    def rng(self) -> random.Random:
        """A fresh generator per call, derived from the seed and a counter.

        This keeps the generator state a single integer, so replay and undo restore it exactly
        (REQ-SRV-15, REQ-UNDO-40).
        """
        self.rng_calls += 1
        return random.Random(f"{self.seed}:{self.rng_calls}")

    def shuffle(self, cards: list[Inst]) -> None:
        self.rng().shuffle(cards)

    def emit(self, text: str, *, seat: int | None = None, private_to: int | None = None, irreversible: bool = False) -> None:
        self.log.append(Event(text=text, seat=seat, private_to=private_to, irreversible=irreversible))

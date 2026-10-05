"""2KIRK07 Hikaru Sulu (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK07.md"""

from dataclasses import dataclass

from engine.cards import development_cost, operation
from engine.ops import A, Cost, Spend

from ._util import ships

development_cost("2KIRK07", Spend(dilithium=2))


@dataclass
class ExhaustAShip(Cost):
    """Exhaust one of your ready Ships (cost)."""

    def can_pay(self, ctx):
        return any(not s.exhausted for s in ships(ctx))

    def pay(self, actions):
        ship = yield from actions.pick_card("Exhaust which Ship (cost)?", [s for s in ships(actions.ctx) if not s.exhausted])
        ship.exhausted = True
        actions.emit(f"{actions.ctx.me.name} exhausts {actions.ctx.name(ship)}.")


@operation("2KIRK07", 0, uses=[A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def helmsman(ctx, actions):
    """PLAY: Take an Incident to your Discard pile. Send 2 [Away Team] to a Location where you have a Ship."""
    yield from actions.take_incident(to="discard")
    yield from actions.send_away_team(2, where=lambda loc: bool(ctx.ships_at(loc)), same_location=True)


@operation("2KIRK07", 1, uses=[A.EXHAUST], cost=[ExhaustAShip()],
           trigger=lambda ctx, ev: ev["kind"] == "would_attack" and ev["seat"] == ctx.me.seat)
def evasive_action(ctx, actions):
    """REACTION: When you would be attacked, exhaust a Ship to ignore the negative effect."""
    return True
    yield  # pragma: no cover

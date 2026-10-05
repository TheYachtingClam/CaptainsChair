"""0LOC01 Starbase 80 (Location, promo). Spec: resources/scans/promo2/cards/location/0LOC01.md"""

from dataclasses import dataclass

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, Cost

from ._util import is_suit


@dataclass
class BeamPersonHere(Cost):
    """Beam a Person from your hand to this Location (cost)."""

    def can_pay(self, ctx):
        return any(is_suit(i, "Person") for i in ctx.me.hand)

    def pay(self, actions):
        person = yield from actions.pick_card("Beam which Person to Starbase 80 (cost)?",
                                              [i for i in actions.ctx.me.hand if is_suit(i, "Person")])
        yield from actions.beam(person, actions.ctx.this_card)


@dataclass
class LogBeamedHere(Cost):
    """Log a card beamed to this Location (cost)."""

    def can_pay(self, ctx):
        return ctx.this_card is not None and bool(ctx.this_card.beamed)

    def pay(self, actions):
        card = yield from actions.pick_card("Log which card beamed to Starbase 80 (cost)?",
                                            list(actions.ctx.this_card.beamed))
        actions._log(card)


@operation("0LOC01", 0, uses=[A.GAIN_CARD])
def salvage(ctx, actions):
    """CONTROL: Gain a Person/Cargo/Ship from the Junk."""
    yield from actions.gain_card(["Person", "Cargo", "Ship"], label="a Person, Cargo or Ship from the Junk",
                                 only_junk=True)


@operation("0LOC01", 1, uses=[A.BEAM, A.JUNK], cost=[BeamPersonHere()],
           requires=lambda ctx: any(is_suit(i, "Incident") for i in ctx.me.hand + ctx.me.discard))
def disposal(ctx, actions):
    """ACTIVATION: Beam a Person here to junk an Incident from your hand or Discard pile. You may junk a card from the
    Market. Ruling: a junked Incident is out of play and no longer counts toward the Burn."""
    incidents = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Incident")]
    incident = yield from actions.pick_card("Junk which Incident?", incidents)
    yield from actions.junk_card(incident)
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@operation("0LOC01", 2, uses=[A.LOG], cost=[LogBeamedHere()],
           trigger=lambda ctx, ev: ev["kind"] == "would_gain" and ev["seat"] == ctx.me.seat)
def salvage_yard(ctx, actions):
    """REACTION: When gaining a card, log a card beamed here to include the Junk."""
    return True
    yield  # pragma: no cover


registry.INCIDENTS_FROM_JUNK.add("0LOC01")  # PASSIVE: When taking an Incident, you may take it from the Junk.

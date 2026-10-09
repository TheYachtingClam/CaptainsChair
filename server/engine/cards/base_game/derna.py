"""1LOC09 Derna (Location). Spec: resources/scans/base_game/cards/location/1LOC09.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, incidents_in_hand, location_of_player


def _weapon(i):
    return has_trait(i, "Weapon")


@operation("1LOC09", 0, uses=[A.SPEND, A.SCAN_FOR, A.DRAW])
def depot(ctx, actions):
    """CONTROL: You may spend 2 [Dilithium] to scan for either Weapon or Doctor. Draw a card."""
    if actions.can_spend(dilithium=2):
        choice = yield from actions.choose("Spend 2 Dilithium to scan for a Weapon or a Doctor?",
                                           [("Weapon", "A Weapon"), ("Doctor", "A Doctor"), ("none", "No")])
        if choice != "none":
            yield from actions.spend(dilithium=2)
            yield from actions.scan_for(lambda i: has_trait(i, choice), f"a {choice}")
    yield from actions.draw(1)


@operation("1LOC09", 1, uses=[A.BEAM], requires=lambda ctx: any(_weapon(i) for i in ctx.me.hand + ctx.me.discard))
def stockpile(ctx, actions):
    """ACTIVATION: Beam a Weapon here from your hand or Discard pile."""
    weapon = yield from actions.pick_card("Beam which Weapon here?", [i for i in ctx.me.hand + ctx.me.discard if _weapon(i)])
    yield from actions.beam(weapon, ctx.this_card)


@operation("1LOC09", 2, uses=[A.DISCARD, A.GAIN_RESOURCE, A.RETURN_INCIDENT],
           cost=[DiscardFromHand(1, lambda ctx, i: _weapon(i), "a Weapon")])
def disarm(ctx, actions):
    """ACTIVATION: Discard a Weapon to gain 1 [Dilithium] and return an Incident."""
    yield from actions.gain_resource("dilithium", 1)
    incident = yield from actions.pick_card("Return which Incident?", incidents_in_hand(ctx))
    if incident:
        yield from actions.return_incident(incident)


@endgame("1LOC09")
def arsenal(state, player):
    """ENDGAME: Score 2 [VP] for each Weapon beamed here."""
    loc = location_of_player(player, "1LOC09")
    return 2 * sum(1 for b in loc.beamed if _weapon(b)) if loc else 0

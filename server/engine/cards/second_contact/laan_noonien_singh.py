"""3PIK22 La'an Noonien Singh (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK22.md"""

from engine.cards import operation, skill_rewrite
from engine.ops import A, TakeIncidentCost, card

from ._util import others_in_hand, ships, table_of


@operation("3PIK22", 0, uses=[A.TAKE_INCIDENT, A.SCAN, A.DRAW, A.GAIN_SPECIALTY], cost=[TakeIncidentCost()])
def security_chief(ctx, actions):
    """PLAY: Take an Incident to scan 1 of Cargo. For each controlled Location where you have an [Away Team], draw a
    card. If you have 2+ [Away Team] on a neutral Location, gain 1 [Military]."""
    yield from actions.scan(1, ["Cargo"])
    n = sum(1 for loc in ctx.me.locations if ctx.away_at(loc))
    if n:
        yield from actions.draw(n)
    if any(ctx.away_at(loc) >= 2 for loc in ctx.state.neutral):
        yield from actions.gain_specialty("military", 1)


@operation("3PIK22", 1, uses=[A.BEAM], requires=lambda ctx: bool(ships(ctx)) and bool(others_in_hand(ctx)))
def beam_up(ctx, actions):
    """ACTIVATION: Beam a card to a Ship."""
    item = yield from actions.pick_card("Beam which card?", others_in_hand(ctx))
    ship = yield from actions.pick_card("To which Ship?", ships(ctx))
    yield from actions.beam(item, ship)


@skill_rewrite("3PIK22")
def tactical(state, owner, source, icons):
    """PASSIVE: If you have a Weapon in play, all [Military] on your cards are treated as [Any Skill] instead."""
    cards = [*table_of(owner), *owner.staging]
    cards += [b for host in cards for b in host.beamed]
    if not any("Weapon" in card(i).traits for i in cards):
        return icons
    return ["Any" if icon == "Military" else icon for icon in icons]

"""Small helpers shared by card modules. Registers nothing."""

from engine.ops import SPECIES, Ctx


def suit_is(*suits):
    return lambda ctx_or_inst, inst=None: _card(ctx_or_inst, inst).suit in suits


def _card(a, b):
    from engine.ops import card

    return card(b if b is not None else a)


def is_suit(inst, *suits) -> bool:
    from engine.ops import card

    return card(inst).suit in suits


def has_trait(inst, *traits) -> bool:
    from engine.ops import card

    return bool(set(card(inst).traits) & set(traits))


def ships(ctx: Ctx):
    """Your deployed Ships."""
    return [s for s in ctx.me.fleet if is_suit(s, "Ship") or ctx.card(s).ship_token]


def locations_with_your_ship(ctx: Ctx):
    return [loc for loc in ctx.all_locations() if ctx.ships_at(loc)]


def species_of(inst):
    from engine.ops import card

    return set(card(inst).traits) & SPECIES

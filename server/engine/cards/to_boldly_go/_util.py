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


def opponent_ships(ctx: Ctx):
    """The opponent's deployed Ships."""
    opp = ctx.opponent
    return [s for s in opp.fleet if is_suit(s, "Ship") or ctx.card(s).ship_token] if opp else []


def count_traits(ctx: Ctx, *traits, player=None, beamed: bool = True, exclude=None) -> int:
    """Cards in play (Staging Area and table, beamed too unless excluded) with any of the traits."""
    return ctx.count_in_play(lambda i: has_trait(i, *traits) and i is not exclude, player, beamed=beamed)


def others_in_hand(ctx: Ctx, pred=None):
    """Your hand, without the card resolving now."""
    this = ctx.this_card
    return [i for i in ctx.me.hand if i is not this and (pred is None or pred(i))]


# ----------------------------------------------------------------------- standard Ship operations
# Many Ships print the same Activations. Each card module registers these with its own ids and indexes.


def warp_this_ship(ctx, actions):
    """Warp this ship."""
    yield from actions.warp(ctx.this_card)


def beam_a_card_here(ctx, actions):
    """Beam a card here (from hand, KW-BEAM). Used after a "Discard a card to" cost."""
    card = yield from actions.pick_card(f"Beam which card to {ctx.name(ctx.this_card)}?", others_in_hand(ctx))
    if card:
        yield from actions.beam(card, ctx.this_card)


def can_discard_then_beam(ctx) -> bool:
    """A discard cost plus a card left to beam."""
    return len(others_in_hand(ctx)) >= 2


def send_team_to_this_ship(ctx, actions):
    """Send an Away Team to this ship's Location. A Ship whose token is still on its card has no Location."""
    loc = ctx.location_of(ctx.this_card)
    if loc is None:
        actions.emit(f"{ctx.name(ctx.this_card)} is not at a Location.")
        return
    yield from actions.send_away_team(1, target=loc)


def deploy_and_warp_this(ctx, actions):
    """Deploy and warp this ship."""
    yield from actions.deploy(ctx.this_card)
    if ctx.this_card in ctx.me.fleet:
        yield from actions.warp(ctx.this_card)

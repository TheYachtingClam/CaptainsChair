"""Small helpers shared by card modules. Registers nothing."""

from engine.ops import SPECIES, Ctx


def suit_is(*suits):
    return lambda ctx_or_inst, inst=None: _card(ctx_or_inst, inst).suit in suits


def _card(a, b):
    from engine.ops import card

    return card(b if b is not None else a)


def is_suit(inst, *suits) -> bool:
    """The card's suit, or a suit a SPECIAL says it is also considered (Gomtuu is a Ship, Species 10-C an Ally)."""
    from engine.ops import suits_of

    return bool(suits_of(inst) & set(suits))


def has_trait(inst, *traits) -> bool:
    """Whether the card has any of the traits, counting "treated as" traits and, for the acting player's own cards,
    Wildcard (REQ-TR-05). Outside an operation (e.g. final scoring) only the card's own traits count."""
    from engine.ops import trait_matches

    return trait_matches(inst, traits)


def printed_trait(inst, *traits) -> bool:
    """Only the traits printed on the card: no Wildcard, no "treated as"."""
    from engine.ops import card

    return bool(set(card(inst).traits) & set(traits))


def distinct_traits(cards, among) -> int:
    """How many different traits from `among` the cards have. Each Wildcard the acting player owns adds one more
    (AS-12: Bajoran + Klingon + Wildcard is 3 different species), up to the number in `among` (REQ-TR-05)."""
    from engine.ops import card, wildcards_owned_by_actor

    cards = list(cards)
    found = {t for c in cards for t in card(c).traits if t in set(among)}
    return min(len(set(among)), len(found) + wildcards_owned_by_actor(cards))


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
    """Cards in play (Staging Area and table, beamed too unless excluded) with any of the traits, counting "treated
    as" traits such as Protocol 12's Augment Doctors."""
    from engine.ops import trait_matches

    return ctx.count_in_play(lambda i: i is not exclude and trait_matches(i, traits, state=ctx.state),
                             player, beamed=beamed)


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


def virtual(ctx: Ctx) -> bool:
    """Cadet Training: the opponent is the virtual opponent with one of everything (REQ-CTM-12)."""
    return ctx.opponent is None and ctx.virtual_opponent


def opponent_has(ctx: Ctx, pred) -> bool:
    """Whether the opponent has a matching card in play. The virtual opponent has one of everything."""
    if ctx.opponent is None:
        return ctx.virtual_opponent
    return ctx.count_in_play(pred, ctx.opponent) > 0


# ----------------------------------------------------------------------- scoring-time helpers (ENDGAME, VP_SPECIAL)


def owned_cards(player):
    """Every card the player owns that counts at final scoring: not Reserve or Development (REQ-FS-02)."""
    from engine.scoring import owned_cards as owned

    return owned(player)


def table_of(player):
    """The player's table positions: Captain, Status, Fleet, Locations, Duty Officers."""
    from engine.ops import table_cards

    return table_cards(player)


def ctx_for(state, player) -> Ctx:
    """A query context for a player outside an operation, e.g. in an ENDGAME or a modifier."""
    from engine.state import OpRef

    return Ctx(state, OpRef(mode="auto", seat=player.seat))

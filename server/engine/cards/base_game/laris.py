"""1PER11 Laris (Person). Spec: resources/scans/base_game/cards/person/1PER11.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, is_suit, table_of


@operation("1PER11", 0, uses=[A.GAIN_SPECIALTY, A.DRAW], cost=[Spend(dilithium=1)])
def tal_shiar_training(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to gain 1 [Research]/[Military]. If you have an Android in play, draw 2 cards."""
    track = yield from actions.choose("Gain 1 on which track?", [("research", "Research"), ("military", "Military")])
    yield from actions.gain_specialty(track, 1)
    if count_traits(ctx, "Android"):
        yield from actions.draw(2)


@operation("1PER11", 1, uses=[A.DUPLICATE])
def again(ctx, actions):
    """RESUPPLY: Duplicate a Resupply operation you have already resolved this turn. Ruling: RESUPPLY operations
    resolve in table order (Captain, Status, Fleet, Locations, Duty Officers), so those are the cards before Laris."""
    table = table_of(ctx.me)
    this = ctx.this_card
    position = next((n for n, i in enumerate(table) if i.uid == this.uid), len(table))
    yield from actions.duplicate(table[:position], label="a card whose RESUPPLY has resolved", kind="RESUPPLY")


def _exhausted(ctx):
    cards = [ctx.me.captain, *ctx.me.fleet, *ctx.me.locations, *ctx.me.status]
    return [i for i in cards if i.exhausted and (i is ctx.me.captain or is_suit(i, "Cargo", "Ship", "Location"))]


@operation("1PER11", 2, uses=[A.SPEND, A.REFRESH],
           requires=lambda ctx: bool(_exhausted(ctx)) and (ctx.me.dilithium >= 2 or ctx.me.latinum >= 1))
def restore(ctx, actions):
    """ACTIVATION: Spend 2 [Dilithium] or 1 [Latinum] to refresh a Captain/Cargo/Ship/Location."""
    options = ([("dilithium", "Spend 2 Dilithium")] if actions.can_spend(dilithium=2) else []) + \
        ([("latinum", "Spend 1 Latinum")] if actions.can_spend(latinum=1) else [])
    pay = options[0][0] if len(options) == 1 else (yield from actions.choose("Pay with which?", options))
    if pay == "dilithium":
        yield from actions.spend(dilithium=2)
    else:
        yield from actions.spend(latinum=1)
    card = yield from actions.pick_card("Refresh which card?", _exhausted(ctx))
    if card:
        yield from actions.refresh(card)

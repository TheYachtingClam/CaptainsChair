"""2LOC04 Cold Station 12 (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC04.md"""

from engine.cards import endgame, operation
from engine.ops import A

from ._locations import beamed_here
from ._util import has_trait


@operation("2LOC04", 0, uses=[A.BEAM])
def store(ctx, actions):
    """CONTROL: You may beam a card from your hand or Discard pile here."""
    card = yield from actions.pick_card("Beam a card from your hand or Discard pile to Cold Station 12?",
                                        ctx.me.hand + ctx.me.discard, optional=True, none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)


@operation("2LOC04", 1, uses=[A.SPEND, A.RECALL])
def thaw(ctx, actions):
    """RESUPPLY: You may spend 1 [Dilithium] to recall a card from here."""
    if beamed_here(ctx) and actions.can_spend(dilithium=1):
        card = yield from actions.pick_card("Spend 1 Dilithium to recall a card from Cold Station 12?",
                                            beamed_here(ctx), optional=True, none_label="No")
        if card:
            yield from actions.spend(dilithium=1)
            yield from actions.recall(card)


@operation("2LOC04", 2, uses=[A.BEAM],
           trigger=lambda ctx, ev: ev["kind"] == "discard" and ev["seat"] == ctx.me.seat and ev.get("step") == "action"
           and ctx.event_card is not None and ctx.event_card in ctx.me.discard)
def preserve(ctx, actions):
    """REACTION: After discarding a card during your Action Step, beam the discarded card here."""
    yield from actions.beam(ctx.event_card, ctx.this_card)


@endgame("2LOC04")
def augments_beamed(state, player):
    """ENDGAME: Score 1 [VP] for each Augment beamed here."""
    station = next((i for i in player.locations if i.card == "2LOC04"), None)
    return sum(1 for b in station.beamed if has_trait(b, "Augment")) if station else 0



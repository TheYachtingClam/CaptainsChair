"""2ENC02 Gomtuu (Encounter, also a Ship). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC02.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import others_in_hand, warp_this_ship

registry.ALSO_SUIT["2ENC02"] = "Ship"  # SPECIAL: This card is considered a Ship for all purposes.


@operation("2ENC02", 0, uses=[A.DEPLOY, A.SPEND, A.GAIN_SPECIALTY])
def living_ship(ctx, actions):
    """PLAY: Deploy this card. You may spend an [Action] to gain 1 [Military] for each [Research] you have in play
    (excluding beamed cards). Any Skill icons count as Research."""
    yield from actions.deploy(ctx.this_card)
    research = sum(1 for c in ctx.in_play(beamed=False) for s in ctx.skills(c) if s in ("Research", "Any"))
    if research and actions.can_spend(actions=1) and (
            yield from actions.may(f"Spend an Action to gain {research} Military?")):
        yield from actions.spend(actions=1)
        yield from actions.gain_specialty("military", research)


operation("2ENC02", 1, uses=[A.WARP])(warp_this_ship)


@operation("2ENC02", 2, uses=[A.BEAM, A.ATTACK, A.WARP])
def tow(ctx, actions):
    """ATTACK ACTIVATION: You may beam a card here. You may warp an opponent Ship from this ship's Location to another
    neutral Location."""
    card = yield from actions.pick_card("Beam a card to Gomtuu?", others_in_hand(ctx), optional=True, none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)
    here = ctx.location_of(ctx.this_card)
    opp = ctx.opponent
    targets = ctx.ships_at(here, opp) if here is not None and opp is not None else []
    if targets and (yield from actions.may("Warp an opponent Ship from here to another neutral Location?")):
        if (yield from actions.attack()):
            ship = yield from actions.pick_card("Warp which opponent Ship?", targets)
            yield from actions.warp(ship, destinations=[l for l in ctx.state.neutral if l.uid != here.uid])

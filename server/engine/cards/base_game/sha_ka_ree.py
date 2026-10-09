"""1ENC07 Sha Ka Ree (Encounter). Spec: resources/scans/base_game/cards/encounter/1ENC07.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import is_suit, others_in_hand

# SPECIAL: This card is considered a Location for all purposes. Deploying this card counts as taking control of a
# Location: its PLAY puts it among your controlled Locations, which raises the take-control event.
registry.ALSO_SUIT["1ENC07"] = "Location"


@operation("1ENC07", 0, uses=[A.TAKE_CONTROL, A.BEAM, A.ATTACK, A.TAKE_INCIDENT])
def centre_of_the_galaxy(ctx, actions):
    """ATTACK PLAY: Deploy this card. You may beam a Ship here. If you do, your opponent takes 2 Incident."""
    yield from actions.take_control(ctx.this_card)
    ship = yield from actions.pick_card("Beam a Ship here?", others_in_hand(ctx, lambda i: is_suit(i, "Ship")),
                                        optional=True, none_label="No")
    if not ship:
        return
    yield from actions.beam(ship, ctx.this_card)
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
        yield from actions.take_incident(opponent=True)

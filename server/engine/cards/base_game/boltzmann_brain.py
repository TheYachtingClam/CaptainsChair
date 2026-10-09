"""1ENC02 Boltzmann Brain (Encounter). Spec: resources/scans/base_game/cards/encounter/1ENC02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import incidents_in_hand


@operation("1ENC02", 0, uses=[A.DRAW, A.RETURN_INCIDENT])
def insight(ctx, actions):
    """PLAY: Draw a card. You may return 1 Incident."""
    yield from actions.draw(1)
    incident = yield from actions.pick_card("Return an Incident from your hand?", incidents_in_hand(ctx),
                                            optional=True, none_label="No")
    if incident:
        yield from actions.return_incident(incident)

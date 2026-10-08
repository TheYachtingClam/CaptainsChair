"""1CAR02 Borg Spatial Trajector (Cargo), the older Core Box version. Spec: resources/scans/base_game/cards/cargo/1CAR02.md
Its first PLAY is registered with To Boldly Go's version (2CAR02), which prints the same text."""

from engine.cards import operation


@operation("1CAR02", 1, uses=[], requires=lambda ctx: False)
def regenerate(ctx, actions):
    """PLAY: If your Captain has Borg and you have 6+ [Borg icon] value: regenerate 1 [Drone] and you may send a
    [Drone] to any Location. Ruling: Borg Collective rules are not in these boxes (KW-DRONE-01), so this can never be
    played."""
    return
    yield  # pragma: no cover

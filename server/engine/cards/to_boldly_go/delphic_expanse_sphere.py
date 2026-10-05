"""2ENC01 Delphic Expanse Sphere (Encounter). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC01.md"""

from engine.cards import operation, trait_modifier
from engine.ops import A, card

from ._util import count_traits


@operation("2ENC01", 0, uses=[A.SCAN, A.GAIN_RESOURCE])
def survey(ctx, actions):
    """PLAY: Scan 1 of either Person, Cargo, Ship, Ally, or Mission. Gain 2 [Dilithium].
    Ruling: Mission is a suit not used in these boxes, so scanning it finds nothing."""
    yield from actions.scan(1, ["Person", "Cargo", "Ship", "Ally"])
    yield from actions.gain_resource("dilithium", 2)


@operation("2ENC01", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def outpost(ctx, actions):
    """PLAY: You may send an [Away Team] to a controlled Location. Gain 1 [Dilithium]/[Latinum] for each Xindi you
    have in play."""
    if ctx.me.locations and (yield from actions.may("Send an Away Team to a controlled Location?")):
        yield from actions.send_away_team(1, where=lambda loc: loc in ctx.me.locations)
    for n in range(1, count_traits(ctx, "Xindi") + 1):
        kind = yield from actions.choose(f"Xindi {n}: gain 1 Dilithium or 1 Latinum?",
                                         [("dilithium", "Dilithium"), ("latinum", "Latinum")])
        yield from actions.gain_resource(kind, 1)


@trait_modifier("2ENC01", staging=True)
def sphere_network(state, owner, inst, target):
    """SPECIAL: While this card is in your Staging Area and you have an Anomaly in your Fleet Area, this card is
    additionally treated as Wildcard."""
    if target is not inst:
        return set()
    return {"Wildcard"} if any("Anomaly" in card(i).traits for i in owner.fleet) else set()

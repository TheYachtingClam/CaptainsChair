"""3PIK25 Negotiate (Directive). Spec: resources/scans/second_contact/cards/captains/pike/3PIK25.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("3PIK25", 0, uses=[A.GAIN_RESOURCE, A.DISCARD, A.FIND])
def negotiate(ctx, actions):
    """PLAY: Gain 1 [Latinum] or 2 [Dilithium]. You may discard up to 3 Cargo/Ship/Ally. Gain 1 [Latinum] and 1
    [Dilithium] for each card discarded this way. You may find an Encounter."""
    choice = yield from actions.choose("Gain which?", [("latinum", "1 Latinum"), ("dilithium", "2 Dilithium")])
    yield from actions.gain_resource(choice, 1 if choice == "latinum" else 2)
    for n in (1, 2, 3):
        out = yield from actions.discard(1, pred=lambda i: is_suit(i, "Cargo", "Ship", "Ally"),
                                         label=f"a Cargo, Ship or Ally ({n} of up to 3)", optional=True)
        if not out:
            break
        yield from actions.gain_resource("latinum", 1)
        yield from actions.gain_resource("dilithium", 1)
    yield from actions.find(lambda i: is_suit(i, "Encounter"), "an Encounter", optional=True)

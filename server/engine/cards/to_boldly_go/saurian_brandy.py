"""2CAR16 Saurian Brandy (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR16.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits


@operation("2CAR16", 0, uses=[A.GAIN_RESOURCE, A.REFRESH], requires=lambda ctx: ctx.track("influence") >= 5)
def toast(ctx, actions):
    """PLAY: Requires [Influence] 5. Gain 1 [Latinum] for each Starfleet you have in play (max 3). Refresh your
    Captain and a Duty Officer."""
    yield from actions.gain_resource("latinum", min(3, count_traits(ctx, "Starfleet")))
    yield from actions.refresh(ctx.me.captain)
    tired = [i for i in ctx.me.duty if i.exhausted]
    officer = yield from actions.pick_card("Refresh which Duty Officer?", tired)
    if officer:
        yield from actions.refresh(officer)


@operation("2CAR16", 1, uses=[A.SCAN, A.JUNK], cost=[Spend(latinum=2)])
def party(ctx, actions):
    """PLAY: Spend 2 [Latinum] to scan 2 of Person, including from the Junk. Junk a card from the Market."""
    yield from actions.scan(2, ["Person"], include_junk=True)
    yield from actions.junk()

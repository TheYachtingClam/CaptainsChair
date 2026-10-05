"""2CAR07 Holosuite (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR07.md"""

from engine.cards import operation
from engine.ops import A, can_afford


@operation("2CAR07", 0, uses=[A.GAIN_RESOURCE, A.REFRESH, A.JUNK])
def recreation(ctx, actions):
    """PLAY: Gain 2 [Latinum]. You may refresh your Duty Officer. Junk a card from the Market."""
    yield from actions.gain_resource("latinum", 2)
    tired = [i for i in ctx.me.duty if i.exhausted]
    officer = yield from actions.pick_card("Refresh a Duty Officer?", tired, optional=True, none_label="No")
    if officer:
        yield from actions.refresh(officer)
    yield from actions.junk()


@operation("2CAR07", 1, uses=[A.SPEND, A.SCAN, A.DRAW], requires=lambda ctx: can_afford(ctx.me, latinum=1))
def program(ctx, actions):
    """PLAY: Spend 1/2/3 [Latinum] to scan 1/2/3 of either Person, Cargo, or Ally. If you spent 2 or more, draw a card."""
    amounts = [n for n in (1, 2, 3) if can_afford(ctx.me, latinum=n)]
    n = int((yield from actions.choose("Spend how much Latinum?", [(str(a), f"{a} Latinum: scan {a}") for a in amounts])))
    yield from actions.spend(latinum=n)
    yield from actions.scan(n, ["Person", "Cargo", "Ally"])
    if n >= 2:
        yield from actions.draw(1)

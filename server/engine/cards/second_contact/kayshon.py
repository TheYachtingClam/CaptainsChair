"""3FRE09 Kayshon (Person, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit

development_cost("3FRE09", Spend(dilithium=2))
SUITS = ("Person", "Cargo", "Ship", "Ally", "Encounter", "Incident")


@operation("3FRE09", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_RESOURCE, A.PROMOTE])
def security_chief(ctx, actions):
    """PLAY: Draw a card. You may discard up to one of each of the following: Person, Cargo, Ship, Ally, Encounter,
    Incident. Gain 1 [Glory] for each card discarded this way. Promote this card to Duty Officer."""
    yield from actions.draw(1)
    used: set[str] = set()
    while True:
        left = [s for s in SUITS if s not in used]
        out = yield from actions.discard(1, pred=lambda i: any(is_suit(i, s) for s in left),
                                         label="a card of a suit not yet discarded", optional=True)
        if not out:
            break
        used.add(next(s for s in left if is_suit(out[0], s)))
        yield from actions.gain_resource("glory", 1)
    if ctx.this_card in ctx.me.staging:
        yield from actions.promote(ctx.this_card)


def _spies(ctx):
    if ctx.opponent is None:
        return 1 if ctx.virtual_opponent else 0  # the virtual opponent has one of everything (REQ-CTM-12)
    return ctx.count_in_play(lambda i: has_trait(i, "Spy"), ctx.opponent)


@operation("3FRE09", 1, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("military") >= 5)
def deploy_team(ctx, actions):
    """ACTIVATION: Requires [Military] 5. Send an [Away Team] to a Location. Repeat this for each Spy your opponent
    has in play."""
    yield from actions.send_away_team(1 + _spies(ctx))

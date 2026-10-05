"""2REB15 Rebelution (Directive). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB15.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_helmet

registry.CANNOT_LOG.add("2REB15")  # SPECIAL: This card cannot be logged.


def _helmets(ctx):
    """Your Helmets in play, wherever they are beamed ("every Helmet" means your own: this is not an attack). Cards in
    the Staging Area cannot be dismissed (KW-DSM-04)."""
    return [i for i in ctx.in_play() if is_helmet(i) and i not in ctx.me.staging]


def _dismiss_helmets(ctx, actions):
    n = 0
    for helmet in _helmets(ctx):
        yield from actions.dismiss(helmet)
        n += 1
    return n


@operation("2REB15", 0, uses=[A.GAIN_RESOURCE, A.DISMISS])
def uprising(ctx, actions):
    """PLAY: Gain 1 [Glory]. Dismiss every Helmet."""
    yield from actions.gain_resource("glory", 1)
    yield from _dismiss_helmets(ctx, actions)


@operation("2REB15", 1, uses=[A.DISMISS, A.EXHAUST, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("military") >= 5)
def revolution(ctx, actions):
    """PLAY: Requires [Military] 5. Dismiss every Helmet and exhaust every unexhausted Ongoing / Location you have in
    play. If you dismissed at least 2 Helmet, send an [Away Team] to a Location."""
    n = yield from _dismiss_helmets(ctx, actions)
    for card in [i for i in ctx.me.fleet if has_trait(i, "Ongoing")] + list(ctx.me.locations):
        if not card.exhausted:
            yield from actions.exhaust(card)
    if n >= 2:
        yield from actions.send_away_team(1)

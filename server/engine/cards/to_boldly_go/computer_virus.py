"""2CAR04 Computer Virus (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR04.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, opponent_ships


@operation("2CAR04", 0, uses=[A.DEPLOY, A.ATTACK, A.FORCE, A.DISMISS, A.TAKE_INCIDENT])
def infect(ctx, actions):
    """ATTACK PLAY: Deploy this card. Force your opponent to dismiss a card beamed to a Ship. If they cannot, they
    take an Incident. Cadet: the virtual opponent dismisses its beamed card, which gives you nothing."""
    yield from actions.deploy(ctx.this_card)
    if not (yield from actions.attack()) or ctx.opponent is None:
        return
    opp = ctx.opponent
    beamed = [b for ship in opponent_ships(ctx) for b in ship.beamed]
    if beamed:
        card = yield from actions.pick_card("Computer Virus: dismiss one of your cards beamed to a Ship.", beamed,
                                            seat=opp.seat)
        yield from actions.dismiss(card)
    else:
        yield from actions.take_incident(opponent=True)


@operation("2CAR04", 1, uses=[A.RECALL], requires=lambda ctx: ctx.track("military") >= 4,
           trigger=lambda ctx, ev: ev["kind"] == "warp" and ev["seat"] != ctx.me.seat
           and ctx.state.step == "action" and ctx.track("military") >= 4)
def retreat(ctx, actions):
    """REACTION: Requires [Military] 4. After your opponent warps a Ship during their Action Step, recall this card."""
    yield from actions.recall(ctx.this_card)


@operation("2CAR04", 2, uses=[A.GAIN_RESOURCE, A.LOG],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] != ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Security", "Engineer"))
def detected(ctx, actions):
    """PASSIVE: After your opponent puts a Security/Engineer into play, gain 1 [Glory] and log this card."""
    yield from actions.gain_resource("glory", 1)
    yield from actions.log(ctx.this_card)

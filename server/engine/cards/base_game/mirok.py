"""1PER15 Mirok (Person). Spec: resources/scans/base_game/cards/person/1PER15.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("1PER15", 0, uses=[A.LOG, A.ATTACK, A.FORCE, A.GAIN_RESOURCE, A.TAKE_INCIDENT, A.PROMOTE])
def interphase(ctx, actions):
    """ATTACK PLAY: You may log a Cloak from your hand or from play to force your opponent to log a Ship from their
    Discard pile. If they do, gain 1 [Glory]. If they cannot, they take an Incident. You may promote this card to Duty
    Officer. Against the Bot you say whether it succeeded (REQ-SOLO-190)."""
    this = ctx.this_card
    cloaks = [i for i in ctx.me.hand + ctx.in_play() if i.uid != this.uid and has_trait(i, "Cloak")]
    cloak = yield from actions.pick_card("Log a Cloak from your hand or from play?", cloaks, optional=True,
                                         none_label="No")
    if cloak:
        yield from actions.log(cloak)
        opp = ctx.opponent
        if (yield from actions.attack()):
            if opp is None:
                if ctx.virtual_opponent:
                    yield from actions.gain_resource("glory", 1)
            elif opp.bot is not None:
                if (yield from actions.bot_hand_attack(opp)):
                    yield from actions.gain_resource("glory", 1)
                else:
                    yield from actions.take_incident(opponent=True)
            else:
                wrecks = [i for i in opp.discard if is_suit(i, "Ship")]
                if wrecks:
                    ship = yield from actions.pick_card("Mirok: log a Ship from your Discard pile.", wrecks,
                                                        seat=opp.seat)
                    yield from actions.log(ship)
                    yield from actions.gain_resource("glory", 1)
                else:
                    yield from actions.take_incident(opponent=True)
    if (yield from actions.may("Promote Mirok to Duty Officer?")):
        yield from actions.promote(this)


@operation("1PER15", 1, uses=[A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Cargo"))
def analysis(ctx, actions):
    """REACTION: After putting a Cargo into play, draw a card."""
    yield from actions.draw(1)

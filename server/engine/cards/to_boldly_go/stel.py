"""2SOV15 Stel (Person). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV15.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, ships


@operation("2SOV15", 0, uses=[A.SEND_AWAY_TEAM, A.BEAM])
def security_detail(ctx, actions):
    """PLAY: Send an [Away Team] to a controlled Location. You may beam a card to a deployed Ship."""
    yield from actions.send_away_team(1, where=lambda loc: loc in ctx.me.locations)
    others = [i for i in ctx.me.hand if i is not ctx.this_card]
    if ships(ctx) and others:
        card = yield from actions.pick_card("Beam a card to a deployed Ship?", others, optional=True, none_label="No")
        if card:
            ship = yield from actions.pick_card("To which Ship?", ships(ctx))
            yield from actions.beam(card, ship)


@operation("2SOV15", 1, uses=[A.ATTACK, A.FORCE, A.DISMISS, A.GAIN_RESOURCE, A.LOG])
def expose(ctx, actions):
    """ATTACK PLAY: Force your opponent to dismiss a Romulan/Andorian. If they do, gain 1 [Glory]. You may log a card
    from your hand or Discard pile. Ruling: a Wildcard cannot be forced to count as Romulan or Andorian."""
    opp = ctx.opponent
    if (yield from actions.attack()):
        if opp is None:
            yield from actions.gain_resource("glory", 1)  # the virtual opponent has one of everything
        else:
            # In-play cards that can be dismissed; Locations cannot be (KW-DSM-05).
            targets = [i for i in [*opp.fleet, *opp.duty, *opp.status] if has_trait(i, "Romulan", "Andorian")]
            card = yield from actions.pick_card("Stel: dismiss one of your Romulan or Andorian cards.", targets,
                                                seat=opp.seat)
            if card:
                yield from actions.dismiss(card)
                yield from actions.gain_resource("glory", 1)
    card = yield from actions.pick_card("Log a card from your hand or Discard pile?",
                                        [i for i in ctx.me.hand + ctx.me.discard if i is not ctx.this_card],
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)


@operation("2SOV15", 2, uses=[A.EXHAUST, A.RECALL, A.FREE_PLAY])
def sweep(ctx, actions):
    """ACTIVATION: You may exhaust a deployed Ship to recall a card beamed to it. You may free play an Incident."""
    ready = [s for s in ships(ctx) if not s.exhausted and s.beamed]
    ship = yield from actions.pick_card("Exhaust a Ship to recall a card beamed to it?", ready, optional=True,
                                        none_label="No")
    if ship:
        yield from actions.exhaust(ship)
        card = yield from actions.pick_card("Recall which beamed card?", list(ship.beamed))
        yield from actions.recall(card)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)

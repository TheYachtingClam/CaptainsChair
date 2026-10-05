"""3RIK03 Nepenthe (Location, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK03.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, ExhaustCaptain, LogFromHand

from ._util import has_trait, is_suit

development_cost("3RIK03", LogFromHand(lambda ctx, i: i in ctx.me.fleet and is_suit(i, "Ship"), "a deployed Ship",
                                       ("play",)))


@operation("3RIK03", 0, uses=[A.EXHAUST, A.TAKE_CONTROL], cost=[ExhaustCaptain()])
def retreat(ctx, actions):
    """PLAY: Exhaust your Captain to take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("3RIK03", 1, uses=[A.SCAN_FOR])
def kestra(ctx, actions):
    """CONTROL: You may scan for a Synthetic."""
    if (yield from actions.may("Scan for a Synthetic?")):
        yield from actions.scan_for(lambda i: has_trait(i, "Synthetic"), "a Synthetic")


@operation("3RIK03", 2, uses=[A.LOG, A.RETURN_INCIDENT, A.GAIN_RESOURCE],
           requires=lambda ctx: bool(ctx.me.hand or ctx.me.discard))
def homestead(ctx, actions):
    """ACTIVATION: Log a card from your hand or Discard pile. You may return an Incident from the same place. If the
    logged card is Android, gain 3 [Glory]."""
    zones = [z for z in ("hand", "discard") if getattr(ctx.me, z)]
    zone = zones[0] if len(zones) == 1 else (
        yield from actions.choose("Log a card from where?", [("hand", "Your hand"), ("discard", "Your Discard pile")]))
    logged = yield from actions.pick_card("Log which card?", list(getattr(ctx.me, zone)))
    yield from actions.log(logged)
    incidents = [i for i in getattr(ctx.me, zone) if is_suit(i, "Incident")]
    incident = yield from actions.pick_card("Return an Incident from the same place?", incidents, optional=True,
                                            none_label="No")
    if incident:
        yield from actions.return_incident(incident)
    if has_trait(logged, "Android"):
        yield from actions.gain_resource("glory", 3)


@endgame("3RIK03")
def peace(state, player):
    """ENDGAME: Requires [Research] 9. Score 3 [VP]."""
    return 3 if player.tracks["research"] >= 9 else 0

"""2GEO06 Binary Stars Comms Relay (Location). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DismissDutyOfficer, Spend

from ._util import has_trait, is_suit

development_cost("2GEO06", Spend(dilithium=3), DismissDutyOfficer())


@operation("2GEO06", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2GEO06", 1, uses=[A.LOG, A.SCAN_FOR])
def log_starfleet_scan_klingon(ctx, actions):
    """CONTROL: Up to three times: log a Starfleet from your hand to scan for a Klingon."""
    for _ in range(3):
        starfleet = [i for i in ctx.me.hand if has_trait(i, "Starfleet")]
        card = yield from actions.pick_card("Log a Starfleet from your hand to scan for a Klingon?", starfleet,
                                            optional=True, none_label="Stop")
        if not card:
            break
        yield from actions.log(card)
        yield from actions.scan_for(lambda i: has_trait(i, "Klingon"), "a Klingon")


@operation("2GEO06", 2, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat and _is_ship(ctx, ev))
def glory_on_deploy(ctx, actions):
    """REACTION: After deploying a Ship, gain 1 Glory."""
    yield from actions.gain_resource("glory", 1)


def _is_ship(ctx, ev):
    from engine.ops import find_inst

    inst = find_inst(ctx.state, ev["uid"])
    return inst is not None and (is_suit(inst, "Ship") or ctx.card(inst).ship_token)

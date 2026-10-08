"""The Freeman Bot's Automated Command rows. Spec: resources/scans/second_contact/command/freeman.md"""

from engine.bot import LOG_TOP_DISCARDS, VALUE_BONUS, row
from engine.bot.georgiou import _directive_with_officer
from engine.ops import A, card

CREW = "freeman"

# Special rule: a Lower Decker logged from the top of the Bot deck is discarded instead, and Lower Deckers are worth
# 1 more to the Bot. (A Fleet of 30 California-Class Ships counts as 2 tokens for the Bot too: engine SHIP_WEIGHT.)
LOG_TOP_DISCARDS[CREW] = ("Lower Decker",)
VALUE_BONUS[CREW] = lambda state, bot, inst: 1 if "Lower Decker" in card(inst).traits else 0


def _lower_decker(inst) -> bool:
    return inst is not None and "Lower Decker" in card(inst).traits


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.GAIN_RESOURCE, A.CONTINUE_RESOLUTION])
def orion(ctx, actions):
    """Orion: If the Bot has 3 or fewer [Influence], gain 1 [Influence]. Otherwise, if able gain an Orion including
    from the Junk; otherwise gain 2 [Glory]. Gain 1 [Influence]. Continue resolution."""
    if actions.track("influence") <= 3:
        yield from actions.gain_specialty("influence", 1)
    elif (yield from actions.gain_card("Orion", including_junk=True)) is None:
        yield from actions.gain_glory(2)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.continue_resolution()


@row(CREW, "traits", 3, uses=[A.PROMOTE, A.RESOLVE_CARD, A.DISCARD, A.CONTINUE_RESOLUTION])
def lower_decker(ctx, actions):
    """Lower Decker: If this card is a Person and the Bot has no Duty Officer, promote this card to Duty Officer and
    resolve the top card of the Bot deck; otherwise discard the top 2 cards of the Bot deck and continue
    resolution."""
    if actions.is_("Person") and actions.duty_officer is None:
        yield from actions.promote()
        yield from actions.resolve_top()
    else:
        yield from actions.discard_top(2)
        yield from actions.continue_resolution()


@row(CREW, "traits", 4, uses=[A.JUNK, A.TAKE_INCIDENT, A.GAIN_CARD, A.TAKE_ENCOUNTER, A.DESTROY, A.LOG])
def anomaly(ctx, actions):
    """Anomaly: Junk the most valuable card in the Market (ignoring any with tokens). Gain an Incident and a Cargo. If
    there is an Anomaly in the Bot's Log already, gain the top Encounter and destroy this card; otherwise log this
    card."""
    yield from actions.junk()
    yield from actions.gain_incident()
    yield from actions.gain_card("Cargo")
    if any("Anomaly" in card(i).traits for i in ctx.me.log):
        yield from actions.take_encounter(gain=True)
        yield from actions.destroy()
    else:
        yield from actions.log()


@row(CREW, "traits", 5, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.RETURN_INCIDENT])
def doctor(ctx, actions):
    """Doctor: Gain 1 [Research]. Discard the top 2 cards of the Bot deck. If able, return an Incident from the Bot
    Discard pile; otherwise gain 1 [Research]."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.discard_top(2)
    if not (yield from actions.return_incident_from_discard()):
        yield from actions.gain_specialty("research", 1)


@row(CREW, "traits", 6, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_SPECIALTY, A.GAIN_RESOURCE])
def security_ops(ctx, actions):
    """Security / Ops: If able, you remove an [Away Team] from a neutral Location and the Bot gains 1 [Research] /
    [Influence] / [Military] (whichever is lower); otherwise gain 2 [Glory] and 2 [Military]. A cancelled attack
    counts as not able."""
    human = actions.human
    removed = None
    if human is not None and any(loc.away.get(human.seat) for loc in ctx.state.neutral):
        if (yield from actions.attack(removes_away_teams=True)):
            removed = yield from actions.human_removes_away_team(lambda loc: loc in ctx.state.neutral)
    if removed is not None:
        yield from actions.gain_lowest()
    else:
        yield from actions.gain_glory(2)
        yield from actions.gain_specialty("military", 2)


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Return this card."""
    yield from actions.log_top(1)
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.PROMOTE, A.GAIN_CARD])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. If able, promote a Person from
    Bot Discard pile to Duty Officer; otherwise gain a Lower Decker > Orion / Security / Ops > Ally."""
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()
    if (yield from actions.promote_from_discard()) is None:
        yield from actions.gain_card("Lower Decker > Orion / Security / Ops > Ally")


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally(ctx, actions):
    """Ally: Gain a Person. Log the top card of the Bot deck. Log this card."""
    yield from actions.gain_card("Person")
    yield from actions.log_top(1)
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.PROMOTE, A.GAIN_CARD])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. If able, promote a
    Person from Bot Discard pile to Duty Officer; otherwise gain Ship / Ally."""
    yield from actions.discard_top(2)
    yield from actions.send_away_team()
    if (yield from actions.promote_from_discard()) is None:
        yield from actions.gain_card("Ship / Ally")


@row(CREW, "no_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). If the Bot has 4
    or more [Research], gain Lower Decker / Anomaly / Doctor, including from the Junk. If the Bot has 4 or more
    [Military], send an [Away Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "military")
    if actions.track("research") >= 4:
        yield from actions.gain_card("Lower Decker / Anomaly / Doctor", including_junk=True)
    if actions.track("military") >= 4:
        yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_CARD, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Take a Lower Decker if able; otherwise gain a Ship / Ally and take an Incident. Send an [Away Team]
    to a neutral Location."""
    if (yield from actions.gain_card("Lower Decker", take=True)) is None:
        yield from actions.gain_card("Ship / Ally")
        yield from actions.take_incident()
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.GAIN_RESOURCE, A.LOG])
def encounter(ctx, actions):
    """Encounter: Gain 2 [Glory] and log this card."""
    yield from actions.gain_glory(2)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.RETURN_INCIDENT, A.GAIN_CARD])
def location(ctx, actions):
    """Location: Gain 1 [Influence]. Discard the top card of the Bot deck. Return an Incident from the Bot Discard pile
    if able; otherwise gain a Person."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.discard_top(1)
    if not (yield from actions.return_incident_from_discard()):
        yield from actions.gain_card("Person")


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Send an [Away Team] to a neutral Location. Gain 1 [Military]. Return this card."""
    yield from actions.send_away_team()
    yield from actions.gain_specialty("military", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.DISMISS, A.LOG])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. If Duty Officer is Lower Decker,
    dismiss them; otherwise log them and the top card of the Bot deck."""
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()
    if _lower_decker(actions.duty_officer):
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.log_duty_officer()
        yield from actions.log_top(1)


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. Gain a Person. Log the top card of the Bot deck. Log this
    card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Person")
    yield from actions.log_top(1)
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.DISCARD, A.GAIN_CARD, A.RESOLVE_CARD, A.GAIN_SPECIALTY, A.LOG])
def cargo_officer(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Gain a Person. If able, resolve a Ship from the Bot Discard
    pile; otherwise gain 1 [Research]/[Influence]/[Military], whichever is higher. Log the top card of the Bot deck.
    Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Person")
    if (yield from actions.resolve_from_discard("Ship")) is None:
        yield from actions.gain_highest()
    yield from actions.log_top(1)
    yield from actions.log()


@row(CREW, "with_duty_officer", 5, uses=[A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.DISCARD, A.GAIN_CARD, A.DISMISS])
def person_officer(ctx, actions):
    """Person: Gain 1 [Research]. If this card is Synthetic take an Incident and discard the top card of the
    Supplement deck. If able, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Ship. Dismiss Duty
    Officer."""
    yield from actions.gain_specialty("research", 1)
    if "Synthetic" in card(actions.this).traits:
        yield from actions.take_incident()
        yield from actions.discard_supplement_top()
    yield from actions.gain_card("[Research Focus] / [Influence Focus] / [Military Focus] > Ship")
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_SPECIALTY, A.DISCARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise gain 1 [Research] / [Military], whichever is lower, and discard the top card of the Bot
    deck."""
    if not (yield from _directive_with_officer(actions)):
        yield from actions.gain_lowest("research", "military")
        yield from actions.discard_top(1)


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Take a Lower Decker / Orion / Anomaly / Doctor / Security / Ops, if able, and log this card;
    otherwise log the top 2 cards of the Bot deck."""
    if (yield from actions.gain_card("Lower Decker / Orion / Anomaly / Doctor / Security / Ops", take=True)):
        yield from actions.log()
    else:
        yield from actions.log_top(2)


@row(CREW, "with_duty_officer", 8, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.LOG, A.DISMISS])
def location_officer(ctx, actions):
    """Location: Discard the top 2 cards of the Bot deck. Gain 1 [Influence]. Log the top card of the Bot deck. If the
    Duty Officer is Lower Decker, dismiss them; otherwise log them."""
    yield from actions.discard_top(2)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.log_top(1)
    if _lower_decker(actions.duty_officer):
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.log_duty_officer()

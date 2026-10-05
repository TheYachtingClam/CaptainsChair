"""The Georgiou Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/georgiou.md"""

from engine.bot import row
from engine.ops import A

CREW = "georgiou"


def _directive_with_officer(actions):
    """"If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log this
    card." Returns True if it did."""
    if not actions.can_log_location_and_remove_two():
        return False
    yield from actions.log_controlled_location()
    yield from actions.remove_away_team(2)
    yield from actions.take_encounter()
    yield from actions.log()
    return True


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.JUNK, A.TAKE_INCIDENT, A.LOG, A.RESOLVE_CARD])
def anomaly(ctx, actions):
    """Anomaly: Junk the most valuable card in the Market (ignoring any with tokens). Gain an Incident. Log this card.
    Resolve the top card of the Bot deck."""
    yield from actions.junk()
    yield from actions.gain_incident()
    yield from actions.log()
    yield from actions.resolve_top()


@row(CREW, "traits", 3, uses=[A.LOG, A.GAIN_SPECIALTY, A.CONTINUE_RESOLUTION])
def kelpien(ctx, actions):
    """Kelpien: Log the top card of the Bot deck. Gain 1 [Research]. Continue resolution."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.continue_resolution()


@row(CREW, "traits", 4, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.CONTINUE_RESOLUTION])
def vulcan(ctx, actions):
    """Vulcan: Discard the top card of the Bot deck. Gain 1 [Influence]. Continue resolution."""
    yield from actions.discard_top(1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.continue_resolution()


@row(CREW, "traits", 5, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_CARD, A.GAIN_SPECIALTY, A.GAIN_RESOURCE,
                             A.PROMOTE])
def security_ops(ctx, actions):
    """Security / Ops: You remove [Away Team]. Gain Spy / Klingon if able. Otherwise, gain 1 [Military] and 1
    [Glory]. If this card is a Person, promote it to Duty Officer."""
    if (yield from actions.attack(removes_away_teams=True)):
        yield from actions.human_removes_away_team(lambda loc: True)
    if (yield from actions.gain_card("Spy / Klingon")) is None:
        yield from actions.gain_specialty("military", 1)
        yield from actions.gain_glory(1)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 6, uses=[A.GAIN_RESOURCE, A.CONTINUE_RESOLUTION, A.DISMISS, A.TAKE_INCIDENT, A.ATTACK,
                             A.GAIN_CARD, A.GAIN_SPECIALTY, A.PROMOTE])
def attack(ctx, actions):
    """Attack: If [Research] is higher than [Military], gain 1 [Glory] and continue resolution. Otherwise: Dismiss
    Duty Officer if able, otherwise take an Incident. You dismiss a Duty Officer, if able, otherwise the bot takes
    Kelpien / Vulcan > Ship and gains 1 [Research]. If this card is a Person, promote it to Duty Officer.
    A cancelled attack counts as the human not dismissing one."""
    if actions.track("research") > actions.track("military"):
        yield from actions.gain_glory(1)
        yield from actions.continue_resolution()
        return
    if actions.duty_officer is not None:
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.take_incident()
    dismissed = False
    if (yield from actions.attack()):
        dismissed = yield from actions.human_dismisses_duty_officer()
    if not dismissed:
        yield from actions.gain_card("Kelpien / Vulcan > Ship", take=True)
        yield from actions.gain_specialty("research", 1)
    if actions.is_("Person"):
        yield from actions.promote()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain a Person. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Person")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral
    Location."""
    yield from actions.deploy()
    yield from actions.explore()
    if actions.topmost_in_discard("Person") is not None:
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.LOG])
def ally(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. If a Person is in Bot Discard pile, gain 1 [Research] /
    [Influence] / [Military] (whichever is lower). For each Ship in Bot Discard pile, send an [Away Team] to a neutral
    Location. Log this card."""
    yield from actions.discard_top(2)
    if actions.topmost_in_discard("Person") is not None:
        yield from actions.gain_lowest()
    from engine.bot.actions import card_matches

    for _ in [i for i in ctx.me.discard if card_matches(i, "Ship")]:
        yield from actions.send_away_team()
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_CARD, A.LOG])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. Take a Person. Log
    this card."""
    yield from actions.discard_top(2)
    yield from actions.send_away_team()
    yield from actions.gain_card("Person", take=True)
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). Send an [Away
    Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "military")
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_CARD, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Gain a Ship / Ally and take an Incident. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_card("Ship / Ally")
    yield from actions.take_incident()
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.LOG, A.GAIN_CARD])
def encounter(ctx, actions):
    """Encounter: Log the top 2 cards of the Bot deck. Take a Ship. Log this card."""
    yield from actions.log_top(2)
    yield from actions.gain_card("Ship", take=True)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_RESOURCE])
def location(ctx, actions):
    """Location: Discard the top card of the Bot deck. Return an Incident from Bot Discard pile if able, otherwise
    gain 1 [Glory]."""
    yield from actions.discard_top(1)
    incident_card = actions.topmost_in_discard("Incident")
    if incident_card is not None:
        yield from actions.return_incident(incident_card)
    else:
        yield from actions.gain_glory(1)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Send an [Away Team] to a neutral Location. Gain 1 [Military]. Return this card."""
    yield from actions.send_away_team()
    yield from actions.gain_specialty("military", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Gain 1 [Research]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Discard the top card of the Bot deck. Gain a Kelpien > Ally. Log Duty Officer. Log this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_card("Kelpien > Ally")
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.DISCARD, A.GAIN_CARD, A.DEPLOY, A.EXPLORE])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. Gain a Ship. Deploy the
    gained Ship; it explores. Log Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.discard_top(2)
    gained = yield from actions.gain_card("Ship")
    if gained is not None:
        yield from actions.deploy(gained)
        yield from actions.explore(gained)
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.LOG, A.SEND_AWAY_TEAM])
def person_officer(ctx, actions):
    """Person: Log the top card of the Bot deck. Send an [Away Team] to a neutral Location."""
    yield from actions.log_top(1)
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then
    log this card. Otherwise, gain a [Research Focus]/[Military Focus] > Anomaly > Cargo."""
    if not (yield from _directive_with_officer(actions)):
        yield from actions.gain_card("[Research Focus] / [Military Focus] > Anomaly > Cargo")


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Research] / [Military] (whichever is higher). Take a Vulcan > Ally > Ship. Log this card."""
    yield from actions.gain_highest("research", "military")
    yield from actions.gain_card("Vulcan > Ally > Ship", take=True)
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.LOG, A.GAIN_SPECIALTY])
def location_officer(ctx, actions):
    """Location: Log the top 2 cards of the Bot deck. Gain 1 [Research]. Log Duty Officer."""
    yield from actions.log_top(2)
    yield from actions.gain_specialty("research", 1)
    yield from actions.log_duty_officer()

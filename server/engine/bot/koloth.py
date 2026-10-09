"""The Koloth Bot's Automated Command rows. Spec: resources/scans/base_game/command/koloth.md"""

from engine.bot import row
from engine.bot.actions import card_matches
from engine.ops import A

CREW = "koloth"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.JUNK, A.GAIN_SPECIALTY, A.DISMISS, A.GAIN_RESOURCE, A.LOG, A.ATTACK,
                             A.REMOVE_AWAY_TEAM])
def weapon(ctx, actions):
    """Weapon: Junk the most valuable card in the Market (ignoring any with tokens). Gain 1 [Military]. If Bot has 9+
    [Military] and Bot Duty Officer is a Klingon, dismiss Duty Officer, gain 4 [Glory], and log this card. Otherwise,
    if able, you remove [Away Team]. Otherwise, gain 1 [Military]."""
    yield from actions.junk()
    yield from actions.gain_specialty("military", 1)
    officer = actions.duty_officer
    if actions.track("military") >= 9 and officer is not None and card_matches(officer, "Klingon"):
        yield from actions.dismiss_duty_officer()
        yield from actions.gain_glory(4)
        yield from actions.log()
        return
    removed = None
    if (yield from actions.attack(removes_away_teams=True)):
        removed = yield from actions.human_removes_away_team(lambda loc: True)
    if removed is None:
        yield from actions.gain_specialty("military", 1)


@row(CREW, "traits", 3, uses=[A.JUNK, A.PUT, A.ATTACK, A.DISMISS, A.GAIN_RESOURCE])
def attack(ctx, actions):
    """Attack: Junk the most valuable card in the Market (ignoring any with tokens). If able, return a Ship from
    discard to the top of the Bot deck. Otherwise, if able, you dismiss Ship. Otherwise gain 1 [Glory]."""
    yield from actions.junk()
    if (yield from actions.put_ship_from_discard_on_top()) is not None:
        return
    dismissed = None
    if actions.human_deployed_ships() and (yield from actions.attack()):
        dismissed = yield from actions.human_dismisses_ship()
    if dismissed is None:
        yield from actions.gain_glory(1)


@row(CREW, "traits", 4, uses=[A.LOG, A.PUT])
def romulan(ctx, actions):
    """Romulan: Log the top card of the Bot deck. Take the top card of the Supplement deck. Log this card."""
    yield from actions.log_top(1)
    yield from actions.take_supplement_top()
    yield from actions.log()


@row(CREW, "traits", 5, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_SPECIALTY])
def scientist(ctx, actions):
    """Scientist: Discard the top card of the Bot deck. Gain 2 [Glory]. Gain 1 [Influence]."""
    yield from actions.discard_top(1)
    yield from actions.gain_glory(2)
    yield from actions.gain_specialty("influence", 1)


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.DRAW, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Gain a [Military Focus] > Person / Ship. Send an [Away Team] to a neutral Location. You may draw a
    card. Return this card."""
    yield from actions.gain_card("[Military Focus] > Person / Ship")
    yield from actions.send_away_team()
    yield from actions.human_may_draw()
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. Send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_CARD, A.ATTACK, A.TAKE_INCIDENT, A.LOG])
def ally(ctx, actions):
    """Ally: If able, gain a Romulan. Otherwise, take a Ship / Person and you take an Incident. Log this card."""
    if (yield from actions.gain_card("Romulan")) is None:
        yield from actions.gain_card("Ship / Person", take=True)
        if (yield from actions.attack()):
            yield from actions.human_takes_incident()
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD])
def cargo(ctx, actions):
    """Cargo: Gain 1 [Influence]. Gain 1 [Military]. Gain a Person / Ship / Ally."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Person / Ship / Ally")


@row(CREW, "no_duty_officer", 5, uses=[A.DISCARD, A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD, A.PROMOTE])
def person(ctx, actions):
    """Person: Discard the top card of the Bot deck. Log the top card of the Bot deck. Gain 1 [Military] / [Influence]
    (whichever is lower). Gain a Weapon > Ship. Promote this card to Duty Officer."""
    yield from actions.discard_top(1)
    yield from actions.log_top(1)
    yield from actions.gain_lowest("military", "influence")
    yield from actions.gain_card("Weapon > Ship")
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Take an Incident. Send an [Away Team] to
    a neutral Location."""
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("military", 1)
    yield from actions.take_incident()
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.LOG])
def encounter(ctx, actions):
    """Encounter: Gain a Person / Ally. Send an [Away Team] to a neutral Location. Log this card."""
    yield from actions.gain_card("Person / Ally")
    yield from actions.send_away_team()
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.DISCARD, A.GAIN_RESOURCE])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. If a Ship is in Bot Discard
    pile, gain 1 [Glory]."""
    yield from actions.log_top(1)
    yield from actions.discard_top(2)
    if actions.in_discard("Ship"):
        yield from actions.gain_glory(1)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.SEND_AWAY_TEAM, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Gain 1 [Military]. If able, gain a Romulan. Otherwise, take a [Military Focus] > Cargo. Send an [Away
    Team] to a neutral Location. Return this card."""
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.gain_card("Romulan")) is None:
        yield from actions.gain_card("[Military Focus] > Cargo", take=True)
    yield from actions.send_away_team()
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Gain 1 [Influence]. Deploy this Ship; it engages. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_CARD, A.TAKE_INCIDENT, A.GAIN_RESOURCE, A.ATTACK, A.DISCARD,
                                        A.DISMISS, A.LOG])
def ally_officer(ctx, actions):
    """Ally: If able, gain a Romulan. Otherwise, take an Incident, gain 1 [Glory], you take an Incident and discard it,
    then dismiss Duty Officer. Log this card."""
    if (yield from actions.gain_card("Romulan")) is None:
        yield from actions.take_incident()
        yield from actions.gain_glory(1)
        if (yield from actions.attack()):
            yield from actions.human_takes_and_discards_incident()
        yield from actions.dismiss_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.LOG])
def cargo_officer(ctx, actions):
    """Cargo: Gain 1 [Influence]. Gain 1 [Military]. Discard the top card of the Supplement deck. Log Duty Officer."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.discard_supplement_top()
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.LOG, A.GAIN_CARD, A.PUT])
def person_officer(ctx, actions):
    """Person: Log the top card of Bot deck. Gain a Cargo. If able, return a Ship from Bot Discard pile to the top of
    the Bot deck. Otherwise, take a Ship."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Cargo")
    if (yield from actions.put_ship_from_discard_on_top()) is None:
        yield from actions.gain_card("Ship", take=True)


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_RESOURCE,
                                        A.GAIN_SPECIALTY, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a Ship and remove an [Away Team] to take top Encounter, then log this card
    and log Duty Officer. Otherwise, gain 1 [Glory], 1 [Military], and a Person. The Ship is a deployed one."""
    deployed = any(card_matches(s, "Ship") for s in ctx.me.fleet)
    if deployed and actions.away_teams_on_board() >= 1:
        yield from actions.log_deployed_ship()
        yield from actions.remove_away_team(1)
        yield from actions.take_encounter()
        yield from actions.log()
        yield from actions.log_duty_officer()
        return
    yield from actions.gain_glory(1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Person")


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.DEPLOY, A.ENGAGE])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Influence] / [Military] (whichever is higher). Gain a Ship. Deploy the gained Ship; it
    engages."""
    yield from actions.gain_highest("influence", "military")
    gained = yield from actions.gain_card("Ship")
    if gained is not None:
        yield from actions.deploy(gained)
        yield from actions.engage(gained)


@row(CREW, "with_duty_officer", 8, uses=[A.DISMISS, A.GAIN_RESOURCE, A.RESOLVE_CARD])
def location_officer(ctx, actions):
    """Location: Dismiss Duty Officer. Gain 1 [Glory]. Resolve the top card of the Bot deck."""
    yield from actions.dismiss_duty_officer()
    yield from actions.gain_glory(1)
    yield from actions.resolve_top()

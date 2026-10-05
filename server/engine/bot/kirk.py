"""The Kirk Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/kirk.md"""

from engine.bot import row
from engine.bot.georgiou import _directive_with_officer
from engine.ops import A

CREW = "kirk"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_SPECIALTY, A.RESOLVE_CARD, A.LOG])
def time_travel(ctx, actions):
    """Time Travel: Gain 2 [Research] / [Influence] / [Military] (whichever is lower). Resolve the top card of the Bot
    deck. Log this card."""
    yield from actions.gain_lowest(n=2)
    yield from actions.resolve_top()
    yield from actions.log()


@row(CREW, "traits", 3, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.ENGAGE, A.PROMOTE, A.RESOLVE_CARD, A.SEND_AWAY_TEAM])
def klingon(ctx, actions):
    """Klingon: Gain 1 [Military]. If this card is a Ship, deploy it; it engages. If this card is a Person, promote it
    to Duty Officer. If able, resolve a Directive from Bot Discard pile. Otherwise, send an [Away Team] to a neutral
    Location."""
    yield from actions.gain_specialty("military", 1)
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.engage()
    if actions.is_("Person"):
        yield from actions.promote()
    if (yield from actions.resolve_from_discard("Directive")) is None:
        yield from actions.send_away_team()


@row(CREW, "traits", 4, uses=[A.LOG, A.SEND_AWAY_TEAM, A.ATTACK, A.DISCARD, A.DISMISS, A.TAKE_INCIDENT, A.PROMOTE])
def attack(ctx, actions):
    """Attack: If able, log a deployed Ship to send 2 [Away Team] to a neutral Location and you discard a card.
    Otherwise, discard the top 2 cards of the Bot deck and you dismiss a Duty Officer and take an Incident. If this
    card is a Person, promote it to Duty Officer."""
    if (yield from actions.log_deployed_ship()) is not None:
        loc = yield from actions.send_away_team()
        if loc is not None:
            yield from actions.send_away_team(target=loc)
        if (yield from actions.attack()):
            yield from actions.human_discards()
    else:
        yield from actions.discard_top(2)
        if (yield from actions.attack()):
            yield from actions.human_dismisses_duty_officer()
            yield from actions.human_takes_incident()
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 5, uses=[A.DISCARD, A.RESOLVE_CARD, A.PROMOTE])
def engineer(ctx, actions):
    """Engineer: Discard the top 2 cards of the Bot deck. If able, resolve a Ship in Bot Discard pile. Otherwise,
    discard the top card of the Supplement deck. If this card is a Person, promote it to Duty Officer."""
    yield from actions.discard_top(2)
    if (yield from actions.resolve_from_discard("Ship")) is None:
        yield from actions.discard_supplement_top()
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 6, uses=[A.LOG, A.GAIN_SPECIALTY, A.PROMOTE, A.SEND_AWAY_TEAM])
def scientist_vulcan(ctx, actions):
    """Scientist / Vulcan: Log the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever
    is lower), twice. If this card is a Person and the Bot has no Duty Officer, promote it to Duty Officer. Otherwise,
    send an [Away Team] to a neutral Location."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest()
    yield from actions.gain_lowest()
    if actions.is_("Person") and actions.duty_officer is None:
        yield from actions.promote()
    else:
        yield from actions.send_away_team()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain a Person. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Person")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If Bot has 5+ [Influence], send an [Away Team] to a neutral Location,
    ignoring any opponent Ship. Otherwise, gain 1 [Influence]."""
    yield from actions.deploy()
    yield from actions.explore()
    if actions.track("influence") >= 5:
        yield from actions.send_away_team(ignore_ships=True)
    else:
        yield from actions.gain_specialty("influence", 1)


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.LOG])
def ally(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is
    lower). If Bot has 5+ [Influence], gain 2 [Glory] and log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_lowest()
    if actions.track("influence") >= 5:
        yield from actions.gain_glory(2)
        yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.PROMOTE, A.GAIN_CARD, A.LOG])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. If able, promote a Person from Bot Discard pile to Duty
    Officer. Otherwise, gain a Vulcan > Person and log this card."""
    yield from actions.discard_top(2)
    if (yield from actions.promote_from_discard()) is None:
        yield from actions.gain_card("Vulcan > Person")
        yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Send an [Away Team] to a neutral
    Location. Promote this card to Duty Officer."""
    yield from actions.gain_lowest()
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
    """Encounter: Log the top card of the Bot deck. Gain the card in the Market with the most [Glory]."""
    yield from actions.log_top(1)
    yield from actions.gain_most_glory()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower).
    Send an [Away Team] to a neutral Location."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest()
    yield from actions.send_away_team()


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.LOG, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Discard the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is
    lower). Log Duty Officer. Return this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_lowest()
    yield from actions.log_duty_officer()
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Gain 1 [Military]. Deploy this Ship; it engages. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Discard the top card of the Bot deck. Gain 1 [Research]. Gain Any Species excluding Human > Person /
    Ally. Log Duty Officer. Log this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_card("Any Species excluding Human > Person / Ally")
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD, A.DEPLOY, A.EXPLORE])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Gain 1 [Research]. Gain a Ship. Deploy the gained Ship; it
    explores."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    gained = yield from actions.gain_card("Ship")
    if gained is not None:
        yield from actions.deploy(gained)
        yield from actions.explore(gained)


@row(CREW, "with_duty_officer", 5, uses=[A.DISCARD, A.GAIN_CARD])
def person_officer(ctx, actions):
    """Person: Discard the top card of the Bot deck. Gain a Vulcan > Any Species excluding Human > Person / Cargo /
    Ship / Ally."""
    yield from actions.discard_top(1)
    yield from actions.gain_card("Vulcan > Any Species excluding Human > Person / Cargo / Ship / Ally")


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.DISCARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise, discard the top card of the Supplement deck."""
    if not (yield from _directive_with_officer(actions)):
        yield from actions.discard_supplement_top()


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Research]. Gain 1 [Influence]. Gain 1 [Military]. Gain 1 [Glory]. Log this card."""
    for track in ("research", "influence", "military"):
        yield from actions.gain_specialty(track, 1)
    yield from actions.gain_glory(1)
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM,
                                        A.LOG])
def location_officer(ctx, actions):
    """Location: Gain 1 [Research]. Gain 1 [Influence]. Gain 1 [Military]. Take an Incident. If able, deploy a Ship
    from Bot Discard pile; it explores. Otherwise, send an [Away Team] to neutral Location. Log Duty Officer."""
    for track in ("research", "influence", "military"):
        yield from actions.gain_specialty(track, 1)
    yield from actions.take_incident()
    ship_card = yield from actions.deploy_from_discard()
    if ship_card is not None:
        yield from actions.explore(ship_card)
    else:
        yield from actions.send_away_team()
    yield from actions.log_duty_officer()

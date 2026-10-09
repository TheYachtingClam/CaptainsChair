"""The Sela Bot's Automated Command rows. Spec: resources/scans/base_game/command/sela.md"""

from engine.bot import row
from engine.ops import A

CREW = "sela"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.TAKE_CONTROL, A.LOG])
def shady(ctx, actions):
    """Shady: Gain 1 [Military]. If able, gain a Klingon > Shady. If Bot has 8+ [Military], take control of the neutral
    Location with most Bot tokens (minimum 1) and log this card. If Bot has 7 or fewer [Military], gain 1 [Military]
    and 1 [Influence]."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Klingon > Shady")
    if actions.track("military") >= 8:
        held = [loc for loc in ctx.state.neutral if actions.bot_tokens(loc) >= 1]
        if held:
            most = max(actions.bot_tokens(loc) for loc in held)
            from engine.bot import most_valuable

            target = most_valuable(ctx.state, [loc for loc in held if actions.bot_tokens(loc) == most], ctx.me)
            yield from actions.take_control(target)
        yield from actions.log()
    else:
        yield from actions.gain_specialty("military", 1)
        yield from actions.gain_specialty("influence", 1)


@row(CREW, "traits", 3, uses=[A.SEND_AWAY_TEAM, A.DEPLOY, A.ENGAGE, A.LOG, A.GAIN_RESOURCE])
def cloak(ctx, actions):
    """Cloak: If this card is a Ship, send an [Away Team] to a neutral Location, ignoring any opponent Ship, and deploy
    this Ship; it engages. Otherwise, log this card and gain 3 [Glory]."""
    if actions.is_("Ship"):
        yield from actions.send_away_team(ignore_ships=True)
        yield from actions.deploy()
        yield from actions.engage()
    else:
        yield from actions.log()
        yield from actions.gain_glory(3)


@row(CREW, "traits", 4, uses=[A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD, A.PROMOTE])
def vulcan(ctx, actions):
    """Vulcan: Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Gain a Klingon >
    Ship. If this card is a Person, promote it to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "influence")
    yield from actions.gain_card("Klingon > Ship")
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 5, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE, A.ATTACK, A.DISMISS,
                             A.RESOLVE_CARD])
def klingon(ctx, actions):
    """Klingon: Discard the top 2 cards of the Bot deck. Gain 2 [Influence] / [Military], whichever is lower. If this
    card is a Ship, then deploy this Ship; it explores. Otherwise, either you dismiss a Ship OR resolve the top card
    of the Bot deck. The human chooses; with no Ship to dismiss, the Bot resolves the top card."""
    yield from actions.discard_top(2)
    yield from actions.gain_lowest("influence", "military", n=2)
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.explore()
        return
    choice = "resolve"
    if actions.human_deployed_ships():
        choice = yield from actions.human_choice(
            "The Bot's card: dismiss one of your Ships, or let the Bot resolve the top card of its deck?",
            [("dismiss", "Dismiss one of your Ships"), ("resolve", "The Bot resolves the top card of its deck")])
    if choice == "dismiss":
        if (yield from actions.attack()):
            yield from actions.human_dismisses_ship()
    else:
        yield from actions.resolve_top()


@row(CREW, "traits", 6, uses=[A.JUNK, A.SEND_AWAY_TEAM, A.ATTACK, A.TAKE_INCIDENT, A.DISMISS, A.LOG, A.DISCARD])
def attack(ctx, actions):
    """Attack: Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral
    Location. You take an Incident OR dismiss (one of) your Duty Officer(s). If Bot has 8+ [Military], log this card
    and either you log a controlled Location OR discard a card."""
    yield from actions.junk()
    yield from actions.send_away_team()
    human = ctx.opponent
    attacked = yield from actions.attack()
    if attacked and human is not None:
        choice = "incident"
        if human.duty:
            choice = yield from actions.human_choice(
                "The Bot attacks: take an Incident, or dismiss one of your Duty Officers?",
                [("incident", "Take an Incident"), ("officer", "Dismiss a Duty Officer")])
        if choice == "officer":
            yield from actions.human_dismisses_duty_officer()
        else:
            yield from actions.human_takes_incident()
    if actions.track("military") < 8:
        return
    yield from actions.log()
    if attacked and human is not None:
        options = ([("location", "Log one of your controlled Locations")] if human.locations else []) + \
            ([("discard", "Discard a card")] if human.hand else [])
        if not options:
            return
        choice = options[0][0] if len(options) == 1 else (
            yield from actions.human_choice("The Bot attacks: log a controlled Location, or discard a card?", options))
        if choice == "location":
            yield from actions.human_logs_location()
        else:
            yield from actions.human_discards()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Gain a Person / Ally. Return this
    card."""
    yield from actions.gain_lowest()
    yield from actions.gain_card("Person / Ally")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE])
def ship(ctx, actions):
    """Ship: Gain 1 [Military]. Deploy this Ship; it explores."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.deploy()
    yield from actions.explore()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_CARD, A.SEND_AWAY_TEAM, A.DRAW])
def ally(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. Gain a Klingon > Shady > Person. Send an [Away Team] to a neutral
    Location, ignoring any opponent Ship. You may draw a card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Klingon > Shady > Person")
    yield from actions.send_away_team(ignore_ships=True)
    yield from actions.human_may_draw()


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.GAIN_RESOURCE])
def cargo(ctx, actions):
    """Cargo: Gain an Ally > Person. If Bot has 7+ [Military], gain 1 [Research] and 1 [Influence]. Otherwise, gain 2
    [Glory] and 1 [Military]."""
    yield from actions.gain_card("Ally > Person")
    if actions.track("military") >= 7:
        yield from actions.gain_specialty("research", 1)
        yield from actions.gain_specialty("influence", 1)
    else:
        yield from actions.gain_glory(2)
        yield from actions.gain_specialty("military", 1)


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.DISMISS, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain 1 [Military]. If able, gain a Vulcan > Klingon. Otherwise, if able, dismiss a Ship to gain a Person
    / Ship. Otherwise, gain a Cargo. Promote this card to Duty Officer. The Ship is one of the Bot's deployed Ships."""
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.gain_card("Vulcan > Klingon")) is None:
        if (yield from actions.dismiss_deployed_ship()) is not None:
            yield from actions.gain_card("Person / Ship")
        else:
            yield from actions.gain_card("Cargo")
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.GAIN_SPECIALTY])
def directive(ctx, actions):
    """Directive: Discard the top 3 cards of the Bot deck. Gain 2 [Research] / [Influence] / [Military] (whichever is
    lower)."""
    yield from actions.discard_top(3)
    yield from actions.gain_lowest(n=2)


@row(CREW, "no_duty_officer", 7, uses=[A.RESOLVE_CARD, A.LOG])
def encounter(ctx, actions):
    """Encounter: Resolve the top card of the Supplement deck. Log this card."""
    yield from actions.resolve_supplement_top()
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.GAIN_CARD, A.PROMOTE])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Gain a Person and promote it to Duty Officer."""
    yield from actions.log_top(1)
    gained = yield from actions.gain_card("Person")
    if gained is not None:
        yield from actions.promote(gained)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.DRAW, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 1 [Military]. Send an [Away Team] to a neutral Location. You
    may draw a card. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.send_away_team()
    yield from actions.human_may_draw()
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it engages. Send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.ATTACK, A.DISMISS, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. Take an Incident. Gain 2 [Research] / [Influence] / [Military]
    (whichever is lower), and you take an Incident. Dismiss Duty Officer. Log this card."""
    yield from actions.discard_top(2)
    yield from actions.take_incident()
    yield from actions.gain_lowest(n=2)
    if (yield from actions.attack()):
        yield from actions.human_takes_incident()
    yield from actions.dismiss_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.RESOLVE_CARD, A.LOG])
def cargo_officer(ctx, actions):
    """Cargo: Resolve the top card of the Supplement deck. Log Duty Officer. Log this card."""
    yield from actions.resolve_supplement_top()
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 5, uses=[A.LOG, A.DISCARD, A.GAIN_CARD, A.GAIN_SPECIALTY])
def person_officer(ctx, actions):
    """Person: Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. If able, gain a Shady >
    Vulcan. Otherwise, gain 2 [Military]."""
    yield from actions.log_top(1)
    yield from actions.discard_top(3)
    if (yield from actions.gain_card("Shady > Vulcan")) is None:
        yield from actions.gain_specialty("military", 2)


@row(CREW, "with_duty_officer", 6, uses=[A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.LOG, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able, remove 2 [Away Team] to gain top Encounter, then log this card and log Duty Officer.
    Otherwise, gain a Shady > Attack > Cargo / Ship. The Encounter is gained: it goes to the Bot Discard pile."""
    if actions.away_teams_on_board() >= 2 and ctx.state.encounter:
        yield from actions.remove_away_team(2)
        yield from actions.take_encounter(gain=True)
        yield from actions.log()
        yield from actions.log_duty_officer()
    else:
        yield from actions.gain_card("Shady > Attack > Cargo / Ship")


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_RESOURCE, A.SEND_AWAY_TEAM, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 2 [Glory]. Send an [Away Team] to a neutral Location. Send an [Away Team] to a neutral Location.
    Log Duty Officer. Log this card."""
    yield from actions.gain_glory(2)
    yield from actions.send_away_team()
    yield from actions.send_away_team()
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_CARD, A.DISMISS, A.ATTACK, A.DISCARD])
def location_officer(ctx, actions):
    """Location: If able, gain a Shady. Otherwise, dismiss Duty Officer, gain a Person / Cargo / Ally, and you discard
    a card."""
    if (yield from actions.gain_card("Shady")) is None:
        yield from actions.dismiss_duty_officer()
        yield from actions.gain_card("Person / Cargo / Ally")
        if (yield from actions.attack()):
            yield from actions.human_discards()

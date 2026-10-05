"""The Archer Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/archer.md"""

from engine.bot import row
from engine.bot.georgiou import _directive_with_officer
from engine.ops import A, card

CREW = "archer"
XINDI_OR_TELLARITE = "Xindi / Tellarite > Location"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_SPECIALTY, A.CONTINUE_RESOLUTION])
def time_travel(ctx, actions):
    """Time Travel: Gain 1 [Research], 1 [Influence], 1 [Military]. Continue resolution."""
    for track in ("research", "influence", "military"):
        yield from actions.gain_specialty(track, 1)
    yield from actions.continue_resolution()


@row(CREW, "traits", 3, uses=[A.GAIN_CARD, A.TAKE_INCIDENT, A.RESOLVE_CARD, A.CONTINUE_RESOLUTION])
def nx01(ctx, actions):
    """NX-01: If this card is a Person, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Cargo. Otherwise,
    if this card is a Cargo, gain an Incident and resolve the top card of the Supplement deck. Otherwise, continue
    resolution."""
    if actions.is_("Person"):
        yield from actions.gain_card("[Research Focus] / [Influence Focus] / [Military Focus] > Cargo")
    elif actions.is_("Cargo"):
        yield from actions.gain_incident()
        yield from actions.resolve_supplement_top()
    else:
        yield from actions.continue_resolution()


@row(CREW, "traits", 4, uses=[A.DISCARD, A.GAIN_CARD, A.ADD_AWAY_TEAM, A.SEND_AWAY_TEAM, A.CONTINUE_RESOLUTION])
def coalition(ctx, actions):
    """Vulcan / Andorian / Tellarite: Discard the top card of the Supplement deck. If able, gain Andorian / Vulcan /
    Tellarite. Otherwise add an [Away Team] token from the supply to the Bot Captain card (max 6 [Away Team] total),
    and send it to a neutral Location. Continue resolution."""
    yield from actions.discard_supplement_top()
    if (yield from actions.gain_card("Andorian / Vulcan / Tellarite")) is None:
        if (yield from actions.add_away_team(6)):
            yield from actions.send_away_team()
    yield from actions.continue_resolution()


@row(CREW, "traits", 5, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.TAKE_ENCOUNTER, A.LOG, A.ATTACK, A.EXHAUST,
                             A.TAKE_INCIDENT])
def xindi(ctx, actions):
    """Xindi: Gain 1 [Influence]. If Bot has 7 or fewer [Influence], gain (if able) Xindi > Time Travel > Andorian /
    Tellarite / Vulcan, including from the Junk. Otherwise, gain top Encounter and log this card, and you exhaust a
    controlled Location, and if you have a Xindi in play, both the bot and you take an Incident."""
    yield from actions.gain_specialty("influence", 1)
    if actions.track("influence") <= 7:
        yield from actions.gain_card("Xindi > Time Travel > Andorian / Tellarite / Vulcan", including_junk=True)
        return
    yield from actions.take_encounter(gain=True)
    yield from actions.log()
    human_xindi = actions.human_has("Xindi")
    attacked = yield from actions.attack()
    if attacked:
        yield from actions.human_exhausts_location()
    if human_xindi:
        yield from actions.take_incident()
        if attacked:
            yield from actions.human_takes_incident()


@row(CREW, "traits", 6, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.REMOVE_AWAY_TEAM, A.LOG, A.GAIN_RESOURCE])
def attack(ctx, actions):
    """Attack: Send an [Away Team] to a neutral Location. If able, you remove all your [Away Team] from a neutral
    Location where the bot has a Ship then log this card. Otherwise, log a non-NX-01 card from the bot Discard pile
    and gain all resources from a card in the Market."""
    yield from actions.send_away_team()
    bot, human = ctx.me, actions.human
    with_ship = {s.at for s in bot.fleet if s.at}
    able = human is not None and any(loc.uid in with_ship and loc.away.get(human.seat) for loc in ctx.state.neutral)
    if able:
        if (yield from actions.attack(removes_away_teams=True)):
            yield from actions.human_removes_all_away_teams(lambda loc: loc.uid in with_ship)
        yield from actions.log()
    else:
        yield from actions.log_from_discard(lambda i: "NX-01" not in card(i).traits)
        yield from actions.gain_resources_from_market()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 1 [Research]. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DISCARD, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def ship(ctx, actions):
    """Ship: Discard the top 2 cards of the Bot deck. Deploy this Ship; it explores. If able, send an [Away Team] to a
    neutral Xindi / Tellarite; otherwise gain 1 [Glory]."""
    yield from actions.discard_top(2)
    yield from actions.deploy()
    yield from actions.explore()
    if (yield from actions.send_away_team("Xindi / Tellarite")) is None:
        yield from actions.gain_glory(1)


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally(ctx, actions):
    """Ally: Gain Andorian / Vulcan > Alien / Ambassador > Person. Log this card."""
    yield from actions.gain_card("Andorian / Vulcan > Alien / Ambassador > Person")
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.RESOLVE_CARD, A.GAIN_CARD, A.TAKE_INCIDENT])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Resolve an NX-01 from Bot Discard if able; otherwise gain a
    Ship and gain an Incident."""
    yield from actions.discard_top(2)
    if (yield from actions.resolve_from_discard("NX-01")) is None:
        yield from actions.gain_card("Ship")
        yield from actions.gain_incident()


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_CARD, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain Xindi / Andorian > Cargo. Promote this card to Duty Officer."""
    yield from actions.gain_card("Xindi / Andorian > Cargo")
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_SPECIALTY, A.PROMOTE])
def directive(ctx, actions):
    """Directive: Discard the top card of the Bot deck. Gain NX-01 if able; otherwise twice: gain 1 [Research] /
    [Influence] / [Military] (whichever is lower). Promote a Person with NX-01 from the Bot Discard pile to Duty
    Officer, if able."""
    yield from actions.discard_top(1)
    if (yield from actions.gain_card("NX-01")) is None:
        yield from actions.gain_lowest()
        yield from actions.gain_lowest()
    yield from actions.promote_from_discard("NX-01")


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the top card of the Supplement deck. Log this card."""
    yield from actions.discard_supplement_top()
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_RESOURCE])
def location(ctx, actions):
    """Location: Discard the top 2 cards of the Bot deck. Gain a Person. Gain 3 [Glory] from the supply."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Person")
    yield from actions.gain_glory(3, supply=True)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.LOG, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 1 [Research]. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY, A.DISMISS])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it engages. Send an [Away Team] to a neutral Xindi / Tellarite > Location. Gain 1
    [Military]. Dismiss Duty Officer."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team(XINDI_OR_TELLARITE)
    yield from actions.gain_specialty("military", 1)
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain Xindi > Tellarite > Ship. Log this card."""
    yield from actions.gain_card("Xindi > Tellarite > Ship")
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.SEND_AWAY_TEAM, A.DISMISS])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Send an [Away Team] to a neutral Xindi / Tellarite > Location. Dismiss
    Duty Officer. Log this card."""
    yield from actions.log_top(1)
    yield from actions.send_away_team(XINDI_OR_TELLARITE)
    yield from actions.dismiss_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 5, uses=[A.RESOLVE_CARD, A.GAIN_RESOURCE, A.DISMISS])
def person_officer(ctx, actions):
    """Person: Resolve a Directive from the Bot Discard pile if able; otherwise gain 1 [Glory]. Dismiss Duty
    Officer."""
    if (yield from actions.resolve_from_discard("Directive")) is None:
        yield from actions.gain_glory(1)
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_CARD, A.DISMISS,
                                        A.SEND_AWAY_TEAM])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise, gain NX-01 > Ally / Ship. If a Ship was gained, dismiss Duty Officer; otherwise send
    [Away Team] to a neutral Location."""
    if (yield from _directive_with_officer(actions)):
        return
    gained = yield from actions.gain_card("NX-01 > Ally / Ship")
    if gained is not None and card(gained).suit == "Ship":
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 7, uses=[A.RESOLVE_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Resolve the top card of the Supplement deck. Log this card."""
    yield from actions.resolve_supplement_top()
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.DISCARD, A.LOG, A.GAIN_RESOURCE])
def location_officer(ctx, actions):
    """Location: Discard the top card of the Supplement deck. Log the top 2 cards of the Bot deck. Gain 1 [Glory]
    (from the Stardate card), and another 2 [Glory] from the supply. Log Duty Officer."""
    yield from actions.discard_supplement_top()
    yield from actions.log_top(2)
    yield from actions.gain_glory(1)
    yield from actions.gain_glory(2, supply=True)
    yield from actions.log_duty_officer()

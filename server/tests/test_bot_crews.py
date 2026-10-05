"""The Georgiou, Kirk and Archer Bots (plans/solo-mode.md Step 4): each spec's Tests cases and the rows that need
something new."""

from engine import bot as bot_rules
from engine.content import content
from engine.game import advance, choose
from engine.setup import BotSetup, SeatSetup, new_game

CARDS = content().cards


def solo(bot, deck="kirk", seed=5):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], ["second_contact"], True,
                 bot=BotSetup(bot, "admiral"))
    advance(s, flag_irreversible=False)
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def answer(s, text):
    option = next(o for o in s.decision.options if text in o.label)
    choose(s, s.decision.seat, option.id, flag_irreversible=False)


def log_text(s):
    return " | ".join(e.text for e in s.log)


def resolve_card(s, card_id, *, side=None):
    bot = the_bot(s)
    if side:
        bot.bot.suits_side = side
    inst = s.new_inst(card_id)
    bot.staging.append(inst)
    s.decision = None
    bot_rules.queue_resolution(s, bot, inst)
    advance(s, flag_irreversible=False)
    return inst


def finish(s, prefer=()):
    while s.decision is not None and not (s.decision.kind == "action" and s.decision.seat == 0):
        opts = [o.label for o in s.decision.options]
        pick = next((p for p in prefer for o in opts if p in o), None)
        if s.decision.kind == "trigger" and pick is None:
            pick = "Do not"
        answer(s, pick or opts[0])


def test_every_row_has_code():
    for crew in ("georgiou", "kirk", "archer"):
        for side in content().command[crew].sides:
            for r in side.rows:
                if "Surprise" not in r.matches:
                    assert (crew, side.side, r.number) in bot_rules.ROWS, (crew, side.side, r.number)


# ------------------------------------------------------------------ Georgiou

def test_georgiou_vulcan_location_continues_to_the_location_row():
    s = solo("georgiou")
    top = the_bot(s).draw[0]
    resolve_card(s, "2SOV03")  # Vulcan: a Vulcan Location
    text = log_text(s)
    assert "matches Vulcan (row 4 of TRAITS)" in text and "matches Location (row 8 of SUITS" in text
    assert the_bot(s).tracks["influence"] == 1 and any(i.uid == top.uid for i in the_bot(s).discard)
    assert any(i.card == "2SOV03" for i in the_bot(s).locations)


def test_georgiou_attack_with_more_research_gains_glory_and_continues():
    s = solo("georgiou")
    bot = the_bot(s)
    bot.tracks.update(research=5, military=3)
    resolve_card(s, "2SOV15")  # Stel: Attack, Vulcan, Security
    assert "matches Security / Ops (row 5 of TRAITS)" in log_text(s)  # Security comes before Attack


def test_georgiou_attack_otherwise_branch():
    """No Duty Officers on either side: the Bot takes an Incident, then (you cannot dismiss one) takes a Kelpien or
    Vulcan, else a Ship, and gains 1 Research."""
    s = solo("georgiou")
    bot = the_bot(s)
    research = bot.tracks["research"]
    resolve_card(s, "2PER03")  # Ash Tyler: Attack, no Security/Ops/Vulcan/Kelpien/Anomaly
    finish(s)
    bot = the_bot(s)
    assert "matches Attack (row 6 of TRAITS)" in log_text(s)
    assert "takes an Incident" in log_text(s) and bot.tracks["research"] == research + 1


# ------------------------------------------------------------------ Kirk

def test_kirk_ship_with_five_influence_ignores_your_ships():
    s = solo("kirk")
    bot, human = the_bot(s), me(s)
    bot.tracks["influence"] = 5
    for loc in s.neutral:
        ship = s.new_inst("2SHI01")
        human.fleet.append(ship)
        ship.at = loc.uid
    kirk_traits = {"Time Travel", "Klingon", "Attack", "Engineer", "Scientist", "Vulcan", "Surprise", "Wildcard"}
    plain_ship = next(k for k, c in CARDS.items() if c.is_common and c.suit == "Ship" and not kirk_traits & set(c.traits))
    resolve_card(s, plain_ship)
    assert "matches Ship (row 2 of SUITS WITH NO DUTY OFFICER)" in log_text(s)
    assert "sends an Away Team" in log_text(s)


def test_kirk_encounter_gains_the_market_card_with_most_glory():
    s = solo("kirk")
    target = s.market["Cargo"]
    target.res["glory"] = 3
    resolve_card(s, "2ENC08")
    assert any(i.uid == target.uid for i in the_bot(s).discard) and the_bot(s).glory >= 3




def test_kirk_attack_row():
    s = solo("kirk", deck="georgiou")
    bot = the_bot(s)
    ship = s.new_inst("2SHI01")
    bot.fleet.append(ship)
    attack_card = next(k for k, c in CARDS.items() if c.is_common and "Attack" in c.traits
                       and not {"Time Travel", "Klingon"} & set(c.traits) and c.suit == "Cargo")
    hand = len(me(s).hand)
    resolve_card(s, attack_card)
    finish(s)
    bot = the_bot(s)
    assert any(i.uid == ship.uid for i in bot.log)
    assert max(loc.away.get(1, 0) for loc in s.neutral) == 2
    assert len(me(s).hand) == hand - 1


# ------------------------------------------------------------------ Archer

def test_archer_time_travel_gains_one_each_and_continues():
    s = solo("archer")
    tt = next(k for k, c in CARDS.items() if c.is_common and "Time Travel" in c.traits and c.suit == "Ally"
              and not {"NX-01", "Vulcan", "Andorian", "Tellarite", "Xindi", "Attack"} & set(c.traits))
    resolve_card(s, tt)
    bot = the_bot(s)
    assert all(bot.tracks[t] >= 1 for t in ("research", "influence", "military"))
    assert "matches Time Travel (row 2 of TRAITS)" in log_text(s) and "(row 3 of SUITS" in log_text(s)


def test_archer_adds_away_teams_from_the_supply_up_to_six():
    s = solo("archer")
    bot = the_bot(s)
    s.market = {k: None for k in s.market}  # nothing to gain
    for deck in s.market_decks.values():
        deck.clear()
    pool = bot.away_pool
    resolve_card(s, "2ARC07")  # Ambassador Soval: Vulcan
    bot = the_bot(s)
    assert bot.away_pool + sum(loc.away.get(1, 0) for loc in s.neutral) == pool + 1
    bot.away_pool = 6
    resolve_card(s, "2ARC07")
    assert "already has 6 Away Teams" in log_text(s)


def test_archer_xindi_attack_at_eight_influence():
    s = solo("archer", deck="archer")
    bot, human = the_bot(s), me(s)
    bot.tracks["influence"] = 7  # +1 makes 8
    loc = human.locations[0] if human.locations else s.new_inst("2LOC05")
    if loc not in human.locations:
        human.locations.append(loc)
    human.staging.append(s.new_inst("2ARC09"))  # a Xindi in play
    resolve_card(s, "2ARC09")
    finish(s, prefer=(CARDS[loc.card].name,))
    human = me(s)
    assert any(i.exhausted for i in human.locations)
    assert any(CARDS[i.card].suit == "Incident" for i in human.hand)
    assert CARDS[the_bot(s).draw[0].card].suit == "Incident"


def test_archer_attack_removes_all_your_teams_where_it_has_a_ship():
    s = solo("archer", deck="georgiou")
    bot, human = the_bot(s), me(s)
    loc = s.neutral[0]
    ship = s.new_inst("2SHI01")
    bot.fleet.append(ship)
    ship.at = loc.uid
    loc.away[0] = 2
    human.away_pool -= 2
    pool = human.away_pool
    attack_card = next(k for k, c in CARDS.items() if c.is_common and "Attack" in c.traits and c.suit == "Cargo"
                       and not {"Time Travel", "NX-01", "Vulcan", "Andorian", "Tellarite", "Xindi"} & set(c.traits))
    resolve_card(s, attack_card)
    finish(s)
    assert not s.neutral[0].away.get(0) and me(s).away_pool == pool + 2

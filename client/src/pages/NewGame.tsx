import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  BotChoice, Box, DEFAULT_BOX, DIFFICULTIES, Deck, GameMode, MODE_LABELS, SeatChoice, api, byComplexity, saveSeatToken, setsFor,
} from "../api";
import { SeatForm } from "../components/SeatForm";

export function NewGame() {
  const navigate = useNavigate();
  const expansions = useQuery({ queryKey: ["expansions"], queryFn: api.expansions });
  const [mode, setMode] = useState<GameMode>("two_player");
  const boxes = useQuery({ queryKey: ["boxes"], queryFn: api.boxes });
  const [box, setBox] = useState<Box>(DEFAULT_BOX);
  const [chosen, setChosen] = useState<string[]>([]);
  const [promos, setPromos] = useState(false);
  const [seat, setSeat] = useState<SeatChoice>({ display_name: "", deck_id: "", board_side: "basic" });
  const [bot, setBot] = useState<BotChoice>({ deck_id: "", difficulty: "ensign", ticking_clock: false });
  const decks = useQuery({ queryKey: ["decks"], queryFn: api.decks });
  const sets = setsFor(boxes.data, box, chosen);
  const bots = (decks.data ?? []).filter((d: Deck) => d.bot && sets.includes(d.set)).sort(byComplexity);
  const solo = mode === "solo";

  const create = useMutation({
    mutationFn: () => api.createGame({ ...seat, mode, box, expansions: chosen, promos, ...(solo ? { bot } : {}) }),
    onSuccess: (grant) => {
      saveSeatToken(grant.game.id, grant.seat_token);
      navigate(`/games/${grant.game.id}`);
    },
  });

  // A Crew deck or Bot of another box cannot stay chosen (REQ-CORE-11).
  function chooseBox(next: Box) {
    setBox(next);
    setSeat((s) => ({ ...s, deck_id: "" }));
    setBot((b) => ({ ...b, deck_id: "", conspiracy: false }));
  }

  function toggle(id: string) {
    setChosen((c) => (c.includes(id) ? c.filter((x) => x !== id) : [...c, id]));
    setSeat((s) => ({ ...s, deck_id: "" }));
    setBot((b) => ({ ...b, deck_id: "" }));
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    create.mutate();
  }

  return (
    <main className="page">
      <h1>New game</h1>
      <form className="card stack" onSubmit={submit}>
        <fieldset>
          <legend>Mode</legend>
          {(Object.keys(MODE_LABELS) as GameMode[]).map((m) => (
            <label key={m} className="inline">
              <input type="radio" name="mode" checked={mode === m} onChange={() => setMode(m)} />
              {MODE_LABELS[m]}
            </label>
          ))}
          {solo && (
            <p className="muted">
              Solo mode has extra rules for the Bot. New to Captain's Chair? Try Cadet Training first.
            </p>
          )}
        </fieldset>
        <fieldset>
          <legend>Box</legend>
          {(Object.entries(boxes.data ?? {}) as [Box, { name: string }][]).map(([id, b]) => (
            <label key={id} className="inline">
              <input type="radio" name="box" checked={box === id} onChange={() => chooseBox(id)} />
              {b.name}
            </label>
          ))}
          <p className="muted">
            The box sets the Market, Locations and which Crew decks you can choose.
          </p>
        </fieldset>
        <fieldset>
          <legend>Expansions</legend>
          {Object.entries(expansions.data ?? {}).map(([id, name]) => (
            <label key={id} className="inline">
              <input type="checkbox" checked={chosen.includes(id)} onChange={() => toggle(id)} />
              {name}
            </label>
          ))}
          <label className="inline">
            <input type="checkbox" checked={promos} onChange={(e) => setPromos(e.target.checked)} />
            Promo cards
          </label>
        </fieldset>
        <SeatForm value={seat} onChange={setSeat} sets={sets} />
        {solo && (
          <fieldset className="stack">
            <legend>The Bot</legend>
            <label>
              Bot Crew
              <select value={bot.deck_id} onChange={(e) => setBot({ ...bot, deck_id: e.target.value })}>
                <option value="">{bots.length ? "Choose the Bot's captain…" : "No Bot is available for this box yet"}</option>
                {bots.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.captain} ({d.faction})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Difficulty
              <select value={bot.difficulty} onChange={(e) => setBot({ ...bot, difficulty: e.target.value as BotChoice["difficulty"] })}>
                {DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>
                    {d[0].toUpperCase() + d.slice(1)}
                  </option>
                ))}
              </select>
            </label>
            <label className="inline">
              <input type="checkbox" checked={bot.ticking_clock} onChange={(e) => setBot({ ...bot, ticking_clock: e.target.checked })} />
              Ticking Clock challenge (for experts: <em>Time Is Running Out</em> joins the Bot's Supplement deck)
            </label>
            {sets.includes("base_game") && (
              <label className="inline">
                <input type="checkbox" checked={!!bot.conspiracy} onChange={(e) => setBot({ ...bot, conspiracy: e.target.checked })} />
                Ticking Clock challenge, Core Box (<em>Conspiracy</em> joins the Bot's Supplement deck; tick both for a bigger challenge)
              </label>
            )}
          </fieldset>
        )}
        {create.error && <p className="error" role="alert">{create.error.message}</p>}
        <button type="submit" disabled={create.isPending || !seat.display_name.trim() || !seat.deck_id || (solo && !bot.deck_id)}>
          Create game
        </button>
      </form>
    </main>
  );
}

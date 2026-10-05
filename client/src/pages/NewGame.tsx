import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BotChoice, DIFFICULTIES, Deck, GameMode, MODE_LABELS, SeatChoice, api, saveSeatToken } from "../api";
import { SeatForm } from "../components/SeatForm";

export function NewGame() {
  const navigate = useNavigate();
  const expansions = useQuery({ queryKey: ["expansions"], queryFn: api.expansions });
  const [mode, setMode] = useState<GameMode>("two_player");
  const [chosen, setChosen] = useState<string[]>([]);
  const [promos, setPromos] = useState(false);
  const [seat, setSeat] = useState<SeatChoice>({ display_name: "", deck_id: "", board_side: "basic" });
  const [bot, setBot] = useState<BotChoice>({ deck_id: "", difficulty: "ensign", ticking_clock: false });
  const decks = useQuery({ queryKey: ["decks"], queryFn: api.decks });
  const sets = ["to_boldly_go", ...chosen];
  const bots = (decks.data ?? []).filter((d: Deck) => d.bot && sets.includes(d.set)).sort((a, b) => a.complexity - b.complexity);
  const solo = mode === "solo";

  const create = useMutation({
    mutationFn: () => api.createGame({ ...seat, mode, expansions: chosen, promos, ...(solo ? { bot } : {}) }),
    onSuccess: (grant) => {
      saveSeatToken(grant.game.id, grant.seat_token);
      navigate(`/games/${grant.game.id}`);
    },
  });

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
                <option value="">Choose the Bot's captain…</option>
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

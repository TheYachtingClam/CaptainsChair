import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { GameMode, MODE_LABELS, SeatChoice, api, saveSeatToken } from "../api";
import { SeatForm } from "../components/SeatForm";

export function NewGame() {
  const navigate = useNavigate();
  const expansions = useQuery({ queryKey: ["expansions"], queryFn: api.expansions });
  const [mode, setMode] = useState<GameMode>("two_player");
  const [chosen, setChosen] = useState<string[]>([]);
  const [promos, setPromos] = useState(false);
  const [seat, setSeat] = useState<SeatChoice>({ display_name: "", deck_id: "", board_side: "basic" });

  const create = useMutation({
    mutationFn: () => api.createGame({ ...seat, mode, expansions: chosen, promos }),
    onSuccess: (grant) => {
      saveSeatToken(grant.game.id, grant.seat_token);
      navigate(`/games/${grant.game.id}`);
    },
  });

  function toggle(id: string) {
    setChosen((c) => (c.includes(id) ? c.filter((x) => x !== id) : [...c, id]));
    setSeat((s) => ({ ...s, deck_id: "" }));
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
        <SeatForm value={seat} onChange={setSeat} sets={["to_boldly_go", ...chosen]} />
        {create.error && <p className="error" role="alert">{create.error.message}</p>}
        <button type="submit" disabled={create.isPending || !seat.display_name.trim() || !seat.deck_id}>
          Create game
        </button>
      </form>
    </main>
  );
}

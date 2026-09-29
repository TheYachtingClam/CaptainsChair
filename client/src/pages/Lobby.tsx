import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Game, MODE_LABELS, SeatChoice, api, loadSeatToken, saveSeatToken } from "../api";
import { SeatForm } from "../components/SeatForm";

export function Lobby() {
  const games = useQuery({ queryKey: ["games"], queryFn: api.games, refetchInterval: 5000 });
  const mine = (games.data ?? []).filter((g) => loadSeatToken(g.id));
  const open = (games.data ?? []).filter((g) => !loadSeatToken(g.id) && g.open_seats > 0);

  return (
    <main className="page">
      <div className="row between">
        <h1>Lobby</h1>
        <Link className="button" to="/new">New game</Link>
      </div>
      {games.isError && <p className="error">{games.error.message}</p>}

      <section>
        <h2>Your games</h2>
        {mine.length === 0 ? <p className="muted">You have no games yet.</p> : (
          <ul className="list">
            {mine.map((g) => (
              <li key={g.id} className="card row between">
                <GameLine game={g} />
                <Link className="button" to={`/games/${g.id}`}>Open</Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>Open games</h2>
        {open.length === 0 ? <p className="muted">No one is waiting for an opponent.</p> : (
          <ul className="list">
            {open.map((g) => <OpenGame key={g.id} game={g} />)}
          </ul>
        )}
      </section>
    </main>
  );
}

function GameLine({ game }: { game: Game }) {
  const players = game.seats.map((s) => `${s.display_name} (${s.deck_id})`).join(" vs ");
  return (
    <div>
      <strong>{MODE_LABELS[game.mode]}</strong> · {players}
      {game.open_seats > 0 && <span className="muted"> · waiting for opponent</span>}
    </div>
  );
}

function OpenGame({ game }: { game: Game }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [joining, setJoining] = useState(false);
  const [seat, setSeat] = useState<SeatChoice>({ display_name: "", deck_id: "", board_side: "basic" });

  const join = useMutation({
    mutationFn: () => api.joinGame(game.id, seat),
    onSuccess: (grant) => {
      saveSeatToken(game.id, grant.seat_token);
      queryClient.invalidateQueries({ queryKey: ["games"] });
      navigate(`/games/${game.id}`);
    },
  });

  return (
    <li className="card stack">
      <div className="row between">
        <GameLine game={game} />
        {!joining && <button onClick={() => setJoining(true)}>Join</button>}
      </div>
      {joining && (
        <>
          <SeatForm
            value={seat}
            onChange={setSeat}
            sets={["to_boldly_go", ...game.expansions]}
            takenDecks={game.seats.map((s) => s.deck_id)}
          />
          {join.error && <p className="error" role="alert">{join.error.message}</p>}
          <div className="row">
            <button disabled={join.isPending || !seat.display_name.trim() || !seat.deck_id} onClick={() => join.mutate()}>
              Take the seat
            </button>
            <button className="link" onClick={() => setJoining(false)}>Cancel</button>
          </div>
        </>
      )}
    </li>
  );
}

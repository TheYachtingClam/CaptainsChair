import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Game, MODE_LABELS, SeatChoice, api, campaignApi, forgetSeatToken, knownCampaigns, loadSeatToken, saveSeatToken } from "../api";
import { SeatForm } from "../components/SeatForm";

export function Lobby() {
  const games = useQuery({ queryKey: ["games"], queryFn: api.games, refetchInterval: 5000 });
  const mine = (games.data ?? []).filter((g) => loadSeatToken(g.id));
  const open = (games.data ?? []).filter((g) => !loadSeatToken(g.id) && g.open_seats > 0);

  return (
    <main className="page">
      <div className="row between">
        <h1>Lobby</h1>
        <div className="row">
          <Link className="button secondary" to="/campaigns/new">New Five-Year Mission</Link>
          <Link className="button" to="/new">New game</Link>
        </div>
      </div>
      {games.isError && <p className="error">{games.error.message}</p>}

      <section>
        <h2>Your games</h2>
        {mine.length === 0 ? <p className="muted">You have no games yet.</p> : (
          <ul className="list">
            {mine.map((g) => <MyGame key={g.id} game={g} />)}
          </ul>
        )}
      </section>

      <MyCampaigns />

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

function MyGame({ game }: { game: Game }) {
  const queryClient = useQueryClient();
  const [confirming, setConfirming] = useState(false);
  const remove = useMutation({
    mutationFn: () => api.deleteGame(game.id),
    onSuccess: () => {
      forgetSeatToken(game.id);
      queryClient.invalidateQueries({ queryKey: ["games"] });
    },
  });
  const others = game.seats.length > 1;

  return (
    <li className="card stack">
      <div className="row between">
        <GameLine game={game} />
        <div className="row">
          <Link className="button" to={`/games/${game.id}`}>Open</Link>
          {!confirming && <button className="secondary" onClick={() => setConfirming(true)}>Delete</button>}
        </div>
      </div>
      {confirming && (
        <div className="row between confirm-delete" role="alert">
          <span>
            Delete this game{others ? " for both players" : ""}? This cannot be undone.
          </span>
          <div className="row">
            <button className="danger" disabled={remove.isPending} onClick={() => remove.mutate()}>Delete game</button>
            <button className="link" onClick={() => setConfirming(false)}>Cancel</button>
          </div>
        </div>
      )}
      {remove.error && <p className="error" role="alert">{remove.error.message}</p>}
    </li>
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


/** Five-Year Missions this browser has the link of (REQ-CAMP-54). */
function MyCampaigns() {
  const ids = knownCampaigns();
  const campaigns = useQuery({
    queryKey: ["campaigns", ids.join(",")],
    queryFn: () => Promise.all(ids.map((id) => campaignApi.get(id).catch(() => null))),
    enabled: ids.length > 0,
  });
  if (ids.length === 0) return null;
  return (
    <section>
      <h2>Your Five-Year Missions</h2>
      <ul className="list">
        {(campaigns.data ?? []).filter((c): c is NonNullable<typeof c> => !!c).map((c) => (
          <li key={c.id}>
            <Link to={`/campaigns/${c.id}`}>{c.display_name}</Link> · {c.captain}&apos;s crew · {c.rank} ·{" "}
            {c.assignments.length} of 10 assignments{c.phase === "finished" ? " · finished" : ""}
          </li>
        ))}
      </ul>
    </section>
  );
}

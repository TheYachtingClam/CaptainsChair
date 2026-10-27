import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Game, MODE_LABELS, SeatChoice, api, campaignApi, setsFor } from "../api";
import { SeatForm } from "../components/SeatForm";

export function Lobby() {
  const games = useQuery({ queryKey: ["games"], queryFn: api.games, refetchInterval: 5000 });
  // Your games: the account's, on any device (REQ-USER-40).
  const myGames = useQuery({ queryKey: ["my-games"], queryFn: api.myGames, refetchInterval: 5000 });
  const mine = myGames.data ?? [];
  const ownIds = new Set(mine.map((g) => g.id));
  const open = (games.data ?? []).filter((g) => !ownIds.has(g.id) && g.open_seats > 0);

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

      <Tutorials />

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

      <p className="muted lobby-footer"><Link to="/admin">Admin</Link></p>
    </main>
  );
}

function GameLine({ game }: { game: Game }) {
  const players = game.seats.map((s) => `${s.display_name} (${s.deck_id})`).join(" vs ");
  return (
    <div>
      <strong>{game.tutorial ? "Tutorial" : MODE_LABELS[game.mode]}</strong> · {players}
      {game.box === "core" && <span className="muted"> · Core Box</span>}
      {game.box === "both" && <span className="muted"> · both boxes</span>}
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
      queryClient.invalidateQueries({ queryKey: ["games"] });
      queryClient.invalidateQueries({ queryKey: ["my-games"] });
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
  const boxes = useQuery({ queryKey: ["boxes"], queryFn: api.boxes });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [joining, setJoining] = useState(false);
  const [seat, setSeat] = useState<SeatChoice>({ deck_id: "", board_side: "basic" });

  const join = useMutation({
    mutationFn: () => api.joinGame(game.id, seat),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] });
      queryClient.invalidateQueries({ queryKey: ["my-games"] });
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
            sets={setsFor(boxes.data, game.box, game.expansions)}
            takenDecks={game.seats.map((s) => s.deck_id)}
          />
          {join.error && <p className="error" role="alert">{join.error.message}</p>}
          <div className="row">
            <button disabled={join.isPending || !seat.deck_id} onClick={() => join.mutate()}>
              Take the seat
            </button>
            <button className="link" onClick={() => setJoining(false)}>Cancel</button>
          </div>
        </>
      )}
    </li>
  );
}


/** The account's Five-Year Missions (REQ-CAMP-54). */
function MyCampaigns() {
  const owned = useQuery({ queryKey: ["my-campaigns"], queryFn: api.myCampaigns });
  const ids = (owned.data ?? []).map((c) => c.id);
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


/** Learn to play (requirements/24-tutorials.md §1.6): each tutorial, continued or started again, and marked finished.
 *  Shown first and highlighted until the first tutorial is finished. */
function Tutorials() {
  const tutorials = useQuery({ queryKey: ["tutorials"], queryFn: api.tutorials });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const start = useMutation({
    mutationFn: (id: string) => api.startTutorial(id),
    onSuccess: (grant) => {
      queryClient.invalidateQueries({ queryKey: ["my-games"] });
      queryClient.invalidateQueries({ queryKey: ["tutorials"] });
      navigate(`/games/${grant.game.id}`);
    },
  });
  const list = tutorials.data ?? [];
  if (!list.length) return null;
  const learning = !list[0].finished;
  return (
    <section className={`card stack learn-to-play ${learning ? "featured" : ""}`}>
      <h2>{learning ? "Learn to play" : "Tutorials"}</h2>
      {learning && <p className="muted">New to Captain&apos;s Chair? Play a practice game with a coach beside you.</p>}
      {list.map((t) => (
        <div key={t.id} className="row between tutorial-row">
          <div>
            <strong>{t.title}</strong>{t.finished && <span className="pill">Finished</span>}
            <p className="muted">{t.summary}</p>
          </div>
          <div className="row">
            {t.game_id && <Link className="button" to={`/games/${t.game_id}`}>Continue</Link>}
            <button className={t.game_id || t.finished ? "secondary" : undefined} disabled={start.isPending}
              onClick={() => start.mutate(t.id)}>{t.game_id || t.finished ? "Start again" : "Start"}</button>
          </div>
        </div>
      ))}
      {start.error && <p className="error" role="alert">{start.error.message}</p>}
    </section>
  );
}

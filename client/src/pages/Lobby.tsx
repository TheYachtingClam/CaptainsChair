import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Game, MODE_LABELS, TutorialInfo, api, campaignApi } from "../api";
import { useAccount } from "../account";
import { JoinForm } from "../components/JoinForm";

export function Lobby() {
  const games = useQuery({ queryKey: ["games"], queryFn: api.games, refetchInterval: 5000 });
  // Your games: the account's, on any device (REQ-USER-40).
  const myGames = useQuery({ queryKey: ["my-games"], queryFn: api.myGames, refetchInterval: 5000 });
  const mine = myGames.data ?? [];
  const ownIds = new Set(mine.map((g) => g.id));
  const account = useAccount();
  const waiting = (games.data ?? []).filter((g) => !ownIds.has(g.id) && g.open_seats > 0);
  // A challenge is for one player only (REQ-USER-51, -52); the server lists it to no one else.
  const challenges = waiting.filter((g) => g.challenge && g.challenge.user_id === account?.id);
  const open = waiting.filter((g) => !g.challenge);

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

      {challenges.length > 0 && (
        <section>
          <h2>Challenges for you</h2>
          <ul className="list">
            {challenges.map((g) => (
              <li key={g.id} className="card stack">
                <GameLine game={g} />
                <JoinForm game={g} />
              </li>
            ))}
          </ul>
        </section>
      )}

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
  const account = useAccount();
  const players = game.seats.map((s) => `${s.display_name} (${s.deck_id})`).join(" vs ");
  const forYou = !!game.challenge && game.challenge.user_id === account?.id;
  return (
    <div>
      <strong>{game.tutorial ? "Tutorial" : MODE_LABELS[game.mode]}</strong> · {players}
      {game.box === "core" && <span className="muted"> · Core Box</span>}
      {game.box === "both" && <span className="muted"> · both boxes</span>}
      {game.open_seats > 0 && (
        <span className="muted">
          {forYou ? " · challenges you"
            : game.challenge ? ` · waiting for ${game.challenge.display_name} to accept` : " · waiting for opponent"}
        </span>
      )}
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
  const [joining, setJoining] = useState(false);
  return (
    <li className="card stack">
      <div className="row between">
        <GameLine game={game} />
        {!joining && <button onClick={() => setJoining(true)}>Join</button>}
      </div>
      {joining && <JoinForm game={game} onCancel={() => setJoining(false)} />}
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


/** Learn to play (requirements/24-tutorials.md §1.6): one tutorial at a time, chosen from a dropdown, with its
 *  description and its own Start / Continue buttons. Highlighted until the first tutorial is finished. The dropdown
 *  starts on a tutorial in progress, else the first one not finished. */
function Tutorials() {
  const tutorials = useQuery({ queryKey: ["tutorials"], queryFn: api.tutorials });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [chosen, setChosen] = useState<string | null>(null);
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
  const t = list.find((x) => x.id === chosen) ?? list.find((x) => x.game_id) ?? list.find((x) => !x.finished) ?? list[0];
  const label = (x: TutorialInfo) => `${x.title}${x.game_id ? " (in progress)" : x.finished ? " ✓" : ""}`;
  return (
    <section className={`card stack learn-to-play ${learning ? "featured" : ""}`}>
      <h2>{learning ? "Learn to play" : "Tutorials"}</h2>
      {learning && <p className="muted">New to Captain&apos;s Chair? Play a practice game with a coach beside you.</p>}
      <select value={t.id} onChange={(e) => setChosen(e.target.value)} aria-label="Tutorial">
        {([["learn", "Learn to play"], ["captains", "Captains"]] as const).map(([group, name]) => {
          const shown = list.filter((x) => x.group === group);
          return shown.length ? (
            <optgroup key={group} label={name}>
              {shown.map((x) => <option key={x.id} value={x.id}>{label(x)}</option>)}
            </optgroup>
          ) : null;
        })}
      </select>
      <div className="row between tutorial-row">
        <p className="muted">{t.summary}{t.finished && <span className="pill">Finished</span>}</p>
        <div className="row">
          {t.game_id && <Link className="button" to={`/games/${t.game_id}`}>Continue</Link>}
          <button className={t.game_id || t.finished ? "secondary" : undefined} disabled={start.isPending}
            onClick={() => start.mutate(t.id)}>{t.game_id || t.finished ? "Start again" : "Start"}</button>
        </div>
      </div>
      {start.error && <p className="error" role="alert">{start.error.message}</p>}
    </section>
  );
}

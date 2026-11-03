import { ReactNode, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { Game, GameStanding, MODE_LABELS, TutorialInfo, api, campaignApi } from "../api";
import { useAccount } from "../account";
import { JoinForm } from "../components/JoinForm";

type MyGameData = Game & { your_seat: number };

/**
 * The lobby (REQ-CLI-60): challenges for you, then your games by where they stand (your move, waiting for your
 * opponent), tutorials and campaigns, open games to join, and completed games last, folded away.
 */
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

  // A tutorial in progress is continued from the Tutorials card, not listed twice.
  const playing = mine.filter((g) => g.status !== "finished" && !g.tutorial);
  const yourMove = playing.filter((g) => g.status === "active" && isYourMove(g)).sort(byLastMove);
  const theirMove = playing.filter((g) => !yourMove.includes(g)).sort(byLastMove);
  const completed = mine.filter((g) => g.status === "finished").sort(byLastMove);
  const loaded = myGames.isSuccess;

  return (
    <main className="page lobby">
      <div className="row between lobby-head">
        <h1>Lobby</h1>
        <div className="row">
          <Link className="button secondary" to="/campaigns/new">New Five-Year Mission</Link>
          <Link className="button" to="/new">New game</Link>
        </div>
      </div>
      {(games.isError || myGames.isError) && <p className="error">{(games.error ?? myGames.error)!.message}</p>}

      {challenges.length > 0 && (
        <Section title="Challenges for you" count={challenges.length}>
          {challenges.map((g) => (
            <li key={g.id} className="game-row your-move stack">
              <GameSummary game={g} />
              <JoinForm game={g} />
            </li>
          ))}
        </Section>
      )}

      {yourMove.length > 0 && (
        <Section title="Your move" count={yourMove.length}>
          {yourMove.map((g) => <MyGame key={g.id} game={g} />)}
        </Section>
      )}

      {theirMove.length > 0 && (
        <Section title="Waiting for your opponent" count={theirMove.length}>
          {theirMove.map((g) => <MyGame key={g.id} game={g} />)}
        </Section>
      )}

      {loaded && yourMove.length + theirMove.length === 0 && (
        <section className="card lobby-empty">
          <p><strong>No games in progress.</strong></p>
          <p className="muted">Start a <Link to="/new">new game</Link>: two players, solo against a Bot, or Cadet
            Training. Or join one of the open games below.</p>
        </section>
      )}

      <Tutorials />

      <MyCampaigns />

      <Section title="Open games" count={open.length}
        empty={<p className="muted">No one is waiting for an opponent.</p>}>
        {open.map((g) => <OpenGame key={g.id} game={g} />)}
      </Section>

      {completed.length > 0 && (
        <details className="lobby-completed">
          <summary><h2>Completed games <span className="count">{completed.length}</span></h2></summary>
          <ul className="list">
            {completed.map((g) => <MyGame key={g.id} game={g} />)}
          </ul>
        </details>
      )}

      <p className="muted lobby-footer"><Link to="/admin">Admin</Link></p>
    </main>
  );
}

function Section({ title, count, empty, children }: { title: string; count: number; empty?: ReactNode; children: ReactNode }) {
  return (
    <section className="lobby-section">
      <h2>{title}{count > 0 && <span className="count">{count}</span>}</h2>
      {count === 0 ? empty : <ul className="list">{children}</ul>}
    </section>
  );
}

/** Your decision is pending. Solo and Cadet Training games are always yours; a game whose standing could not be
 *  worked out is shown as yours too, so it is not hidden. */
function isYourMove(g: MyGameData): boolean {
  if (g.open_seats > 0) return false;
  const waiting = g.standing?.waiting_on;
  return waiting == null || waiting === g.your_seat;
}

function lastMove(g: Game): number {
  return Date.parse(g.standing?.at ?? g.created_at);
}

function byLastMove(a: Game, b: Game): number {
  return lastMove(b) - lastMove(a);
}

/** "5 min ago", "3 h ago", "yesterday", "12 Oct". */
function ago(iso: string): string {
  const minutes = Math.round((Date.now() - Date.parse(iso)) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  if (hours < 48) return "yesterday";
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function useCaptains(): (deckId: string) => string {
  const decks = useQuery({ queryKey: ["decks"], queryFn: api.decks });
  return (id) => decks.data?.find((d) => d.id === id)?.captain ?? id;
}

/** Where a game stands, as one short status: Your move, their move, waiting to join, or the result. */
function status(g: Game, yourSeat: number | null, forYou: boolean): { text: string; tone: "accent" | "quiet" | "won" | "lost" } {
  if (forYou) return { text: "Challenges you", tone: "accent" };
  if (g.open_seats > 0) {
    return { text: g.challenge ? `Waiting for ${g.challenge.display_name} to accept` : "Waiting for someone to join", tone: "quiet" };
  }
  const st: GameStanding | null | undefined = g.standing;
  if (g.status === "finished") {
    const winners = st?.winners ?? [];
    if (g.mode === "cadet") return { text: "Finished", tone: "quiet" };
    if (yourSeat == null || winners.length === 0) return { text: "Finished", tone: "quiet" };
    if (winners.length > 1) return { text: "Tie", tone: "quiet" };
    return winners[0] === yourSeat ? { text: "You won", tone: "won" } : { text: "You lost", tone: "lost" };
  }
  if (yourSeat == null) return { text: "In progress", tone: "quiet" };
  if (st?.waiting_on == null || st.waiting_on === yourSeat) return { text: "Your move", tone: "accent" };
  const them = g.seats.find((s) => s.index === st.waiting_on)?.display_name ?? "your opponent";
  return { text: `Waiting for ${them}`, tone: "quiet" };
}

/** One game: the mode, who plays whom, and its details. */
function GameSummary({ game, yourSeat = null }: { game: Game; yourSeat?: number | null }) {
  const account = useAccount();
  const captain = useCaptains();
  const forYou = !!game.challenge && game.challenge.user_id === account?.id && yourSeat == null;
  const st = game.standing;
  const name = (i: number) => (i === yourSeat ? "You" : game.seats.find((s) => s.index === i)?.display_name ?? "");
  const side = (s: { index: number; deck_id: string }) => {
    const score = st?.scores?.find((x) => x.seat === s.index)?.total;
    return `${name(s.index)} (${captain(s.deck_id)})${game.status === "finished" && score != null ? ` ${score}` : ""}`;
  };
  let players = game.seats.map(side).join(" vs ");
  if (game.mode === "solo" && game.bot) {
    const botScore = st?.scores?.find((x) => x.seat === 1)?.total;
    players += ` vs Bot ${captain(game.bot.deck_id)}${game.status === "finished" && botScore != null ? ` ${botScore}` : ""}`;
  }
  if (game.mode === "two_player" && game.seats.length === 1) players += game.challenge ? ` vs ${game.challenge.display_name}` : " vs ?";
  const details = [
    game.campaign_id ? "Five-Year Mission" : game.tutorial ? "Tutorial" : null,
    game.box === "core" ? "Core Box" : game.box === "both" ? "both boxes" : null,
    game.expansions.includes("second_contact") ? "Second Contact" : null,
    game.mode === "solo" && game.bot ? game.bot.difficulty[0].toUpperCase() + game.bot.difficulty.slice(1) : null,
    st && game.status !== "waiting" ? `turn ${st.turn + 1}` : null,  // as the game's log counts them, from 1
    st?.at ? (game.status === "finished" ? `ended ${ago(st.at)}` : `last move ${ago(st.at)}`) : `created ${ago(game.created_at)}`,
  ].filter(Boolean);
  const { text, tone } = status(game, yourSeat, forYou);
  return (
    <div className="game-summary">
      <div className="game-title-line">
        <strong>{MODE_LABELS[game.mode]}</strong>
        <span className={`status-pill ${tone}`}>{text}</span>
      </div>
      <div>{players}</div>
      <div className="muted game-meta">{details.join(" · ")}</div>
    </div>
  );
}

function MyGame({ game }: { game: MyGameData }) {
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
  const yours = game.status === "active" && isYourMove(game);

  return (
    <li className={`game-row ${yours ? "your-move" : ""} ${game.status === "finished" ? "done" : ""}`}>
      <div className="game-row-main">
        <GameSummary game={game} yourSeat={game.your_seat} />
        <div className="row game-actions">
          <Link className={`button ${yours ? "" : "secondary"}`} to={`/games/${game.id}`}>
            {game.status === "finished" ? "View" : yours ? "Play" : "Open"}
          </Link>
          {!confirming && (
            <button className="icon-button" onClick={() => setConfirming(true)} aria-label="Delete game" title="Delete game">✕</button>
          )}
        </div>
      </div>
      {confirming && (
        <div className="row between confirm-delete" role="alert">
          <span>Delete this game{others ? " for both players" : ""}? This cannot be undone.</span>
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
    <li className="game-row">
      <div className="game-row-main">
        <GameSummary game={game} />
        {!joining && <div className="row game-actions"><button onClick={() => setJoining(true)}>Join</button></div>}
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
    <section className="lobby-section">
      <h2>Your Five-Year Missions<span className="count">{ids.length}</span></h2>
      <ul className="list">
        {(campaigns.data ?? []).filter((c): c is NonNullable<typeof c> => !!c).map((c) => (
          <li key={c.id} className={`game-row ${c.phase === "finished" ? "done" : ""}`}>
            <div className="game-row-main">
              <div className="game-summary">
                <div className="game-title-line">
                  <strong>{c.display_name}</strong>
                  {c.phase === "finished" && <span className="status-pill quiet">Finished</span>}
                </div>
                <div className="muted game-meta">
                  {c.captain}&apos;s crew · {c.rank} · {c.assignments.length} of 10 assignments
                </div>
              </div>
              <div className="row game-actions">
                <Link className="button secondary" to={`/campaigns/${c.id}`}>Open</Link>
              </div>
            </div>
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

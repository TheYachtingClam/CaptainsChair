import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AuthError, MODE_LABELS, api } from "../api";
import { Board } from "../components/Board";
import { usePhone } from "../components/Sheet";
import { DevPanel } from "../components/DevPanel";

type SocketState = "connecting" | "open" | "closed" | "no-seat";

export function GameTable() {
  const { gameId = "" } = useParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const game = useQuery({ queryKey: ["game", gameId], queryFn: () => api.game(gameId) });
  const started = game.data?.status === "active" || game.data?.status === "finished";
  const state = useQuery({ queryKey: ["state", gameId], queryFn: () => api.state(gameId), enabled: started });
  const command = useMutation({
    mutationFn: (option: string) => api.command(gameId, option),
    onSuccess: (view) => queryClient.setQueryData(["state", gameId], view),
  });
  const undo = useMutation({
    mutationFn: () => api.undo(gameId),
    onSuccess: (view) => queryClient.setQueryData(["state", gameId], view),
  });
  const coach = useMutation({
    mutationFn: (action: "next" | "free" | "tip") => api.coach(gameId, action),
    onSuccess: (view) => queryClient.setQueryData(["state", gameId], view),
  });
  const [socket, setSocket] = useState<SocketState>("connecting");
  const [exiting, setExiting] = useState(false);
  const [reporting, setReporting] = useState<"bug" | "feature" | null>(null);
  const phone = usePhone();
  const quitting = useRef(false);
  const hello = useRef<number | null>(null); // the seat this page's socket connected as
  const quit = useMutation({
    mutationFn: () => {
      quitting.current = true; // we deleted the game ourselves: the page moves on, not the socket handler
      return api.deleteGame(gameId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] });
      const campaignId = game.data?.campaign_id;
      navigate(campaignId ? `/campaigns/${campaignId}` : "/", { replace: true });
    },
    onError: () => { quitting.current = false; },
  });
  const [online, setOnline] = useState<number[]>([]);
  const [seatTaken, setSeatTaken] = useState(false);
  const [log, setLog] = useState<string[]>([]);

  // The signed-in account's seat (REQ-USER-42). Watchers have no socket.
  const seated = game.data?.your_seat != null;
  useEffect(() => {
    if (!seated) {
      setSocket("no-seat");
      return;
    }
    let ws: WebSocket | null = null;
    let retry: number | undefined;
    let stopped = false;

    const connect = () => {
      const scheme = location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${scheme}://${location.host}/api/games/${gameId}/ws`);
      setSocket("connecting");
      ws.onopen = () => setSocket("open");
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "presence") setOnline(msg.connected);
        if (msg.type === "seat_taken" && msg.seat === hello.current) {
          // The admin took over this seat (REQ-ADMIN-06): this page can only watch from now on.
          stopped = true;
          setSeatTaken(true);
          queryClient.invalidateQueries({ queryKey: ["game", gameId] });
          queryClient.invalidateQueries({ queryKey: ["state", gameId] });
        }
        if (msg.type === "hello") hello.current = msg.your_seat;
        if (msg.type === "game_deleted") {
          stopped = true;
          if (quitting.current) return;
          queryClient.invalidateQueries({ queryKey: ["games"] });
          navigate("/", { replace: true });
          return;
        }
        if (msg.type === "game_updated") queryClient.invalidateQueries({ queryKey: ["game", gameId] });
        if (msg.type === "state_changed" || msg.type === "game_updated") queryClient.invalidateQueries({ queryKey: ["state", gameId] });
        setLog((l) => [`${new Date().toLocaleTimeString()} ${describe(msg)}`, ...l].slice(0, 50));
      };
      ws.onclose = () => {
        setSocket("closed");
        if (stopped) return;
        // Reconnect (REQ-SRV-43), but only while the game exists and this account still has a seat in it: the server
        // refuses the socket otherwise, and retrying would never end.
        retry = window.setTimeout(async () => {
          // A network error (offline, server restarting) keeps retrying; a deleted game, a lost seat or an ended session stops.
          const current = await api.game(gameId).catch((err: Error) =>
            err instanceof AuthError || err.message === "Game not found" ? null : undefined);
          if (stopped) return;
          if (current === null || (current && current.your_seat == null)) {
            stopped = true;
            queryClient.invalidateQueries({ queryKey: ["game", gameId] });
            return;
          }
          connect();
        }, 2000);
      };
    };
    connect();
    return () => {
      stopped = true;
      window.clearTimeout(retry);
      ws?.close();
    };
  }, [gameId, queryClient, navigate, seated]);

  if (game.isPending) return <main className="page">Loading game…</main>;
  if (game.isError) return <main className="page error">{game.error.message}</main>;

  const g = game.data;
  const systemButtons = (
    <div className="row">
      {started && g.your_seat != null && (
        <>
          <button className="secondary" onClick={() => setReporting("feature")}>Suggest a feature</button>
          <button className="secondary" onClick={() => setReporting("bug")}>Report a bug</button>
        </>
      )}
      <button className="secondary" onClick={() => setExiting(true)}>Exit game</button>
    </div>
  );
  // The game's details and its players.
  const gameInfo = (
    <>
      <p className="muted">
        Game {g.id.slice(0, 8)} · {g.status === "waiting" ? "waiting for players" : g.status}
        {g.box === "core" && " · Core Box"}
        {g.box === "both" && " · Core Box and To Boldly Go combined"}
        {g.expansions.length > 0 && ` · expansions: ${g.expansions.join(", ")}`}
        {g.promos && " · promo cards"}
      </p>

      <section className="card">
        <h2>Players</h2>
        <ul className="list plain">
          {g.seats.map((s) => (
            <li key={s.index}>
              <span className={`dot ${online.includes(s.index) ? "on" : ""}`} aria-hidden />
              {s.display_name} – {s.deck_id}, {s.board_side} side
              {s.index === g.your_seat && <strong> (you)</strong>}
              <span className="muted"> · {online.includes(s.index) ? "online" : "offline"}</span>
            </li>
          ))}
          {g.open_seats > 0 && <li className="muted">Open seat. Share this page's link with your opponent.</li>}
        </ul>
      </section>
    </>
  );
  // The live connection and its events.
  const connection = (
    <>
      <p className="muted">Connection: {socket === "no-seat" ? "you have no seat in this game" : socket}</p>

      <section className="card">
        <h2>Events</h2>
        {log.length === 0 ? <p className="muted">No events yet.</p> : (
          <ul className="list plain mono">{log.map((line, i) => <li key={i}>{line}</li>)}</ul>
        )}
      </section>
    </>
  );
  // On a phone, once the table is showing, the buttons, the game's details, the players and the connection live on
  // its System tab
  // instead (REQ-CLI-32).
  const onTable = started && !!state.data;
  return (
    <main className="page">
      <div className="row between game-title">
        <h1>{MODE_LABELS[g.mode]}</h1>
        {!(phone && onTable) && systemButtons}
      </div>
      {reporting && <BugDialog gameId={gameId} kind={reporting} onClose={() => setReporting(null)} />}
      {exiting && (
        <ExitDialog mode={g.mode} campaign={!!g.campaign_id} seated={g.your_seat != null} over={g.status === "finished"}
          busy={quit.isPending} error={quit.error?.message}
          onLeave={() => navigate(g.campaign_id ? `/campaigns/${g.campaign_id}` : "/")}
          onQuit={() => quit.mutate()} onCancel={() => setExiting(false)} />
      )}
      {seatTaken && (
        <p className="error" role="alert">The admin has taken over your seat in this game. You can still watch it, but
          not play.</p>
      )}
      {g.campaign_id && (
        <p><Link to={`/campaigns/${g.campaign_id}`}>Back to the Five-Year Mission</Link> (the result is recorded there when
          the game ends)</p>
      )}
      {!(phone && onTable) && gameInfo}

      {started && state.data ? (
        <Board gameId={gameId} view={state.data} busy={command.isPending || undo.isPending || coach.isPending}
          onChoose={(o) => command.mutate(o)} onUndo={() => undo.mutate()} onCoach={(a) => coach.mutate(a)}
          system={<><section className="card">{systemButtons}</section>{gameInfo}{connection}</>} />
      ) : (
        <section className="card">
          <p className="muted">The game starts when every seat is filled.</p>
        </section>
      )}
      {state.data?.dev_tools && g.your_seat != null && g.status === "active" && <DevPanel gameId={gameId} />}
      {(command.error || undo.error) && <p className="error" role="alert">{(command.error || undo.error)!.message}</p>}
      {!(phone && onTable) && connection}
    </main>
  );
}

function describe(msg: { type: string; [k: string]: unknown }): string {
  switch (msg.type) {
    case "hello": return `Connected as seat ${msg.your_seat}`;
    case "presence": return `Online seats: ${(msg.connected as number[]).join(", ") || "none"}`;
    case "game_updated": return "A player joined";
    default: return JSON.stringify(msg);
  }
}

/** Report a bug: the player says what they saw; the server keeps it with the game's setup, seed and every move so
 *  far, so the game can be recreated as it is now or a few moves back (REQ-BUG-01 to -04). */
function BugDialog({ gameId, kind, onClose }: { gameId: string; kind: "bug" | "feature"; onClose: () => void }) {
  const [text, setText] = useState("");
  const box = useRef<HTMLTextAreaElement>(null);
  useEffect(() => box.current?.focus(), []);
  const send = useMutation({ mutationFn: () => api.reportBug(gameId, text.trim(), kind) });
  const feature = kind === "feature";
  return (
    <div className="modal-backdrop" onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="card modal stack bug-dialog" role="dialog" aria-labelledby="bug-title">
        <h2 id="bug-title">{feature ? "Suggest a feature" : "Report a bug"}</h2>
        {send.isSuccess ? (
          <>
            <p>Thank you. Your {feature ? "suggestion" : "report"} is saved with the game as it is right now, so you can
              keep playing.</p>
            <p className="muted">{feature ? "Suggestion" : "Report"} {send.data.id.slice(0, 8)}</p>
            <button onClick={onClose}>Close</button>
          </>
        ) : (
          <form className="stack" onSubmit={(e) => { e.preventDefault(); send.mutate(); }}>
            <label>
              {feature ? "What would you like the game to do?" : "What did you see, and what did you expect?"}
              <textarea ref={box} rows={7} maxLength={4000} value={text} onChange={(e) => setText(e.target.value)}
                placeholder={feature
                  ? "For example: let me see which cards my opponent has played this turn."
                  : "For example: I played Quark's second PLAY with 2 Ferengi in play and gained 1 Latinum, not 2."} />
            </label>
            <p className="muted">The game's setup and every move so far are saved with your {feature ? "suggestion" : "report"},
              so the position can be recreated. Nothing else is sent.</p>
            {send.error && <p className="error" role="alert">{send.error.message}</p>}
            <div className="row">
              <button type="button" className="secondary" onClick={onClose} disabled={send.isPending}>Cancel</button>
              <button type="submit" disabled={!text.trim() || send.isPending}>{feature ? "Send suggestion" : "Send report"}</button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

/** Leave the game for now (it stays in "Your games"), or quit it for good, which deletes it. */
function ExitDialog({ mode, campaign, seated, over, busy, error, onLeave, onQuit, onCancel }: {
  mode: string;
  campaign: boolean;
  seated: boolean;
  over: boolean;
  busy: boolean;
  error?: string;
  onLeave: () => void;
  onQuit: () => void;
  onCancel: () => void;
}) {
  const [sure, setSure] = useState(false);
  const first = useRef<HTMLButtonElement>(null);
  useEffect(() => first.current?.focus(), []);
  const consequence = campaign && !over
    ? "This assignment counts as a failure in your Five-Year Mission."
    : mode === "two_player" ? "The game ends for both players." : "The game and its history are gone.";
  return (
    <div className="modal-backdrop" onKeyDown={(e) => e.key === "Escape" && onCancel()}>
      <div className="card modal stack" role="dialog" aria-labelledby="exit-title">
        <h2 id="exit-title">Exit game</h2>
        {!sure ? (
          <>
            <button ref={first} onClick={onLeave}>{campaign ? "Back to the Five-Year Mission" : "Back to the lobby"}</button>
            <p className="muted">The game is kept. Continue it any time from {campaign ? "the campaign page" : "\u201cYour games\u201d in the lobby"}.</p>
            {seated && (
              <>
                <button className="danger" onClick={() => setSure(true)}>Quit and delete the game…</button>
                <p className="muted">Ends the game for good. You are asked to confirm.</p>
              </>
            )}
            <button className="secondary" onClick={onCancel}>Cancel</button>
          </>
        ) : (
          <>
            <p><strong>Quit and delete this game?</strong> {consequence} This can’t be undone.</p>
            <div className="row">
              <button className="secondary" onClick={() => setSure(false)} disabled={busy}>Go back</button>
              <button className="danger" onClick={onQuit} disabled={busy}>Quit and delete</button>
            </div>
          </>
        )}
        {error && <p className="error" role="alert">{error}</p>}
      </div>
    </div>
  );
}

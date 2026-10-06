import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { MODE_LABELS, api, forgetSeatToken, loadSeatToken } from "../api";
import { Board } from "../components/Board";
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
  const [socket, setSocket] = useState<SocketState>("connecting");
  const [exiting, setExiting] = useState(false);
  const quitting = useRef(false); // we deleted the game ourselves: the page moves on, not the socket handler
  const quit = useMutation({
    mutationFn: () => {
      quitting.current = true;
      return api.deleteGame(gameId);
    },
    onSuccess: () => {
      forgetSeatToken(gameId);
      queryClient.invalidateQueries({ queryKey: ["games"] });
      const campaignId = game.data?.campaign_id;
      navigate(campaignId ? `/campaigns/${campaignId}` : "/", { replace: true });
    },
    onError: () => { quitting.current = false; },
  });
  const [online, setOnline] = useState<number[]>([]);
  const [log, setLog] = useState<string[]>([]);

  useEffect(() => {
    const token = loadSeatToken(gameId);
    if (!token) {
      setSocket("no-seat");
      return;
    }
    let ws: WebSocket | null = null;
    let retry: number | undefined;
    let stopped = false;

    const connect = () => {
      const scheme = location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${scheme}://${location.host}/api/games/${gameId}/ws?seat=${encodeURIComponent(token)}`);
      setSocket("connecting");
      ws.onopen = () => setSocket("open");
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "presence") setOnline(msg.connected);
        if (msg.type === "game_deleted") {
          stopped = true;
          if (quitting.current) return;
          forgetSeatToken(gameId);
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
        if (!stopped) retry = window.setTimeout(connect, 2000); // reconnect (REQ-SRV-43)
      };
    };
    connect();
    return () => {
      stopped = true;
      window.clearTimeout(retry);
      ws?.close();
    };
  }, [gameId, queryClient, navigate]);

  if (game.isPending) return <main className="page">Loading game…</main>;
  if (game.isError) return <main className="page error">{game.error.message}</main>;

  const g = game.data;
  return (
    <main className="page">
      <div className="row between game-title">
        <h1>{MODE_LABELS[g.mode]}</h1>
        <button className="secondary" onClick={() => setExiting(true)}>Exit game</button>
      </div>
      {exiting && (
        <ExitDialog mode={g.mode} campaign={!!g.campaign_id} seated={g.your_seat != null} over={g.status === "finished"}
          busy={quit.isPending} error={quit.error?.message}
          onLeave={() => navigate(g.campaign_id ? `/campaigns/${g.campaign_id}` : "/")}
          onQuit={() => quit.mutate()} onCancel={() => setExiting(false)} />
      )}
      {g.campaign_id && (
        <p><Link to={`/campaigns/${g.campaign_id}`}>Back to the Five-Year Mission</Link> (the result is recorded there when
          the game ends)</p>
      )}
      <p className="muted">
        Game {g.id.slice(0, 8)} · {g.status === "waiting" ? "waiting for players" : g.status}
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

      {started && state.data ? (
        <Board gameId={gameId} view={state.data} busy={command.isPending || undo.isPending}
          onChoose={(o) => command.mutate(o)} onUndo={() => undo.mutate()} />
      ) : (
        <section className="card">
          <p className="muted">The game starts when every seat is filled.</p>
        </section>
      )}
      {state.data?.dev_tools && g.your_seat != null && g.status === "active" && <DevPanel gameId={gameId} />}
      {(command.error || undo.error) && <p className="error" role="alert">{(command.error || undo.error)!.message}</p>}
      <p className="muted">Connection: {socket === "no-seat" ? "you have no seat in this game" : socket}</p>

      <section className="card">
        <h2>Events</h2>
        {log.length === 0 ? <p className="muted">No events yet.</p> : (
          <ul className="list plain mono">{log.map((line, i) => <li key={i}>{line}</li>)}</ul>
        )}
      </section>
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

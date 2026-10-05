import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
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
      <h1>{MODE_LABELS[g.mode]}</h1>
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

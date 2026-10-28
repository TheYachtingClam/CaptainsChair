import { useEffect, useMemo, useRef, useState } from "react";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { MODE_LABELS, Timeline, ViewAs, adminApi, api } from "../api";
import { Board } from "../components/Board";
import { usePhone } from "../components/Sheet";

/**
 * The admin watches a game (requirements/19-technical-architecture.md §5.6, REQ-ADMIN-07 to -12): the table,
 * read-only, at any position, with a bar to step through the moves, go to a turn and follow the game live. The address
 * holds the position (`at`, left out while following live) and the View as choice (`as`), so a reload keeps both.
 */
export function Observe() {
  const { gameId = "" } = useParams();
  const [params, setParams] = useSearchParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const phone = usePhone();
  const asParam = params.get("as");
  const viewAs: ViewAs = asParam === "watcher" || (asParam && /^\d+$/.test(asParam)) ? (asParam as ViewAs) : "all";
  const atParam = params.get("at");
  const wanted = atParam != null && /^\d+$/.test(atParam) ? Number(atParam) : null; // null: follow live

  const game = useQuery({ queryKey: ["game", gameId], queryFn: () => api.game(gameId) });
  const timeline = useQuery({ queryKey: ["timeline", gameId], queryFn: () => adminApi.timeline(gameId) });
  const last = timeline.data?.last ?? 0;
  const at = wanted == null ? null : Math.min(wanted, last);
  const view = useQuery({
    queryKey: ["observe", gameId, at, viewAs],
    queryFn: () => adminApi.observe(gameId, at, viewAs),
    placeholderData: keepPreviousData,
    enabled: timeline.isSuccess,
  });
  // The position asked for. Stepping counts from it, not from the one loaded, so quick presses each take a step; the
  // table dims until the position arrives.
  const shown = at ?? last;

  // Stepping feels instant when the positions either side are already fetched.
  useEffect(() => {
    if (!timeline.isSuccess) return;
    for (const p of [shown - 1, shown + 1]) {
      if (p < 0 || p > last) continue;
      const key = p === last ? null : p;  // the last position is the live one
      queryClient.prefetchQuery({ queryKey: ["observe", gameId, key, viewAs], queryFn: () => adminApi.observe(gameId, key, viewAs) });
    }
  }, [shown, last, viewAs, gameId, timeline.isSuccess, queryClient]);

  // Live follow (REQ-ADMIN-11): the admin's socket watches unseen, and every change refreshes the timeline and the
  // latest position.
  const [deleted, setDeleted] = useState(false);
  useEffect(() => {
    let ws: WebSocket | null = null;
    let retry: number | undefined;
    let stopped = false;
    const connect = () => {
      const scheme = location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${scheme}://${location.host}/api/games/${gameId}/ws?watch=1`);
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "game_deleted") {
          stopped = true;
          setDeleted(true);
        }
        if (msg.type === "state_changed" || msg.type === "game_updated") {
          queryClient.invalidateQueries({ queryKey: ["timeline", gameId] });
          queryClient.invalidateQueries({ queryKey: ["observe", gameId, null] });
          queryClient.invalidateQueries({ queryKey: ["game", gameId] });
        }
      };
      ws.onclose = () => {
        if (!stopped) retry = window.setTimeout(connect, 2000);
      };
    };
    connect();
    return () => {
      stopped = true;
      window.clearTimeout(retry);
      ws?.close();
    };
  }, [gameId, queryClient]);

  // The position just asked for: the address changes a moment after a step, and quick presses must each count from
  // the step before.
  const asked = useRef<number | null>(null);
  useEffect(() => {
    if (asked.current === shown) asked.current = null;
  }, [shown]);
  function go(p: number) {
    p = Math.min(Math.max(0, p), last);
    asked.current = p;
    const next = new URLSearchParams(params);
    if (p >= last) next.delete("at");  // the last position follows the game live
    else next.set("at", String(Math.max(0, p)));
    setParams(next, { replace: true });
  }
  function setViewAs(v: ViewAs) {
    const next = new URLSearchParams(params);
    if (v === "all") next.delete("as");
    else next.set("as", v);
    setParams(next, { replace: true });
  }

  // Each distinct position a turn opens at, in order: for stepping a whole turn (REQ-ADMIN-10).
  const turnStarts = useMemo(() => [...new Set((timeline.data?.turns ?? []).map((t) => t.at))].sort((a, b) => a - b),
    [timeline.data]);
  const turnFrom = (from: number, dir: -1 | 1) =>
    dir < 0 ? [...turnStarts].reverse().find((p) => p < from) : turnStarts.find((p) => p > from);
  const prevTurn = turnFrom(shown, -1);
  const nextTurn = turnFrom(shown, 1);
  // A step counts from the position just asked for, else from the one shown.
  const step = (kind: "move" | "turn", dir: -1 | 1) => {
    const from = asked.current ?? shown;
    const to = kind === "move" ? from + dir : turnFrom(from, dir);
    if (to != null && to >= 0 && to <= last) go(to);
  };

  // Keys on a laptop (REQ-ADMIN-09): ← → a move, Page Up / Page Down a turn, Home the start, End live.
  const keys = useRef({ go, step, last });
  keys.current = { go, step, last };
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "INPUT" || t.tagName === "SELECT" || t.tagName === "TEXTAREA")) return;
      const k = keys.current;
      if (e.key === "ArrowLeft") k.step("move", -1);
      else if (e.key === "ArrowRight") k.step("move", 1);
      else if (e.key === "PageUp") k.step("turn", -1);
      else if (e.key === "PageDown") k.step("turn", 1);
      else if (e.key === "Home") k.go(0);
      else if (e.key === "End") k.go(k.last);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const copy = useMutation({
    mutationFn: () => adminApi.copyGame(gameId, shown),
    onSuccess: (r) => {
      queryClient.invalidateQueries({ queryKey: ["admin-games"] });
      navigate(`/games/${r.game_id}`);
    },
  });

  if (game.isError) return <main className="page error">{game.error.message}</main>;
  if (timeline.isError) return <main className="page error">{timeline.error.message}</main>;
  if (!game.data || !timeline.data) return <main className="page">Loading game…</main>;
  const g = game.data;
  const t = timeline.data;
  // The View as choices, known before the first view arrives so a reload keeps the choice shown.
  const seats = view.data?.players.map((p) => ({ seat: p.seat, name: p.name, bot: !!p.bot }))
    ?? [...g.seats.map((x) => ({ seat: x.index, name: x.display_name, bot: false })),
      ...(g.bot ? [{ seat: g.seats.length, name: `${g.bot.deck_id} Bot`, bot: true }] : [])];

  return (
    <main className="page observe-page">
      <div className="row between game-title">
        <h1>Watching: {MODE_LABELS[g.mode]}</h1>
        {!phone && <Link to="/admin">Back to Admin</Link>}
      </div>
      <p className="muted">
        {g.seats.map((s) => `${s.display_name} (${s.deck_id})`).join(" vs ")}{g.bot && ` vs the ${g.bot.deck_id} Bot`}
        {" · "}{g.status} · read-only: watching stores nothing, and the players do not see you
      </p>
      {deleted && <p className="error" role="alert">This game was deleted. What is shown is its last state.</p>}
      {t.stopped && (
        <p className="error" role="alert">
          The moves end at {t.stopped.at}: move {t.stopped.at + 1} no longer applies with the current rules
          ({t.stopped.reason}). The game itself is untouched.
        </p>
      )}

      <ObserverBar t={t} shown={shown} live={at == null} prevTurn={prevTurn} nextTurn={nextTurn} onGo={go} onStep={step}
        viewAs={viewAs} onViewAs={setViewAs} seats={seats}
        onCopy={() => copy.mutate()} copying={copy.isPending} turn={view.data?.turn} />
      {copy.error && <p className="error" role="alert">{copy.error.message}</p>}
      {view.isError && <p className="error" role="alert">{view.error.message}</p>}

      {view.data && (
        <div className={view.isPlaceholderData ? "observe-loading" : undefined}>
          <Board gameId={gameId} view={view.data} busy readOnly onChoose={() => {}} onUndo={() => {}}
            system={<section className="card"><Link to="/admin">Back to Admin</Link></section>} />
        </div>
      )}
    </main>
  );
}

function ObserverBar({ t, shown, live, prevTurn, nextTurn, onGo, onStep, viewAs, onViewAs, seats, onCopy, copying, turn }: {
  t: Timeline;
  onStep: (kind: "move" | "turn", dir: -1 | 1) => void;
  shown: number;
  live: boolean;
  prevTurn?: number;
  nextTurn?: number;
  onGo: (at: number) => void;
  viewAs: ViewAs;
  onViewAs: (v: ViewAs) => void;
  seats: { seat: number; name: string; bot: boolean }[];
  onCopy: () => void;
  copying: boolean;
  turn?: number;
}) {
  const phone = usePhone();
  const [more, setMore] = useState(false);
  const [turnText, setTurnText] = useState("");
  const [movesOpen, setMovesOpen] = useState(false);
  const goToTurn = () => {
    const n = Number(turnText);
    const found = t.turns.find((x) => x.turn === n);
    if (found) onGo(found.at);
  };
  const behind = t.last - shown;
  const move = shown > 0 ? t.moves[shown - 1] : null;
  const turnBox = (
    <form className="row observe-turn" onSubmit={(e) => { e.preventDefault(); goToTurn(); }}>
      <label className="inline">
        Turn
        <input type="number" min={1} max={t.turns.length} inputMode="numeric" value={turnText}
          placeholder={turn ? String(turn) : ""} onChange={(e) => setTurnText(e.target.value)} aria-label="Go to turn" />
      </label>
      <button type="submit" className="secondary" disabled={!t.turns.some((x) => x.turn === Number(turnText))}>Go</button>
    </form>
  );
  const rest = (
    <>
      <label className="inline">
        View as
        <select value={viewAs} onChange={(e) => onViewAs(e.target.value as ViewAs)}>
          <option value="all">Everything</option>
          {seats.map((s) => <option key={s.seat} value={String(s.seat)}>{s.name}{s.bot ? " (Bot)" : ""}</option>)}
          <option value="watcher">A watcher without a seat</option>
        </select>
      </label>
      <button className="secondary" onClick={onCopy} disabled={copying}
        title="A playable copy of the game as shown here; every seat is yours, and the game itself is untouched">
        Copy from here
      </button>
      <button className="secondary" onClick={() => setMovesOpen((o) => !o)} aria-expanded={movesOpen}>
        {movesOpen ? "Hide moves" : `Moves (${t.last})`}
      </button>
    </>
  );
  return (
    <section className="card observer-bar" aria-label="Watching controls">
      <div className="row observe-steps">
        {!phone && <button className="secondary" title="Start (Home)" disabled={shown === 0} onClick={() => onGo(0)}>|◀</button>}
        <button className="secondary" title="Previous turn (Page Up)" disabled={prevTurn == null}
          onClick={() => onStep("turn", -1)}>◀◀</button>
        <button className="secondary" title="Previous move (←)" disabled={shown === 0} onClick={() => onStep("move", -1)}>◀</button>
        <button className="secondary" title="Next move (→)" disabled={shown >= t.last} onClick={() => onStep("move", 1)}>▶</button>
        <button className="secondary" title="Next turn (Page Down)" disabled={nextTurn == null}
          onClick={() => onStep("turn", 1)}>▶▶</button>
        {!phone && <button className="secondary" title="Live (End)" disabled={live} onClick={() => onGo(t.last)}>▶|</button>}
        {phone && <button className="secondary" onClick={() => setMore((m) => !m)} aria-expanded={more} title="More">⋯</button>}
        <span className="observe-where">
          Move {shown} of {t.last}{turn != null && ` · turn ${turn}`}
          {live ? <strong className="live-mark"> · live</strong> : (
            <> · {behind} move{behind === 1 ? "" : "s"} behind <button className="link" onClick={() => onGo(t.last)}>Back to live</button></>
          )}
        </span>
      </div>
      <input type="range" className="observe-slider" min={0} max={t.last} value={shown}
        onChange={(e) => onGo(Number(e.target.value))} aria-label="Position in the game" disabled={t.last === 0} />
      {move && (!phone || more) && (
        <p className="muted observe-move">
          Last move: <strong>{t.turns.find((x) => x.seat === move.seat)?.name ?? `Seat ${move.seat}`}</strong>
          {move.prompt && <> · {move.prompt}</>} → {move.move}{move.dev && " (developer command)"}
        </p>
      )}
      {(!phone || more) && <div className="row observe-more">{turnBox}{rest}</div>}
      {movesOpen && <MoveList t={t} shown={shown} onGo={onGo} />}
    </section>
  );
}

/** Every move, grouped by turn; clicking one goes to the position after it (REQ-ADMIN-09). */
function MoveList({ t, shown, onGo }: { t: Timeline; shown: number; onGo: (at: number) => void }) {
  const current = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    current.current?.scrollIntoView({ block: "nearest" });  // newer browsers return a Promise: not a clean-up
  }, [shown]);
  return (
    <ol className="move-list">
      {t.turns.map((turn) => {
        const moves = t.moves.filter((m) => m.turn === turn.turn);
        return (
          <li key={turn.turn}>
            <button className={`link move-turn ${shown === turn.at ? "current" : ""}`} ref={shown === turn.at ? current : undefined}
              onClick={() => onGo(turn.at)}>
              Turn {turn.turn} · {turn.name}{turn.bot && " (Bot: played inside the move before)"}
            </button>
            {moves.length > 0 && (
              <ol>
                {moves.map((m) => (
                  <li key={m.at}>
                    <button className={`link ${shown === m.at ? "current" : ""}`} ref={shown === m.at && shown !== turn.at ? current : undefined}
                      onClick={() => onGo(m.at)} title={m.prompt}>
                      {m.at}. {m.move}{m.dev && " (developer)"}
                    </button>
                  </li>
                ))}
              </ol>
            )}
          </li>
        );
      })}
    </ol>
  );
}

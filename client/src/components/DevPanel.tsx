import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DevCommand, api } from "../api";

const ZONES: [string, string][] = [
  ["hand", "Hand"],
  ["staging", "Staging Area"],
  ["duty", "Duty Officer"],
  ["fleet", "Fleet Area"],
  ["locations", "Location Area"],
  ["discard", "Discard pile"],
  ["draw", "Top of Draw deck"],
  ["log", "Captain's Log"],
];
const RESOURCES = ["dilithium", "latinum", "glory", "actions"] as const;
const TRACKS = ["research", "influence", "military"] as const;

/** Testing tools, shown only when the server has DEV_TOOLS on. Every change is a normal, undoable command. */
export function DevPanel({ gameId }: { gameId: string }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [zone, setZone] = useState("hand");
  const cards = useQuery({ queryKey: ["card-text"], queryFn: api.cardText, staleTime: Infinity });
  const send = useMutation({
    mutationFn: (cmd: DevCommand) => api.dev(gameId, cmd),
    onSuccess: (view) => queryClient.setQueryData(["state", gameId], view),
  });

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q || !cards.data) return [];
    return Object.entries(cards.data)
      .filter(([id, c]) => id.toLowerCase().includes(q) || c.name.toLowerCase().includes(q))
      .slice(0, 12);
  }, [query, cards.data]);

  if (!open) {
    return <button className="dev-toggle" onClick={() => setOpen(true)} aria-label="Open developer tools">🛠 Dev</button>;
  }
  return (
    <aside className="dev-panel card" aria-label="Developer tools">
      <div className="row between">
        <strong>Developer tools</strong>
        <button className="icon-button" onClick={() => setOpen(false)} aria-label="Close developer tools">✕</button>
      </div>

      <label className="dev-field">
        Put a copy of a card in
        <select value={zone} onChange={(e) => setZone(e.target.value)}>
          {ZONES.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
        </select>
      </label>
      <input type="search" placeholder="Card name or id, e.g. Horta or 2CAR08" value={query}
        onChange={(e) => setQuery(e.target.value)} aria-label="Find a card" />
      {matches.length > 0 && (
        <ul className="dev-results">
          {matches.map(([id, c]) => (
            <li key={id}>
              <button className="link" disabled={send.isPending}
                onClick={() => send.mutate({ kind: "card", card: id, zone })}>
                {c.name} <span className="muted">{id} · {c.suit}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="dev-grid">
        {RESOURCES.map((r) => (
          <div key={r} className="dev-row">
            <span>{r[0].toUpperCase() + r.slice(1)}</span>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "resource", resource: r, amount: -1 })}>−1</button>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "resource", resource: r, amount: 1 })}>+1</button>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "resource", resource: r, amount: 5 })}>+5</button>
          </div>
        ))}
        {TRACKS.map((t) => (
          <div key={t} className="dev-row">
            <span>{t[0].toUpperCase() + t.slice(1)}</span>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "track", track: t, amount: -1 })}>−1</button>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "track", track: t, amount: 1 })}>+1</button>
            <button className="secondary" disabled={send.isPending} onClick={() => send.mutate({ kind: "track", track: t, amount: 5 })}>+5</button>
          </div>
        ))}
      </div>
      {send.error && <p className="error" role="alert">{send.error.message}</p>}
      <p className="muted small">Each change is an undoable command, and shows in the log as [Dev].</p>
    </aside>
  );
}

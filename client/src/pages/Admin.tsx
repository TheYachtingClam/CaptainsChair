import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AdminCampaign, AdminGame, MODE_LABELS, adminApi } from "../api";

const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString() : "—");

/** The admin: delete any game or campaign (requirements/19-technical-architecture.md §5.3). */
export function Admin() {
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["admin-status"], queryFn: adminApi.status });
  const admin = !!status.data?.admin;
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["admin-status"] });
  const logout = useMutation({ mutationFn: adminApi.logout, onSuccess: refresh });

  if (status.isPending) return <main className="page">Loading…</main>;
  if (status.isError) return <main className="page error">{status.error.message}</main>;
  return (
    <main className="page stack">
      <div className="row between">
        <h1>Admin</h1>
        <div className="row">
          {admin && <button className="secondary" onClick={() => logout.mutate()}>Sign out of admin</button>}
          <Link to="/">Lobby</Link>
        </div>
      </div>
      {!status.data.enabled ? (
        <p className="muted">There is no admin on this server. Set <code>ADMIN_PASSWORD</code> in the server&apos;s
          environment to turn it on.</p>
      ) : !admin ? <AdminLogin onDone={refresh} /> : (
        <>
          <AdminGames />
          <AdminCampaigns />
        </>
      )}
    </main>
  );
}

function AdminLogin({ onDone }: { onDone: () => void }) {
  const [password, setPassword] = useState("");
  const login = useMutation({ mutationFn: () => adminApi.login(password), onSuccess: onDone });
  function submit(e: FormEvent) {
    e.preventDefault();
    login.mutate();
  }
  return (
    <form className="card stack" onSubmit={submit}>
      <label>
        Admin password
        <input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      {login.error && <p className="error" role="alert">{login.error.message}</p>}
      <button type="submit" disabled={!password || login.isPending}>Sign in</button>
    </form>
  );
}

/** A Delete button that asks first. */
function ConfirmDelete({ what, onDelete, busy }: { what: string; onDelete: () => void; busy: boolean }) {
  const [asking, setAsking] = useState(false);
  if (!asking) return <button className="secondary" onClick={() => setAsking(true)}>Delete</button>;
  return (
    <span className="row confirm-delete">
      <span>Delete {what}? This can&apos;t be undone.</span>
      <button className="secondary" onClick={() => setAsking(false)} disabled={busy}>Cancel</button>
      <button className="danger" onClick={onDelete} disabled={busy}>Delete</button>
    </span>
  );
}

function AdminGames() {
  const queryClient = useQueryClient();
  const games = useQuery({ queryKey: ["admin-games"], queryFn: adminApi.games, refetchInterval: 10000 });
  const remove = useMutation({
    mutationFn: adminApi.deleteGame,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-games"] });
      queryClient.invalidateQueries({ queryKey: ["games"] });
    },
  });
  const [filter, setFilter] = useState<"all" | "waiting" | "active" | "finished">("all");
  const shown = (games.data ?? []).filter((g) => filter === "all" || g.status === filter);
  return (
    <section className="card">
      <div className="row between">
        <h2>Games ({games.data?.length ?? 0})</h2>
        <label className="inline">
          Show
          <select value={filter} onChange={(e) => setFilter(e.target.value as typeof filter)}>
            <option value="all">All</option>
            <option value="waiting">Waiting for an opponent</option>
            <option value="active">In progress</option>
            <option value="finished">Finished</option>
          </select>
        </label>
      </div>
      {games.isError && <p className="error">{games.error.message}</p>}
      {remove.error && <p className="error">{remove.error.message}</p>}
      {shown.length === 0 ? <p className="muted">No games.</p> : (
        <table className="admin-table">
          <thead>
            <tr><th>Created</th><th>Mode</th><th>Status</th><th>Players</th><th>Moves</th><th /></tr>
          </thead>
          <tbody>
            {shown.map((g: AdminGame) => (
              <tr key={g.id}>
                <td>{when(g.created_at)}</td>
                <td>{MODE_LABELS[g.mode] ?? g.mode}{g.bot && ` (${g.bot} Bot)`}{g.campaign_id && " · campaign"}</td>
                <td>{g.status}</td>
                <td>{g.players.join(", ") || "—"}</td>
                <td>{g.moves}</td>
                <td className="admin-actions">
                  <ConfirmDelete what="this game for everyone" busy={remove.isPending} onDelete={() => remove.mutate(g.id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

function AdminCampaigns() {
  const queryClient = useQueryClient();
  const camps = useQuery({ queryKey: ["admin-campaigns"], queryFn: adminApi.campaigns });
  const remove = useMutation({
    mutationFn: adminApi.deleteCampaign,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-campaigns"] }),
  });
  return (
    <section className="card">
      <h2>Five-Year Missions ({camps.data?.length ?? 0})</h2>
      <p className="muted">Deleting a campaign keeps its games; delete those above if you want them gone too.</p>
      {remove.error && <p className="error">{remove.error.message}</p>}
      {(camps.data ?? []).length === 0 ? <p className="muted">No campaigns.</p> : (
        <table className="admin-table">
          <thead>
            <tr><th>Created</th><th>Name</th><th>Crew</th><th>Rank</th><th>Assignments</th><th>Status</th><th /></tr>
          </thead>
          <tbody>
            {camps.data!.map((c: AdminCampaign) => (
              <tr key={c.id}>
                <td>{when(c.created_at)}</td>
                <td>{c.display_name}</td>
                <td>{c.deck_id}</td>
                <td>{c.rank}</td>
                <td>{c.assignments}</td>
                <td>{c.status}</td>
                <td className="admin-actions">
                  <ConfirmDelete what="this campaign" busy={remove.isPending} onDelete={() => remove.mutate(c.id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

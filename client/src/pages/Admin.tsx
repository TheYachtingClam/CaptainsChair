import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { AdminBug, AdminCampaign, AdminGame, AdminInvite, AdminUser, MODE_LABELS, MailOutcome, adminApi } from "../api";

/** What happened to an email the admin just caused, and what to do about it. */
function mailNote(outcome: MailOutcome | undefined, email: string): string {
  if (outcome === "sent") return `Emailed to ${email}. If it does not arrive, send them this link:`;
  if (outcome === "failed") return `The email to ${email} could not be sent (see the server log). Send them this link yourself:`;
  return `Email is not set up on this server, so send ${email} this link yourself:`;
}

const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString() : "—");

/** The admin: accounts, invitations, bug reports, and every game and campaign (requirements/19-technical-architecture.md §5.4). */
export function Admin() {
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["admin-status"], queryFn: adminApi.status });
  const admin = !!status.data?.admin;

  if (status.isPending) return <main className="page">Loading…</main>;
  if (status.isError) return <main className="page error">{status.error.message}</main>;
  return (
    <main className="page stack">
      <div className="row between">
        <h1>Admin</h1>
        <Link to="/">Lobby</Link>
      </div>
      {!admin ? (
        <p className="muted">Your account is not an admin. The first admin is made on the server with{" "}
          <code>python -m app.create_admin</code>.</p>
      ) : (
        <>
          <AdminInvites />
          <AdminUsers />
          <AdminBugs />
          <AdminGames />
          <AdminCampaigns />
        </>
      )}
    </main>
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

/** Invite people (REQ-USER-30): the invitation is emailed, and its link shown once here to pass on another way. */
function AdminInvites() {
  const queryClient = useQueryClient();
  const invites = useQuery({ queryKey: ["admin-invites"], queryFn: adminApi.invites });
  const [email, setEmail] = useState("");
  const [asAdmin, setAsAdmin] = useState(false);
  const [made, setMade] = useState<AdminInvite | null>(null);
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["admin-invites"] });
  const invite = useMutation({
    mutationFn: () => adminApi.invite(email.trim(), asAdmin),
    onSuccess: (row) => { setMade(row); setEmail(""); setAsAdmin(false); refresh(); },
  });
  const cancel = useMutation({ mutationFn: adminApi.cancelInvite, onSuccess: refresh });
  const error = invites.error ?? invite.error ?? cancel.error;
  return (
    <section className="card stack">
      <h2>Invitations</h2>
      <form className="row" onSubmit={(e: FormEvent) => { e.preventDefault(); invite.mutate(); }}>
        <input type="email" placeholder="Email address to invite" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="inline"><input type="checkbox" checked={asAdmin} onChange={(e) => setAsAdmin(e.target.checked)} /> as an admin</label>
        <button type="submit" disabled={!email.trim() || invite.isPending}>Invite</button>
      </form>
      {made?.link && (
        <p role="status">{mailNote(made.mail, made.email)} <code className="invite-link">{made.link}</code>
          <span className="muted"> (works once, for 7 days)</span></p>
      )}
      {error && <p className="error">{error.message}</p>}
      {(invites.data ?? []).length > 0 && (
        <table className="admin-table">
          <thead><tr><th>Invited</th><th>Email</th><th>Expires</th><th /></tr></thead>
          <tbody>
            {invites.data!.map((i) => (
              <tr key={i.id}>
                <td>{when(i.created_at)}</td>
                <td>{i.email}{i.is_admin && " (admin)"}</td>
                <td>{when(i.expires_at)}</td>
                <td className="admin-actions">
                  <button className="secondary" disabled={cancel.isPending} onClick={() => cancel.mutate(i.id)}>Cancel</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

/** Every account (REQ-USER-31): disable, enable, make admin, send a password reset. */
function AdminUsers() {
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: ["admin-users"], queryFn: adminApi.users });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["admin-users"] });
  const change = useMutation({
    mutationFn: ({ id, ...c }: { id: string; disabled?: boolean; is_admin?: boolean }) => adminApi.changeUser(id, c),
    onSuccess: refresh,
  });
  const reset = useMutation({
    mutationFn: (u: AdminUser) => adminApi.resetUser(u.id).then((r) => ({ link: r.link, outcome: r.mail, address: u.email })),
  });
  const error = users.error ?? change.error ?? reset.error;
  return (
    <section className="card stack">
      <h2>Accounts ({users.data?.length ?? 0})</h2>
      {reset.data && (
        <p role="status">{mailNote(reset.data.outcome, reset.data.address)} <code className="invite-link">{reset.data.link}</code>
          <span className="muted"> (works once, for 1 hour)</span></p>
      )}
      {error && <p className="error">{error.message}</p>}
      <table className="admin-table">
        <thead><tr><th>Name</th><th>Email</th><th>Joined</th><th>Last sign-in</th><th /></tr></thead>
        <tbody>
          {(users.data ?? []).map((u) => (
            <tr key={u.id} className={u.disabled ? "resolved" : undefined}>
              <td>{u.display_name}{u.is_admin && <span className="pill">Admin</span>}{u.disabled && " (disabled)"}</td>
              <td>{u.email}</td>
              <td>{when(u.created_at)}</td>
              <td>{when(u.last_seen_at)}</td>
              <td className="admin-actions">
                <button className="secondary" disabled={reset.isPending} onClick={() => reset.mutate(u)}>Reset password</button>{" "}
                <button className="secondary" disabled={change.isPending}
                  onClick={() => change.mutate({ id: u.id, is_admin: !u.is_admin })}>{u.is_admin ? "Remove admin" : "Make admin"}</button>{" "}
                <button className="secondary" disabled={change.isPending}
                  onClick={() => change.mutate({ id: u.id, disabled: !u.disabled })}>{u.disabled ? "Enable" : "Disable"}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

/** Bug reports from players (REQ-BUG-05 to -08): read them, download one for `scripts/replay_bug.py`, or open a
 *  playable copy of the game as it was reported, or a few moves earlier. */
function AdminBugs() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const bugs = useQuery({ queryKey: ["admin-bugs"], queryFn: adminApi.bugs, refetchInterval: 15000 });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["admin-bugs"] });
  const setStatus = useMutation({
    mutationFn: (b: AdminBug) => adminApi.setBugStatus(b.id, b.status === "open" ? "resolved" : "open"),
    onSuccess: refresh,
  });
  const remove = useMutation({ mutationFn: adminApi.deleteBug, onSuccess: refresh });
  const recreate = useMutation({
    mutationFn: ({ bug, back }: { bug: AdminBug; back: number }) =>
      adminApi.recreateBug(bug.id, back > 0 ? Math.max(0, bug.moves - back) : undefined),
    onSuccess: (copy) => {
      // The admin holds every seat of the copy; it is an ordinary game from here on.
      queryClient.invalidateQueries({ queryKey: ["admin-games"] });
      navigate(`/games/${copy.game_id}`);
    },
  });
  const [show, setShow] = useState<"open" | "all">("open");
  const [kind, setKind] = useState<"all" | "bug" | "feature">("all");
  const [back, setBack] = useState(0);
  const shown = (bugs.data ?? []).filter((b) => (show === "all" || b.status === "open") && (kind === "all" || b.kind === kind));
  const error = bugs.error ?? setStatus.error ?? remove.error ?? recreate.error;
  return (
    <section className="card">
      <div className="row between">
        <h2>Bug reports and feature requests ({(bugs.data ?? []).filter((b) => b.status === "open").length} open)</h2>
        <div className="row">
          <label className="inline">
            Recreate
            <select value={back} onChange={(e) => setBack(Number(e.target.value))}>
              <option value={0}>as reported</option>
              <option value={1}>1 move earlier</option>
              <option value={3}>3 moves earlier</option>
              <option value={5}>5 moves earlier</option>
              <option value={10}>10 moves earlier</option>
            </select>
          </label>
          <label className="inline">
            Kind
            <select value={kind} onChange={(e) => setKind(e.target.value as typeof kind)}>
              <option value="all">Both</option>
              <option value="bug">Bugs</option>
              <option value="feature">Feature requests</option>
            </select>
          </label>
          <label className="inline">
            Show
            <select value={show} onChange={(e) => setShow(e.target.value as typeof show)}>
              <option value="open">Open</option>
              <option value="all">All</option>
            </select>
          </label>
        </div>
      </div>
      <p className="muted">Recreate makes a new game you can play, from the report's setup and moves, and seats you
        where the reporter sat. The original game is not touched. Download gives the file
        for <code>scripts/replay_bug.py</code>.</p>
      {error && <p className="error">{error.message}</p>}
      {shown.length === 0 ? <p className="muted">Nothing to show.</p> : (
        <table className="admin-table bug-table">
          <thead>
            <tr><th>Reported</th><th>Kind</th><th>By</th><th>Game</th><th>What they said</th><th /></tr>
          </thead>
          <tbody>
            {shown.map((b) => (
              <tr key={b.id} className={b.status === "resolved" ? "resolved" : undefined}>
                <td>{when(b.created_at)}</td>
                <td>{b.kind === "feature" ? <span className="pill feature-pill">Feature</span> : <span className="pill">Bug</span>}</td>
                <td>{b.reporter}</td>
                <td>
                  {MODE_LABELS[b.mode] ?? b.mode}{b.bot && ` (${b.bot} Bot)`}<br />
                  <span className="muted">{b.players.join(", ")} · turn {b.turn + 1}, {b.step} · {b.moves} moves</span>
                </td>
                <td className="bug-text">{b.description}</td>
                <td className="admin-actions">
                  <button className="secondary" disabled={recreate.isPending}
                    onClick={() => recreate.mutate({ bug: b, back })}>Recreate</button>{" "}
                  {/* The server writes the file: passing it through JavaScript would round the game's seed. */}
                  <a className="button secondary" href={`/api/admin/bugs/${b.id}/download`} download>Download</a>{" "}
                  <button className="secondary" disabled={setStatus.isPending} onClick={() => setStatus.mutate(b)}>
                    {b.status === "open" ? "Resolve" : "Reopen"}
                  </button>{" "}
                  <ConfirmDelete what="this report" busy={remove.isPending} onDelete={() => remove.mutate(b.id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

/** Take over a seat in a real game (REQ-ADMIN-06). Asks first: the player is locked out of their seat. */
function TakeSeat({ game }: { game: AdminGame }) {
  const navigate = useNavigate();
  const [asking, setAsking] = useState<number | null>(null);
  const take = useMutation({
    mutationFn: (seat: number) => adminApi.takeSeat(game.id, seat),
    onSuccess: (grant) => navigate(`/games/${grant.game_id}`),
  });
  if (game.players.length === 0) return null;
  if (asking === null) {
    return (
      <span className="row take-seat">
        {game.players.map((name, seat) => (
          <button key={seat} className="secondary" onClick={() => setAsking(seat)} title={`Play as ${name} from now on`}>
            Take {game.players.length > 1 ? name : "seat"}
          </button>
        ))}
      </span>
    );
  }
  return (
    <span className="row confirm-delete">
      <span>Take over {game.players[asking]}&apos;s seat? They are locked out of it and cannot get back in.</span>
      <button className="secondary" onClick={() => setAsking(null)} disabled={take.isPending}>Cancel</button>
      <button className="danger" onClick={() => take.mutate(asking)} disabled={take.isPending}>Take seat</button>
      {take.error && <span className="error">{take.error.message}</span>}
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
                  <TakeSeat game={g} />{" "}
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

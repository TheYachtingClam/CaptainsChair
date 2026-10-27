import { FormEvent, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAccount } from "../account";
import { api } from "../api";

/** Your account: display name and password (requirements/19-technical-architecture.md §5, REQ-USER-01, -14). */
export function AccountPage() {
  const account = useAccount();
  if (!account) return <main className="page">Loading…</main>;
  return (
    <main className="page stack">
      <div className="row between">
        <h1>Your account</h1>
        <Link to="/">Lobby</Link>
      </div>
      <p className="muted">Signed in as {account.email}.</p>
      <ChangeName current={account.display_name} />
      <Notifications on={account.turn_emails} />
      <ChangePassword />
    </main>
  );
}

function ChangeName({ current }: { current: string }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState(current);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  useEffect(() => setName(current), [current]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      queryClient.setQueryData(["me"], await api.rename(name.trim()));
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not change the name");
    } finally {
      setBusy(false);
    }
  }

  const trimmed = name.trim();
  return (
    <form className="card stack" onSubmit={submit}>
      <h2>Display name</h2>
      <label>
        The name other players see (games already started keep the old one)
        <input maxLength={40} value={name} onChange={(e) => { setName(e.target.value); setSaved(false); }} />
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      {saved && <p role="status">Saved.</p>}
      <div className="row">
        <button type="submit" disabled={busy || !trimmed || trimmed === current}>Save name</button>
      </div>
    </form>
  );
}

/** Whether to get an email when a two-player game is waiting for you (REQ-USER-25). Saved as soon as it changes. */
function Notifications({ on }: { on: boolean }) {
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function change(next: boolean) {
    setBusy(true);
    setError(null);
    try {
      queryClient.setQueryData(["me"], await api.setTurnEmails(next));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save the setting");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card stack">
      <h2>Emails</h2>
      <label className="inline">
        <input type="checkbox" checked={on} disabled={busy} onChange={(e) => change(e.target.checked)} />
        Email me when a two-player game is waiting for me
      </label>
      <p className="muted">
        When it becomes your turn, or the other player's move needs a decision from you (a Reaction, an attack, a
        choice they force on you), and you don't have the game open. One email until you make a move.
      </p>
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}

function ChangePassword() {
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [again, setAgain] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setSaved(false);
    if (password !== again) return setError("The two new passwords are not the same.");
    setBusy(true);
    setError(null);
    try {
      await api.changePassword(current, password);
      setCurrent("");
      setPassword("");
      setAgain("");
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not change the password");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <h2>Password</h2>
      <p className="muted">Changing it signs you out on every other browser and device, and emails you a notice.</p>
      <label>
        Current password
        <input type="password" autoComplete="current-password" value={current} onChange={(e) => setCurrent(e.target.value)} />
      </label>
      <label>
        New password (at least 8 characters)
        <input type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      <label>
        New password again
        <input type="password" autoComplete="new-password" value={again} onChange={(e) => setAgain(e.target.value)} />
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      {saved && <p role="status">Password changed.</p>}
      <div className="row">
        <button type="submit" disabled={busy || !current || password.length < 8 || !again}>Change password</button>
      </div>
    </form>
  );
}

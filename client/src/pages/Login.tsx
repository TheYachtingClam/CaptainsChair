import { FormEvent, useState } from "react";
import { api } from "../api";

/** Sign in with an account (REQ-USER-10). */
export function Login({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [forgot, setForgot] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.login(email.trim(), password);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function sendReset() {
    setError(null);
    try {
      setForgot((await api.forgot(email.trim())).detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send the link");
    }
  }

  return (
    <main className="page center">
      <form className="card login stack" onSubmit={submit}>
        <h1>Captain's Chair</h1>
        <label>
          Email
          <input type="email" autoComplete="username" autoFocus value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        {forgot && <p role="status">{forgot}</p>}
        <button type="submit" disabled={busy || !password || !email.trim()}>Sign in</button>
        <button type="button" className="link" disabled={!email.trim()} onClick={sendReset}
          title={email.trim() ? undefined : "Type your email address first"}>Forgot password?</button>
      </form>
    </main>
  );
}

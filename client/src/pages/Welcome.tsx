import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

function useCode() {
  return new URLSearchParams(window.location.search).get("code") ?? "";
}

function done() {
  window.location.replace("/"); // start the app afresh, signed in
}

/** Create an account from an invitation link (REQ-USER-02). Reached without being signed in. */
export function SignUp() {
  const code = useCode();
  const invitation = useQuery({ queryKey: ["invitation", code], queryFn: () => api.invitation(code), enabled: !!code });
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [again, setAgain] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (password !== again) return setError("The two passwords are not the same.");
    setBusy(true);
    setError(null);
    try {
      await api.signUp(code, name.trim(), password);
      done();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-up failed");
      setBusy(false);
    }
  }

  return (
    <main className="page center">
      <form className="card login stack" onSubmit={submit}>
        <h1>Create your account</h1>
        {!code || invitation.isError ? (
          <p className="error" role="alert">This invitation has expired or was already used. Ask the admin for a new one.</p>
        ) : (
          <>
            <label>
              Email
              <input type="email" value={invitation.data?.email ?? ""} readOnly />
            </label>
            <label>
              Display name (what other players see)
              <input autoFocus maxLength={40} value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label>
              Password (at least 8 characters)
              <input type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            <label>
              Password again
              <input type="password" autoComplete="new-password" value={again} onChange={(e) => setAgain(e.target.value)} />
            </label>
            {error && <p className="error" role="alert">{error}</p>}
            <button type="submit" disabled={busy || !invitation.data || !name.trim() || password.length < 8 || !again}>
              Create account
            </button>
          </>
        )}
        <a href="/">Already have an account? Sign in</a>
      </form>
    </main>
  );
}

/** Choose a new password from a reset link (REQ-USER-21). Reached without being signed in. */
export function ResetPassword() {
  const code = useCode();
  const [password, setPassword] = useState("");
  const [again, setAgain] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (password !== again) return setError("The two passwords are not the same.");
    setBusy(true);
    setError(null);
    try {
      await api.resetPassword(code, password);
      done();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not set the password");
      setBusy(false);
    }
  }

  return (
    <main className="page center">
      <form className="card login stack" onSubmit={submit}>
        <h1>Choose a new password</h1>
        <label>
          New password (at least 8 characters)
          <input type="password" autoFocus autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <label>
          New password again
          <input type="password" autoComplete="new-password" value={again} onChange={(e) => setAgain(e.target.value)} />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button type="submit" disabled={busy || !code || password.length < 8 || !again}>Set password</button>
        <a href="/">Back to sign in</a>
      </form>
    </main>
  );
}

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Route, Routes, useNavigate } from "react-router-dom";
import { AuthError, api } from "./api";
import { Login } from "./pages/Login";
import { Lobby } from "./pages/Lobby";
import { NewGame } from "./pages/NewGame";
import { GameTable } from "./pages/GameTable";

export function App() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const session = useQuery({ queryKey: ["session"], queryFn: api.checkSession });

  if (session.isPending) return <main className="page center">Connecting…</main>;
  // Without a valid session only the password page is shown (REQ-AUTH-02).
  if (session.isError && session.error instanceof AuthError) {
    return <Login onSuccess={() => queryClient.invalidateQueries()} />;
  }
  if (session.isError) {
    return (
      <main className="page center">
        <div className="card stack">
          <p className="error" role="alert">Can't reach the server: {session.error.message}</p>
          <button onClick={() => session.refetch()}>Try again</button>
        </div>
      </main>
    );
  }

  async function logout() {
    await api.logout();
    navigate("/");
    // Drop every cached server response except the session check, then reset the
    // session check so it asks the server again, gets 401 and shows the password page.
    queryClient.removeQueries({ predicate: (q) => q.queryKey[0] !== "session" });
    await queryClient.resetQueries({ queryKey: ["session"] });
  }

  return (
    <>
      <header className="topbar">
        <Link to="/" className="brand">Captain's Chair</Link>
        <button className="link" onClick={logout}>Sign out</button>
      </header>
      <Routes>
        <Route path="/" element={<Lobby />} />
        <Route path="/new" element={<NewGame />} />
        <Route path="/games/:gameId" element={<GameTable />} />
        <Route path="*" element={<main className="page">Page not found. <Link to="/">Back to lobby</Link></main>} />
      </Routes>
    </>
  );
}

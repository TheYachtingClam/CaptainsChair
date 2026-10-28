import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Route, Routes, useNavigate } from "react-router-dom";
import { AuthError, api } from "./api";
import { Login } from "./pages/Login";
import { Lobby } from "./pages/Lobby";
import { NewGame } from "./pages/NewGame";
import { GameTable } from "./pages/GameTable";
import { Admin } from "./pages/Admin";
import { Observe } from "./pages/Observe";
import { Campaign } from "./pages/Campaign";
import { NewCampaign } from "./pages/NewCampaign";
import { AccountPage } from "./pages/Account";
import { ResetPassword, SignUp } from "./pages/Welcome";

export function App() {
  // Links from emails work without being signed in (REQ-USER-02, -21).
  if (window.location.pathname === "/signup") return <SignUp />;
  if (window.location.pathname === "/reset") return <ResetPassword />;
  return <SignedInApp />;
}

function SignedInApp() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const session = useQuery({ queryKey: ["session"], queryFn: api.checkSession });
  const account = useQuery({ queryKey: ["me"], queryFn: api.me, enabled: session.isSuccess });

  if (session.isPending) return <main className="page center">Connecting…</main>;
  // Without a valid session only the sign-in page is shown (REQ-USER-03).
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
        <span className="row">
          {account.data && <Link to="/account" title="Your account">{account.data.display_name}</Link>}
          {account.data?.is_admin && <Link to="/admin">Admin</Link>}
          <button className="link" onClick={logout}>Sign out</button>
        </span>
      </header>
      <Routes>
        <Route path="/" element={<Lobby />} />
        <Route path="/new" element={<NewGame />} />
        <Route path="/games/:gameId" element={<GameTable />} />
        <Route path="/campaigns/new" element={<NewCampaign />} />
        <Route path="/campaigns/:campaignId" element={<Campaign />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/games/:gameId/observe" element={<Observe />} />
        <Route path="/account" element={<AccountPage />} />
        <Route path="*" element={<main className="page">Page not found. <Link to="/">Back to lobby</Link></main>} />
      </Routes>
    </>
  );
}

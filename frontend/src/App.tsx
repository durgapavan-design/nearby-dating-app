import { Navigate, Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import { useAuth } from "./context/AuthContext";
import Chat from "./pages/Chat";
import Discover from "./pages/Discover";
import Login from "./pages/Login";
import Matches from "./pages/Matches";
import Profile from "./pages/Profile";
import ProfileSetup from "./pages/ProfileSetup";
import VerifyOtp from "./pages/VerifyOtp";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="centered">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function RequireCompleteProfile({ children }: { children: JSX.Element }) {
  const { me } = useAuth();
  if (me && !me.profile_completed) return <Navigate to="/profile-setup" replace />;
  return children;
}

export default function App() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <div className="app-shell">
      {isAuthenticated && <NavBar />}
      <main className="app-main">
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/discover" replace /> : <Login />} />
          <Route path="/verify" element={<VerifyOtp />} />
          <Route
            path="/profile-setup"
            element={
              <RequireAuth>
                <ProfileSetup />
              </RequireAuth>
            }
          />
          <Route
            path="/discover"
            element={
              <RequireAuth>
                <RequireCompleteProfile>
                  <Discover />
                </RequireCompleteProfile>
              </RequireAuth>
            }
          />
          <Route
            path="/matches"
            element={
              <RequireAuth>
                <RequireCompleteProfile>
                  <Matches />
                </RequireCompleteProfile>
              </RequireAuth>
            }
          />
          <Route
            path="/chat/:matchId"
            element={
              <RequireAuth>
                <RequireCompleteProfile>
                  <Chat />
                </RequireCompleteProfile>
              </RequireAuth>
            }
          />
          <Route
            path="/profile"
            element={
              <RequireAuth>
                <Profile />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to={loading ? "/login" : isAuthenticated ? "/discover" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}

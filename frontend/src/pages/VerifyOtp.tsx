import { FormEvent, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface LocationState {
  phone?: string;
  debugCode?: string | null;
}

export default function VerifyOtp() {
  const location = useLocation();
  const state = (location.state || {}) as LocationState;
  const [phone] = useState(state.phone || "");
  const [code, setCode] = useState(state.debugCode || "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  if (!phone) {
    navigate("/login", { replace: true });
    return null;
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.verifyOtp(phone, code);
      await login(res.access_token);
      navigate(res.profile_completed ? "/discover" : "/profile-setup", { replace: true });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="centered">
      <form className="card" onSubmit={submit}>
        <h1>Verify code</h1>
        <p className="subtitle">Sent to {phone}</p>
        {state.debugCode && <p className="hint">Dev mode: code pre-filled ({state.debugCode})</p>}
        <input
          type="text"
          placeholder="123456"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Verifying..." : "Verify"}
        </button>
      </form>
    </div>
  );
}

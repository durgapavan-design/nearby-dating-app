import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, DiscoveryProfile } from "../api/client";
import SwipeCard from "../components/SwipeCard";

export default function Discover() {
  const [feed, setFeed] = useState<DiscoveryProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [matchName, setMatchName] = useState<string | null>(null);
  const navigate = useNavigate();

  const loadFeed = () => {
    setLoading(true);
    api
      .getFeed()
      .then(setFeed)
      .finally(() => setLoading(false));
  };

  useEffect(loadFeed, []);

  const current = feed[0];

  const act = async (action: "like" | "pass") => {
    if (!current) return;
    setFeed((prev) => prev.slice(1));
    const result = await api.swipe(current.id, action);
    if (result.matched) {
      setMatchName(current.name);
    }
  };

  if (loading) return <div className="centered">Loading...</div>;

  return (
    <div className="page discover-page">
      {matchName && (
        <div className="match-modal" onClick={() => setMatchName(null)}>
          <div className="match-modal-content">
            <h2>It's a match!</h2>
            <p>You and {matchName} liked each other.</p>
            <button onClick={() => navigate("/matches")}>Go to matches</button>
            <button className="secondary" onClick={() => setMatchName(null)}>
              Keep browsing
            </button>
          </div>
        </div>
      )}

      {current ? (
        <>
          <SwipeCard profile={current} />
          <div className="swipe-actions">
            <button className="pass-btn" onClick={() => act("pass")}>
              Pass
            </button>
            <button className="like-btn" onClick={() => act("like")}>
              Like
            </button>
          </div>
        </>
      ) : (
        <div className="centered">
          <p>No more profiles nearby right now.</p>
          <button onClick={loadFeed}>Refresh</button>
        </div>
      )}
    </div>
  );
}

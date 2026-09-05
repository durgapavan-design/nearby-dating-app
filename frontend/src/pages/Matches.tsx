import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, LikedMe, MatchSummary, mediaUrl } from "../api/client";

export default function Matches() {
  const [tab, setTab] = useState<"matches" | "liked">("matches");
  const [matches, setMatches] = useState<MatchSummary[]>([]);
  const [likedMe, setLikedMe] = useState<LikedMe[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.listMatches().then(setMatches);
    api.listLikedMe().then(setLikedMe);
  }, []);

  return (
    <div className="page">
      <div className="tab-row">
        <button className={tab === "matches" ? "tab-active" : ""} onClick={() => setTab("matches")}>
          Matches ({matches.length})
        </button>
        <button className={tab === "liked" ? "tab-active" : ""} onClick={() => setTab("liked")}>
          Liked you ({likedMe.length})
        </button>
      </div>

      {tab === "matches" && (
        <div className="list">
          {matches.length === 0 && <p className="empty">No matches yet — keep swiping!</p>}
          {matches.map((m) => (
            <button key={m.match_id} className="list-row" onClick={() => navigate(`/chat/${m.match_id}`)}>
              {m.primary_photo ? (
                <img src={mediaUrl(m.primary_photo.url)} alt="" className="avatar" />
              ) : (
                <div className="avatar avatar-placeholder" />
              )}
              <div className="list-row-text">
                <strong>{m.name}</strong>
                <span>{m.last_message || "Say hi!"}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {tab === "liked" && (
        <div className="list">
          {likedMe.length === 0 && <p className="empty">No one has liked you yet.</p>}
          {likedMe.map((l) => (
            <div key={l.user_id} className="list-row">
              {l.primary_photo ? (
                <img src={mediaUrl(l.primary_photo.url)} alt="" className="avatar" />
              ) : (
                <div className="avatar avatar-placeholder" />
              )}
              <div className="list-row-text">
                <strong>{l.name}</strong>
                <span>Liked you — swipe in Discover to match back</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

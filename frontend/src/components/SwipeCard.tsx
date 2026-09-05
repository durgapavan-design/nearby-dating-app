import { DiscoveryProfile, mediaUrl } from "../api/client";

interface Props {
  profile: DiscoveryProfile;
}

export default function SwipeCard({ profile }: Props) {
  const photo = profile.photos[0];

  return (
    <div className="swipe-card">
      <div className="swipe-card-photo">
        {photo ? <img src={mediaUrl(photo.url)} alt={profile.name || ""} /> : <div className="no-photo">No photo</div>}
      </div>
      <div className="swipe-card-info">
        <h2>
          {profile.name}
          {profile.age !== null && <span className="age">, {profile.age}</span>}
        </h2>
        {profile.city && <p className="city">{profile.city}</p>}
        {profile.bio && <p className="bio">{profile.bio}</p>}
        {profile.shared_interest_count > 0 && (
          <p className="shared">{profile.shared_interest_count} shared interest{profile.shared_interest_count > 1 ? "s" : ""}</p>
        )}
        <div className="tag-row">
          {profile.interests.map((i) => (
            <span key={i.id} className="tag">
              {i.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

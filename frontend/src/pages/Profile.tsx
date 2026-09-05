import { FormEvent, useEffect, useState } from "react";
import { api, Photo } from "../api/client";
import InterestPicker from "../components/InterestPicker";
import PhotoUploader from "../components/PhotoUploader";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { me, refreshMe, logout } = useAuth();
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [city, setCity] = useState("");
  const [cities, setCities] = useState<string[]>([]);
  const [interestIds, setInterestIds] = useState<string[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.listCities().then(setCities);
    if (me) {
      setName(me.name || "");
      setBio(me.bio || "");
      setCity(me.city || "");
      setInterestIds(me.interests.map((i) => i.id));
      setPhotos(me.photos);
    }
  }, [me]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSaved(false);
    await api.updateMe({ name, bio, city });
    await api.updateMyInterests(interestIds);
    await refreshMe();
    setSaved(true);
  };

  return (
    <div className="page">
      <form className="card wide" onSubmit={submit}>
        <h1>Your profile</h1>

        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />

        <label>City</label>
        <select value={city} onChange={(e) => setCity(e.target.value)}>
          {cities.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <label>Bio</label>
        <textarea value={bio} onChange={(e) => setBio(e.target.value)} maxLength={500} rows={3} />

        <label>Photos</label>
        <PhotoUploader photos={photos} onChange={setPhotos} />

        <label>Interests</label>
        <InterestPicker selectedIds={interestIds} onChange={setInterestIds} />

        {saved && <p className="hint">Saved!</p>}
        <button type="submit">Save changes</button>
        <button type="button" className="secondary" onClick={logout}>
          Log out
        </button>
      </form>
    </div>
  );
}

import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Photo } from "../api/client";
import InterestPicker from "../components/InterestPicker";
import PhotoUploader from "../components/PhotoUploader";
import { useAuth } from "../context/AuthContext";

export default function ProfileSetup() {
  const { me, refreshMe } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [gender, setGender] = useState("male");
  const [showMe, setShowMe] = useState("everyone");
  const [bio, setBio] = useState("");
  const [city, setCity] = useState("");
  const [cities, setCities] = useState<string[]>([]);
  const [interestIds, setInterestIds] = useState<string[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.listCities().then((list) => {
      setCities(list);
      setCity((prev) => prev || list[0] || "");
    });
    if (me) {
      setName(me.name || "");
      setBirthdate(me.birthdate || "");
      setGender(me.gender || "male");
      setShowMe(me.show_me || "everyone");
      setBio(me.bio || "");
      setCity(me.city || "");
      setInterestIds(me.interests.map((i) => i.id));
      setPhotos(me.photos);
    }
  }, [me]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (photos.length === 0) {
      setError("Add at least one photo");
      return;
    }
    setLoading(true);
    try {
      await api.updateMe({ name, birthdate, gender, show_me: showMe, bio, city });
      await api.updateMyInterests(interestIds);
      await refreshMe();
      navigate("/discover", { replace: true });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <form className="card wide" onSubmit={submit}>
        <h1>Set up your profile</h1>

        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />

        <label>Birthdate</label>
        <input type="date" value={birthdate} onChange={(e) => setBirthdate(e.target.value)} required />

        <label>Gender</label>
        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="non_binary">Non-binary</option>
          <option value="other">Other</option>
        </select>

        <label>Show me</label>
        <select value={showMe} onChange={(e) => setShowMe(e.target.value)}>
          <option value="male">Men</option>
          <option value="female">Women</option>
          <option value="everyone">Everyone</option>
        </select>

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

        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save and continue"}
        </button>
      </form>
    </div>
  );
}

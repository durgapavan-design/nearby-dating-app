import { useRef, useState } from "react";
import { api, mediaUrl, Photo } from "../api/client";

interface Props {
  photos: Photo[];
  onChange: (photos: Photo[]) => void;
}

export default function PhotoUploader({ photos, onChange }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setUploading(true);
    try {
      const photo = await api.uploadPhoto(file);
      onChange([...photos, photo]);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (photoId: string) => {
    await api.deletePhoto(photoId);
    onChange(photos.filter((p) => p.id !== photoId));
  };

  return (
    <div className="photo-uploader">
      <div className="photo-grid">
        {photos.map((photo) => (
          <div key={photo.id} className="photo-thumb">
            <img src={mediaUrl(photo.url)} alt="" />
            <button type="button" className="photo-remove" onClick={() => handleDelete(photo.id)}>
              ×
            </button>
          </div>
        ))}
        {photos.length < 6 && (
          <button type="button" className="photo-add" onClick={() => fileInput.current?.click()} disabled={uploading}>
            {uploading ? "..." : "+ Add"}
          </button>
        )}
      </div>
      <input
        ref={fileInput}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
          e.target.value = "";
        }}
      />
      {error && <p className="error">{error}</p>}
    </div>
  );
}

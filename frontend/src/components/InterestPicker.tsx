import { useEffect, useState } from "react";
import { api, Interest } from "../api/client";

interface Props {
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}

export default function InterestPicker({ selectedIds, onChange }: Props) {
  const [interests, setInterests] = useState<Interest[]>([]);

  useEffect(() => {
    api.listInterests().then(setInterests);
  }, []);

  const toggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((i) => i !== id));
    } else {
      onChange([...selectedIds, id]);
    }
  };

  const byCategory = interests.reduce<Record<string, Interest[]>>((acc, interest) => {
    (acc[interest.category] ??= []).push(interest);
    return acc;
  }, {});

  return (
    <div className="interest-picker">
      {Object.entries(byCategory).map(([category, items]) => (
        <div key={category} className="interest-category">
          <p className="interest-category-label">{category}</p>
          <div className="tag-row">
            {items.map((interest) => (
              <button
                type="button"
                key={interest.id}
                className={`tag ${selectedIds.includes(interest.id) ? "tag-selected" : ""}`}
                onClick={() => toggle(interest.id)}
              >
                {interest.name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

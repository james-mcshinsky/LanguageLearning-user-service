import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api';

interface Props {
  userId: number;
  onBack: () => void;
}

interface Counts {
  unknown: number;
  learning: number;
  mastered: number;
}

export default function ProfilePage({ userId, onBack }: Props) {
  const [total, setTotal] = useState(0);
  const [counts, setCounts] = useState<Counts>({ unknown: 0, learning: 0, mastered: 0 });

  useEffect(() => {
    apiFetch(`/api/user/words?user_id=${userId}`)
      .then(res => res.json())
      .then(data => {
        const c = { unknown: 0, learning: 0, mastered: 0 } as Counts;
        data.forEach((w: any) => {
          if (c[w.mastery_level] !== undefined) c[w.mastery_level] += 1;
        });
        setTotal(data.length);
        setCounts(c);
      });
  }, [userId]);

  return (
    <div>
      <h1>Profile</h1>
      <p>Known words: {total}</p>
      <div>
        <div>unknown: {counts.unknown}</div>
        <div>learning: {counts.learning}</div>
        <div>mastered: {counts.mastered}</div>
      </div>
      <button onClick={onBack}>Back</button>
    </div>
  );
}

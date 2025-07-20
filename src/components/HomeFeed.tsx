import React, { useEffect, useState } from 'react';
import { apiFetch } from '../api';

interface Video {
  id: number;
  title: string;
  thumbnail_url: string;
  new_word_count: number;
}

interface Props {
  userId: number;
  onSelectVideo: (id: number) => void;
  onShowProfile: () => void;
}

export default function HomeFeed({ userId, onSelectVideo, onShowProfile }: Props) {
  const [videos, setVideos] = useState<Video[]>([]);

  useEffect(() => {
    apiFetch(`/api/videos/recommendations?user_id=${userId}&limit=8`)
      .then(res => res.json())
      .then(setVideos);
  }, [userId]);

  return (
    <div>
      <h1>Video Library</h1>
      <div>
        {videos.map(v => (
          <div key={v.id} data-testid="video" onClick={() => onSelectVideo(v.id)}>
            <img src={v.thumbnail_url} alt={v.title} />
            <span>{v.title}</span>
            <span>{v.new_word_count}</span>
          </div>
        ))}
      </div>
      <button onClick={onShowProfile}>Profile</button>
    </div>
  );
}

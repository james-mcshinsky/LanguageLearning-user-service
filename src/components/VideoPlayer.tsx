import React, { useEffect, useRef } from 'react';
import TranscriptPanel from './TranscriptPanel';

interface Props {
  videoId: number;
  userId: number;
  onDone: () => void;
}

declare global {
  interface Window { YT: any; onYouTubeIframeAPIReady: any; }
}

export default function VideoPlayer({ videoId, userId, onDone }: Props) {
  const playerRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.body.appendChild(tag);
    window.onYouTubeIframeAPIReady = () => {
      playerRef.current = new window.YT.Player(containerRef.current, {
        videoId,
        events: {
          onStateChange: (e: any) => {
            if (e.data === window.YT.PlayerState.ENDED) onDone();
          }
        }
      });
    };
  }, [videoId, onDone]);

  return (
    <div>
      <div id="player" ref={containerRef}></div>
      {playerRef.current && (
        <TranscriptPanel videoId={videoId} userId={userId} player={playerRef.current} onWordUpdated={() => {}} />
      )}
    </div>
  );
}

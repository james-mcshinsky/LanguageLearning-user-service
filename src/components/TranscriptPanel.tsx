import React, { useEffect, useRef, useState } from 'react';
import { apiFetch } from '../api';

interface Token {
  word_id: number;
  text: string;
  start_sec: number;
  end_sec: number;
}

interface Line {
  start_sec: number;
  end_sec: number;
}

interface Props {
  videoId: number;
  userId: number;
  player: any;
  onWordUpdated: () => void;
}

export default function TranscriptPanel({ videoId, userId, player, onWordUpdated }: Props) {
  const [lines, setLines] = useState<Line[]>([]);
  const [tokens, setTokens] = useState<Token[]>([]);
  const [lineTokens, setLineTokens] = useState<Token[][]>([]);
  const [knownWords, setKnownWords] = useState<Set<number>>(new Set());
  const [active, setActive] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    Promise.all([
      apiFetch(`/api/videos/${videoId}/transcript`).then(r => r.json()),
      apiFetch(`/api/videos/${videoId}/tokens`).then(r => r.json()),
      apiFetch(`/api/user/words?user_id=${userId}`).then(r => r.json())
    ]).then(([l, t, w]) => {
      setLines(l);
      setTokens(t);
      const grouped: Token[][] = l.map(() => []);
      let idx = 0;
      for (const tok of t) {
        while (
          idx < l.length &&
          tok.start_sec >= l[idx].end_sec
        ) {
          idx += 1;
        }
        if (idx < l.length && tok.end_sec <= l[idx].end_sec) {
          grouped[idx].push(tok);
        }
      }
      setLineTokens(grouped);
      setKnownWords(new Set(w.map((x: any) => x.word_id)));
    });
  }, [videoId, userId]);

  useEffect(() => {
    if (!player) return;
    const interval = setInterval(() => {
      const current = player.getCurrentTime ? player.getCurrentTime() : 0;
      const idx = lines.findIndex(l => current >= l.start_sec && current < l.end_sec);
      setActive(idx);
    }, 500);
    return () => clearInterval(interval);
  }, [player, lines]);

  const updateWord = async (wordId: number) => {
    await apiFetch(`/api/user/words/${wordId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, mastery_level: 'learning' })
    });
    setKnownWords(new Set([...knownWords, wordId]));
    onWordUpdated();
  };

  return (
    <div ref={containerRef}>
      {lines.map((l, i) => (
        <div key={i} className={i === active ? 'active' : ''}>
          {lineTokens[i]?.map(t => (
            <span
              key={t.word_id}
              className={knownWords.has(t.word_id) ? 'known' : 'unknown'}
              onClick={() => updateWord(t.word_id)}
            >
              {t.text}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}

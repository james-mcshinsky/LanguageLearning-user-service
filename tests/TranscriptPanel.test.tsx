import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import TranscriptPanel from '../src/components/TranscriptPanel';

const fetchMock = jest.fn();

global.fetch = fetchMock as any;

describe('TranscriptPanel', () => {
  test('fetches transcript and marks known words', async () => {
    fetchMock
      .mockResolvedValueOnce({ json: () => Promise.resolve([{ start_sec: 0, end_sec: 2 }]) })
      .mockResolvedValueOnce({ json: () => Promise.resolve([{ word_id: 1, text: 'Hi', start_sec: 0, end_sec: 2 }]) })
      .mockResolvedValueOnce({ json: () => Promise.resolve([{ word_id: 1 }]) });

    render(<TranscriptPanel videoId={1} userId={1} player={null} onWordUpdated={jest.fn()} />);

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    const span = await screen.findByText('Hi');
    expect(span.className).toBe('known');
  });
});

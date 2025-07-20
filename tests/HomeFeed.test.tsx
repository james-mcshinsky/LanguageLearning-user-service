import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import HomeFeed from '../src/components/HomeFeed';

global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve([
      { id: 1, title: 'A', thumbnail_url: 't1', new_word_count: 2 },
      { id: 2, title: 'B', thumbnail_url: 't2', new_word_count: 1 }
    ])
  })
) as jest.Mock;

describe('HomeFeed', () => {
  test('fetches and renders videos', async () => {
    render(<HomeFeed userId={1} onSelectVideo={jest.fn()} onShowProfile={jest.fn()} />);
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    const vids = await screen.findAllByTestId('video');
    expect(vids).toHaveLength(2);
  });
});

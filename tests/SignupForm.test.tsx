(window as any).API_BASE = 'http://example.com';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SignupForm from '../src/components/SignupForm';

describe('SignupForm', () => {
  test('submits signup and handles success', async () => {
    const fetchMock = jest.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ user_id: 3 }) })
    );
    global.fetch = fetchMock as any;
    const onSuccess = jest.fn();
    render(<SignupForm onSuccess={onSuccess} />);
    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'u' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'p' } });
    fireEvent.click(screen.getByText('Create Account'));
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(fetchMock).toHaveBeenCalledWith(
      'http://example.com/signup',
      expect.objectContaining({ method: 'POST' })
    );
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(3));
  });
});

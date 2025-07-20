import React, { useState } from 'react';
import { apiFetch } from '../api';

interface Props {
  onSuccess: (userId: number) => void;
}

export default function SignupForm({ onSuccess }: Props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const signup = async () => {
    try {
      const res = await apiFetch(`/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) throw new Error('Signup failed');
      const data = await res.json();
      onSuccess(data.user_id);
    } catch (err) {
      setError('Signup failed');
    }
  };

  return (
    <div className="page">
      <div className="login-container">
        <h1 className="login-title">Sign Up</h1>
        <div className="login-form">
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
          <button onClick={signup}>Create Account</button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

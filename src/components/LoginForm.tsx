import React, { useState } from 'react';
import { apiFetch } from '../api';

interface Props {
  onSuccess: (userId: number) => void;
  onShowSignup: () => void;
}

export default function LoginForm({ onSuccess, onShowSignup }: Props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const login = async () => {
    try {
      const res = await apiFetch(`/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json();
      onSuccess(data.user_id);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="page">
      <div className="login-container">
        <h1 className="login-title">Sign In</h1>
        <div className="login-form">
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
          <button onClick={login}>Log In</button>
          <button onClick={onShowSignup}>Create account</button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

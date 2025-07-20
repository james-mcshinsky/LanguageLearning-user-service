import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import HomeFeed from './components/HomeFeed';
import ProfilePage from './components/ProfilePage';
import VideoPlayer from './components/VideoPlayer';

export default function App() {
  const [page, setPage] = useState<'login' | 'signup' | 'home' | 'profile' | 'player'>('login');
  const [videoId, setVideoId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const handleLogin = (id: number) => {
    setUserId(id);
    setPage('home');
  };

  return (
    <div>
      {page === 'login' && (
        <LoginForm onSuccess={handleLogin} onShowSignup={() => setPage('signup')} />
      )}
      {page === 'signup' && <SignupForm onSuccess={handleLogin} />}
      {page === 'home' && userId && (
        <HomeFeed userId={userId} onSelectVideo={(id) => { setVideoId(id); setPage('player'); }} onShowProfile={() => setPage('profile')} />
      )}
      {page === 'profile' && userId && (
        <ProfilePage userId={userId} onBack={() => setPage('home')} />
      )}
      {page === 'player' && userId && videoId !== null && (
        <VideoPlayer videoId={videoId} userId={userId} onDone={() => setPage('home')} />
      )}
    </div>
  );
}

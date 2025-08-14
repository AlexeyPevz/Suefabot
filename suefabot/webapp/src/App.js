import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useTelegram } from './hooks/useTelegram';
import api, { setupApiAuth } from './utils/api';

// Pages
import HomePage from './pages/HomePage';
import PlayPage from './pages/PlayPage';
import MatchPage from './pages/MatchPage';
import ProfilePage from './pages/ProfilePage';
import ShopPage from './pages/ShopPage';

function App() {
  const { tg, user } = useTelegram();
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Настройка Telegram WebApp
    tg.ready();
    tg.expand();
    tg.setHeaderColor('bg_color');
    tg.enableClosingConfirmation();

    // Выполнить аутентификацию через backend, получить JWT
    const init = async () => {
      try {
        const initData = tg?.initData || '';
        if (initData) {
          const res = await api.post('/api/auth/telegram', { initData });
          if (res?.data?.token) {
            setToken(res.data.token);
            setupApiAuth({ token: res.data.token, user: tg?.initDataUnsafe?.user, initData });
          } else {
            setupApiAuth({ token: null, user: tg?.initDataUnsafe?.user, initData });
          }
        } else {
          // Dev режим без initData
          setupApiAuth({ token: null, user: tg?.initDataUnsafe?.user, initData: null });
        }
      } catch (_) {
        // В dev режиме продолжаем без токена
        setupApiAuth({ token: null, user: tg?.initDataUnsafe?.user, initData: tg?.initData });
      }
    };

    init();
  }, [tg]);

  return (
    <Router>
      <div className="min-h-screen bg-telegram-bg">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/play" element={<PlayPage />} />
          <Route path="/play/:mode" element={<PlayPage />} />
          <Route path="/match/:matchId" element={<MatchPage authToken={token} />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: 'var(--tg-theme-secondary-bg-color)',
              color: 'var(--tg-theme-text-color)',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
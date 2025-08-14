import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useTelegram } from './hooks/useTelegram';

// Pages
import HomePage from './pages/HomePage';
import PlayPage from './pages/PlayPage';
import MatchPage from './pages/MatchPage';
import ProfilePage from './pages/ProfilePage';
import ShopPage from './pages/ShopPage';

function App() {
  const { tg, user } = useTelegram();

  useEffect(() => {
    // Настройка Telegram WebApp
    tg.ready();
    tg.expand();
    
    // Установка цвета заголовка
    tg.setHeaderColor('bg_color');
    
    // Включение кнопки закрытия
    tg.enableClosingConfirmation();
  }, [tg]);

  return (
    <Router>
      <div className="min-h-screen bg-telegram-bg">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/play" element={<PlayPage />} />
          <Route path="/play/:mode" element={<PlayPage />} />
          <Route path="/match/:matchId" element={<MatchPage />} />
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
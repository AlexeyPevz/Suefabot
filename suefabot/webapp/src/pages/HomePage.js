import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTelegram } from '../hooks/useTelegram';

const HomePage = () => {
  const navigate = useNavigate();
  const { user, hapticFeedback } = useTelegram();

  const handleNavigate = (path) => {
    hapticFeedback('impact', 'light');
    navigate(path);
  };

  return (
    <div className="flex flex-col min-h-screen p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl font-bold mb-2">
          <span className="text-gradient">Suefabot</span>
        </h1>
        <p className="text-telegram-hint text-lg">Решай споры красиво!</p>
        {user && (
          <p className="text-telegram-text mt-2">
            Привет, {user.first_name}! 👋
          </p>
        )}
      </motion.div>

      <div className="flex-1 flex flex-col gap-4 max-w-md mx-auto w-full">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          onClick={() => handleNavigate('/play')}
          className="btn-primary flex items-center justify-center gap-2 py-4 text-lg"
        >
          <span className="text-2xl">🎮</span>
          <span>Играть</span>
        </motion.button>

        <div className="grid grid-cols-2 gap-4">
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            onClick={() => handleNavigate('/profile')}
            className="btn-secondary flex flex-col items-center gap-1 py-4"
          >
            <span className="text-2xl">👤</span>
            <span>Профиль</span>
          </motion.button>

          <motion.button
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            onClick={() => handleNavigate('/shop')}
            className="btn-secondary flex flex-col items-center gap-1 py-4"
          >
            <span className="text-2xl">🛍</span>
            <span>Магазин</span>
          </motion.button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="btn-secondary flex flex-col items-center gap-1 py-4"
          >
            <span className="text-2xl">🏆</span>
            <span>Рейтинг</span>
          </motion.button>

          <motion.button
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="btn-secondary flex flex-col items-center gap-1 py-4"
          >
            <span className="text-2xl">📊</span>
            <span>Статистика</span>
          </motion.button>
        </div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="btn-secondary flex items-center justify-center gap-2"
        >
          <span className="text-xl">❓</span>
          <span>Помощь</span>
        </motion.button>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center text-telegram-hint text-sm mt-8"
      >
        <p>✊✌️✋</p>
        <p className="mt-1">Версия 1.0.0</p>
      </motion.div>
    </div>
  );
};

export default HomePage;
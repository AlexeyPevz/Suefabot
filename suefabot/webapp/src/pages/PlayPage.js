import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useTelegram } from '../hooks/useTelegram';
import { matchAPI } from '../utils/api';

const PlayPage = () => {
  const navigate = useNavigate();
  const { mode } = useParams();
  const { user, hapticFeedback, showBackButton, hideBackButton } = useTelegram();
  const [promise, setPromise] = useState('');
  const [stakeAmount, setStakeAmount] = useState(0);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [showBackButton, hideBackButton, navigate]);

  const createMatch = async () => {
    if (!user) {
      toast.error('Пользователь не авторизован');
      return;
    }

    setIsCreating(true);
    hapticFeedback('impact', 'medium');

    try {
      const matchData = await matchAPI.create(user, promise || null, stakeAmount);
      toast.success('Матч создан! Ожидаем соперника...');
      navigate(`/match/${matchData.match_id}`);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Ошибка создания матча');
      hapticFeedback('notification', 'error');
    } finally {
      setIsCreating(false);
    }
  };

  if (mode) {
    // Страница создания матча для конкретного режима
    return (
      <div className="flex flex-col min-h-screen p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-2xl font-bold text-center mb-2">
            {mode === 'casual' && '🎲 Обычный матч'}
            {mode === 'bet' && '🤝 Матч на спор'}
            {mode === 'stars' && '⭐ PvP на Stars'}
          </h1>
          <p className="text-telegram-hint text-center">
            {mode === 'casual' && 'Играйте просто для веселья'}
            {mode === 'bet' && 'Добавьте обещание для проигравшего'}
            {mode === 'stars' && 'Сыграйте на Telegram Stars'}
          </p>
        </motion.div>

        <div className="flex-1 flex flex-col gap-4 max-w-md mx-auto w-full">
          {mode === 'bet' && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <label className="block text-sm font-medium mb-2">
                Обещание проигравшего:
              </label>
              <input
                type="text"
                value={promise}
                onChange={(e) => setPromise(e.target.value)}
                placeholder="Например: помыть посуду"
                maxLength={100}
                className="w-full px-3 py-2 bg-telegram-bg rounded-lg border border-telegram-hint/20 focus:outline-none focus:border-telegram-button"
              />
              <p className="text-xs text-telegram-hint mt-1">
                {promise.length}/100 символов
              </p>
            </motion.div>
          )}

          {mode === 'stars' && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <label className="block text-sm font-medium mb-2">
                Ставка (Stars):
              </label>
              <div className="flex gap-2">
                {[1, 5, 10, 25, 50].map((amount) => (
                  <button
                    key={amount}
                    onClick={() => setStakeAmount(amount)}
                    className={`flex-1 py-2 rounded-lg transition-all ${
                      stakeAmount === amount
                        ? 'bg-telegram-button text-telegram-button-text'
                        : 'bg-telegram-secondary'
                    }`}
                  >
                    {amount}⭐
                  </button>
                ))}
              </div>
              <input
                type="number"
                value={stakeAmount}
                onChange={(e) => setStakeAmount(Math.max(0, Math.min(100, parseInt(e.target.value) || 0)))}
                placeholder="Своя ставка"
                min="1"
                max="100"
                className="w-full mt-3 px-3 py-2 bg-telegram-bg rounded-lg border border-telegram-hint/20 focus:outline-none focus:border-telegram-button"
              />
              <p className="text-xs text-telegram-hint mt-1">
                Максимальная ставка: 100 Stars
              </p>
            </motion.div>
          )}

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onClick={createMatch}
            disabled={isCreating || (mode === 'stars' && stakeAmount === 0)}
            className="btn-primary mt-auto"
          >
            {isCreating ? 'Создание...' : 'Создать матч'}
          </motion.button>
        </div>
      </div>
    );
  }

  // Страница выбора режима
  return (
    <div className="flex flex-col min-h-screen p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl font-bold mb-2">Выберите режим</h1>
        <p className="text-telegram-hint">Как будем играть?</p>
      </motion.div>

      <div className="flex-1 flex flex-col gap-4 max-w-md mx-auto w-full">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          onClick={() => {
            hapticFeedback('impact', 'light');
            navigate('/play/casual');
          }}
          className="card p-6 text-left hover:bg-telegram-button/10 transition-colors"
        >
          <div className="flex items-start gap-4">
            <span className="text-3xl">🎲</span>
            <div>
              <h3 className="font-semibold text-lg">Обычный матч</h3>
              <p className="text-telegram-hint text-sm mt-1">
                Быстрая игра без ставок
              </p>
            </div>
          </div>
        </motion.button>

        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          onClick={() => {
            hapticFeedback('impact', 'light');
            navigate('/play/bet');
          }}
          className="card p-6 text-left hover:bg-telegram-button/10 transition-colors"
        >
          <div className="flex items-start gap-4">
            <span className="text-3xl">🤝</span>
            <div>
              <h3 className="font-semibold text-lg">Матч на спор</h3>
              <p className="text-telegram-hint text-sm mt-1">
                Проигравший выполняет обещание
              </p>
            </div>
          </div>
        </motion.button>

        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          onClick={() => {
            hapticFeedback('impact', 'light');
            navigate('/play/stars');
          }}
          className="card p-6 text-left hover:bg-telegram-button/10 transition-colors"
        >
          <div className="flex items-start gap-4">
            <span className="text-3xl">⭐</span>
            <div>
              <h3 className="font-semibold text-lg">PvP на Stars</h3>
              <p className="text-telegram-hint text-sm mt-1">
                Играйте на Telegram Stars
              </p>
            </div>
          </div>
        </motion.button>
      </div>
    </div>
  );
};

export default PlayPage;
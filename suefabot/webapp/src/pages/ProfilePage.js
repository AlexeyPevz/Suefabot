import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useTelegram } from '../hooks/useTelegram';
import { userAPI } from '../utils/api';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, showBackButton, hideBackButton } = useTelegram();
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [showBackButton, hideBackButton, navigate]);

  useEffect(() => {
    if (user) {
      loadUserStats();
    }
  }, [user]);

  const loadUserStats = async () => {
    try {
      const stats = await userAPI.getInfo(user.id);
      setUserStats(stats);
    } catch (error) {
      toast.error('Ошибка загрузки статистики');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon, label, value, color = 'text-telegram-text' }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card text-center p-4"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-sm text-telegram-hint">{label}</div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-telegram-hint">Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <div className="text-6xl mb-4">👤</div>
        <h1 className="text-2xl font-bold">{user?.first_name} {user?.last_name}</h1>
        {user?.username && (
          <p className="text-telegram-hint">@{user.username}</p>
        )}
      </motion.div>

      <div className="mb-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6 mb-4"
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-semibold">Баланс Stars</span>
            <span className="text-3xl font-bold">
              {userStats?.stars_balance || 0} ⭐
            </span>
          </div>
          <button className="btn-primary w-full">
            Пополнить баланс
          </button>
        </motion.div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <StatCard
            icon="🎮"
            label="Всего игр"
            value={userStats?.total_games || 0}
          />
          <StatCard
            icon="📈"
            label="Винрейт"
            value={`${Math.round(userStats?.win_rate || 0)}%`}
            color={userStats?.win_rate > 50 ? 'text-green-500' : 'text-telegram-text'}
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <StatCard
            icon="✅"
            label="Побед"
            value={userStats?.wins || 0}
            color="text-green-500"
          />
          <StatCard
            icon="❌"
            label="Поражений"
            value={userStats?.losses || 0}
            color="text-red-500"
          />
          <StatCard
            icon="🤝"
            label="Ничьих"
            value={userStats?.draws || 0}
            color="text-yellow-500"
          />
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="space-y-3"
      >
        <div className="card p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏆</span>
            <div>
              <div className="font-semibold">Лига</div>
              <div className="text-sm text-telegram-hint">Бронза</div>
            </div>
          </div>
          <div className="text-telegram-hint">
            0 / 50 побед
          </div>
        </div>

        <div className="card p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🥇</span>
            <div>
              <div className="font-semibold">Место в рейтинге</div>
              <div className="text-sm text-telegram-hint">Общий рейтинг</div>
            </div>
          </div>
          <div className="text-2xl font-bold">
            -
          </div>
        </div>

        <div className="card p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📅</span>
            <div>
              <div className="font-semibold">Дата регистрации</div>
              <div className="text-sm text-telegram-hint">
                {userStats?.created_at 
                  ? new Date(userStats.created_at).toLocaleDateString('ru-RU')
                  : 'Неизвестно'}
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default ProfilePage;
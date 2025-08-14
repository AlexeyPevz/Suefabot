import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useTelegram } from '../hooks/useTelegram';

const ShopPage = () => {
  const navigate = useNavigate();
  const { hapticFeedback, showBackButton, hideBackButton } = useTelegram();
  const [activeCategory, setActiveCategory] = useState('all');

  useEffect(() => {
    showBackButton(() => navigate(-1));
    return () => hideBackButton();
  }, [showBackButton, hideBackButton, navigate]);

  const categories = [
    { id: 'all', name: 'Все', icon: '🎯' },
    { id: 'hands', name: 'Руки', icon: '✋' },
    { id: 'sleeves', name: 'Рукава', icon: '👕' },
    { id: 'accessories', name: 'Аксессуары', icon: '💍' },
    { id: 'items', name: 'Предметы', icon: '🎨' },
    { id: 'arenas', name: 'Арены', icon: '🏟' },
    { id: 'chests', name: 'Сундуки', icon: '🎁' },
  ];

  // Моковые данные для MVP
  const shopItems = [
    {
      id: 1,
      category: 'hands',
      name: 'Золотая рука',
      price: 50,
      rarity: 'rare',
      icon: '✋',
      description: 'Блестящая золотая рука'
    },
    {
      id: 2,
      category: 'items',
      name: 'Рубиновый камень',
      price: 100,
      rarity: 'epic',
      icon: '💎',
      description: 'Красивый рубиновый камень'
    },
    {
      id: 3,
      category: 'chests',
      name: 'Обычный сундук',
      price: 10,
      rarity: 'common',
      icon: '📦',
      description: '1 случайный предмет'
    },
    {
      id: 4,
      category: 'sleeves',
      name: 'Кожаный рукав',
      price: 30,
      rarity: 'common',
      icon: '🧥',
      description: 'Стильный кожаный рукав'
    },
    {
      id: 5,
      category: 'arenas',
      name: 'Космическая арена',
      price: 200,
      rarity: 'legendary',
      icon: '🌌',
      description: 'Играйте среди звезд'
    },
  ];

  const filteredItems = activeCategory === 'all' 
    ? shopItems 
    : shopItems.filter(item => item.category === activeCategory);

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'common': return 'border-gray-400';
      case 'rare': return 'border-blue-500';
      case 'epic': return 'border-purple-500';
      case 'legendary': return 'border-yellow-500';
      default: return 'border-gray-400';
    }
  };

  const getRarityBg = (rarity) => {
    switch (rarity) {
      case 'common': return 'bg-gray-400/10';
      case 'rare': return 'bg-blue-500/10';
      case 'epic': return 'bg-purple-500/10';
      case 'legendary': return 'bg-yellow-500/10';
      default: return 'bg-gray-400/10';
    }
  };

  const handlePurchase = (item) => {
    hapticFeedback('impact', 'medium');
    toast.success(`Вы купили ${item.name} за ${item.price} ⭐`);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-6"
        >
          <h1 className="text-2xl font-bold mb-2">🛍 Магазин</h1>
          <p className="text-telegram-hint">Кастомизируйте своего персонажа</p>
        </motion.div>

        {/* Категории */}
        <div className="overflow-x-auto mb-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="flex gap-2 pb-2"
          >
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => {
                  setActiveCategory(category.id);
                  hapticFeedback('selection');
                }}
                className={`flex items-center gap-1 px-4 py-2 rounded-full whitespace-nowrap transition-all ${
                  activeCategory === category.id
                    ? 'bg-telegram-button text-telegram-button-text'
                    : 'bg-telegram-secondary'
                }`}
              >
                <span>{category.icon}</span>
                <span className="text-sm">{category.name}</span>
              </button>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Товары */}
      <div className="flex-1 px-4 pb-4">
        <div className="grid grid-cols-2 gap-4">
          {filteredItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`card border-2 ${getRarityColor(item.rarity)} ${getRarityBg(item.rarity)} p-4`}
            >
              <div className="text-center mb-3">
                <div className="text-5xl mb-2">{item.icon}</div>
                <h3 className="font-semibold text-sm">{item.name}</h3>
                <p className="text-xs text-telegram-hint mt-1">
                  {item.description}
                </p>
              </div>
              
              <button
                onClick={() => handlePurchase(item)}
                className="btn-primary w-full text-sm py-2"
              >
                {item.price} ⭐
              </button>
            </motion.div>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="text-6xl mb-4">🚧</div>
            <p className="text-telegram-hint">
              В этой категории пока нет товаров
            </p>
          </motion.div>
        )}
      </div>

      {/* Баланс */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky bottom-0 bg-telegram-bg border-t border-telegram-hint/20 p-4"
      >
        <div className="flex items-center justify-between">
          <span className="text-sm text-telegram-hint">Ваш баланс:</span>
          <span className="font-bold text-lg">0 ⭐</span>
        </div>
      </motion.div>
    </div>
  );
};

export default ShopPage;
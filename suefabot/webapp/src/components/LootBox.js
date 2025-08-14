import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/animations.css';

const LootBox = ({ 
  type = 'common', 
  isOpening = false,
  items = [],
  onOpen,
  onClose
}) => {
  const [showRewards, setShowRewards] = useState(false);
  const [currentItemIndex, setCurrentItemIndex] = useState(0);

  // Конфигурация лутбоксов
  const lootboxConfig = {
    starter: {
      name: 'Стартовый сундук',
      emoji: '🎁',
      color: 'from-green-400 to-green-600',
      glow: '',
      particleColor: '#4ade80'
    },
    common: {
      name: 'Обычный сундук',
      emoji: '📦',
      color: 'from-gray-400 to-gray-600',
      glow: '',
      particleColor: '#9ca3af'
    },
    rare: {
      name: 'Редкий сундук',
      emoji: '🎁',
      color: 'from-yellow-400 to-yellow-600',
      glow: 'glow-rare',
      particleColor: '#fbbf24'
    },
    epic: {
      name: 'Эпический сундук',
      emoji: '💎',
      color: 'from-purple-400 to-purple-600',
      glow: 'glow-epic',
      particleColor: '#a855f7'
    },
    legendary: {
      name: 'Легендарный сундук',
      emoji: '👑',
      color: 'from-pink-400 to-red-500',
      glow: 'glow-legendary',
      particleColor: '#ec4899'
    }
  };

  const config = lootboxConfig[type] || lootboxConfig.common;

  // Рарность предметов
  const rarityConfig = {
    common: { name: 'Обычный', color: 'text-gray-500', bgColor: 'bg-gray-100' },
    rare: { name: 'Редкий', color: 'text-yellow-500', bgColor: 'bg-yellow-50' },
    epic: { name: 'Эпический', color: 'text-purple-500', bgColor: 'bg-purple-50' },
    legendary: { name: 'Легендарный', color: 'text-pink-500', bgColor: 'bg-pink-50' }
  };

  const handleOpen = async () => {
    if (onOpen) {
      onOpen();
      // Анимация открытия
      setTimeout(() => {
        setShowRewards(true);
      }, 1500);
    }
  };

  const handleNextItem = () => {
    if (currentItemIndex < items.length - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    } else {
      handleClose();
    }
  };

  const handleClose = () => {
    setShowRewards(false);
    setCurrentItemIndex(0);
    if (onClose) onClose();
  };

  return (
    <div className="relative">
      <AnimatePresence>
        {!showRewards ? (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="text-center"
          >
            {/* Лутбокс */}
            <div className={`
              relative inline-block
              ${isOpening ? 'animate-lootbox' : 'animate-pulse'}
            `}>
              <div className={`
                w-40 h-40
                bg-gradient-to-br ${config.color}
                rounded-3xl
                shadow-2xl
                flex items-center justify-center
                text-7xl
                ${config.glow}
                cursor-pointer
                transition-transform hover:scale-105
              `}
              onClick={!isOpening ? handleOpen : undefined}
              >
                {config.emoji}
              </div>

              {/* Частицы при открытии */}
              {isOpening && (
                <div className="absolute inset-0 pointer-events-none">
                  {[...Array(8)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full"
                      style={{ 
                        backgroundColor: config.particleColor,
                        top: '50%',
                        left: '50%'
                      }}
                      animate={{
                        x: [0, Math.cos(i * Math.PI / 4) * 100],
                        y: [0, Math.sin(i * Math.PI / 4) * 100],
                        opacity: [1, 0],
                        scale: [1, 0.5]
                      }}
                      transition={{
                        duration: 1,
                        ease: 'easeOut',
                        delay: 0.5
                      }}
                    />
                  ))}
                </div>
              )}
            </div>

            <h3 className="mt-4 text-xl font-bold text-gray-800">
              {config.name}
            </h3>

            {!isOpening && (
              <button
                onClick={handleOpen}
                className="mt-4 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Открыть сундук
              </button>
            )}
          </motion.div>
        ) : (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="text-center"
          >
            {/* Отображение полученного предмета */}
            {items[currentItemIndex] && (
              <div className="space-y-4">
                <h3 className="text-2xl font-bold text-gray-800">
                  Поздравляем!
                </h3>

                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className={`
                    mx-auto
                    w-32 h-32
                    rounded-2xl
                    flex items-center justify-center
                    text-6xl
                    ${rarityConfig[items[currentItemIndex].rarity].bgColor}
                    ${items[currentItemIndex].rarity !== 'common' ? `glow-${items[currentItemIndex].rarity}` : ''}
                  `}
                >
                  {items[currentItemIndex].emoji}
                </motion.div>

                <div>
                  <h4 className="text-xl font-semibold">
                    {items[currentItemIndex].name}
                  </h4>
                  <p className={`text-sm ${rarityConfig[items[currentItemIndex].rarity].color}`}>
                    {rarityConfig[items[currentItemIndex].rarity].name}
                  </p>
                  <p className="text-gray-600 mt-1">
                    {items[currentItemIndex].description}
                  </p>
                </div>

                {/* Индикатор предметов */}
                {items.length > 1 && (
                  <div className="flex justify-center space-x-1 mt-4">
                    {items.map((_, index) => (
                      <div
                        key={index}
                        className={`
                          w-2 h-2 rounded-full transition-colors
                          ${index === currentItemIndex ? 'bg-blue-500' : 'bg-gray-300'}
                        `}
                      />
                    ))}
                  </div>
                )}

                <button
                  onClick={handleNextItem}
                  className="mt-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  {currentItemIndex < items.length - 1 ? 'Следующий предмет' : 'Отлично!'}
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LootBox;
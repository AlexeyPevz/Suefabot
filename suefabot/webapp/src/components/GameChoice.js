import React from 'react';
import '../styles/animations.css';

const GameChoice = ({ 
  choice, 
  onClick, 
  disabled = false,
  isWinner = null,
  isAnimating = false,
  skin = 'default',
  size = 'medium'
}) => {
  // Маппинг выборов на эмодзи и стили
  const choiceConfig = {
    rock: {
      emoji: '✊',
      label: 'Камень',
      color: 'from-gray-400 to-gray-600',
      skins: {
        default: { emoji: '✊', effect: '' },
        gold: { emoji: '✊', effect: 'shimmer-effect', color: 'from-yellow-400 to-yellow-600' },
        diamond: { emoji: '💎', effect: 'glow-epic', color: 'from-blue-300 to-blue-500' },
        fire: { emoji: '🔥', effect: 'glow-rare', color: 'from-red-400 to-orange-500' },
        ice: { emoji: '🧊', effect: 'glow-rare', color: 'from-cyan-300 to-blue-400' }
      }
    },
    scissors: {
      emoji: '✌️',
      label: 'Ножницы',
      color: 'from-blue-400 to-blue-600',
      skins: {
        default: { emoji: '✌️', effect: '' },
        gold: { emoji: '✌️', effect: 'shimmer-effect', color: 'from-yellow-400 to-yellow-600' },
        laser: { emoji: '⚡', effect: 'glow-epic', color: 'from-purple-400 to-pink-500' },
        blade: { emoji: '🗡️', effect: 'glow-rare', color: 'from-gray-400 to-gray-700' }
      }
    },
    paper: {
      emoji: '✋',
      label: 'Бумага',
      color: 'from-green-400 to-green-600',
      skins: {
        default: { emoji: '✋', effect: '' },
        gold: { emoji: '✋', effect: 'shimmer-effect', color: 'from-yellow-400 to-yellow-600' },
        magic: { emoji: '📜', effect: 'glow-epic', color: 'from-purple-400 to-indigo-500' },
        shield: { emoji: '🛡️', effect: 'glow-rare', color: 'from-blue-400 to-gray-500' }
      }
    }
  };

  const config = choiceConfig[choice];
  const skinConfig = config.skins[skin] || config.skins.default;
  const finalColor = skinConfig.color || config.color;

  // Размеры
  const sizeClasses = {
    small: 'w-20 h-20 text-3xl',
    medium: 'w-28 h-28 text-5xl',
    large: 'w-36 h-36 text-6xl'
  };

  // Классы анимации
  const animationClasses = () => {
    if (isAnimating) {
      if (isWinner === true) return 'animate-victory';
      if (isWinner === false) return 'animate-shake';
      return 'animate-spin';
    }
    return '';
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${sizeClasses[size]}
        relative
        bg-gradient-to-br ${finalColor}
        rounded-2xl
        shadow-lg
        flex items-center justify-center
        transition-all duration-300
        ${!disabled ? 'choice-hover' : 'choice-disabled'}
        ${animationClasses()}
        ${skinConfig.effect}
      `}
    >
      {/* Основной эмодзи */}
      <span className="relative z-10 select-none">
        {skinConfig.emoji}
      </span>

      {/* Лейбл */}
      <span className="absolute -bottom-6 left-0 right-0 text-center text-sm font-medium text-gray-700">
        {config.label}
      </span>

      {/* Эффект свечения для редких скинов */}
      {skinConfig.effect.includes('glow') && (
        <div className={`absolute inset-0 rounded-2xl ${skinConfig.effect}`} />
      )}

      {/* Индикатор выигрыша/проигрыша */}
      {isWinner !== null && !isAnimating && (
        <div className={`
          absolute -top-2 -right-2 
          w-8 h-8 rounded-full 
          flex items-center justify-center
          text-white font-bold
          ${isWinner ? 'bg-green-500' : 'bg-red-500'}
          animate-fade-in
        `}>
          {isWinner ? '✓' : '✗'}
        </div>
      )}
    </button>
  );
};

export default GameChoice;
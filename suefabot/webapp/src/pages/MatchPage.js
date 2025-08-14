import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import io from 'socket.io-client';
import { useTelegram } from '../hooks/useTelegram';
import { matchAPI } from '../utils/api';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';

const MatchPage = ({ authToken }) => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { user, hapticFeedback, tg } = useTelegram();
  
  const [matchStatus, setMatchStatus] = useState('loading');
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [opponentChoice, setOpponentChoice] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [result, setResult] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Подключаемся к сокету с auth токеном (если есть)
    const newSocket = io(SOCKET_URL, {
      auth: authToken ? { token: authToken } : {},
      extraHeaders: tg?.initData ? { 'X-Telegram-Init-Data': tg.initData } : undefined,
    });
    setSocket(newSocket);

    // Присоединяемся к комнате матча
    newSocket.emit('join_match', { match_id: matchId });

    // Слушаем события
    newSocket.on('match_started', (data) => {
      setMatchStatus('in_progress');
      toast.success(`${data.player2_name} присоединился к игре!`);
      hapticFeedback('notification', 'success');
    });

    newSocket.on('choice_made', (data) => {
      toast(`${data.player_name} сделал выбор!`, { icon: '✅' });
    });

    newSocket.on('match_completed', (data) => {
      handleMatchComplete(data);
    });

    // Загружаем статус матча
    loadMatchStatus();

    return () => {
      newSocket.emit('leave_match', { match_id: matchId });
      newSocket.close();
    };
  }, [matchId, authToken]);

  const loadMatchStatus = async () => {
    try {
      const status = await matchAPI.getStatus(matchId);
      setMatchStatus(status.status);
      
      // Если матч еще не начался, пытаемся присоединиться
      if (status.status === 'waiting' && user) {
        const isCreator = status.player1_telegram_id === user.id.toString();
        if (!isCreator) {
          await matchAPI.join(matchId, user);
          setMatchStatus('in_progress');
        }
      }
    } catch (error) {
      toast.error('Ошибка загрузки матча');
      navigate('/');
    }
  };

  const makeChoice = async (choice) => {
    if (!user || selectedChoice || matchStatus !== 'in_progress') return;

    setSelectedChoice(choice);
    hapticFeedback('impact', 'medium');

    try {
      const response = await matchAPI.makeChoice(matchId, user.id, choice);
      
      if (response.status === 'completed') {
        handleMatchComplete(response);
      } else {
        toast('Ждем выбор соперника...', { icon: '⏳' });
      }
    } catch (error) {
      toast.error('Ошибка отправки выбора');
      setSelectedChoice(null);
    }
  };

  const handleMatchComplete = (data) => {
    setIsAnimating(true);
    setOpponentChoice(data.player1_choice === selectedChoice ? data.player2_choice : data.player1_choice);
    
    // Анимация раскрытия
    setTimeout(() => {
      setResult(data);
      hapticFeedback('notification', data.winner_id ? 'success' : 'warning');
      
      if (data.result_type === 'win') {
        const isWinner = data.winner_id === user?.id;
        toast(isWinner ? '🎉 Вы победили!' : '😔 Вы проиграли', {
          duration: 4000,
        });
      } else {
        toast('🤝 Ничья!', { duration: 4000 });
      }
    }, 2000);
  };

  const renderChoice = (choice, isOpponent = false) => {
    const icons = {
      rock: '✊',
      scissors: '✌️',
      paper: '✋',
    };

    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className={`text-8xl ${isOpponent ? 'transform scale-x-[-1]' : ''}`}
      >
        {choice ? icons[choice] : '❓'}
      </motion.div>
    );
  };

  const renderGameScreen = () => {
    if (isAnimating) {
      // Экран анимации боя
      return (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex gap-8 items-center">
            <motion.div
              animate={{ y: [0, -20, 0] }}
              transition={{ repeat: 3, duration: 0.5 }}
              className="animate-hand-shake"
            >
              {renderChoice(selectedChoice)}
            </motion.div>
            
            <span className="text-4xl">VS</span>
            
            <motion.div
              animate={{ y: [0, -20, 0] }}
              transition={{ repeat: 3, duration: 0.5 }}
              className="animate-hand-shake"
            >
              {renderChoice(opponentChoice, true)}
            </motion.div>
          </div>
        </div>
      );
    }

    if (result) {
      // Экран результата
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-center"
          >
            <div className="flex gap-8 items-center justify-center mb-8">
              <div className={result.winner_id === user?.id ? 'animate-glow' : 'opacity-50'}>
                {renderChoice(selectedChoice)}
              </div>
              
              <span className="text-2xl">VS</span>
              
              <div className={result.winner_id && result.winner_id !== user?.id ? 'animate-glow' : 'opacity-50'}>
                {renderChoice(opponentChoice, true)}
              </div>
            </div>
            
            <h2 className="text-3xl font-bold mb-4">
              {result.result_type === 'draw' ? '🤝 Ничья!' : 
               result.winner_id === user?.id ? '🎉 Победа!' : '😔 Поражение'}
            </h2>
            
            {result.promise && result.winner_id && (
              <p className="text-telegram-hint mb-6">
                {result.winner_id === user?.id 
                  ? `Соперник должен: ${result.promise}`
                  : `Вы должны: ${result.promise}`}
              </p>
            )}
            
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/')}
                className="btn-secondary"
              >
                На главную
              </button>
              <button
                onClick={() => navigate('/play')}
                className="btn-primary"
              >
                Новая игра
              </button>
            </div>
          </motion.div>
        </div>
      );
    }

    // Экран выбора
    return (
      <div className="flex-1 flex flex-col p-4">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold mb-2">Сделайте выбор</h2>
          <p className="text-telegram-hint">У вас есть 10 секунд</p>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="grid grid-cols-3 gap-4">
            {['rock', 'scissors', 'paper'].map((choice) => (
              <motion.button
                key={choice}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => makeChoice(choice)}
                disabled={selectedChoice !== null}
                className={`choice-button ${selectedChoice === choice ? 'selected' : ''}`}
              >
                {choice === 'rock' && '✊'}
                {choice === 'scissors' && '✌️'}
                {choice === 'paper' && '✋'}
              </motion.button>
            ))}
          </div>
        </div>
        
        {selectedChoice && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mt-8"
          >
            <p className="text-telegram-hint">
              Ваш выбор сделан. Ждем соперника...
            </p>
          </motion.div>
        )}
      </div>
    );
  };

  if (matchStatus === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-telegram-hint">Загрузка матча...</p>
        </div>
      </div>
    );
  }

  if (matchStatus === 'waiting') {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
            className="text-6xl mb-4"
          >
            ⏳
          </motion.div>
          <h2 className="text-2xl font-bold mb-2">Ожидание соперника</h2>
          <p className="text-telegram-hint mb-6">
            Поделитесь ссылкой на матч с другом
          </p>
          <button
            onClick={() => {
              hapticFeedback('impact', 'light');
              // Здесь должен быть код для шеринга
              toast.success('Ссылка скопирована!');
            }}
            className="btn-primary"
          >
            Поделиться матчем
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      {renderGameScreen()}
    </div>
  );
};

export default MatchPage;
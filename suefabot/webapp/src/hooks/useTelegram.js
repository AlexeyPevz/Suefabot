import { useEffect, useState } from 'react';

const tg = window.Telegram?.WebApp;

export function useTelegram() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (tg?.initDataUnsafe?.user) {
      setUser(tg.initDataUnsafe.user);
    }
  }, []);

  const onClose = () => {
    tg.close();
  };

  const onToggleButton = () => {
    if (tg.MainButton.isVisible) {
      tg.MainButton.hide();
    } else {
      tg.MainButton.show();
    }
  };

  const showMainButton = (text, onClick) => {
    tg.MainButton.setText(text);
    tg.MainButton.onClick(onClick);
    tg.MainButton.show();
  };

  const hideMainButton = () => {
    tg.MainButton.hide();
  };

  const showBackButton = (onClick) => {
    tg.BackButton.onClick(onClick);
    tg.BackButton.show();
  };

  const hideBackButton = () => {
    tg.BackButton.hide();
  };

  const showAlert = (message) => {
    tg.showAlert(message);
  };

  const showConfirm = (message) => {
    return new Promise((resolve) => {
      tg.showConfirm(message, (result) => {
        resolve(result);
      });
    });
  };

  const hapticFeedback = (type = 'impact', style = 'light') => {
    if (tg.HapticFeedback) {
      if (type === 'impact') {
        tg.HapticFeedback.impactOccurred(style);
      } else if (type === 'notification') {
        tg.HapticFeedback.notificationOccurred(style);
      } else if (type === 'selection') {
        tg.HapticFeedback.selectionChanged();
      }
    }
  };

  return {
    tg,
    user,
    onClose,
    onToggleButton,
    showMainButton,
    hideMainButton,
    showBackButton,
    hideBackButton,
    showAlert,
    showConfirm,
    hapticFeedback,
    queryId: tg?.initDataUnsafe?.query_id,
  };
}
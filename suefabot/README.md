# Suefabot 🎮✊✌️✋

**Решай споры красиво!**

PvP-мини-игра в жанре «Камень, ножницы, бумага» для Telegram с элементами кастомизации и коллекционирования.

## 🚀 Быстрый старт

### Требования
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Telegram Bot Token
- Telegram WebApp

### Установка

1. Клонируйте репозиторий
```bash
git clone https://github.com/yourusername/suefabot.git
cd suefabot
```

2. Настройте бота
```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
# Добавьте ваш BOT_TOKEN в .env
```

3. Настройте backend
```bash
cd ../backend
pip install -r requirements.txt
cp .env.example .env
```

4. Настройте webapp
```bash
cd ../webapp
npm install
cp .env.example .env
```

5. Запустите все сервисы
```bash
# В разных терминалах:
cd bot && python main.py
cd backend && python app.py
cd webapp && npm start
```

## 📁 Структура проекта

```
suefabot/
├── bot/           # Telegram bot (aiogram)
├── backend/       # Flask API
├── webapp/        # React Mini App
├── database/      # SQL схемы и миграции
├── assets/        # Изображения и анимации
└── docs/          # Документация
```

## 🎮 Основные функции

- **PvP матчи** - Быстрые игры между пользователями в чатах
- **Кастомизация** - Скины для рук, предметов и арен
- **Монетизация** - Telegram Stars для покупок и ставок
- **Рулетки** - Gacha-механика для получения редких предметов
- **Турниры** - Соревнования с призами

## 🛠 Технологии

- **Bot**: Python, aiogram 3.x
- **Backend**: Flask, Redis, PostgreSQL, SQLAlchemy
- **Frontend**: React, Tailwind CSS, Telegram WebApp SDK
- **Анимации**: CSS animations, Lottie (post-MVP)

## 📱 Поддерживаемые команды

- `/start` - Начать игру
- `@suefabot` - Inline режим для вызова в чатах
- `/profile` - Просмотр профиля
- `/shop` - Магазин скинов
- `/help` - Помощь

## 💎 Монетизация

- Дополнительные игры
- Премиум скины и эффекты
- Лутбоксы с редкими предметами
- Комиссия с PvP ставок (5%)
- Сезонные пропуска

## 🚦 Roadmap

### MVP (Месяц 1-2)
- [x] Базовая игровая механика
- [x] Интеграция с Telegram
- [ ] Простые анимации
- [ ] Система матчей

### Post-MVP (Месяц 3-6)
- [ ] Telegram Stars интеграция
- [ ] Кастомизация скинов
- [ ] Рулетки и лутбоксы
- [ ] Турниры
- [ ] Глобальные рейтинги

## 📊 Метрики

- DAU (Daily Active Users)
- ARPPU (Average Revenue Per Paying User)
- Retention (D1, D7, D30)
- Conversion Rate

## 🤝 Вклад в проект

Мы приветствуем контрибьюторов! См. [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 📞 Контакты

- Telegram: @suefabot_support
- Email: support@suefabot.com

---

**Suefabot** - Решай споры красиво! 🎮
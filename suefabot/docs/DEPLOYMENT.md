# Suefabot - Руководство по развертыванию

## Требования

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Telegram Bot Token от @BotFather

## 1. Создание Telegram бота

1. Откройте @BotFather в Telegram
2. Отправьте `/newbot`
3. Выберите имя и username для бота (например, @suefabot)
4. Сохраните полученный токен
5. Настройте бота:
   ```
   /setdescription - Решай споры красиво в игре «Камень, ножницы, бумага»!
   /setabouttext - PvP-мини-игра с кастомизацией и ставками на Telegram Stars
   /setuserpic - загрузите логотип
   /setinline - включите inline режим
   /setinlinefeedback - включите
   ```

## 2. Настройка Telegram WebApp

1. В @BotFather выполните:
   ```
   /newapp
   Выберите вашего бота
   Введите название: Suefabot Game
   Введите описание: Играй в камень-ножницы-бумага
   Загрузите иконку 640x360px
   Выберите тип: Web App
   Введите URL: https://your-domain.com (будет обновлен позже)
   ```

## 3. Локальная разработка

### PostgreSQL
```bash
# Создайте базу данных
createdb suefabot

# Примените схему
psql -d suefabot -f database/schema.sql
```

### Redis
```bash
# Запустите Redis
redis-server
```

### Backend
```bash
cd backend
cp .env.example .env
# Отредактируйте .env с вашими настройками

pip install -r requirements.txt
python app.py
```

### Bot
```bash
cd bot
cp .env.example .env
# Добавьте BOT_TOKEN и другие настройки

pip install -r requirements.txt
python main.py
```

### WebApp
```bash
cd webapp
cp .env.example .env
npm install
npm start
```

## 4. Деплой на продакшн

### Вариант 1: Heroku (бесплатный для MVP)

#### Backend на Heroku
```bash
cd backend
heroku create suefabot-backend
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Установите переменные окружения
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Создайте Procfile
echo "web: gunicorn app:app" > Procfile

git add .
git commit -m "Deploy backend"
git push heroku main
```

#### Bot на Heroku
```bash
cd bot
heroku create suefabot-bot

# Используйте webhook вместо polling
heroku config:set BOT_TOKEN=your-bot-token
heroku config:set WEBHOOK_HOST=https://suefabot-bot.herokuapp.com
heroku config:set ENVIRONMENT=production

echo "web: python main.py" > Procfile

git add .
git commit -m "Deploy bot"
git push heroku main
```

#### WebApp на Vercel
```bash
cd webapp
npm install -g vercel

# Обновите переменные окружения
echo "REACT_APP_API_URL=https://suefabot-backend.herokuapp.com" > .env.production

npm run build
vercel --prod
```

### Вариант 2: VPS (DigitalOcean/Hetzner)

#### Настройка сервера
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите зависимости
sudo apt install python3-pip python3-venv nodejs npm postgresql redis nginx certbot python3-certbot-nginx -y

# Создайте пользователя
sudo useradd -m -s /bin/bash suefabot
sudo su - suefabot
```

#### Настройка PostgreSQL
```bash
sudo -u postgres createuser suefabot
sudo -u postgres createdb suefabot -O suefabot
sudo -u postgres psql -c "ALTER USER suefabot PASSWORD 'your-password';"
```

#### Клонирование и настройка
```bash
git clone https://github.com/yourusername/suefabot.git
cd suefabot

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env

# Bot
cd ../bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env

# WebApp
cd ../webapp
npm install
npm run build
```

#### Systemd сервисы

`/etc/systemd/system/suefabot-backend.service`:
```ini
[Unit]
Description=Suefabot Backend
After=network.target

[Service]
Type=simple
User=suefabot
WorkingDirectory=/home/suefabot/suefabot/backend
Environment="PATH=/home/suefabot/suefabot/backend/venv/bin"
ExecStart=/home/suefabot/suefabot/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/suefabot-bot.service`:
```ini
[Unit]
Description=Suefabot Telegram Bot
After=network.target

[Service]
Type=simple
User=suefabot
WorkingDirectory=/home/suefabot/suefabot/bot
Environment="PATH=/home/suefabot/suefabot/bot/venv/bin"
ExecStart=/home/suefabot/suefabot/bot/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### Nginx конфигурация

`/etc/nginx/sites-available/suefabot`:
```nginx
server {
    listen 80;
    server_name api.suefabot.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name app.suefabot.com;
    root /home/suefabot/suefabot/webapp/build;
    
    location / {
        try_files $uri /index.html;
    }
}
```

#### SSL сертификаты
```bash
sudo certbot --nginx -d api.suefabot.com -d app.suefabot.com
```

#### Запуск сервисов
```bash
sudo systemctl enable suefabot-backend suefabot-bot
sudo systemctl start suefabot-backend suefabot-bot
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## 5. Настройка Telegram Stars (Post-MVP)

1. Подайте заявку на использование Telegram Stars через @BotSupport
2. После одобрения добавьте в бота обработку платежей:
   ```python
   # В bot/main.py добавьте обработчики
   @dp.pre_checkout_query()
   async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
       await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
   
   @dp.message(F.successful_payment)
   async def process_successful_payment(message: types.Message):
       # Обработка успешного платежа
       pass
   ```

## 6. Мониторинг и логирование

### Бесплатные сервисы
- **Sentry**: Отслеживание ошибок
- **UptimeRobot**: Мониторинг доступности
- **Google Analytics**: Аналитика использования

### Настройка логов
```python
# В backend/app.py и bot/main.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/suefabot.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

## 7. Обновление WebApp URL

После деплоя обновите URL в @BotFather:
```
/myapps
Выберите Suefabot Game
Edit App
Change Web App URL
Введите: https://app.suefabot.com
```

## 8. Тестирование

1. Откройте бота в Telegram
2. Нажмите /start
3. Попробуйте создать матч
4. Проверьте inline режим: введите @suefabot в любом чате
5. Проверьте WebApp: нажмите кнопку "Играть"

## Проблемы и решения

### WebApp не открывается
- Проверьте HTTPS сертификат
- Проверьте CORS настройки
- Убедитесь, что URL правильный в @BotFather

### Бот не отвечает
- Проверьте токен
- Проверьте логи: `journalctl -u suefabot-bot -f`
- Проверьте webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

### База данных недоступна
- Проверьте подключение: `psql -h localhost -U suefabot -d suefabot`
- Проверьте Redis: `redis-cli ping`

## Масштабирование

При росте нагрузки:
1. Переместите Redis в отдельный сервер (Redis Labs)
2. Используйте managed PostgreSQL (Supabase, Neon)
3. Добавьте CDN для статики (Cloudflare)
4. Используйте горизонтальное масштабирование для backend
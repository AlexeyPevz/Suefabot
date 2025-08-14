# План действий по проекту Suefabot

## Сводка обратной связи

### Консенсус коллег:
- **Идея**: Сильная, 4-5/5 ⭐
- **Реализация**: Хорошая для MVP, 3-4.5/5 ⭐
- **Вердикт**: Проект имеет высокий потенциал, но требует критических доработок перед production

### Ключевые риски:
1. **Безопасность** - отсутствует валидация Telegram данных
2. **Игровая логика** - критические баги с определением победителя
3. **Экономика** - транзакции не логируются, комиссия теряется
4. **Надежность** - проблемы с таймаутами и race conditions

## Этап 1: Критические исправления (P0) - 1 неделя

### 1.1 Безопасность и аутентификация
```python
# Добавить в backend/auth.py
def validate_telegram_webapp_data(init_data: str) -> dict:
    """Валидация подписи данных от Telegram WebApp"""
    # Проверка HMAC с использованием bot token
    # Возврат распарсенных и проверенных данных
```

**Задачи:**
- [ ] Реализовать проверку initData на всех критичных endpoints
- [ ] Добавить JWT токены для API аутентификации
- [ ] Настроить аутентификацию для WebSocket соединений
- [ ] Ограничить CORS только доменом WebApp

### 1.2 Исправление игровой логики
```python
# backend/app.py - изменить ответ API
@app.route('/api/match/<match_id>/complete', methods=['POST'])
def complete_match(match_id):
    # ...
    return jsonify({
        'winner_telegram_id': winner.telegram_id,  # Добавить
        'winner_num': winner_num,                  # Добавить
        'promise': match.promise,                  # Добавить
        # остальные поля...
    })
```

**Задачи:**
- [ ] Исправить возврат winner_telegram_id вместо winner_id
- [ ] Добавить promise в ответ завершения матча
- [ ] Убрать дублирование обновления статистики
- [ ] Протестировать корректность определения победителя

### 1.3 Атомарность операций
```python
# backend/app.py - атомарное присоединение
@app.route('/api/match/<match_id>/join', methods=['POST'])
def join_match(match_id):
    with db.session.begin():
        match = Match.query.filter_by(
            id=match_id,
            status=MatchStatus.WAITING,
            player2_id=None
        ).with_for_update().first()
        
        if not match:
            return jsonify({'error': 'Cannot join'}), 400
            
        match.player2_id = user.id
        # ...
```

**Задачи:**
- [ ] Реализовать атомарное присоединение к матчу
- [ ] Добавить продление TTL при первом выборе
- [ ] Использовать Lua скрипты для атомарных операций в Redis

### 1.4 Обработка таймаутов
```python
# backend/timeout_worker.py - новый файл
import schedule

def check_expired_matches():
    """Проверка и финализация истекших матчей"""
    expired = Match.query.filter(
        Match.status.in_([MatchStatus.WAITING, MatchStatus.IN_PROGRESS]),
        Match.created_at < datetime.now() - timedelta(seconds=MATCH_TIMEOUT)
    ).all()
    
    for match in expired:
        finalize_timeout(match)
        refund_stakes(match)
```

**Задачи:**
- [ ] Создать worker для обработки таймаутов
- [ ] Реализовать возврат ставок при таймауте
- [ ] Отправлять уведомления об истечении времени

## Этап 2: Экономика и транзакции (P0) - 3 дня

### 2.1 Система транзакций
```python
# backend/models.py - улучшенная модель
class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    match_id = Column(String(50), ForeignKey('matches.id'))
    type = Column(Enum(TransactionType))
    amount = Column(Integer)
    commission = Column(Integer, default=0)
    balance_before = Column(Integer)
    balance_after = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Задачи:**
- [ ] Создать систему логирования всех транзакций
- [ ] Добавить отдельный счет для комиссий
- [ ] Реализовать атомарные операции с балансами

### 2.2 Защита от гонок
```python
# backend/services/balance.py
def transfer_with_commission(from_user, to_user, amount, commission_rate):
    """Атомарный перевод с комиссией"""
    with db.session.begin():
        # Блокировка счетов
        from_user = User.query.filter_by(id=from_user.id).with_for_update().first()
        to_user = User.query.filter_by(id=to_user.id).with_for_update().first()
        
        # Проверки и перевод
        # Создание транзакций
```

**Задачи:**
- [ ] Использовать row-level locking для балансов
- [ ] Добавить проверку инвариантов
- [ ] Логировать все изменения балансов

## Этап 3: DevOps и инфраструктура (P1) - 1 неделя

### 3.1 Контейнеризация
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
  redis:
    image: redis:7-alpine
  backend:
    build: ./backend
    depends_on: [postgres, redis]
  bot:
    build: ./bot
    depends_on: [backend]
  webapp:
    build: ./webapp
```

**Задачи:**
- [ ] Создать Dockerfile для каждого сервиса
- [ ] Настроить docker-compose.yml
- [ ] Добавить .env.example файлы

### 3.2 Миграции БД
```bash
# Инициализация Alembic
cd backend
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Задачи:**
- [ ] Настроить Alembic
- [ ] Создать начальную миграцию
- [ ] Исправить SQL синтаксис для PostgreSQL

### 3.3 CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose run backend pytest
```

**Задачи:**
- [ ] Настроить GitHub Actions
- [ ] Добавить линтеры (flake8, eslint)
- [ ] Настроить автоматический деплой

## Этап 4: Тестирование (P1) - 1 неделя

### 4.1 Unit тесты
```python
# tests/test_game_logic.py
def test_determine_winner():
    assert GameLogic.determine_winner('rock', 'scissors') == (1, 'win')
    assert GameLogic.determine_winner('rock', 'rock') == (None, 'draw')
    
def test_commission_calculation():
    winner, commission = GameLogic.calculate_stake_distribution(100)
    assert winner == 95
    assert commission == 5
```

**Задачи:**
- [ ] Покрыть GameLogic тестами (100%)
- [ ] Добавить тесты для моделей
- [ ] Тестировать API endpoints

### 4.2 Integration тесты
```python
# tests/test_match_flow.py
def test_complete_match_flow():
    # Создание матча
    # Присоединение второго игрока
    # Выборы игроков
    # Проверка результата
```

**Задачи:**
- [ ] Тестировать полный флоу матча
- [ ] Проверить WebSocket события
- [ ] Тестировать таймауты

## Этап 5: Улучшения (P2) - 2 недели

### 5.1 Переход на FastAPI
```python
# Миграция с Flask на FastAPI
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

app = FastAPI()

class MatchCreate(BaseModel):
    promise: str
    stake_amount: int = 0
```

**Задачи:**
- [ ] Мигрировать на FastAPI + asyncio
- [ ] Использовать Pydantic для валидации
- [ ] Настроить async WebSockets

### 5.2 Мониторинг
**Задачи:**
- [ ] Добавить Prometheus метрики
- [ ] Настроить Grafana дашборды
- [ ] Интегрировать Sentry для ошибок

### 5.3 Интеграция бота
**Задачи:**
- [ ] Связать inline режим с реальными матчами
- [ ] Добавить deep links в WebApp
- [ ] Реализовать команды decline/rematch

## Метрики успеха

После выполнения плана:
- ✅ 0 критических уязвимостей безопасности
- ✅ 100% тестовое покрытие критичной логики
- ✅ < 100ms latency для игровых действий
- ✅ 99.9% uptime
- ✅ Полный аудит всех транзакций

## Timeline

- **Неделя 1**: Критические исправления (P0)
- **Неделя 2**: DevOps и тестирование
- **Неделя 3-4**: Улучшения и оптимизация
- **Неделя 5**: Soft launch с ограниченной аудиторией

## Ресурсы

- 2 backend разработчика
- 1 DevOps инженер
- 1 QA инженер
- Бюджет на инфраструктуру: $500/месяц
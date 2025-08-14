-- Suefabot Database Schema
-- PostgreSQL

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Типы перечислений
CREATE TYPE user_status AS ENUM ('active', 'banned', 'inactive');
CREATE TYPE match_status AS ENUM ('waiting', 'in_progress', 'completed', 'cancelled', 'timeout');
CREATE TYPE item_rarity AS ENUM ('common', 'rare', 'epic', 'legendary');
CREATE TYPE transaction_type AS ENUM ('purchase', 'match_win', 'match_loss', 'chest_open', 'refund', 'bonus');

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100),
    full_name VARCHAR(200),
    
    -- Игровая статистика
    total_games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    
    -- Экономика
    stars_balance INTEGER DEFAULT 0 CHECK (stars_balance >= 0),
    free_games_used INTEGER DEFAULT 0,
    free_games_reset_date TIMESTAMP,
    
    -- Статус
    status user_status DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_username (username),
    INDEX idx_last_active (last_active)
);

-- Таблица предметов
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    category VARCHAR(50), -- hands, sleeves, accessories, items, arenas
    type VARCHAR(50), -- rock, scissors, paper (для предметов)
    
    -- Экономика
    price_stars INTEGER DEFAULT 0,
    rarity item_rarity DEFAULT 'common',
    
    -- Визуал
    image_url VARCHAR(500),
    animation_url VARCHAR(500),
    
    -- Статус
    is_active BOOLEAN DEFAULT TRUE,
    is_seasonal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы
    INDEX idx_category (category),
    INDEX idx_rarity (rarity),
    INDEX idx_is_active (is_active)
);

-- Таблица матчей
CREATE TABLE matches (
    id VARCHAR(50) PRIMARY KEY, -- UUID
    player1_id INTEGER NOT NULL REFERENCES users(id),
    player2_id INTEGER REFERENCES users(id),
    
    -- Игровые данные
    player1_choice VARCHAR(20),
    player2_choice VARCHAR(20),
    promise VARCHAR(200),
    
    -- Ставки
    stake_amount INTEGER DEFAULT 0,
    stake_item_id INTEGER REFERENCES items(id),
    
    -- Статус
    status match_status DEFAULT 'waiting',
    winner_id INTEGER REFERENCES users(id),
    
    -- Временные метки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Индексы
    INDEX idx_player1_id (player1_id),
    INDEX idx_player2_id (player2_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Таблица инвентаря пользователей
CREATE TABLE user_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    item_id INTEGER NOT NULL REFERENCES items(id),
    
    -- Данные предмета
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    is_equipped BOOLEAN DEFAULT FALSE,
    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Уникальный индекс
    UNIQUE(user_id, item_id),
    
    -- Индексы
    INDEX idx_user_id (user_id),
    INDEX idx_item_id (item_id),
    INDEX idx_is_equipped (is_equipped)
);

-- Таблица транзакций
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- Данные транзакции
    type transaction_type NOT NULL,
    amount INTEGER NOT NULL,
    stars_before INTEGER NOT NULL,
    stars_after INTEGER NOT NULL,
    
    -- Дополнительные данные
    item_id INTEGER REFERENCES items(id),
    match_id VARCHAR(50) REFERENCES matches(id),
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at)
);

-- Таблица сундуков
CREATE TABLE chests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    
    -- Экономика
    price_stars INTEGER NOT NULL,
    
    -- Конфигурация лута
    items_count INTEGER DEFAULT 1,
    drop_rates JSONB DEFAULT '{"common": 0.7, "rare": 0.2, "epic": 0.08, "legendary": 0.02}',
    
    -- Визуал
    image_url VARCHAR(500),
    
    -- Статус
    is_active BOOLEAN DEFAULT TRUE,
    is_seasonal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица достижений
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    icon VARCHAR(50),
    
    -- Условия
    requirement_type VARCHAR(50), -- wins, games, streak, collection
    requirement_value INTEGER,
    
    -- Награды
    reward_stars INTEGER DEFAULT 0,
    reward_item_id INTEGER REFERENCES items(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица прогресса достижений
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    achievement_id INTEGER NOT NULL REFERENCES achievements(id),
    
    -- Прогресс
    current_value INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    
    -- Уникальный индекс
    UNIQUE(user_id, achievement_id),
    
    -- Индексы
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed)
);

-- Представление для статистики пользователя
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.telegram_id,
    u.username,
    u.full_name,
    u.total_games,
    u.wins,
    u.losses,
    u.draws,
    CASE 
        WHEN u.total_games = 0 THEN 0
        ELSE ROUND((u.wins::NUMERIC / u.total_games) * 100, 2)
    END AS win_rate,
    u.stars_balance,
    u.created_at,
    COUNT(DISTINCT ui.item_id) AS items_count,
    COUNT(DISTINCT ua.achievement_id) FILTER (WHERE ua.completed) AS achievements_count
FROM users u
LEFT JOIN user_items ui ON u.id = ui.user_id
LEFT JOIN user_achievements ua ON u.id = ua.user_id
GROUP BY u.id;

-- Функция для обновления статистики после матча
CREATE OR REPLACE FUNCTION update_match_stats() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        -- Обновляем статистику игроков
        UPDATE users SET total_games = total_games + 1 WHERE id IN (NEW.player1_id, NEW.player2_id);
        
        IF NEW.winner_id IS NOT NULL THEN
            -- Есть победитель
            UPDATE users SET wins = wins + 1 WHERE id = NEW.winner_id;
            UPDATE users SET losses = losses + 1 
            WHERE id IN (NEW.player1_id, NEW.player2_id) AND id != NEW.winner_id;
        ELSE
            -- Ничья
            UPDATE users SET draws = draws + 1 WHERE id IN (NEW.player1_id, NEW.player2_id);
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_match_stats
AFTER UPDATE ON matches
FOR EACH ROW
EXECUTE FUNCTION update_match_stats();

-- Вставка начальных данных

-- Базовые предметы
INSERT INTO items (name, description, category, type, price_stars, rarity) VALUES
-- Руки
('Базовая рука', 'Обычная человеческая рука', 'hands', NULL, 0, 'common'),
('Золотая рука', 'Блестящая золотая рука', 'hands', NULL, 50, 'rare'),
('Алмазная рука', 'Рука из чистого алмаза', 'hands', NULL, 500, 'legendary'),

-- Предметы
('Камень', 'Обычный серый камень', 'items', 'rock', 0, 'common'),
('Рубиновый камень', 'Красивый красный рубин', 'items', 'rock', 100, 'epic'),
('Ножницы', 'Простые металлические ножницы', 'items', 'scissors', 0, 'common'),
('Золотые ножницы', 'Ножницы из чистого золота', 'items', 'scissors', 100, 'epic'),
('Бумага', 'Обычный лист бумаги', 'items', 'paper', 0, 'common'),
('Магический свиток', 'Древний магический свиток', 'items', 'paper', 100, 'epic'),

-- Рукава
('Футболка', 'Простая хлопковая футболка', 'sleeves', NULL, 10, 'common'),
('Кожаная куртка', 'Стильная кожаная куртка', 'sleeves', NULL, 50, 'rare'),

-- Арены
('Классическая арена', 'Простой белый фон', 'arenas', NULL, 0, 'common'),
('Космос', 'Играйте среди звезд', 'arenas', NULL, 200, 'legendary');

-- Сундуки
INSERT INTO chests (name, description, price_stars, items_count) VALUES
('Обычный сундук', 'Содержит 1 случайный предмет', 10, 1),
('Редкий сундук', 'Содержит 3 случайных предмета', 50, 3),
('Легендарный сундук', 'Содержит 5 предметов с повышенным шансом редких', 200, 5);

-- Достижения
INSERT INTO achievements (code, name, description, icon, requirement_type, requirement_value, reward_stars) VALUES
('first_win', 'Первая победа', 'Выиграйте свой первый матч', '🏆', 'wins', 1, 10),
('win_streak_5', 'Серия побед', 'Выиграйте 5 матчей подряд', '🔥', 'streak', 5, 50),
('collector_10', 'Коллекционер', 'Соберите 10 различных предметов', '📦', 'collection', 10, 100),
('veteran_100', 'Ветеран', 'Сыграйте 100 матчей', '🎮', 'games', 100, 200);
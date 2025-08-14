from functools import wraps
from flask import request, jsonify, current_app
import redis
import time

from auth import get_current_telegram_user


class RateLimiter:
    """Rate limiter с использованием Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def limit(self, max_requests: int = 60, window: int = 60):
        """
        Декоратор для ограничения частоты запросов
        
        Args:
            max_requests: Максимальное количество запросов
            window: Временное окно в секундах
        """
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # Получаем идентификатор пользователя
                identifier = self._get_identifier()
                
                # Ключ для Redis
                key = f"rate_limit:{identifier}:{f.__name__}"
                
                try:
                    # Проверяем количество запросов
                    current = self.redis_client.incr(key)
                    
                    # Устанавливаем TTL при первом запросе
                    if current == 1:
                        self.redis_client.expire(key, window)
                    
                    # Проверяем лимит
                    if current > max_requests:
                        ttl = self.redis_client.ttl(key)
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'retry_after': ttl
                        }), 429
                    
                    # Добавляем заголовки с информацией о лимитах
                    response = f(*args, **kwargs)
                    if hasattr(response, 'headers'):
                        response.headers['X-RateLimit-Limit'] = str(max_requests)
                        response.headers['X-RateLimit-Remaining'] = str(max_requests - current)
                        response.headers['X-RateLimit-Reset'] = str(int(time.time()) + self.redis_client.ttl(key))
                    
                    return response
                    
                except redis.RedisError:
                    # В случае ошибки Redis - пропускаем запрос
                    return f(*args, **kwargs)
            
            return wrapped
        return decorator
    
    def _get_identifier(self) -> str:
        """Получение идентификатора для rate limiting"""
        # Пробуем получить telegram_id из аутентификации
        user = get_current_telegram_user()
        if user and user.get('telegram_id'):
            return f"user:{user['telegram_id']}"
        
        # Иначе используем IP адрес
        return f"ip:{request.remote_addr}"


# Глобальный экземпляр rate limiter
rate_limiter = None


def init_rate_limiter(app, redis_client):
    """Инициализация rate limiter"""
    global rate_limiter
    rate_limiter = RateLimiter(redis_client)
    return rate_limiter
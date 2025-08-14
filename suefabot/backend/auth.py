import hmac
import hashlib
import json
from urllib.parse import unquote, parse_qsl
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from functools import wraps
from flask import request, jsonify, current_app

from config import Config


class TelegramAuth:
    """Класс для валидации и работы с Telegram WebApp аутентификацией"""
    
    @staticmethod
    def validate_init_data(init_data: str, bot_token: str) -> Dict:
        """
        Валидация данных от Telegram WebApp
        
        Args:
            init_data: Строка с данными от Telegram в формате query string
            bot_token: Токен бота для проверки подписи
            
        Returns:
            Dict с распарсенными и проверенными данными
            
        Raises:
            ValueError: Если данные невалидны или истек срок
        """
        # Парсим query string
        parsed_data = dict(parse_qsl(init_data))
        
        # Проверяем наличие обязательных полей
        if 'hash' not in parsed_data:
            raise ValueError("Missing hash in init data")
            
        # Извлекаем hash
        received_hash = parsed_data.pop('hash')
        
        # Проверяем auth_date (не старше 24 часов)
        if 'auth_date' in parsed_data:
            auth_date = int(parsed_data['auth_date'])
            if datetime.now().timestamp() - auth_date > 86400:  # 24 часа
                raise ValueError("Init data is too old")
        
        # Сортируем параметры и формируем data-check-string
        check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # Вычисляем secret_key
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем хеши
        if calculated_hash != received_hash:
            raise ValueError("Invalid hash")
        
        # Парсим user данные если есть
        if 'user' in parsed_data:
            parsed_data['user'] = json.loads(unquote(parsed_data['user']))
            
        return parsed_data
    
    @staticmethod
    def generate_jwt_token(user_data: Dict, secret_key: str, expires_in: int = 3600) -> str:
        """
        Генерация JWT токена для пользователя
        
        Args:
            user_data: Данные пользователя из Telegram
            secret_key: Секретный ключ для подписи JWT
            expires_in: Время жизни токена в секундах
            
        Returns:
            JWT токен
        """
        payload = {
            'telegram_id': str(user_data.get('id')),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token: str, secret_key: str) -> Optional[Dict]:
        """
        Проверка и декодирование JWT токена
        
        Args:
            token: JWT токен
            secret_key: Секретный ключ
            
        Returns:
            Декодированные данные или None
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


def require_telegram_auth(f):
    """
    Декоратор для проверки Telegram аутентификации
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверяем наличие initData или JWT токена
        init_data = request.headers.get('X-Telegram-Init-Data')
        auth_token = request.headers.get('Authorization')
        
        if init_data:
            # Валидация через initData
            try:
                bot_token = current_app.config.get('BOT_TOKEN')
                if not bot_token:
                    return jsonify({'error': 'Bot token not configured'}), 500
                    
                validated_data = TelegramAuth.validate_init_data(init_data, bot_token)
                request.telegram_user = validated_data.get('user', {})
                
            except ValueError as e:
                return jsonify({'error': f'Invalid init data: {str(e)}'}), 401
                
        elif auth_token and auth_token.startswith('Bearer '):
            # Валидация через JWT
            token = auth_token.split(' ')[1]
            secret_key = current_app.config.get('SECRET_KEY')
            
            user_data = TelegramAuth.verify_jwt_token(token, secret_key)
            if not user_data:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            request.telegram_user = user_data
        
        else:
            # Dev-режим: упрощенная аутентификация через заголовки для MVP
            try:
                if current_app.config.get('ENVIRONMENT', 'development') != 'production':
                    dev_user_id = request.headers.get('X-Dev-User-Id')
                    if dev_user_id:
                        request.telegram_user = {
                            'telegram_id': str(dev_user_id),
                            'username': request.headers.get('X-Dev-Username', ''),
                            'first_name': request.headers.get('X-Dev-First-Name', ''),
                            'last_name': request.headers.get('X-Dev-Last-Name', '')
                        }
                        return f(*args, **kwargs)
            except Exception:
                pass
            return jsonify({'error': 'No authentication provided'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_telegram_user() -> Optional[Dict]:
    """
    Получение текущего аутентифицированного пользователя Telegram
    
    Returns:
        Данные пользователя или None
    """
    return getattr(request, 'telegram_user', None)
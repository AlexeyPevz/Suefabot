import uuid
import redis
import json
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import Base, User, Match, MatchStatus, Transaction, TransactionType
from game_logic import GameLogic
from auth import require_telegram_auth, get_current_telegram_user, TelegramAuth
from services.transaction_service import TransactionService
from services.lootbox_service import LootboxService
from middleware.rate_limiter import init_rate_limiter
from monitoring import init_monitoring, match_created_total, match_completed_total, active_matches, websocket_connections

# Инициализация Flask
app = Flask(__name__)
app.config.from_object(Config)

# CORS для WebApp
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

# SocketIO для real-time
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS, async_mode='eventlet')

# Redis для сессий
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)

# Инициализация rate limiter
rate_limiter = init_rate_limiter(app, redis_client)

# Инициализация мониторинга
init_monitoring(app)

# Database
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Вспомогательные функции
def get_or_create_user(telegram_id: str, username: str = None, full_name: str = None):
    """Получает или создает пользователя"""
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name
            )
            session.add(user)
            session.commit()
        else:
            # Обновляем данные пользователя
            user.username = username or user.username
            user.full_name = full_name or user.full_name
            user.last_active = datetime.utcnow()
            session.commit()
        return user
    finally:
        session.close()


# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/auth/telegram', methods=['POST'])
def auth_telegram():
    """Аутентификация через Telegram WebApp"""
    data = request.json
    init_data = data.get('initData')
    
    if not init_data:
        return jsonify({'error': 'initData is required'}), 400
    
    try:
        # Валидируем данные от Telegram
        validated_data = TelegramAuth.validate_init_data(init_data, Config.BOT_TOKEN)
        user_data = validated_data.get('user', {})
        
        if not user_data:
            return jsonify({'error': 'User data not found'}), 400
        
        # Создаем/обновляем пользователя в БД
        telegram_id = str(user_data.get('id'))
        username = user_data.get('username')
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        
        user = get_or_create_user(telegram_id, username, full_name)
        
        # Генерируем JWT токен
        token = TelegramAuth.generate_jwt_token(user_data, Config.SECRET_KEY)
        
        return jsonify({
            'token': token,
            'user': {
                'telegram_id': user.telegram_id,
                'username': user.username,
                'full_name': user.full_name,
                'stars_balance': user.stars_balance
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/user/<telegram_id>', methods=['GET'])
def get_user_info(telegram_id):
    """Получить информацию о пользователе"""
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'telegram_id': user.telegram_id,
            'username': user.username,
            'full_name': user.full_name,
            'total_games': user.total_games,
            'wins': user.wins,
            'losses': user.losses,
            'draws': user.draws,
            'win_rate': user.win_rate,
            'stars_balance': user.stars_balance,
            'created_at': user.created_at.isoformat()
        })
    finally:
        session.close()


@app.route('/api/match/create', methods=['POST'])
@require_telegram_auth
@rate_limiter.limit(max_requests=10, window=60)  # 10 матчей в минуту
def create_match():
    """Создать новый матч"""
    data = request.json
    
    # Получаем данные из аутентификации
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    username = current_user.get('username')
    full_name = current_user.get('first_name', '') + ' ' + current_user.get('last_name', '')
    full_name = full_name.strip()
    
    promise = data.get('promise')
    stake_amount = data.get('stake_amount', 0)
    
    if not telegram_id:
        return jsonify({'error': 'telegram_id is required'}), 400
    
    # Создаем/получаем пользователя
    user = get_or_create_user(telegram_id, username, full_name)
    
    # Проверяем баланс для ставки
    if stake_amount > 0 and not GameLogic.validate_stake(user.stars_balance, stake_amount):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Создаем матч
    match_id = str(uuid.uuid4())
    session = Session()
    try:
        match = Match(
            id=match_id,
            player1_id=user.id,
            promise=promise,
            stake_amount=stake_amount,
            status=MatchStatus.WAITING
        )
        session.add(match)
        session.commit()
        
        # Сохраняем в Redis для быстрого доступа
        match_data = {
            'match_id': match_id,
            'player1_id': user.id,
            'player1_telegram_id': user.telegram_id,
            'player1_name': user.full_name or user.username,
            'player2_id': None,
            'player2_telegram_id': None,
            'player2_name': None,
            'promise': promise,
            'stake_amount': stake_amount,
            'status': 'waiting',
            'created_at': datetime.utcnow().isoformat()
        }
        redis_client.setex(
            f'match:{match_id}',
            Config.MATCH_TIMEOUT_SECONDS,
            json.dumps(match_data)
        )
        
        return jsonify({
            'match_id': match_id,
                    'status': 'waiting',
        'timeout_seconds': Config.MATCH_TIMEOUT_SECONDS
    })
    
    # Обновляем метрики
    match_created_total.inc()
    active_matches.inc()
    finally:
        session.close()


@app.route('/api/match/<match_id>/join', methods=['POST'])
@require_telegram_auth
@rate_limiter.limit(max_requests=20, window=60)  # 20 попыток присоединения в минуту
def join_match(match_id):
    """Присоединиться к матчу"""
    # Получаем данные из аутентификации
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    username = current_user.get('username')
    full_name = current_user.get('first_name', '') + ' ' + current_user.get('last_name', '')
    full_name = full_name.strip()
    
    if not telegram_id:
        return jsonify({'error': 'telegram_id is required'}), 400
    
    # Получаем данные матча из Redis
    match_data = redis_client.get(f'match:{match_id}')
    if not match_data:
        return jsonify({'error': 'Match not found or expired'}), 404
    
    match_data = json.loads(match_data)
    
    # Проверяем, что матч ожидает второго игрока
    if match_data['status'] != 'waiting':
        return jsonify({'error': 'Match is not available'}), 400
    
    # Проверяем, что это не тот же игрок
    if match_data['player1_telegram_id'] == telegram_id:
        return jsonify({'error': 'Cannot play against yourself'}), 400
    
    # Создаем/получаем пользователя
    user = get_or_create_user(telegram_id, username, full_name)
    
    # Проверяем баланс для ставки
    stake_amount = match_data['stake_amount']
    if stake_amount > 0 and not GameLogic.validate_stake(user.stars_balance, stake_amount):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Обновляем матч в БД с атомарной операцией
    session = Session()
    try:
        # Используем row-level lock для предотвращения race condition
        match = session.query(Match).filter(
            Match.id == match_id,
            Match.status == MatchStatus.WAITING,
            Match.player2_id == None
        ).with_for_update().first()
        
        if not match:
            # Матч уже занят или не существует
            return jsonify({'error': 'Match is not available'}), 400
        
        # Проверяем, что первый игрок не пытается присоединиться к своему матчу
        if match.player1_id == user.id:
            return jsonify({'error': 'Cannot play against yourself'}), 400
        
        match.player2_id = user.id
        match.status = MatchStatus.IN_PROGRESS
        match.started_at = datetime.utcnow()
        session.commit()
        
        # Обновляем Redis
        match_data['player2_id'] = user.id
        match_data['player2_telegram_id'] = user.telegram_id
        match_data['player2_name'] = user.full_name or user.username
        match_data['status'] = 'in_progress'
        match_data['started_at'] = datetime.utcnow().isoformat()
        
        redis_client.setex(
            f'match:{match_id}',
            Config.CHOICE_TIMEOUT_SECONDS,
            json.dumps(match_data)
        )
        
        # Уведомляем через WebSocket
        socketio.emit('match_started', {
            'match_id': match_id,
            'player2_name': match_data['player2_name']
        }, room=match_id)
        
        return jsonify({
            'match_id': match_id,
            'status': 'in_progress',
            'timeout_seconds': Config.CHOICE_TIMEOUT_SECONDS
        })
    finally:
        session.close()


@app.route('/api/match/<match_id>/choice', methods=['POST'])
@require_telegram_auth
@rate_limiter.limit(max_requests=30, window=60)  # 30 выборов в минуту
def make_choice(match_id):
    """Сделать выбор в матче"""
    data = request.json
    
    # Получаем данные из аутентификации
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    
    choice = data.get('choice')
    
    if not telegram_id or not choice:
        return jsonify({'error': 'telegram_id and choice are required'}), 400
    
    if choice not in Config.CHOICES:
        return jsonify({'error': 'Invalid choice'}), 400
    
    # Получаем данные матча
    match_data = redis_client.get(f'match:{match_id}')
    if not match_data:
        return jsonify({'error': 'Match not found or expired'}), 404
    
    match_data = json.loads(match_data)
    
    # Проверяем статус матча
    if match_data['status'] != 'in_progress':
        return jsonify({'error': 'Match is not in progress'}), 400
    
    # Определяем номер игрока
    player_num = None
    if match_data['player1_telegram_id'] == telegram_id:
        player_num = 1
    elif match_data['player2_telegram_id'] == telegram_id:
        player_num = 2
    else:
        return jsonify({'error': 'You are not a participant in this match'}), 403
    
    # Сохраняем выбор
    choice_key = f'match:{match_id}:choice:{player_num}'
    existing_choice = redis_client.get(choice_key)
    if existing_choice:
        return jsonify({'error': 'Choice already made'}), 400
    
    redis_client.setex(choice_key, Config.CHOICE_TIMEOUT_SECONDS, choice)
    
    # Продлеваем TTL матча при первом выборе
    choice1_exists = redis_client.exists(f'match:{match_id}:choice:1')
    choice2_exists = redis_client.exists(f'match:{match_id}:choice:2')
    if (choice1_exists and not choice2_exists) or (choice2_exists and not choice1_exists):
        # Это первый выбор - продлеваем TTL матча
        redis_client.expire(f'match:{match_id}', Config.MATCH_TIMEOUT_SECONDS)
    
    # Проверяем, сделали ли оба игрока выбор
    choice1 = redis_client.get(f'match:{match_id}:choice:1')
    choice2 = redis_client.get(f'match:{match_id}:choice:2')
    
    if choice1 and choice2:
        # Оба игрока сделали выбор - определяем победителя
        winner_num, result_type = GameLogic.determine_winner(choice1, choice2)
        
        # Обновляем БД
        session = Session()
        try:
            match = session.query(Match).filter_by(id=match_id).first()
            match.player1_choice = choice1
            match.player2_choice = choice2
            match.status = MatchStatus.COMPLETED
            match.completed_at = datetime.utcnow()
            
            player1 = session.query(User).filter_by(id=match.player1_id).first()
            player2 = session.query(User).filter_by(id=match.player2_id).first()
            
            # Статистика обновится автоматически через триггер БД
            # Устанавливаем победителя
            if winner_num == 1:
                match.winner_id = player1.id
                winner_id = player1.id
                winner_name = match_data['player1_name']
            elif winner_num == 2:
                match.winner_id = player2.id
                winner_id = player2.id
                winner_name = match_data['player2_name']
            else:
                winner_id = None
                winner_name = None
            
            # Обработка ставок с использованием TransactionService
            if match.stake_amount > 0 and winner_num:
                winner_amount, commission = GameLogic.calculate_stake_distribution(match.stake_amount)
                
                if winner_num == 1:
                    TransactionService.process_match_completion(
                        session=session,
                        winner=player1,
                        loser=player2,
                        stake_amount=match.stake_amount,
                        winner_payout=winner_amount,
                        commission=commission,
                        match_id=match_id
                    )
                else:
                    TransactionService.process_match_completion(
                        session=session,
                        winner=player2,
                        loser=player1,
                        stake_amount=match.stake_amount,
                        winner_payout=winner_amount,
                        commission=commission,
                        match_id=match_id
                    )
            
            session.commit()
            
            # Формируем результат
            result_message = GameLogic.get_result_message(
                winner_num,
                match_data['player1_name'],
                match_data['player2_name'],
                choice1,
                choice2,
                match_data.get('promise')
            )
            
            # Получаем telegram_id победителя
            winner_telegram_id = None
            if winner_num == 1:
                winner_telegram_id = player1.telegram_id
            elif winner_num == 2:
                winner_telegram_id = player2.telegram_id
            
            result = {
                'match_id': match_id,
                'status': 'completed',
                'player1_choice': choice1,
                'player2_choice': choice2,
                'winner_id': winner_id,  # ID из БД для обратной совместимости
                'winner_telegram_id': winner_telegram_id,  # Telegram ID для фронтенда
                'winner_num': winner_num,  # 1, 2 или None
                'winner_name': winner_name,
                'result_type': result_type,
                'result_message': result_message,
                'promise': match.promise  # Добавляем promise
            }
            
            # Уведомляем через WebSocket
            socketio.emit('match_completed', result, room=match_id)
            
            # Очищаем Redis
            redis_client.delete(f'match:{match_id}')
            redis_client.delete(f'match:{match_id}:choice:1')
            redis_client.delete(f'match:{match_id}:choice:2')
            
            return jsonify(result)
        finally:
            session.close()
    else:
        # Ждем выбор второго игрока
        socketio.emit('choice_made', {
            'player_num': player_num,
            'player_name': match_data[f'player{player_num}_name']
        }, room=match_id)
        
        return jsonify({
            'status': 'waiting_for_opponent',
            'your_choice': choice
        })


@app.route('/api/lootbox/starter', methods=['POST'])
@require_telegram_auth
def claim_starter_lootbox():
    """Получить стартовый лутбокс"""
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Выдаем стартовый лутбокс
        success = LootboxService.give_starter_lootbox(session, user)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Стартовый лутбокс получен!'
            })
        else:
            return jsonify({
                'error': 'Стартовый лутбокс уже был получен'
            }), 400
            
    finally:
        session.close()


@app.route('/api/lootbox/<int:chest_id>/open', methods=['POST'])
@require_telegram_auth
@rate_limiter.limit(max_requests=30, window=60)  # Ограничение на открытие
def open_lootbox(chest_id):
    """Открыть лутбокс"""
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Открываем лутбокс
        result = LootboxService.open_lootbox(session, user, chest_id)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': 'Failed to open lootbox'}), 500
    finally:
        session.close()


@app.route('/api/user/inventory', methods=['GET'])
@require_telegram_auth
def get_user_inventory():
    """Получить инвентарь пользователя"""
    current_user = get_current_telegram_user()
    telegram_id = current_user.get('telegram_id') or str(current_user.get('id'))
    
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Получаем предметы пользователя
        inventory = []
        for user_item in user.inventory:
            item = user_item.item
            inventory.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'category': item.category,
                'type': item.type,
                'rarity': item.rarity.value,
                'quantity': user_item.quantity,
                'equipped': user_item.equipped,
                'properties': item.properties or {}
            })
        
        return jsonify({
            'inventory': inventory,
            'total_items': len(inventory)
        })
        
    finally:
        session.close()


@app.route('/api/match/<match_id>/status', methods=['GET'])
def get_match_status(match_id):
    """Получить статус матча"""
    # Сначала проверяем Redis
    match_data = redis_client.get(f'match:{match_id}')
    if match_data:
        return jsonify(json.loads(match_data))
    
    # Если нет в Redis, проверяем БД
    session = Session()
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        
        return jsonify({
            'match_id': match.id,
            'status': match.status.value,
            'created_at': match.created_at.isoformat(),
            'completed': match.status == MatchStatus.COMPLETED
        })
    finally:
        session.close()


# WebSocket Events
@socketio.on('connect')
def handle_connect(auth):
    """Обработка подключения"""
    # Проверяем JWT токен
    if not auth or 'token' not in auth:
        print(f'Client connection rejected - no auth: {request.sid}')
        return False  # Отклоняем соединение
    
    try:
        user_data = TelegramAuth.verify_jwt_token(auth['token'], Config.SECRET_KEY)
        if not user_data:
            print(f'Client connection rejected - invalid token: {request.sid}')
            return False
        
        # Сохраняем данные пользователя в сессии
        session['telegram_user'] = user_data
        print(f'Client connected: {request.sid}, user: {user_data.get("telegram_id")}')
        emit('connected', {'message': 'Successfully connected to game server'})
        return True
    except Exception as e:
        print(f'Client connection error: {e}')
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_match')
def handle_join_match(data):
    """Присоединение к комнате матча"""
    match_id = data.get('match_id')
    if match_id:
        join_room(match_id)
        emit('joined_match', {'match_id': match_id})


@socketio.on('leave_match')
def handle_leave_match(data):
    """Выход из комнаты матча"""
    match_id = data.get('match_id')
    if match_id:
        leave_room(match_id)
        emit('left_match', {'match_id': match_id})


if __name__ == '__main__':
    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
import uuid
import redis
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import Base, User, Match, MatchStatus
from game_logic import GameLogic

# Инициализация Flask
app = Flask(__name__)
app.config.from_object(Config)

# CORS для WebApp
CORS(app, origins=Config.CORS_ORIGINS)

# SocketIO для real-time
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Redis для сессий
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)

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
def create_match():
    """Создать новый матч"""
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    full_name = data.get('full_name')
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
    finally:
        session.close()


@app.route('/api/match/<match_id>/join', methods=['POST'])
def join_match(match_id):
    """Присоединиться к матчу"""
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    full_name = data.get('full_name')
    
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
    
    # Обновляем матч в БД
    session = Session()
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        
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
def make_choice(match_id):
    """Сделать выбор в матче"""
    data = request.json
    telegram_id = data.get('telegram_id')
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
            
            # Обновляем статистику
            player1.total_games += 1
            player2.total_games += 1
            
            if winner_num == 1:
                match.winner_id = player1.id
                player1.wins += 1
                player2.losses += 1
                winner_id = player1.id
                winner_name = match_data['player1_name']
            elif winner_num == 2:
                match.winner_id = player2.id
                player1.losses += 1
                player2.wins += 1
                winner_id = player2.id
                winner_name = match_data['player2_name']
            else:
                player1.draws += 1
                player2.draws += 1
                winner_id = None
                winner_name = None
            
            # Обработка ставок
            if match.stake_amount > 0 and winner_num:
                winner_amount, commission = GameLogic.calculate_stake_distribution(match.stake_amount)
                
                if winner_num == 1:
                    player1.stars_balance += winner_amount - match.stake_amount
                    player2.stars_balance -= match.stake_amount
                else:
                    player2.stars_balance += winner_amount - match.stake_amount
                    player1.stars_balance -= match.stake_amount
            
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
            
            result = {
                'match_id': match_id,
                'status': 'completed',
                'player1_choice': choice1,
                'player2_choice': choice2,
                'winner_id': winner_id,
                'winner_name': winner_name,
                'result_type': result_type,
                'result_message': result_message
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
def handle_connect():
    """Обработка подключения"""
    print(f'Client connected: {request.sid}')


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
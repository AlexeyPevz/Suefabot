import pytest
import json
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app, redis_client
from models import Base, User, Match, MatchStatus
from auth import TelegramAuth


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_session():
    """Database session for tests"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {
        'X-Telegram-Init-Data': 'mock_init_data'
    }


@pytest.fixture
def mock_auth(monkeypatch):
    """Mock Telegram authentication"""
    def mock_validate(*args, **kwargs):
        return {
            'user': {
                'id': 123456,
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
    
    monkeypatch.setattr(TelegramAuth, 'validate_init_data', mock_validate)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = True
    redis_mock.exists.return_value = False
    redis_mock.expire.return_value = True
    redis_mock.delete.return_value = True
    return redis_mock


class TestMatchFlow:
    """Integration tests for complete match flow"""
    
    @pytest.mark.integration
    def test_complete_match_flow_no_stake(self, client, mock_auth, mock_redis, monkeypatch):
        """Test complete match flow without stakes"""
        monkeypatch.setattr('app.redis_client', mock_redis)
        
        # 1. Create match
        create_response = client.post('/api/match/create',
            json={'promise': 'Test promise', 'stake_amount': 0},
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        assert create_response.status_code == 200
        data = json.loads(create_response.data)
        match_id = data['match_id']
        assert data['status'] == 'waiting'
        
        # 2. Second player joins
        # Mock different user
        def mock_validate_player2(*args, **kwargs):
            return {
                'user': {
                    'id': 789012,
                    'username': 'player2',
                    'first_name': 'Player',
                    'last_name': 'Two'
                }
            }
        monkeypatch.setattr(TelegramAuth, 'validate_init_data', mock_validate_player2)
        
        # Mock Redis to return match data
        mock_redis.get.return_value = json.dumps({
            'match_id': match_id,
            'status': 'waiting',
            'player1_telegram_id': '123456',
            'player1_name': 'Test User',
            'stake_amount': 0
        })
        
        join_response = client.post(f'/api/match/{match_id}/join',
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        assert join_response.status_code == 200
        
        # 3. Both players make choices
        # Player 1 chooses rock
        monkeypatch.setattr(TelegramAuth, 'validate_init_data', mock_validate)
        mock_redis.get.side_effect = [
            json.dumps({  # Match data
                'match_id': match_id,
                'status': 'in_progress',
                'player1_telegram_id': '123456',
                'player2_telegram_id': '789012',
                'player1_name': 'Test User',
                'player2_name': 'Player Two',
                'stake_amount': 0
            }),
            None,  # No existing choice
            None,  # Choice 1
            None   # Choice 2
        ]
        
        choice1_response = client.post(f'/api/match/{match_id}/choice',
            json={'choice': 'rock'},
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        assert choice1_response.status_code == 200
        
        # Player 2 chooses scissors
        monkeypatch.setattr(TelegramAuth, 'validate_init_data', mock_validate_player2)
        mock_redis.get.side_effect = [
            json.dumps({  # Match data
                'match_id': match_id,
                'status': 'in_progress',
                'player1_telegram_id': '123456',
                'player2_telegram_id': '789012',
                'player1_name': 'Test User',
                'player2_name': 'Player Two',
                'stake_amount': 0,
                'promise': 'Test promise'
            }),
            None,     # No existing choice
            'rock',   # Choice 1
            None      # Choice 2 (will be set)
        ]
        
        with patch('app.Session') as mock_session_class:
            # Mock database session and match
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_match = MagicMock(spec=Match)
            mock_match.id = match_id
            mock_match.promise = 'Test promise'
            mock_match.stake_amount = 0
            
            mock_player1 = MagicMock(spec=User)
            mock_player1.telegram_id = '123456'
            mock_player1.id = 1
            
            mock_player2 = MagicMock(spec=User)
            mock_player2.telegram_id = '789012'
            mock_player2.id = 2
            
            mock_session.query.return_value.filter_by.return_value.first.side_effect = [
                mock_match, mock_player1, mock_player2
            ]
            
            choice2_response = client.post(f'/api/match/{match_id}/choice',
                json={'choice': 'scissors'},
                headers={'X-Telegram-Init-Data': 'mock_data'}
            )
            
            assert choice2_response.status_code == 200
            result = json.loads(choice2_response.data)
            
            # Verify match result
            assert result['status'] == 'completed'
            assert result['winner_num'] == 1  # Rock beats scissors
            assert result['promise'] == 'Test promise'
            assert 'winner_telegram_id' in result
    
    @pytest.mark.integration
    def test_match_with_stakes(self, client, mock_auth, mock_redis, monkeypatch):
        """Test match flow with stakes"""
        monkeypatch.setattr('app.redis_client', mock_redis)
        
        with patch('app.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # Mock user with balance
            mock_user = MagicMock(spec=User)
            mock_user.telegram_id = '123456'
            mock_user.id = 1
            mock_user.stars_balance = 1000
            
            mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
            
            # Create match with stake
            create_response = client.post('/api/match/create',
                json={'promise': 'Loser buys coffee', 'stake_amount': 100},
                headers={'X-Telegram-Init-Data': 'mock_data'}
            )
            
            assert create_response.status_code == 200
            data = json.loads(create_response.data)
            assert data['stake_amount'] == 100
    
    @pytest.mark.integration
    def test_match_timeout_handling(self, client, mock_auth, mock_redis, monkeypatch):
        """Test match timeout scenario"""
        monkeypatch.setattr('app.redis_client', mock_redis)
        
        # Create match
        create_response = client.post('/api/match/create',
            json={'promise': 'Test', 'stake_amount': 50},
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        
        match_id = json.loads(create_response.data)['match_id']
        
        # Simulate timeout - Redis returns None
        mock_redis.get.return_value = None
        
        # Try to get match status
        status_response = client.get(f'/api/match/{match_id}/status')
        
        # Should check database when Redis is empty
        with patch('app.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_match = MagicMock(spec=Match)
            mock_match.id = match_id
            mock_match.status = MatchStatus.TIMEOUT
            
            mock_session.query.return_value.filter_by.return_value.first.return_value = mock_match
            
            status_response = client.get(f'/api/match/{match_id}/status')
            assert status_response.status_code == 200
            
            result = json.loads(status_response.data)
            assert result['status'] == 'timeout'
    
    @pytest.mark.integration
    def test_concurrent_join_attempts(self, client, mock_auth, mock_redis, monkeypatch):
        """Test race condition protection for joining match"""
        monkeypatch.setattr('app.redis_client', mock_redis)
        
        # Create match
        create_response = client.post('/api/match/create',
            json={'promise': 'Test', 'stake_amount': 0},
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        
        match_id = json.loads(create_response.data)['match_id']
        
        # Mock second user
        def mock_validate_player2(*args, **kwargs):
            return {
                'user': {
                    'id': 789012,
                    'username': 'player2',
                    'first_name': 'Player',
                    'last_name': 'Two'
                }
            }
        
        with patch('app.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # First join attempt succeeds
            mock_match = MagicMock(spec=Match)
            mock_match.id = match_id
            mock_match.player2_id = None
            mock_match.status = MatchStatus.WAITING
            
            # with_for_update returns query itself
            mock_query = MagicMock()
            mock_query.first.return_value = mock_match
            mock_session.query.return_value.filter.return_value.with_for_update.return_value = mock_query
            
            monkeypatch.setattr(TelegramAuth, 'validate_init_data', mock_validate_player2)
            
            # First join should succeed
            join_response1 = client.post(f'/api/match/{match_id}/join',
                headers={'X-Telegram-Init-Data': 'mock_data'}
            )
            assert join_response1.status_code == 200
            
            # Second join attempt should fail (match already has player2)
            mock_query.first.return_value = None  # No match found with player2_id=None
            
            join_response2 = client.post(f'/api/match/{match_id}/join',
                headers={'X-Telegram-Init-Data': 'mock_data'}
            )
            assert join_response2.status_code == 400
    
    @pytest.mark.integration
    def test_invalid_choice(self, client, mock_auth, mock_redis, monkeypatch):
        """Test invalid choice handling"""
        monkeypatch.setattr('app.redis_client', mock_redis)
        
        mock_redis.get.return_value = json.dumps({
            'match_id': 'test-match',
            'status': 'in_progress',
            'player1_telegram_id': '123456',
            'player2_telegram_id': '789012'
        })
        
        # Try invalid choice
        response = client.post('/api/match/test-match/choice',
            json={'choice': 'invalid_choice'},
            headers={'X-Telegram-Init-Data': 'mock_data'}
        )
        
        assert response.status_code == 400
        assert 'Invalid choice' in json.loads(response.data)['error']
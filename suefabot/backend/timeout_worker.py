import time
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

from config import Config
from models import Base, Match, MatchStatus, User
from services.transaction_service import TransactionService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация БД
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

# Redis клиент
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)


class TimeoutWorker:
    """Worker для обработки таймаутов матчей"""
    
    def __init__(self, check_interval: int = 30):
        """
        Args:
            check_interval: Интервал проверки в секундах
        """
        self.check_interval = check_interval
        self.running = False
    
    def check_expired_matches(self):
        """Проверка и обработка истекших матчей"""
        session = Session()
        try:
            # Находим матчи с истекшим таймаутом
            timeout_threshold = datetime.utcnow() - timedelta(seconds=Config.MATCH_TIMEOUT_SECONDS)
            
            expired_matches = session.query(Match).filter(
                Match.status.in_([MatchStatus.WAITING, MatchStatus.IN_PROGRESS]),
                Match.created_at < timeout_threshold
            ).all()
            
            logger.info(f"Found {len(expired_matches)} expired matches")
            
            for match in expired_matches:
                try:
                    self.process_expired_match(session, match)
                except Exception as e:
                    logger.error(f"Error processing match {match.id}: {e}")
                    session.rollback()
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Error in check_expired_matches: {e}")
            session.rollback()
        finally:
            session.close()
    
    def process_expired_match(self, session, match: Match):
        """
        Обработка конкретного истекшего матча
        
        Args:
            session: Сессия БД
            match: Истекший матч
        """
        logger.info(f"Processing expired match {match.id}")
        
        # Обновляем статус матча
        match.status = MatchStatus.TIMEOUT
        match.completed_at = datetime.utcnow()
        
        # Если были ставки - возвращаем их
        if match.stake_amount > 0:
            # Возврат ставки первому игроку
            if match.player1_id:
                player1 = session.query(User).filter_by(id=match.player1_id).first()
                if player1:
                    TransactionService.refund_match_stake(
                        session=session,
                        user=player1,
                        stake_amount=match.stake_amount,
                        match_id=match.id,
                        reason="Match timeout"
                    )
                    logger.info(f"Refunded {match.stake_amount} stars to player1 {player1.telegram_id}")
            
            # Возврат ставки второму игроку (если присоединился)
            if match.player2_id:
                player2 = session.query(User).filter_by(id=match.player2_id).first()
                if player2:
                    TransactionService.refund_match_stake(
                        session=session,
                        user=player2,
                        stake_amount=match.stake_amount,
                        match_id=match.id,
                        reason="Match timeout"
                    )
                    logger.info(f"Refunded {match.stake_amount} stars to player2 {player2.telegram_id}")
        
        # Очищаем данные из Redis
        redis_client.delete(f'match:{match.id}')
        redis_client.delete(f'match:{match.id}:choice:1')
        redis_client.delete(f'match:{match.id}:choice:2')
        
        logger.info(f"Match {match.id} marked as timeout")
    
    def run(self):
        """Запуск воркера"""
        self.running = True
        logger.info(f"Timeout worker started with check interval {self.check_interval}s")
        
        while self.running:
            try:
                self.check_expired_matches()
            except Exception as e:
                logger.error(f"Unexpected error in worker: {e}")
            
            time.sleep(self.check_interval)
    
    def stop(self):
        """Остановка воркера"""
        self.running = False
        logger.info("Timeout worker stopped")


if __name__ == "__main__":
    # Запуск воркера
    worker = TimeoutWorker(check_interval=30)
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        worker.stop()
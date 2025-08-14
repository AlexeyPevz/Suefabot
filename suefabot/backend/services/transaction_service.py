from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models import User, Transaction, TransactionType


class TransactionService:
    """Сервис для управления транзакциями и балансами"""
    
    @staticmethod
    def create_transaction(
        session: Session,
        user: User,
        transaction_type: TransactionType,
        amount: int,
        match_id: Optional[str] = None,
        commission: int = 0,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Создает транзакцию и обновляет баланс пользователя
        
        Args:
            session: Сессия БД (должна быть в рамках транзакции)
            user: Пользователь
            transaction_type: Тип транзакции
            amount: Сумма (положительная для пополнения, отрицательная для списания)
            match_id: ID матча (если применимо)
            commission: Сумма комиссии
            description: Описание транзакции
            
        Returns:
            Созданная транзакция
        """
        # Сохраняем баланс до операции
        balance_before = user.stars_balance
        
        # Обновляем баланс
        new_balance = balance_before + amount
        if new_balance < 0:
            raise ValueError(f"Insufficient balance. Current: {balance_before}, Required: {abs(amount)}")
        
        user.stars_balance = new_balance
        
        # Создаем транзакцию
        transaction = Transaction(
            user_id=user.id,
            match_id=match_id,
            type=transaction_type,
            amount=amount,
            commission=commission,
            balance_before=balance_before,
            balance_after=new_balance,
            description=description
        )
        
        session.add(transaction)
        return transaction
    
    @staticmethod
    def process_match_completion(
        session: Session,
        winner: User,
        loser: User,
        stake_amount: int,
        winner_payout: int,
        commission: int,
        match_id: str
    ) -> tuple[Transaction, Transaction, Optional[Transaction]]:
        """
        Обрабатывает финансовые операции при завершении матча
        
        Args:
            session: Сессия БД
            winner: Победитель
            loser: Проигравший
            stake_amount: Размер ставки каждого игрока
            winner_payout: Выплата победителю (за вычетом комиссии)
            commission: Сумма комиссии
            match_id: ID матча
            
        Returns:
            Кортеж из транзакций (winner_transaction, loser_transaction, commission_transaction)
        """
        # Блокируем счета для атомарности
        winner = session.query(User).filter_by(id=winner.id).with_for_update().first()
        loser = session.query(User).filter_by(id=loser.id).with_for_update().first()
        
        # Транзакция проигравшего (списание ставки)
        loser_transaction = TransactionService.create_transaction(
            session=session,
            user=loser,
            transaction_type=TransactionType.MATCH_LOSS,
            amount=-stake_amount,
            match_id=match_id,
            description=f"Проигрыш в матче {match_id}"
        )
        
        # Транзакция победителя (выплата за вычетом комиссии)
        winner_transaction = TransactionService.create_transaction(
            session=session,
            user=winner,
            transaction_type=TransactionType.MATCH_WIN,
            amount=winner_payout - stake_amount,  # Прибыль победителя
            match_id=match_id,
            commission=commission,
            description=f"Победа в матче {match_id}"
        )
        
        # Транзакция комиссии на системный счет
        commission_transaction = None
        if commission > 0:
            # Получаем системного пользователя
            system_user = session.query(User).filter_by(telegram_id="SYSTEM").first()
            if system_user:
                commission_transaction = TransactionService.create_transaction(
                    session=session,
                    user=system_user,
                    transaction_type=TransactionType.COMMISSION,
                    amount=commission,
                    match_id=match_id,
                    description=f"Комиссия с матча {match_id}"
                )
        
        return winner_transaction, loser_transaction, commission_transaction
    
    @staticmethod
    def refund_match_stake(
        session: Session,
        user: User,
        stake_amount: int,
        match_id: str,
        reason: str = "Match timeout"
    ) -> Transaction:
        """
        Возврат ставки при отмене/таймауте матча
        
        Args:
            session: Сессия БД
            user: Пользователь
            stake_amount: Сумма возврата
            match_id: ID матча
            reason: Причина возврата
            
        Returns:
            Транзакция возврата
        """
        user = session.query(User).filter_by(id=user.id).with_for_update().first()
        
        return TransactionService.create_transaction(
            session=session,
            user=user,
            transaction_type=TransactionType.MATCH_REFUND,
            amount=stake_amount,
            match_id=match_id,
            description=f"Возврат ставки: {reason}"
        )
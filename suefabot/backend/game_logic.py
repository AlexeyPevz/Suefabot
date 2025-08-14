from typing import Optional, Tuple
from config import Config


class GameLogic:
    """Основная игровая логика для Камень-Ножницы-Бумага"""
    
    @staticmethod
    def determine_winner(choice1: str, choice2: str) -> Tuple[Optional[int], str]:
        """
        Определяет победителя в раунде
        
        Args:
            choice1: Выбор первого игрока
            choice2: Выбор второго игрока
            
        Returns:
            Tuple[Optional[int], str]: (winner_player_number, result_type)
            winner_player_number: 1, 2 или None (ничья)
            result_type: 'win', 'draw'
        """
        if choice1 not in Config.CHOICES or choice2 not in Config.CHOICES:
            raise ValueError("Invalid choice")
        
        if choice1 == choice2:
            return None, 'draw'
        
        if Config.WINNING_RULES[choice1] == choice2:
            return 1, 'win'
        else:
            return 2, 'win'
    
    @staticmethod
    def calculate_stake_distribution(stake_amount: int, commission_rate: float = Config.COMMISSION_RATE) -> Tuple[int, int]:
        """
        Рассчитывает распределение ставки с учетом комиссии
        
        Args:
            stake_amount: Размер ставки от каждого игрока
            commission_rate: Процент комиссии (по умолчанию 5%)
            
        Returns:
            Tuple[int, int]: (winner_amount, commission_amount)
        """
        total_stake = stake_amount * 2
        commission = int(total_stake * commission_rate)
        winner_amount = total_stake - commission
        
        return winner_amount, commission
    
    @staticmethod
    def validate_stake(user_balance: int, stake_amount: int) -> bool:
        """
        Проверяет, достаточно ли у пользователя звезд для ставки
        
        Args:
            user_balance: Текущий баланс пользователя
            stake_amount: Размер ставки
            
        Returns:
            bool: True если средств достаточно
        """
        return user_balance >= stake_amount and stake_amount > 0
    
    @staticmethod
    def get_choice_emoji(choice: str) -> str:
        """Возвращает эмодзи для выбора"""
        emojis = {
            'rock': '✊',
            'scissors': '✌️',
            'paper': '✋'
        }
        return emojis.get(choice, '❓')
    
    @staticmethod
    def get_result_message(winner_id: Optional[int], player1_name: str, player2_name: str, 
                          choice1: str, choice2: str, promise: Optional[str] = None) -> str:
        """
        Формирует сообщение с результатом матча
        
        Args:
            winner_id: ID победителя (1, 2 или None)
            player1_name: Имя первого игрока
            player2_name: Имя второго игрока
            choice1: Выбор первого игрока
            choice2: Выбор второго игрока
            promise: Текст обещания (если есть)
            
        Returns:
            str: Отформатированное сообщение
        """
        emoji1 = GameLogic.get_choice_emoji(choice1)
        emoji2 = GameLogic.get_choice_emoji(choice2)
        
        if winner_id is None:
            result = f"🤝 **Ничья!**\n\n{player1_name} {emoji1} vs {emoji2} {player2_name}"
        elif winner_id == 1:
            result = f"🎉 **{player1_name} победил!**\n\n{player1_name} {emoji1} vs {emoji2} {player2_name}"
        else:
            result = f"🎉 **{player2_name} победил!**\n\n{player1_name} {emoji1} vs {emoji2} {player2_name}"
        
        if promise and winner_id is not None:
            loser = player2_name if winner_id == 1 else player1_name
            result += f"\n\n📝 Теперь {loser}: *{promise}*"
        
        return result
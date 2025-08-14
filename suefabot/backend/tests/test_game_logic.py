import pytest
from game_logic import GameLogic
from config import Config


class TestGameLogic:
    """Тесты для игровой логики"""
    
    def test_determine_winner_rock_beats_scissors(self):
        """Камень побеждает ножницы"""
        winner, result_type = GameLogic.determine_winner('rock', 'scissors')
        assert winner == 1
        assert result_type == 'win'
    
    def test_determine_winner_scissors_beats_paper(self):
        """Ножницы побеждают бумагу"""
        winner, result_type = GameLogic.determine_winner('scissors', 'paper')
        assert winner == 1
        assert result_type == 'win'
    
    def test_determine_winner_paper_beats_rock(self):
        """Бумага побеждает камень"""
        winner, result_type = GameLogic.determine_winner('paper', 'rock')
        assert winner == 1
        assert result_type == 'win'
    
    def test_determine_winner_rock_loses_to_paper(self):
        """Камень проигрывает бумаге"""
        winner, result_type = GameLogic.determine_winner('rock', 'paper')
        assert winner == 2
        assert result_type == 'win'
    
    def test_determine_winner_scissors_loses_to_rock(self):
        """Ножницы проигрывают камню"""
        winner, result_type = GameLogic.determine_winner('scissors', 'rock')
        assert winner == 2
        assert result_type == 'win'
    
    def test_determine_winner_paper_loses_to_scissors(self):
        """Бумага проигрывает ножницам"""
        winner, result_type = GameLogic.determine_winner('paper', 'scissors')
        assert winner == 2
        assert result_type == 'win'
    
    def test_determine_winner_draw(self):
        """Ничья при одинаковых выборах"""
        for choice in ['rock', 'scissors', 'paper']:
            winner, result_type = GameLogic.determine_winner(choice, choice)
            assert winner is None
            assert result_type == 'draw'
    
    def test_determine_winner_invalid_choice(self):
        """Исключение при невалидном выборе"""
        with pytest.raises(ValueError):
            GameLogic.determine_winner('invalid', 'rock')
        
        with pytest.raises(ValueError):
            GameLogic.determine_winner('rock', 'invalid')
    
    def test_calculate_stake_distribution_default_commission(self):
        """Расчет распределения ставки с комиссией по умолчанию (5%)"""
        stake = 100
        winner_amount, commission = GameLogic.calculate_stake_distribution(stake)
        
        total_stake = stake * 2  # 200
        expected_commission = int(total_stake * Config.COMMISSION_RATE)  # 10
        expected_winner_amount = total_stake - expected_commission  # 190
        
        assert winner_amount == expected_winner_amount
        assert commission == expected_commission
    
    def test_calculate_stake_distribution_custom_commission(self):
        """Расчет распределения ставки с кастомной комиссией"""
        stake = 100
        custom_rate = 0.1  # 10%
        winner_amount, commission = GameLogic.calculate_stake_distribution(stake, custom_rate)
        
        total_stake = stake * 2  # 200
        expected_commission = int(total_stake * custom_rate)  # 20
        expected_winner_amount = total_stake - expected_commission  # 180
        
        assert winner_amount == expected_winner_amount
        assert commission == expected_commission
    
    def test_calculate_stake_distribution_zero_commission(self):
        """Расчет распределения ставки без комиссии"""
        stake = 100
        winner_amount, commission = GameLogic.calculate_stake_distribution(stake, 0)
        
        total_stake = stake * 2  # 200
        
        assert winner_amount == total_stake
        assert commission == 0
    
    def test_validate_stake_sufficient_balance(self):
        """Валидация ставки при достаточном балансе"""
        assert GameLogic.validate_stake(100, 50) is True
        assert GameLogic.validate_stake(100, 100) is True
    
    def test_validate_stake_insufficient_balance(self):
        """Валидация ставки при недостаточном балансе"""
        assert GameLogic.validate_stake(50, 100) is False
        assert GameLogic.validate_stake(0, 10) is False
    
    def test_validate_stake_zero_or_negative(self):
        """Валидация нулевой или отрицательной ставки"""
        assert GameLogic.validate_stake(100, 0) is False
        assert GameLogic.validate_stake(100, -10) is False
    
    def test_get_choice_emoji(self):
        """Получение эмодзи для выбора"""
        assert GameLogic.get_choice_emoji('rock') == '✊'
        assert GameLogic.get_choice_emoji('scissors') == '✌️'
        assert GameLogic.get_choice_emoji('paper') == '✋'
        assert GameLogic.get_choice_emoji('invalid') == '❓'
    
    def test_get_result_message_player1_wins(self):
        """Формирование сообщения при победе первого игрока"""
        message = GameLogic.get_result_message(
            winner_id=1,
            player1_name="Игрок 1",
            player2_name="Игрок 2",
            choice1="rock",
            choice2="scissors"
        )
        
        assert "Игрок 1 победил!" in message
        assert "✊" in message
        assert "✌️" in message
    
    def test_get_result_message_player2_wins(self):
        """Формирование сообщения при победе второго игрока"""
        message = GameLogic.get_result_message(
            winner_id=2,
            player1_name="Игрок 1",
            player2_name="Игрок 2",
            choice1="scissors",
            choice2="rock"
        )
        
        assert "Игрок 2 победил!" in message
        assert "✌️" in message
        assert "✊" in message
    
    def test_get_result_message_draw(self):
        """Формирование сообщения при ничьей"""
        message = GameLogic.get_result_message(
            winner_id=None,
            player1_name="Игрок 1",
            player2_name="Игрок 2",
            choice1="rock",
            choice2="rock"
        )
        
        assert "Ничья!" in message
        assert "✊" in message
    
    def test_get_result_message_with_promise(self):
        """Формирование сообщения с обещанием"""
        promise_text = "Куплю кофе"
        message = GameLogic.get_result_message(
            winner_id=1,
            player1_name="Игрок 1",
            player2_name="Игрок 2",
            choice1="paper",
            choice2="rock",
            promise=promise_text
        )
        
        assert "Игрок 1 победил!" in message
        assert promise_text in message
        assert "Игрок 2" in message  # Проигравший должен выполнить обещание
    
    def test_all_winning_combinations(self):
        """Проверка всех выигрышных комбинаций"""
        winning_combos = [
            ('rock', 'scissors', 1),
            ('scissors', 'paper', 1),
            ('paper', 'rock', 1),
            ('scissors', 'rock', 2),
            ('paper', 'scissors', 2),
            ('rock', 'paper', 2)
        ]
        
        for choice1, choice2, expected_winner in winning_combos:
            winner, result_type = GameLogic.determine_winner(choice1, choice2)
            assert winner == expected_winner
            assert result_type == 'win'
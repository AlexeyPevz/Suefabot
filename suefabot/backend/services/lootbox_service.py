import random
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models import User, Item, UserItem, Transaction, TransactionType, ItemRarity, Chest
from services.transaction_service import TransactionService
from data.starter_items import LOOTBOX_CONFIG


class LootboxService:
    """Сервис для работы с лутбоксами"""
    
    @staticmethod
    def give_starter_lootbox(session: Session, user: User) -> bool:
        """
        Выдает стартовый лутбокс новому пользователю
        
        Args:
            session: Сессия БД
            user: Пользователь
            
        Returns:
            True если лутбокс выдан, False если уже был получен
        """
        # Проверяем, получал ли пользователь стартовый лутбокс
        existing = session.query(UserItem).filter_by(
            user_id=user.id,
            item_id=1  # ID стартового лутбокса
        ).first()
        
        if existing:
            return False
        
        # Выдаем стартовый лутбокс
        starter_box = session.query(Chest).filter_by(
            name='Стартовый подарок'
        ).first()
        
        if starter_box:
            user_item = UserItem(
                user_id=user.id,
                item_id=starter_box.id,
                quantity=1,
                equipped=False
            )
            session.add(user_item)
            session.commit()
            return True
        
        return False
    
    @staticmethod
    def open_lootbox(
        session: Session, 
        user: User, 
        chest_id: int
    ) -> Dict:
        """
        Открывает лутбокс и выдает награды
        
        Args:
            session: Сессия БД
            user: Пользователь
            chest_id: ID сундука
            
        Returns:
            Словарь с результатами открытия
        """
        # Получаем сундук
        chest = session.query(Chest).filter_by(id=chest_id).first()
        if not chest:
            raise ValueError("Chest not found")
        
        # Проверяем, есть ли сундук у пользователя
        user_chest = session.query(UserItem).filter_by(
            user_id=user.id,
            item_id=chest_id
        ).first()
        
        if not user_chest or user_chest.quantity <= 0:
            # Проверяем, можно ли купить
            if chest.price_stars > user.stars_balance:
                raise ValueError("Insufficient balance")
            
            # Списываем звезды
            TransactionService.create_transaction(
                session=session,
                user=user,
                transaction_type=TransactionType.CHEST_OPEN,
                amount=-chest.price_stars,
                description=f"Открытие сундука: {chest.name}"
            )
        else:
            # Уменьшаем количество сундуков
            user_chest.quantity -= 1
            if user_chest.quantity == 0:
                session.delete(user_chest)
        
        # Определяем тип сундука из конфига
        chest_type = 'common'
        for key, config in LOOTBOX_CONFIG.items():
            if config['name'] == chest.name:
                chest_type = key
                break
        
        config = LOOTBOX_CONFIG.get(chest_type, LOOTBOX_CONFIG['common'])
        
        # Генерируем награды
        items = LootboxService._generate_rewards(
            session=session,
            chest_config=config,
            items_count=chest.items_count or config['items_count']
        )
        
        # Выдаем награды пользователю
        for item in items:
            user_item = session.query(UserItem).filter_by(
                user_id=user.id,
                item_id=item.id
            ).first()
            
            if user_item:
                user_item.quantity += 1
            else:
                user_item = UserItem(
                    user_id=user.id,
                    item_id=item.id,
                    quantity=1,
                    equipped=False
                )
                session.add(user_item)
        
        session.commit()
        
        return {
            'chest': {
                'id': chest.id,
                'name': chest.name,
                'type': chest_type
            },
            'items': [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'rarity': item.rarity.value,
                    'category': item.category,
                    'emoji': item.properties.get('emoji', '🎁') if item.properties else '🎁'
                }
                for item in items
            ]
        }
    
    @staticmethod
    def _generate_rewards(
        session: Session,
        chest_config: Dict,
        items_count: int
    ) -> List[Item]:
        """
        Генерирует награды из лутбокса
        
        Args:
            session: Сессия БД
            chest_config: Конфигурация сундука
            items_count: Количество предметов
            
        Returns:
            Список предметов
        """
        rewards = []
        drop_rates = chest_config['drop_rates']
        
        # Если есть гарантированная редкость
        if 'guaranteed_rarity' in chest_config:
            guaranteed_rarity = ItemRarity[chest_config['guaranteed_rarity'].upper()]
            items = session.query(Item).filter_by(
                rarity=guaranteed_rarity,
                is_active=True
            ).all()
            
            if items:
                rewards.append(random.choice(items))
                items_count -= 1
        
        # Генерируем остальные предметы
        for _ in range(items_count):
            # Определяем редкость по drop rates
            rarity = LootboxService._roll_rarity(drop_rates)
            
            # Получаем предметы этой редкости
            items = session.query(Item).filter_by(
                rarity=rarity,
                is_active=True
            ).all()
            
            if items:
                rewards.append(random.choice(items))
        
        return rewards
    
    @staticmethod
    def _roll_rarity(drop_rates: Dict[str, float]) -> ItemRarity:
        """
        Определяет редкость предмета по вероятностям
        
        Args:
            drop_rates: Словарь с вероятностями для каждой редкости
            
        Returns:
            Редкость предмета
        """
        roll = random.random()
        cumulative = 0
        
        for rarity_str, chance in drop_rates.items():
            cumulative += chance
            if roll <= cumulative:
                return ItemRarity[rarity_str.upper()]
        
        # По умолчанию возвращаем common
        return ItemRarity.COMMON